from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import JobCategory, Position, WageTable, StaffMember, EvaluationCriteria, StaffEvaluation, PromotionRecord

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_code', 'category_name']
    search_fields = ['category_name']

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['facility', 'job_category', 'position_name', 'level', 'required_experience_months']
    list_filter = ['facility', 'job_category', 'level']
    search_fields = ['position_name']
    ordering = ['facility', 'job_category', 'level']

@admin.register(WageTable)
class WageTableAdmin(admin.ModelAdmin):
    list_display = ['position', 'base_salary_start', 'step_raise_amount', 'max_steps']
    list_filter = ['position__facility', 'position__job_category']

@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['staff_id', 'name', 'facility', 'current_position', 'employment_status', 'hire_date', 'is_active']
    list_filter = ['facility', 'employment_status', 'is_active']
    search_fields = ['staff_id', 'name']

@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display = ['job_category', 'criteria_name', 'weight', 'max_score']

@admin.register(StaffEvaluation)
class StaffEvaluationAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'evaluation_period', 'evaluation_date', 'overall_score']

@admin.register(PromotionRecord)
class PromotionRecordAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'promotion_date', 'from_position', 'to_position', 'promotion_type']

# career_management/admin.py に追加する管理画面設定
# 既存のadmin登録の後に追加してください

from django.contrib import admin
from .models import (
    CareerPathRequirementOne,
    SalaryIncreaseSystem,
    PromotionCriteria,
    TrainingPlan,
    TrainingRecord
)

# ================================================================
# キャリアパス要件Ⅰ：任用要件と賃金体系
# ================================================================

@admin.register(CareerPathRequirementOne)
class CareerPathRequirementOneAdmin(admin.ModelAdmin):
    list_display = [
        'facility',
        'position',
        'required_experience_years',
        'base_salary_min',
        'base_salary_max',
        'updated_at'
    ]
    list_filter = ['facility', 'position__job_category']
    search_fields = [
        'position__position_name',
        'job_description',
        'required_qualifications'
    ]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('facility', 'position')
        }),
        ('任用要件', {
            'fields': (
                'required_qualifications',
                'required_experience_years',
                'recommended_skills',
                'other_requirements'
            )
        }),
        ('職務内容', {
            'fields': (
                'job_description',
                'responsibilities',
                'authority'
            )
        }),
        ('賃金体系', {
            'fields': (
                'base_salary_min',
                'base_salary_max',
                'allowances',
                'raise_rules'
            )
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編集時
            return ['facility', 'position']
        return []


# ================================================================
# キャリアパス要件Ⅲ：昇給制度
# ================================================================

@admin.register(SalaryIncreaseSystem)
class SalaryIncreaseSystemAdmin(admin.ModelAdmin):
    list_display = [
        'facility',
        'has_regular_increase',
        'increase_timing',
        'increase_amount_per_step',
        'max_steps_per_year',
        'updated_at'
    ]
    list_filter = ['has_regular_increase', 'increase_timing']
    search_fields = ['facility__name']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('facility',)
        }),
        ('定期昇給', {
            'fields': (
                'has_regular_increase',
                'increase_timing',
                'increase_amount_per_step',
                'max_steps_per_year'
            )
        }),
        ('特別昇給', {
            'fields': (
                'has_special_increase',
                'special_increase_conditions'
            )
        }),
        ('評価制度', {
            'fields': (
                'evaluation_affects_raise',
                'evaluation_criteria'
            )
        }),
        ('その他', {
            'fields': ('notes',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編集時
            return ['facility']
        return []


@admin.register(PromotionCriteria)
class PromotionCriteriaAdmin(admin.ModelAdmin):
    list_display = [
        'facility',
        'from_position',
        'to_position',
        'required_experience_years',
        'required_evaluation_score'
    ]
    list_filter = ['facility', 'from_position__job_category']
    search_fields = [
        'from_position__position_name',
        'to_position__position_name'
    ]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('facility', 'from_position', 'to_position')
        }),
        ('昇格要件', {
            'fields': (
                'required_experience_years',
                'required_qualifications',
                'required_evaluation_score',
                'other_conditions'
            )
        }),
        ('審査方法', {
            'fields': ('review_process',)
        }),
    )


# ================================================================
# キャリアパス要件Ⅱ：研修計画
# ================================================================

class TrainingRecordInline(admin.TabularInline):
    model = TrainingRecord
    extra = 0
    fields = ['actual_date', 'content', 'evaluation']
    can_delete = False


@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = [
        'fiscal_year',
        'training_name',
        'training_type',
        'scheduled_date',
        'is_mandatory',
        'facility'
    ]
    list_filter = [
        'fiscal_year',
        'training_type',
        'is_mandatory',
        'facility'
    ]
    search_fields = ['training_name', 'description']
    filter_horizontal = ['target_positions']
    inlines = [TrainingRecordInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': (
                'facility',
                'fiscal_year',
                'training_name',
                'target_positions'
            )
        }),
        ('研修内容', {
            'fields': (
                'description',
                'objectives',
                'training_type',
                'duration_hours',
                'instructor'
            )
        }),
        ('実施予定', {
            'fields': (
                'scheduled_date',
                'is_mandatory'
            )
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編集時
            return ['facility', 'fiscal_year']
        return []


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = [
        'training_plan',
        'actual_date',
        'get_participants_count'
    ]
    list_filter = [
        'actual_date',
        'training_plan__fiscal_year',
        'training_plan__facility'
    ]
    search_fields = ['training_plan__training_name', 'content']
    filter_horizontal = ['participants']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('training_plan', 'actual_date')
        }),
        ('実施内容', {
            'fields': (
                'participants',
                'content',
                'evaluation',
                'attachments'
            )
        }),
    )
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    get_participants_count.short_description = '参加者数'

