from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from facility_management.models import Facility
from .models import Position, WageTable, StaffMember
from .services.wage_table_generator import WageTableGenerator

def index(request):
    """キャリア管理トップページ"""
    facilities = Facility.objects.all()[:5]
    return render(request, 'career_management/index.html', {
        'facilities': facilities
    })

def wage_table_builder(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)
    generator = WageTableGenerator(facility)
    positions = Position.objects.filter(facility=facility).order_by('job_category', 'level')
    
    suggestions = {}
    for position in positions:
        suggestions[position.id] = generator.generate_optimized_wage_table(position)

    if request.method == 'POST':
        position_id = request.POST.get('position_id')
        position = get_object_or_404(Position, id=position_id)
        wage_data = suggestions[position.id]
        WageTable.objects.update_or_create(position=position, defaults=wage_data)
        messages.success(request, f"「{position.position_name}」の賃金テーブルを保存しました。")
        return redirect('wage_table_builder', facility_id=facility_id)

    max_steps = 30
    for p in positions:
        if hasattr(p, 'wage_table') and p.wage_table.max_steps > max_steps:
            max_steps = p.wage_table.max_steps
        suggestion = suggestions.get(p.id, {})
        if suggestion.get('max_steps', 0) > max_steps:
            max_steps = suggestion['max_steps']
    
    positions_data = []
    for p in positions:
        is_saved = hasattr(p, 'wage_table')
        suggestion = suggestions[p.id]
        salary_by_step = {}
        if is_saved:
            for step in range(1, p.wage_table.max_steps + 1):
                salary_by_step[step] = p.wage_table.get_salary_for_step(step)
        else:
            for step in range(1, suggestion['max_steps'] + 1):
                salary_by_step[step] = suggestion['base_salary_start'] + (suggestion['step_raise_amount'] * (step - 1))
        
        positions_data.append({'position': p, 'suggestion': suggestion, 'is_saved': is_saved, 'salary_by_step': salary_by_step})
    
    return render(request, 'career_management/wage_table_builder.html', {
        'facility': facility,
        'positions_data': positions_data,
        'max_steps_range': range(1, max_steps + 1),
    })

def staff_list(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)
    staff_members = StaffMember.objects.filter(facility=facility, is_active=True)
    return render(request, 'career_management/staff_list.html', {'facility': facility, 'staff_members': staff_members})

def promotion_candidates(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)
    return render(request, 'career_management/promotion_candidates.html', {'facility': facility, 'candidates': []})

def staff_detail(request, staff_id):
    staff = get_object_or_404(StaffMember, id=staff_id)
    return render(request, 'career_management/staff_detail.html', {
        'staff': staff,
        'eligibility_result': {'eligible': False, 'issues': [], 'details': {}},
        'promotion_history': []
    })

# career_management/views.py に追加するビュー
# 既存のビューの後に追加してください

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import (
    CareerPathRequirementOne,
    SalaryIncreaseSystem,
    PromotionCriteria,
    TrainingPlan,
    TrainingRecord
)

# ================================================================
# キャリアパス要件設計メインメニュー
# ================================================================

def career_path_requirements_index(request, facility_id):
    """キャリアパス要件設計のメインメニュー"""
    facility = get_object_or_404(Facility, id=facility_id)
    
    # 各要件の設計状況をチェック
    requirement_one_count = CareerPathRequirementOne.objects.filter(
        facility=facility
    ).count()
    
    has_salary_system = SalaryIncreaseSystem.objects.filter(
        facility=facility
    ).exists()
    
    training_plan_count = TrainingPlan.objects.filter(
        facility=facility
    ).count()
    
    context = {
        'facility': facility,
        'requirement_one_count': requirement_one_count,
        'has_salary_system': has_salary_system,
        'training_plan_count': training_plan_count,
    }
    
    return render(
        request,
        'career_management/career_path_requirements_index.html',
        context
    )


# ================================================================
# キャリアパス要件Ⅰ：任用要件と賃金体系
# ================================================================

def requirement_one_list(request, facility_id):
    """要件Ⅰの一覧・設計画面"""
    facility = get_object_or_404(Facility, id=facility_id)
    positions = Position.objects.filter(facility=facility).order_by(
        'job_category', 'level'
    )
    
    # 各職位の要件設定状況をチェック
    positions_data = []
    for position in positions:
        try:
            requirement = position.requirement_one
            has_requirement = True
        except CareerPathRequirementOne.DoesNotExist:
            requirement = None
            has_requirement = False
        
        positions_data.append({
            'position': position,
            'requirement': requirement,
            'has_requirement': has_requirement
        })
    
    context = {
        'facility': facility,
        'positions_data': positions_data
    }
    
    return render(
        request,
        'career_management/requirement_one_list.html',
        context
    )


def requirement_one_edit(request, facility_id, position_id):
    """要件Ⅰの編集画面"""
    facility = get_object_or_404(Facility, id=facility_id)
    position = get_object_or_404(Position, id=position_id, facility=facility)
    
    # 既存の要件を取得または新規作成
    requirement, created = CareerPathRequirementOne.objects.get_or_create(
        facility=facility,
        position=position,
        defaults={
            'base_salary_min': position.wage_table.base_salary_start if hasattr(position, 'wage_table') else 200000,
            'base_salary_max': position.wage_table.get_salary_for_step(position.wage_table.max_steps) if hasattr(position, 'wage_table') else 300000,
            'required_experience_years': 0,
            'job_description': '',
            'responsibilities': '',
            'raise_rules': '定期昇給：年1回（4月）、号級昇給'
        }
    )
    
    if request.method == 'POST':
        # フォームデータを保存
        requirement.required_qualifications = request.POST.get('required_qualifications', '')
        requirement.required_experience_years = int(request.POST.get('required_experience_years', 0))
        requirement.recommended_skills = request.POST.get('recommended_skills', '')
        requirement.other_requirements = request.POST.get('other_requirements', '')
        requirement.job_description = request.POST.get('job_description', '')
        requirement.responsibilities = request.POST.get('responsibilities', '')
        requirement.authority = request.POST.get('authority', '')
        requirement.base_salary_min = int(request.POST.get('base_salary_min', 0))
        requirement.base_salary_max = int(request.POST.get('base_salary_max', 0))
        requirement.allowances = request.POST.get('allowances', '')
        requirement.raise_rules = request.POST.get('raise_rules', '')
        requirement.save()
        
        messages.success(request, f'「{position.position_name}」の要件を保存しました。')
        return redirect('requirement_one_list', facility_id=facility_id)
    
    context = {
        'facility': facility,
        'position': position,
        'requirement': requirement,
        'is_new': created
    }
    
    return render(
        request,
        'career_management/requirement_one_edit.html',
        context
    )


# ================================================================
# キャリアパス要件Ⅲ：昇給制度
# ================================================================

def requirement_three_edit(request, facility_id):
    """要件Ⅲ（昇給制度）の編集画面"""
    facility = get_object_or_404(Facility, id=facility_id)
    
    # 既存の昇給制度を取得または新規作成
    system, created = SalaryIncreaseSystem.objects.get_or_create(
        facility=facility,
        defaults={
            'has_regular_increase': True,
            'increase_timing': 'APRIL',
            'increase_amount_per_step': 1000,
            'max_steps_per_year': 4,
            'has_special_increase': False,
            'evaluation_affects_raise': True
        }
    )
    
    if request.method == 'POST':
        # フォームデータを保存
        system.has_regular_increase = request.POST.get('has_regular_increase') == 'on'
        system.increase_timing = request.POST.get('increase_timing', 'APRIL')
        system.increase_amount_per_step = int(request.POST.get('increase_amount_per_step', 1000))
        system.max_steps_per_year = int(request.POST.get('max_steps_per_year', 4))
        system.has_special_increase = request.POST.get('has_special_increase') == 'on'
        system.special_increase_conditions = request.POST.get('special_increase_conditions', '')
        system.evaluation_affects_raise = request.POST.get('evaluation_affects_raise') == 'on'
        system.evaluation_criteria = request.POST.get('evaluation_criteria', '')
        system.notes = request.POST.get('notes', '')
        system.save()
        
        messages.success(request, '昇給制度を保存しました。')
        return redirect('career_path_requirements_index', facility_id=facility_id)
    
    context = {
        'facility': facility,
        'system': system,
        'is_new': created
    }
    
    return render(
        request,
        'career_management/requirement_three_edit.html',
        context
    )


def promotion_criteria_list(request, facility_id):
    """昇格基準の一覧・設定画面"""
    facility = get_object_or_404(Facility, id=facility_id)
    criteria_list = PromotionCriteria.objects.filter(
        facility=facility
    ).select_related('from_position', 'to_position')
    
    positions = Position.objects.filter(facility=facility).order_by('level')
    
    context = {
        'facility': facility,
        'criteria_list': criteria_list,
        'positions': positions
    }
    
    return render(
        request,
        'career_management/promotion_criteria_list.html',
        context
    )


# ================================================================
# キャリアパス要件Ⅱ：研修計画
# ================================================================

def requirement_two_list(request, facility_id):
    """要件Ⅱ（研修計画）の一覧画面"""
    facility = get_object_or_404(Facility, id=facility_id)
    
    # 年度ごとにグループ化
    import datetime
    current_year = datetime.datetime.now().year
    
    training_plans = TrainingPlan.objects.filter(
        facility=facility
    ).order_by('-fiscal_year', 'scheduled_date')
    
    context = {
        'facility': facility,
        'training_plans': training_plans,
        'current_year': current_year
    }
    
    return render(
        request,
        'career_management/requirement_two_list.html',
        context
    )


def training_plan_edit(request, facility_id, plan_id=None):
    """研修計画の編集画面"""
    facility = get_object_or_404(Facility, id=facility_id)
    
    if plan_id:
        plan = get_object_or_404(TrainingPlan, id=plan_id, facility=facility)
        is_new = False
    else:
        plan = TrainingPlan(facility=facility)
        is_new = True
    
    if request.method == 'POST':
        # フォームデータを保存
        plan.fiscal_year = int(request.POST.get('fiscal_year', 2025))
        plan.training_name = request.POST.get('training_name', '')
        plan.description = request.POST.get('description', '')
        plan.objectives = request.POST.get('objectives', '')
        plan.training_type = request.POST.get('training_type', 'OJT')
        plan.duration_hours = request.POST.get('duration_hours', None)
        plan.instructor = request.POST.get('instructor', '')
        plan.is_mandatory = request.POST.get('is_mandatory') == 'on'
        
        scheduled_date = request.POST.get('scheduled_date')
        if scheduled_date:
            plan.scheduled_date = scheduled_date
        
        plan.save()
        
        # 対象職位の設定
        target_position_ids = request.POST.getlist('target_positions')
        plan.target_positions.set(target_position_ids)
        
        messages.success(request, '研修計画を保存しました。')
        return redirect('requirement_two_list', facility_id=facility_id)
    
    positions = Position.objects.filter(facility=facility)
    
    context = {
        'facility': facility,
        'plan': plan,
        'positions': positions,
        'is_new': is_new
    }
    
    return render(
        request,
        'career_management/training_plan_edit.html',
        context
    )

