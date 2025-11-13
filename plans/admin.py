from django.contrib import admin
from django.utils.html import format_html
from .models import WorkplaceInitiative, ImprovementPlan


@admin.register(WorkplaceInitiative)
class WorkplaceInitiativeAdmin(admin.ModelAdmin):
    list_display = ['item_number', 'category', 'short_description']
    list_filter = ['category']
    search_fields = ['item_number', 'description']
    ordering = ['category', 'item_number']
    
    def short_description(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    short_description.short_description = '取り組み内容'


@admin.register(ImprovementPlan)
class ImprovementPlanAdmin(admin.ModelAdmin):
    list_display = ['provider', 'fiscal_year', 'target_addition_tier', 'determined_addition_tier', 
                    'status', 'career_path_summary', 'estimated_addition_amount']
    list_filter = ['fiscal_year', 'target_addition_tier', 'status']
    search_fields = ['provider__name']
    filter_horizontal = ['target_facilities', 'workplace_initiatives']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('provider', 'fiscal_year', 'target_facilities', 'status')
        }),
        ('加算区分', {
            'fields': ('target_addition_tier', 'determined_addition_tier')
        }),
        ('キャリアパス要件', {
            'fields': ('meets_career_path_1', 'meets_career_path_2', 'meets_career_path_3', 
                      'meets_career_path_4', 'meets_career_path_5'),
            'description': 'キャリアパス要件の充足状況を選択してください'
        }),
        ('職場環境等要件', {
            'fields': ('workplace_initiatives', 'qualification_initiatives_count', 
                      'work_style_initiatives_count', 'balance_initiatives_count'),
            'description': '実施する取り組みを選択してください（各区分から1つ以上）'
        }),
        ('加算見込額', {
            'fields': ('total_service_units', 'addition_rate', 'estimated_addition_amount')
        }),
        ('配分計画', {
            'fields': ('total_salary_increase', 'base_salary_increase', 
                      'allowance_increase', 'bonus_increase')
        }),
        ('その他', {
            'fields': ('notes', 'submitted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def career_path_summary(self, obj):
        """キャリアパス要件の充足状況を表示"""
        status = []
        if obj.meets_career_path_1:
            status.append('I')
        if obj.meets_career_path_2:
            status.append('II')
        if obj.meets_career_path_3:
            status.append('III')
        if obj.meets_career_path_4:
            status.append('IV')
        if obj.meets_career_path_5:
            status.append('V')
        
        if status:
            return format_html('<span style="color: green;">✓ ' + '・'.join(status) + '</span>')
        else:
            return format_html('<span style="color: red;">✗ なし</span>')
    
    career_path_summary.short_description = 'キャリアパス要件'
    
    def save_model(self, request, obj, form, change):
        """保存時に自動計算を実行"""
        super().save_model(request, obj, form, change)
        
        # 職場環境等要件の取り組み数を計算
        obj.calculate_workplace_initiatives_count()
        
        # 取得可能な加算区分を判定
        eligible_tier = obj.determine_eligible_tier()
        if eligible_tier:
            obj.determined_addition_tier = eligible_tier
        
        # 加算見込額を計算
        obj.calculate_estimated_amount()
        
        obj.save()
