from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import ImprovementPlan, WorkplaceInitiative
from facility_management.models import Provider, Facility


def index(request):
    """トップページ"""
    plans = ImprovementPlan.objects.all().order_by('-created_at')[:5]
    return render(request, 'plans/index.html', {'recent_plans': plans})


def plan_list(request):
    """処遇改善計画書一覧"""
    plans = ImprovementPlan.objects.all().order_by('-fiscal_year', '-created_at')
    return render(request, 'plans/plan_list.html', {'plans': plans})


def plan_detail(request, plan_id):
    """処遇改善計画書詳細"""
    plan = get_object_or_404(ImprovementPlan, id=plan_id)
    
    # キャリアパス要件のチェック状況
    career_path_status = [
        {'name': 'キャリアパス要件I（職位・職責等の要件）', 'met': plan.meets_career_path_1},
        {'name': 'キャリアパス要件II（資質向上のための計画）', 'met': plan.meets_career_path_2},
        {'name': 'キャリアパス要件III（昇給の仕組み）', 'met': plan.meets_career_path_3},
        {'name': 'キャリアパス要件IV（処遇改善の見える化）', 'met': plan.meets_career_path_4},
        {'name': 'キャリアパス要件V（介護福祉士の配置）', 'met': plan.meets_career_path_5},
    ]
    
    # 職場環境等要件の状況
    workplace_status = {
        'qualification': {
            'name': '資質の向上',
            'count': plan.qualification_initiatives_count,
            'required': 1
        },
        'work_style': {
            'name': '労働環境・処遇の改善',
            'count': plan.work_style_initiatives_count,
            'required': 1
        },
        'balance': {
            'name': 'やりがい・働きがいの醸成',
            'count': plan.balance_initiatives_count,
            'required': 1
        }
    }
    
    # 加算区分判定
    eligible_tier = plan.determine_eligible_tier()
    
    context = {
        'plan': plan,
        'career_path_status': career_path_status,
        'workplace_status': workplace_status,
        'eligible_tier': eligible_tier,
    }
    
    return render(request, 'plans/plan_detail.html', context)


def plan_wizard(request):
    """処遇改善計画書作成ウィザード"""
    step = request.GET.get('step', '1')
    
    if request.method == 'POST':
        # セッションにデータを保存
        if step == '1':
            # 基本情報
            request.session['provider_id'] = request.POST.get('provider_id')
            request.session['fiscal_year'] = request.POST.get('fiscal_year')
            request.session['facility_ids'] = request.POST.getlist('facility_ids')
            request.session['target_tier'] = request.POST.get('target_tier')
            return redirect(f'/plan-wizard/?step=2')
        
        elif step == '2':
            # キャリアパス要件
            request.session['career_path_1'] = request.POST.get('career_path_1') == 'on'
            request.session['career_path_2'] = request.POST.get('career_path_2') == 'on'
            request.session['career_path_3'] = request.POST.get('career_path_3') == 'on'
            request.session['career_path_4'] = request.POST.get('career_path_4') == 'on'
            request.session['career_path_5'] = request.POST.get('career_path_5') == 'on'
            return redirect(f'/plan-wizard/?step=3')
        
        elif step == '3':
            # 職場環境等要件
            request.session['workplace_initiative_ids'] = request.POST.getlist('workplace_initiatives')
            return redirect(f'/plan-wizard/?step=4')
        
        elif step == '4':
            # 加算見込額
            request.session['total_service_units'] = request.POST.get('total_service_units')
            return redirect(f'/plan-wizard/?step=5')
        
        elif step == '5':
            # 最終確認・保存
            try:
                provider = Provider.objects.get(id=request.session.get('provider_id'))
                
                plan = ImprovementPlan.objects.create(
                    provider=provider,
                    fiscal_year=int(request.session.get('fiscal_year', 2025)),
                    target_addition_tier=request.session.get('target_tier', 'I'),
                    meets_career_path_1=request.session.get('career_path_1', False),
                    meets_career_path_2=request.session.get('career_path_2', False),
                    meets_career_path_3=request.session.get('career_path_3', False),
                    meets_career_path_4=request.session.get('career_path_4', False),
                    meets_career_path_5=request.session.get('career_path_5', False),
                    total_service_units=int(request.session.get('total_service_units', 0)),
                )
                
                # 事業所を追加
                facility_ids = request.session.get('facility_ids', [])
                for fid in facility_ids:
                    plan.target_facilities.add(fid)
                
                # 職場環境等要件の取り組みを追加
                initiative_ids = request.session.get('workplace_initiative_ids', [])
                for iid in initiative_ids:
                    plan.workplace_initiatives.add(iid)
                
                # 自動計算を実行
                plan.calculate_workplace_initiatives_count()
                plan.determined_addition_tier = plan.determine_eligible_tier()
                plan.calculate_estimated_amount()
                plan.save()
                
                # セッションをクリア
                for key in ['provider_id', 'fiscal_year', 'facility_ids', 'target_tier',
                           'career_path_1', 'career_path_2', 'career_path_3', 'career_path_4', 'career_path_5',
                           'workplace_initiative_ids', 'total_service_units']:
                    request.session.pop(key, None)
                
                messages.success(request, '処遇改善計画書を作成しました。')
                return redirect('plan_detail', plan_id=plan.id)
                
            except Exception as e:
                messages.error(request, f'エラーが発生しました: {str(e)}')
                return redirect('plan_wizard')
    
    # GET - ステップごとの表示
    context = {'step': step}
    
    if step == '1':
        context['providers'] = Provider.objects.all()
        context['facilities'] = Facility.objects.all()
    elif step == '2':
        pass  # キャリアパス要件のチェックボックス
    elif step == '3':
        context['initiatives'] = WorkplaceInitiative.objects.all().order_by('category', 'item_number')
    elif step == '4':
        pass  # 加算見込額の入力
    elif step == '5':
        # 最終確認画面
        context['summary'] = {
            'provider': Provider.objects.filter(id=request.session.get('provider_id')).first(),
            'fiscal_year': request.session.get('fiscal_year'),
            'target_tier': request.session.get('target_tier'),
            'career_path': {
                '1': request.session.get('career_path_1', False),
                '2': request.session.get('career_path_2', False),
                '3': request.session.get('career_path_3', False),
                '4': request.session.get('career_path_4', False),
                '5': request.session.get('career_path_5', False),
            }
        }
    
    return render(request, 'plans/plan_wizard.html', context)
