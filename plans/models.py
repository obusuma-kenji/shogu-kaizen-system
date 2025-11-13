from django.db import models
from facility_management.models import Facility, Provider


class WorkplaceInitiative(models.Model):
    """職場環境等要件の取り組み項目"""
    CATEGORY_CHOICES = [
        ('qualification', '資質の向上'),
        ('work_style', '労働環境・処遇の改善'),
        ('balance', 'やりがい・働きがいの醸成'),
    ]
    
    category = models.CharField("区分", max_length=20, choices=CATEGORY_CHOICES)
    item_number = models.CharField("項目番号", max_length=10)
    description = models.TextField("取り組み内容")
    
    class Meta:
        ordering = ['category', 'item_number']
        verbose_name = "職場環境等要件項目"
        verbose_name_plural = "職場環境等要件項目"
    
    def __str__(self):
        return f"[{self.get_category_display()}] {self.item_number}: {self.description[:30]}"


class ImprovementPlan(models.Model):
    """処遇改善計画書"""
    
    ADDITION_TIER_CHOICES = [
        ('I', '処遇改善加算I'),
        ('II', '処遇改善加算II'),
        ('III', '処遇改善加算III'),
        ('IV', '処遇改善加算IV'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '作成中'),
        ('submitted', '提出済み'),
        ('approved', '承認済み'),
        ('rejected', '差し戻し'),
    ]
    
    # 基本情報
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, verbose_name="事業者")
    fiscal_year = models.IntegerField("対象年度", default=2025)
    target_facilities = models.ManyToManyField(Facility, verbose_name="対象事業所")
    
    # 加算情報
    target_addition_tier = models.CharField("申請する加算区分", max_length=3, choices=ADDITION_TIER_CHOICES)
    determined_addition_tier = models.CharField("判定された加算区分", max_length=3, choices=ADDITION_TIER_CHOICES, blank=True)
    
    # キャリアパス要件の充足状況
    meets_career_path_1 = models.BooleanField("キャリアパス要件I（職位・職責・職務内容等の要件）", default=False)
    meets_career_path_2 = models.BooleanField("キャリアパス要件II（資質向上のための計画）", default=False)
    meets_career_path_3 = models.BooleanField("キャリアパス要件III（経験・資格等に応じた昇給の仕組み）", default=False)
    meets_career_path_4 = models.BooleanField("キャリアパス要件IV（昇給以外の処遇改善の見える化）", default=False)
    meets_career_path_5 = models.BooleanField("キャリアパス要件V（介護福祉士の配置等）", default=False)
    
    # 職場環境等要件
    workplace_initiatives = models.ManyToManyField(WorkplaceInitiative, verbose_name="実施する取り組み", blank=True)
    qualification_initiatives_count = models.IntegerField("資質の向上の取り組み数", default=0)
    work_style_initiatives_count = models.IntegerField("労働環境・処遇の改善の取り組み数", default=0)
    balance_initiatives_count = models.IntegerField("やりがい・働きがいの醸成の取り組み数", default=0)
    
    # 加算見込額
    total_service_units = models.BigIntegerField("総単位数（年間見込み）", default=0, help_text="前年度実績等から算出")
    estimated_addition_amount = models.BigIntegerField("加算見込額（円/年）", default=0)
    addition_rate = models.DecimalField("加算率（%）", max_digits=5, decimal_places=2, default=0)
    
    # 配分計画
    total_salary_increase = models.BigIntegerField("賃金改善総額", default=0)
    base_salary_increase = models.BigIntegerField("基本給の引き上げ", default=0)
    allowance_increase = models.BigIntegerField("手当の引き上げ", default=0)
    bonus_increase = models.BigIntegerField("賞与の引き上げ", default=0)
    
    # 管理情報
    status = models.CharField("ステータス", max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    submitted_at = models.DateTimeField("提出日時", null=True, blank=True)
    
    # 備考
    notes = models.TextField("備考・特記事項", blank=True)
    
    class Meta:
        ordering = ['-fiscal_year', '-created_at']
        verbose_name = "処遇改善計画書"
        verbose_name_plural = "処遇改善計画書"
    
    def __str__(self):
        return f"{self.provider.name} - {self.fiscal_year}年度 {self.get_target_addition_tier_display()}"
    
    def get_career_path_status(self):
        """キャリアパス要件の充足状況を返す"""
        return {
            'requirement_1': self.meets_career_path_1,
            'requirement_2': self.meets_career_path_2,
            'requirement_3': self.meets_career_path_3,
            'requirement_4': self.meets_career_path_4,
            'requirement_5': self.meets_career_path_5,
        }
    
    def calculate_workplace_initiatives_count(self):
        """職場環境等要件の区分別取り組み数を計算"""
        initiatives = self.workplace_initiatives.all()
        self.qualification_initiatives_count = initiatives.filter(category='qualification').count()
        self.work_style_initiatives_count = initiatives.filter(category='work_style').count()
        self.balance_initiatives_count = initiatives.filter(category='balance').count()
        self.save()
    
    def determine_eligible_tier(self):
        """取得可能な加算区分を判定"""
        # 加算I: キャリアパス要件I+II+III、職場環境等要件（各区分1つ以上）
        if (self.meets_career_path_1 and self.meets_career_path_2 and self.meets_career_path_3 and
            self.qualification_initiatives_count >= 1 and 
            self.work_style_initiatives_count >= 1 and 
            self.balance_initiatives_count >= 1):
            return 'I'
        
        # 加算II: キャリアパス要件I+II、職場環境等要件（各区分1つ以上）
        elif (self.meets_career_path_1 and self.meets_career_path_2 and
              self.qualification_initiatives_count >= 1 and 
              self.work_style_initiatives_count >= 1 and 
              self.balance_initiatives_count >= 1):
            return 'II'
        
        # 加算III: キャリアパス要件I+II
        elif self.meets_career_path_1 and self.meets_career_path_2:
            return 'III'
        
        # 加算IV: キャリアパス要件I または II のいずれか
        elif self.meets_career_path_1 or self.meets_career_path_2:
            return 'IV'
        
        else:
            return None
    
    def calculate_addition_rate(self):
        """加算率を計算"""
        tier_rates = {
            'I': 16.5,   # 加算I: 16.5%
            'II': 13.7,  # 加算II: 13.7%
            'III': 5.9,  # 加算III: 5.9%
            'IV': 3.3,   # 加算IV: 3.3%
        }
        tier = self.determined_addition_tier or self.target_addition_tier
        return tier_rates.get(tier, 0)
    
    def calculate_estimated_amount(self):
        """加算見込額を計算（簡易版）"""
        rate = self.calculate_addition_rate()
        self.addition_rate = rate
        # 単位数 × 加算率 × 10円（単位単価の概算）
        self.estimated_addition_amount = int(self.total_service_units * rate / 100 * 10)
        self.save()
        return self.estimated_addition_amount
