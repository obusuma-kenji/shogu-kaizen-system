from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from facility_management.models import Facility # 修正点

class JobCategory(models.Model):
    """職種分類マスタ"""
    CATEGORY_CHOICES = [
        ('care', '介護職員'), ('nursing', '看護職員'), ('support', '生活相談員'),
        ('therapy', '機能訓練指導員'), ('nutrition', '栄養士'), ('admin', '事務職員'),
        ('other', 'その他'),
    ]
    category_code = models.CharField("職種コード", max_length=20, choices=CATEGORY_CHOICES, unique=True)
    category_name = models.CharField("職種名", max_length=50)
    def __str__(self): return self.category_name

class Position(models.Model):
    """職位階層定義"""
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='positions')
    job_category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    position_name = models.CharField("職位名", max_length=50)
    level = models.IntegerField("階層レベル", validators=[MinValueValidator(1), MaxValueValidator(10)])
    required_experience_months = models.IntegerField("必要経験月数", default=0)
    required_qualifications = models.TextField("必要資格・要件", blank=True)
    job_description = models.TextField("職務内容", blank=True)
    class Meta:
        unique_together = ['facility', 'job_category', 'level']
        ordering = ['job_category', 'level']
    def __str__(self): return f"{self.facility.name} - {self.job_category.category_name} - {self.position_name}"

class WageTable(models.Model):
    """ゾーン型の号級賃金テーブル"""
    position = models.OneToOneField(Position, on_delete=models.CASCADE, related_name='wage_table')

   # 号級テーブルのパラメータ
    base_salary_start = models.PositiveIntegerField("初任給（1号）", default=0) # default=0 を追加
    step_raise_amount = models.PositiveIntegerField("1号あたりの昇給額", default=0) # default=0 を追加
    max_steps = models.PositiveIntegerField("最大号数", default=20)
    
    # 手当（号級とは別に加算）
    qualification_allowance = models.IntegerField("資格手当", default=0)
    position_allowance = models.IntegerField("役職手当", default=0)

    def __str__(self):
        return f"{self.position.position_name}の賃金テーブル"

    def get_salary_for_step(self, step):
        """指定された号数の基本給を計算する"""
        if step > self.max_steps:
            step = self.max_steps

        salary = self.base_salary_start + (self.step_raise_amount * (step - 1))
        return salary
class StaffMember(models.Model):
    """職員情報"""
    EMPLOYMENT_STATUS_CHOICES = [
        ('full_time', '正職員'),
        ('part_time', 'パート職員'),
        ('contract', '契約職員'),
        ('temp', '派遣職員'),
    ]
    
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='staff_members')
    
    # 基本情報
    staff_id = models.CharField("職員番号", max_length=20, unique=True)
    name = models.CharField("氏名", max_length=100)
    employment_status = models.CharField("雇用形態", max_length=20, choices=EMPLOYMENT_STATUS_CHOICES)
    
    # 職歴情報
    hire_date = models.DateField("入職日")
    current_position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    
    # 給与情報
    current_base_salary = models.IntegerField("現在の基本給", default=0)
    current_total_salary = models.IntegerField("現在の総給与", default=0)
    
    # 資格情報
    qualifications = models.TextField("保有資格", blank=True, help_text="改行区切りで入力")
    qualification_acquisition_dates = models.TextField("資格取得日", blank=True)
    
    # 評価情報
    latest_evaluation_score = models.DecimalField("最新評価点数", max_digits=3, decimal_places=1, default=0.0)
    latest_evaluation_date = models.DateField("最新評価日", null=True, blank=True)
    
    # システム項目
    is_active = models.BooleanField("在籍中", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def experience_months(self):
        """経験月数の計算"""
        from datetime import date
        if self.hire_date:
            today = date.today()
            return (today.year - self.hire_date.year) * 12 + (today.month - self.hire_date.month)
        return 0
    
    @property
    def experience_years(self):
        """経験年数の計算"""
        return self.experience_months // 12
    
    def check_promotion_eligibility(self, target_position):
        """昇格適性のチェック"""
        if not target_position:
            return False, []
        
        issues = []
        
        # 経験年数チェック
        if self.experience_months < target_position.required_experience_months:
            issues.append(f"経験年数不足（必要: {target_position.required_experience_months}ヶ月, 現在: {self.experience_months}ヶ月）")
        
        # 評価点数チェック
        if self.latest_evaluation_score < target_position.required_evaluation_score:
            issues.append(f"評価点数不足（必要: {target_position.required_evaluation_score}, 現在: {self.latest_evaluation_score}）")
        
        # 資格チェック（簡易版）
        if target_position.required_qualifications:
            required_quals = target_position.required_qualifications.lower()
            staff_quals = self.qualifications.lower() if self.qualifications else ""
            if "介護福祉士" in required_quals and "介護福祉士" not in staff_quals:
                issues.append("介護福祉士資格が必要")
        
        return len(issues) == 0, issues
    
    def __str__(self):
        return f"{self.name} ({self.facility.name})"

class EvaluationCriteria(models.Model):
    """評価基準"""
    job_category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    
    criteria_name = models.CharField("評価項目名", max_length=100)
    criteria_description = models.TextField("評価基準説明")
    weight = models.DecimalField("重み", max_digits=3, decimal_places=2, default=1.0)
    max_score = models.IntegerField("最高点", default=5)
    
    def __str__(self):
        return f"{self.job_category.category_name} - {self.criteria_name}"

class StaffEvaluation(models.Model):
    """職員評価記録"""
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='evaluations')
    evaluation_period = models.CharField("評価期間", max_length=20, help_text="例: 2025年上期")
    evaluation_date = models.DateField("評価日")
    
    # 総合評価
    overall_score = models.DecimalField("総合評価点数", max_digits=3, decimal_places=1)
    overall_comment = models.TextField("総合コメント", blank=True)
    
    # 評価者情報
    evaluator_name = models.CharField("評価者名", max_length=100)
    
    def __str__(self):
        return f"{self.staff_member.name} - {self.evaluation_period}"

class PromotionRecord(models.Model):
    """昇進・昇格記録"""
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='promotions')
    
    from_position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='promotions_from')
    to_position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='promotions_to')
    
    promotion_date = models.DateField("昇格日")
    promotion_type = models.CharField("昇格種別", max_length=50, 
                                    choices=[('regular', '定期昇格'), ('special', '特別昇格'), ('lateral', '配置転換')])
    
    salary_before = models.IntegerField("昇格前給与")
    salary_after = models.IntegerField("昇格後給与")
    
    reason = models.TextField("昇格理由", blank=True)
    approved_by = models.CharField("承認者", max_length=100)
    
    def __str__(self):
        return f"{self.staff_member.name} - {self.to_position.position_name}昇格"

# career_management/models.py に追加するモデル
# 既存のモデルの後に追加してください

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# ================================================================
# キャリアパス要件設計モデル
# ================================================================

class CareerPathRequirementOne(models.Model):
    """
    キャリアパス要件Ⅰ：任用要件と賃金体系
    職位ごとの任用要件・職務内容・賃金体系を定義
    """
    facility = models.ForeignKey(
        'facility_management.Facility',
        on_delete=models.CASCADE,
        related_name='career_requirements_one'
    )
    position = models.OneToOneField(
        'Position',
        on_delete=models.CASCADE,
        related_name='requirement_one'
    )
    
    # 任用要件
    required_qualifications = models.TextField(
        verbose_name='必要資格',
        help_text='例：介護福祉士、実務者研修修了者',
        blank=True
    )
    required_experience_years = models.IntegerField(
        verbose_name='必要経験年数',
        default=0,
        validators=[MinValueValidator(0)]
    )
    recommended_skills = models.TextField(
        verbose_name='推奨スキル・能力',
        blank=True,
        help_text='この職位で求められるスキルや能力'
    )
    other_requirements = models.TextField(
        verbose_name='その他要件',
        blank=True
    )
    
    # 職務内容
    job_description = models.TextField(
        verbose_name='主な業務内容',
        help_text='具体的な業務内容を記載'
    )
    responsibilities = models.TextField(
        verbose_name='責任範囲',
        help_text='この職位が担う責任範囲'
    )
    authority = models.TextField(
        verbose_name='権限',
        help_text='この職位に与えられる権限',
        blank=True
    )
    
    # 賃金体系（WageTableと連携）
    base_salary_min = models.IntegerField(
        verbose_name='基本給（最低額）',
        help_text='円',
        validators=[MinValueValidator(0)]
    )
    base_salary_max = models.IntegerField(
        verbose_name='基本給（最高額）',
        help_text='円',
        validators=[MinValueValidator(0)]
    )
    allowances = models.TextField(
        verbose_name='各種手当',
        help_text='職務手当、資格手当など',
        blank=True
    )
    raise_rules = models.TextField(
        verbose_name='昇給ルール',
        help_text='定期昇給、号級昇給などのルール'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'キャリアパス要件Ⅰ'
        verbose_name_plural = 'キャリアパス要件Ⅰ（任用要件と賃金体系）'
        ordering = ['position__level', 'position__job_category']
    
    def __str__(self):
        return f"{self.facility.name} - {self.position.position_name}"


class SalaryIncreaseSystem(models.Model):
    """
    キャリアパス要件Ⅲ：昇給制度
    事業所全体の昇給制度の基本設計
    """
    TIMING_CHOICES = [
        ('APRIL', '4月'),
        ('OCTOBER', '10月'),
        ('BOTH', '4月・10月（年2回）'),
        ('OTHER', 'その他'),
    ]
    
    facility = models.OneToOneField(
        'facility_management.Facility',
        on_delete=models.CASCADE,
        related_name='salary_increase_system'
    )
    
    # 定期昇給
    has_regular_increase = models.BooleanField(
        verbose_name='定期昇給の有無',
        default=True
    )
    increase_timing = models.CharField(
        verbose_name='定期昇給時期',
        max_length=20,
        choices=TIMING_CHOICES,
        default='APRIL'
    )
    increase_amount_per_step = models.IntegerField(
        verbose_name='1号級あたりの昇給額',
        help_text='円',
        default=1000,
        validators=[MinValueValidator(0)]
    )
    max_steps_per_year = models.IntegerField(
        verbose_name='年間最大昇給号級数',
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # 特別昇給
    has_special_increase = models.BooleanField(
        verbose_name='特別昇給制度の有無',
        default=False
    )
    special_increase_conditions = models.TextField(
        verbose_name='特別昇給の条件',
        blank=True,
        help_text='資格取得、優秀な評価など'
    )
    
    # 評価との連携
    evaluation_affects_raise = models.BooleanField(
        verbose_name='評価が昇給に影響するか',
        default=True
    )
    evaluation_criteria = models.TextField(
        verbose_name='評価基準',
        blank=True,
        help_text='評価と昇給の関係性を記載'
    )
    
    # その他
    notes = models.TextField(
        verbose_name='備考',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'キャリアパス要件Ⅲ（昇給制度）'
        verbose_name_plural = 'キャリアパス要件Ⅲ（昇給制度）'
    
    def __str__(self):
        return f"{self.facility.name} - 昇給制度"


class PromotionCriteria(models.Model):
    """
    昇格基準
    職位から職位への昇格に必要な要件を定義
    """
    facility = models.ForeignKey(
        'facility_management.Facility',
        on_delete=models.CASCADE,
        related_name='promotion_criteria'
    )
    from_position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        related_name='promotion_from',
        verbose_name='昇格元職位'
    )
    to_position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        related_name='promotion_to',
        verbose_name='昇格先職位'
    )
    
    # 要件
    required_experience_years = models.IntegerField(
        verbose_name='必要経験年数',
        help_text='現職位での経験年数',
        validators=[MinValueValidator(0)]
    )
    required_qualifications = models.TextField(
        verbose_name='必要資格',
        help_text='例：介護福祉士、実務者研修修了',
        blank=True
    )
    required_evaluation_score = models.DecimalField(
        verbose_name='必要評価点数',
        max_digits=3,
        decimal_places=1,
        help_text='5段階評価の平均など',
        null=True,
        blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    other_conditions = models.TextField(
        verbose_name='その他条件',
        blank=True,
        help_text='研修受講、推薦など'
    )
    
    # 昇格審査
    review_process = models.TextField(
        verbose_name='昇格審査方法',
        help_text='面接、実技試験、レポート提出など'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '昇格基準'
        verbose_name_plural = '昇格基準'
        unique_together = ['facility', 'from_position', 'to_position']
        ordering = ['from_position__level', 'to_position__level']
    
    def __str__(self):
        return f"{self.from_position.position_name} → {self.to_position.position_name}"


class TrainingPlan(models.Model):
    """
    キャリアパス要件Ⅱ：研修計画
    年間の研修計画を管理
    """
    TRAINING_TYPE_CHOICES = [
        ('OJT', 'OJT（職場内訓練）'),
        ('OFF_JT', 'Off-JT（職場外訓練）'),
        ('EXTERNAL', '外部研修'),
        ('ONLINE', 'オンライン研修'),
    ]
    
    facility = models.ForeignKey(
        'facility_management.Facility',
        on_delete=models.CASCADE,
        related_name='training_plans'
    )
    fiscal_year = models.IntegerField(
        verbose_name='年度',
        help_text='例：2025'
    )
    training_name = models.CharField(
        verbose_name='研修名',
        max_length=200
    )
    target_positions = models.ManyToManyField(
        'Position',
        verbose_name='対象職位',
        related_name='training_plans'
    )
    description = models.TextField(
        verbose_name='研修内容',
        help_text='研修の具体的な内容'
    )
    objectives = models.TextField(
        verbose_name='目標・到達目標',
        help_text='この研修で達成すべき目標'
    )
    scheduled_date = models.DateField(
        verbose_name='実施予定日',
        null=True,
        blank=True
    )
    training_type = models.CharField(
        verbose_name='研修形態',
        max_length=20,
        choices=TRAINING_TYPE_CHOICES
    )
    duration_hours = models.DecimalField(
        verbose_name='研修時間',
        max_digits=4,
        decimal_places=1,
        help_text='時間',
        null=True,
        blank=True
    )
    instructor = models.CharField(
        verbose_name='講師・担当者',
        max_length=200,
        blank=True
    )
    is_mandatory = models.BooleanField(
        verbose_name='必須研修',
        default=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'キャリアパス要件Ⅱ（研修計画）'
        verbose_name_plural = 'キャリアパス要件Ⅱ（研修計画）'
        ordering = ['-fiscal_year', 'scheduled_date']
    
    def __str__(self):
        return f"{self.fiscal_year}年度 - {self.training_name}"


class TrainingRecord(models.Model):
    """
    研修実施記録
    実際に実施した研修の記録
    """
    training_plan = models.ForeignKey(
        'TrainingPlan',
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='研修計画'
    )
    actual_date = models.DateField(
        verbose_name='実施日'
    )
    participants = models.ManyToManyField(
        'StaffMember',
        verbose_name='参加者',
        related_name='training_records'
    )
    content = models.TextField(
        verbose_name='実施内容',
        help_text='実際に実施した内容'
    )
    evaluation = models.TextField(
        verbose_name='評価・フィードバック',
        blank=True,
        help_text='研修の評価、参加者のフィードバック'
    )
    attachments = models.TextField(
        verbose_name='添付資料',
        blank=True,
        help_text='資料のファイル名やパスなど'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '研修実施記録'
        verbose_name_plural = '研修実施記録'
        ordering = ['-actual_date']
    
    def __str__(self):
        return f"{self.training_plan.training_name} - {self.actual_date}"
