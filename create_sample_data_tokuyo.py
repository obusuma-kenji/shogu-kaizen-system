"""
特別養護老人ホームのサンプルデータ作成スクリプト（完全版）
実際のモデル定義に完全対応
"""
import os
import sys
import django
from datetime import date
from decimal import Decimal

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shogu_kaizen_system.settings')
django.setup()

from facility_management.models import Provider, Facility
from career_management.models import (
    JobCategory, Position, WageTable, StaffMember,
    CareerPathRequirementOne, TrainingPlan, SalaryIncreaseSystem
)
from plans.models import ImprovementPlan, WorkplaceInitiative

def create_sample_data():
    print("=" * 60)
    print("特別養護老人ホーム サンプルデータ作成開始")
    print("=" * 60)
    
    # 1. 事業者の作成
    print("\n[1] 事業者を作成中...")
    provider, created = Provider.objects.get_or_create(
        name="社会福祉法人 さくら会",
        defaults={
            'address': '東京都世田谷区桜新町1-2-3',
            'phone': '03-1234-5678'
        }
    )
    if created:
        print(f"✓ 事業者を作成: {provider.name}")
    else:
        print(f"✓ 事業者を確認: {provider.name}")
    
    # 2. 事業所の作成
    print("\n[2] 事業所を作成中...")
    facility, created = Facility.objects.get_or_create(
        facility_number="1234567890",
        defaults={
            'name': "特別養護老人ホーム さくらの里",
            'provider': provider,
            'service_type': 'special_nursing_home',
            'address': '東京都世田谷区桜新町2-3-4',
            'phone': '03-1234-5679',
            'capacity': 100,
            'staff_count': 15
        }
    )
    if created:
        print(f"✓ 事業所を作成: {facility.name}")
    else:
        print(f"✓ 事業所を確認: {facility.name}")
    
    # 3. 職種の作成
    print("\n[3] 職種を作成中...")
    job_categories = [
        ('care', '介護職員'),
        ('nursing', '看護職員'),
        ('support', '生活相談員'),
        ('admin', '管理職'),
    ]
    
    job_category_objects = {}
    for code, name in job_categories:
        jc, created = JobCategory.objects.get_or_create(
            category_code=code,
            defaults={'category_name': name}
        )
        job_category_objects[code] = jc
        if created:
            print(f"  ✓ {jc.category_name}")
    
    # 4. 職位の作成
    print("\n[4] 職位を作成中...")
    positions_data = [
        ('care', 1, '介護職員', 0),
        ('care', 2, '主任介護職員', 36),
        ('care', 3, 'フロアリーダー', 60),
        ('nursing', 1, '看護師', 0),
        ('nursing', 3, '看護師長', 84),
        ('support', 1, '生活相談員', 0),
        ('admin', 4, '副施設長', 120),
        ('admin', 5, '施設長', 180),
    ]
    
    position_objects = {}
    for code, level, name, exp_months in positions_data:
        jc = job_category_objects[code]
        pos, created = Position.objects.get_or_create(
            facility=facility,
            job_category=jc,
            level=level,
            defaults={
                'position_name': name,
                'required_experience_months': exp_months,
                'job_description': f'{name}としての業務'
            }
        )
        position_objects[name] = pos
        if created:
            print(f"  ✓ {pos.position_name} (Lv.{pos.level})")
    
    # 5. 賃金テーブルの作成
    print("\n[5] 賃金テーブルを作成中...")
    wage_tables_data = [
        ('介護職員', 180000, 3000, 20),
        ('主任介護職員', 220000, 4000, 20),
        ('フロアリーダー', 270000, 5000, 20),
        ('看護師', 240000, 4000, 20),
        ('看護師長', 300000, 6000, 15),
        ('生活相談員', 200000, 3500, 20),
        ('副施設長', 350000, 8000, 10),
        ('施設長', 450000, 10000, 10),
    ]
    
    wage_count = 0
    for pos_name, base_start, raise_amount, max_steps in wage_tables_data:
        if pos_name in position_objects:
            pos = position_objects[pos_name]
            wt, created = WageTable.objects.get_or_create(
                position=pos,
                defaults={
                    'base_salary_start': base_start,
                    'step_raise_amount': raise_amount,
                    'max_steps': max_steps,
                    'qualification_allowance': 0,
                    'position_allowance': 0
                }
            )
            if created:
                wage_count += 1
    print(f"  ✓ {wage_count}件の賃金テーブルを作成")
    
    # 6. 職員の作成
    print("\n[6] 職員を作成中...")
    staff_data = [
        ('山田 次郎', '施設長', 'S2025001', 'full_time', date(2005, 4, 1), 500000, '介護福祉士'),
        ('佐藤 花子', '副施設長', 'S2025002', 'full_time', date(2010, 4, 1), 385000, '介護福祉士'),
        ('鈴木 一郎', 'フロアリーダー', 'S2025003', 'full_time', date(2015, 4, 1), 295000, '介護福祉士'),
        ('田中 美咲', 'フロアリーダー', 'S2025004', 'full_time', date(2016, 4, 1), 290000, '介護福祉士'),
        ('高橋 健太', '主任介護職員', 'S2025005', 'full_time', date(2018, 4, 1), 240000, '介護福祉士'),
        ('伊藤 さくら', '主任介護職員', 'S2025006', 'full_time', date(2019, 4, 1), 235000, '介護福祉士'),
        ('渡辺 大輔', '介護職員', 'S2025007', 'full_time', date(2021, 4, 1), 195000, '介護福祉士'),
        ('山本 愛', '介護職員', 'S2025008', 'full_time', date(2022, 4, 1), 187000, '介護職員初任者研修'),
        ('中村 優希', '介護職員', 'S2025009', 'full_time', date(2023, 4, 1), 183000, '介護職員初任者研修'),
        ('小林 翔太', '介護職員', 'S2025010', 'part_time', date(2024, 4, 1), 180000, '介護職員初任者研修'),
        ('加藤 恵子', '看護師長', 'S2025011', 'full_time', date(2012, 4, 1), 330000, '看護師'),
        ('吉田 真由美', '看護師', 'S2025012', 'full_time', date(2019, 4, 1), 260000, '看護師'),
        ('山口 陽子', '看護師', 'S2025013', 'full_time', date(2021, 4, 1), 250000, '看護師'),
        ('松本 拓也', '生活相談員', 'S2025014', 'full_time', date(2016, 4, 1), 235000, '社会福祉士'),
        ('井上 美穂', '生活相談員', 'S2025015', 'full_time', date(2020, 4, 1), 215000, '社会福祉士'),
    ]
    
    staff_count = 0
    for name, pos_name, staff_id, emp_status, hire_date, salary, qual in staff_data:
        if pos_name in position_objects:
            pos = position_objects[pos_name]
            sm, created = StaffMember.objects.get_or_create(
                staff_id=staff_id,
                defaults={
                    'name': name,
                    'facility': facility,
                    'current_position': pos,
                    'employment_status': emp_status,
                    'hire_date': hire_date,
                    'current_base_salary': salary,
                    'current_total_salary': salary,
                    'qualifications': qual,
                    'is_active': True
                }
            )
            if created:
                staff_count += 1
                print(f"  ✓ {sm.name} ({pos.position_name})")
    
    print(f"  合計: {staff_count}名の職員を作成")
    
    # 7. キャリアパス要件Ⅰの作成
    print("\n[7] キャリアパス要件Ⅰを作成中...")
    req1_data = [
        {
            'position_name': '介護職員',
            'required_qualifications': '介護職員初任者研修以上',
            'required_experience_years': 0,
            'job_description': '入居者の日常生活支援、身体介護、レクリエーション活動の支援',
            'responsibilities': '担当入居者のケア実施、チーム内での協働',
            'base_salary_min': 180000,
            'base_salary_max': 210000,
            'raise_rules': '年1回定期昇給、評価に基づき1〜4号昇給'
        },
        {
            'position_name': '主任介護職員',
            'required_qualifications': '介護福祉士',
            'required_experience_years': 3,
            'job_description': 'チームリーダーとして介護職員の指導、入居者ケアの統括',
            'responsibilities': 'チームマネジメント、新人職員の指導、ケアプラン作成支援',
            'base_salary_min': 220000,
            'base_salary_max': 260000,
            'raise_rules': '年1回定期昇給、評価に基づき1〜4号昇給'
        },
        {
            'position_name': 'フロアリーダー',
            'required_qualifications': '介護福祉士 + リーダー研修修了',
            'required_experience_years': 5,
            'job_description': 'フロア全体の管理、職員育成、ケアプラン作成支援',
            'responsibilities': 'フロア運営責任、職員育成計画策定、ケア品質管理',
            'base_salary_min': 270000,
            'base_salary_max': 320000,
            'raise_rules': '年1回定期昇給、評価に基づき1〜5号昇給'
        },
    ]
    
    req1_count = 0
    for req_data in req1_data:
        pos_name = req_data.pop('position_name')
        if pos_name in position_objects:
            pos = position_objects[pos_name]
            req1, created = CareerPathRequirementOne.objects.get_or_create(
                facility=facility,
                position=pos,
                defaults=req_data
            )
            if created:
                req1_count += 1
                print(f"  ✓ {pos.position_name}の要件を作成")
    
    print(f"  合計: {req1_count}件の要件Ⅰを作成")
    
    # 8. キャリアパス要件Ⅱ（研修計画）の作成
    print("\n[8] キャリアパス要件Ⅱ（研修計画）を作成中...")
    training_plans = [
        {
            'training_name': '新入職員研修',
            'target_positions': ['介護職員'],
            'description': '施設概要、介護の基本、感染症対策、緊急時対応',
            'objectives': '基本的な介護技術の習得、施設ルールの理解',
            'training_type': 'OJT',
            'duration_hours': 16,
            'is_mandatory': True
        },
        {
            'training_name': '介護技術向上研修',
            'target_positions': ['介護職員', '主任介護職員'],
            'description': '移乗介助、排泄介助、食事介助の技術向上',
            'objectives': '安全で快適な介護技術の習得',
            'training_type': 'OFF_JT',
            'duration_hours': 8,
            'is_mandatory': True
        },
        {
            'training_name': 'リーダー養成研修',
            'target_positions': ['主任介護職員'],
            'description': 'チームマネジメント、職員指導、問題解決技法',
            'objectives': 'リーダーシップスキルの向上',
            'training_type': 'EXTERNAL',
            'duration_hours': 24,
            'is_mandatory': True
        },
        {
            'training_name': '認知症ケア研修',
            'target_positions': ['フロアリーダー', '主任介護職員'],
            'description': '認知症の理解、BPSDへの対応、パーソンセンタードケア',
            'objectives': '認知症ケアの専門知識習得',
            'training_type': 'EXTERNAL',
            'duration_hours': 16,
            'is_mandatory': True
        },
    ]
    
    req2_count = 0
    for plan_data in training_plans:
        target_pos_names = plan_data.pop('target_positions')
        tp, created = TrainingPlan.objects.get_or_create(
            facility=facility,
            fiscal_year=2025,
            training_name=plan_data['training_name'],
            defaults=plan_data
        )
        
        # 常に対象職位を設定
        target_positions = [position_objects[name] for name in target_pos_names if name in position_objects]
        tp.target_positions.set(target_positions)
        
        if created:
            req2_count += 1
            print(f"  ✓ {tp.training_name}")
    
    print(f"  合計: {req2_count}件の研修計画を作成")
    
    # 9. キャリアパス要件Ⅲ（昇給制度）の作成
    print("\n[9] キャリアパス要件Ⅲ（昇給制度）を作成中...")
    sis, created = SalaryIncreaseSystem.objects.get_or_create(
        facility=facility,
        defaults={
            'has_regular_increase': True,
            'increase_timing': 'APRIL',
            'increase_amount_per_step': 3000,
            'max_steps_per_year': 4,
            'has_special_increase': True,
            'special_increase_conditions': '資格取得（介護福祉士、ケアマネ等）、業務改善提案の実現、優秀な評価',
            'evaluation_affects_raise': True,
            'evaluation_criteria': '年2回の人事評価（4月・10月）。5段階評価で3以上が標準昇給、4以上で加算昇給',
            'notes': '特別昇給は年間最大2号まで。資格取得時は即時反映。'
        }
    )
    if created:
        print(f"  ✓ 昇給制度を作成")
    else:
        print(f"  ✓ 昇給制度を確認")
    
    # 10. 処遇改善計画書の作成
    print("\n[10] 処遇改善計画書を作成中...")
    plan, created = ImprovementPlan.objects.get_or_create(
        provider=provider,
        fiscal_year=2025,
        defaults={
            'target_addition_tier': 'I',
            'meets_career_path_1': True,
            'meets_career_path_2': True,
            'meets_career_path_3': True,
            'meets_career_path_4': False,
            'meets_career_path_5': False,
            'estimated_addition_amount': 12500000,
            'status': 'draft'
        }
    )
    
    if created or True:
        # 対象事業所を設定（ManyToManyフィールド）
        plan.target_facilities.add(facility)
        
        # 職場環境等要件を選択（14項目から3つ以上）
        initiatives = WorkplaceInitiative.objects.filter(
            item_number__in=['1-1', '2-1', '3-1']
        )
        if initiatives.exists():
            plan.workplace_initiatives.set(initiatives)
            print(f"  ✓ 処遇改善計画書を作成（職場環境等要件{initiatives.count()}件選択）")
        else:
            print(f"  ✓ 処遇改善計画書を作成")
            print(f"  ⚠ 職場環境等要件が見つかりません（load_workplace_initiatives.pyを実行してください）")
    else:
        print(f"  ✓ 処遇改善計画書を確認")
    
    print("\n" + "=" * 60)
    print("サンプルデータ作成完了！")
    print("=" * 60)
    print(f"\n事業者: {provider.name}")
    print(f"事業所: {facility.name}")
    print(f"職員数: {StaffMember.objects.filter(facility=facility, is_active=True).count()}名")
    print(f"職位数: {Position.objects.filter(facility=facility).count()}件")
    print(f"処遇改善計画書: {ImprovementPlan.objects.filter(provider=provider).count()}件")
    print("\n管理画面から確認できます:")
    print("https://shogu-kaizen-system.onrender.com/admin/")
    print("\n一般画面から確認できます:")
    print("https://shogu-kaizen-system.onrender.com")

if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
