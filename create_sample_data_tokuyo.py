"""
特別養護老人ホームのサンプルデータ作成スクリプト
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Django設定
sys.path.append('/opt/render/project/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shogu_kaizen_system.settings')
django.setup()

from django.contrib.auth.models import User
from facility_management.models import Provider, Facility, ServiceType
from career_management.models import (
    JobCategory, Position, WageTable, StaffMember, StaffEvaluation,
    CareerPathRequirement1, CareerPathRequirement2, CareerPathRequirement3,
    PromotionRecord
)
from plans.models import ImprovementPlan, WorkplaceInitiative

def create_sample_data():
    print("=" * 60)
    print("特別養護老人ホーム サンプルデータ作成開始")
    print("=" * 60)
    
    # 1. サービス種類の取得
    print("\n[1] サービス種類を確認中...")
    service_type, created = ServiceType.objects.get_or_create(
        name="介護老人福祉施設",
        defaults={
            'code': 'S11',
            'category': '施設サービス',
            'requires_qualification': True
        }
    )
    if created:
        print(f"✓ サービス種類を作成: {service_type.name}")
    else:
        print(f"✓ サービス種類を確認: {service_type.name}")
    
    # 2. 事業者の作成
    print("\n[2] 事業者を作成中...")
    provider, created = Provider.objects.get_or_create(
        name="社会福祉法人 さくら会",
        defaults={
            'address': '東京都世田谷区桜新町1-2-3',
            'phone': '03-1234-5678',
            'representative': '理事長 山田 太郎'
        }
    )
    if created:
        print(f"✓ 事業者を作成: {provider.name}")
    else:
        print(f"✓ 事業者を確認: {provider.name}")
    
    # 3. 事業所の作成
    print("\n[3] 事業所を作成中...")
    facility, created = Facility.objects.get_or_create(
        name="特別養護老人ホーム さくらの里",
        provider=provider,
        defaults={
            'service_type': service_type,
            'address': '東京都世田谷区桜新町2-3-4',
            'phone': '03-1234-5679',
            'capacity': 100,
            'current_occupancy': 95
        }
    )
    if created:
        print(f"✓ 事業所を作成: {facility.name}")
    else:
        print(f"✓ 事業所を確認: {facility.name}")
    
    # 4. 職種の作成
    print("\n[4] 職種を作成中...")
    job_categories = [
        {'name': '介護職員', 'code': 'KAIGO', 'description': '介護サービスを提供する職員'},
        {'name': '看護職員', 'code': 'KANGO', 'description': '看護・医療サービスを提供する職員'},
        {'name': '生活相談員', 'code': 'SOUDAN', 'description': '入居者や家族の相談対応'},
        {'name': '介護支援専門員', 'code': 'CARE_MGR', 'description': 'ケアマネジャー'},
        {'name': '管理職', 'code': 'KANRI', 'description': '施設管理を行う職員'},
    ]
    
    job_category_objects = {}
    for jc_data in job_categories:
        jc, created = JobCategory.objects.get_or_create(
            name=jc_data['name'],
            defaults={
                'code': jc_data['code'],
                'description': jc_data['description']
            }
        )
        job_category_objects[jc_data['name']] = jc
        if created:
            print(f"  ✓ {jc.name}")
    
    # 5. 職位の作成
    print("\n[5] 職位を作成中...")
    positions = [
        {'name': '施設長', 'level': 5, 'min_years': 15, 'job_category': '管理職'},
        {'name': '副施設長', 'level': 4, 'min_years': 10, 'job_category': '管理職'},
        {'name': 'フロアリーダー', 'level': 3, 'min_years': 5, 'job_category': '介護職員'},
        {'name': '主任介護職員', 'level': 2, 'min_years': 3, 'job_category': '介護職員'},
        {'name': '介護職員', 'level': 1, 'min_years': 0, 'job_category': '介護職員'},
        {'name': '看護師長', 'level': 3, 'min_years': 7, 'job_category': '看護職員'},
        {'name': '看護師', 'level': 1, 'min_years': 0, 'job_category': '看護職員'},
        {'name': '主任生活相談員', 'level': 2, 'min_years': 5, 'job_category': '生活相談員'},
        {'name': '生活相談員', 'level': 1, 'min_years': 0, 'job_category': '生活相談員'},
    ]
    
    position_objects = {}
    for pos_data in positions:
        jc = job_category_objects[pos_data['job_category']]
        pos, created = Position.objects.get_or_create(
            name=pos_data['name'],
            job_category=jc,
            defaults={
                'level': pos_data['level'],
                'min_experience_years': pos_data['min_years'],
                'description': f"{pos_data['name']}の職位"
            }
        )
        position_objects[pos_data['name']] = pos
        if created:
            print(f"  ✓ {pos.name} (Lv.{pos.level})")
    
    # 6. 賃金テーブルの作成
    print("\n[6] 賃金テーブルを作成中...")
    wage_tables_data = [
        # 介護職員
        {'position': '介護職員', 'grade': 1, 'step': 1, 'base_salary': 180000},
        {'position': '介護職員', 'grade': 1, 'step': 10, 'base_salary': 210000},
        {'position': '主任介護職員', 'grade': 2, 'step': 1, 'base_salary': 220000},
        {'position': '主任介護職員', 'grade': 2, 'step': 10, 'base_salary': 260000},
        {'position': 'フロアリーダー', 'grade': 3, 'step': 1, 'base_salary': 270000},
        {'position': 'フロアリーダー', 'grade': 3, 'step': 10, 'base_salary': 320000},
        # 看護職員
        {'position': '看護師', 'grade': 1, 'step': 1, 'base_salary': 240000},
        {'position': '看護師', 'grade': 1, 'step': 10, 'base_salary': 280000},
        {'position': '看護師長', 'grade': 3, 'step': 1, 'base_salary': 300000},
        {'position': '看護師長', 'grade': 3, 'step': 10, 'base_salary': 360000},
        # 生活相談員
        {'position': '生活相談員', 'grade': 1, 'step': 1, 'base_salary': 200000},
        {'position': '生活相談員', 'grade': 1, 'step': 10, 'base_salary': 240000},
        {'position': '主任生活相談員', 'grade': 2, 'step': 1, 'base_salary': 250000},
        {'position': '主任生活相談員', 'grade': 2, 'step': 10, 'base_salary': 300000},
        # 管理職
        {'position': '副施設長', 'grade': 4, 'step': 1, 'base_salary': 350000},
        {'position': '副施設長', 'grade': 4, 'step': 10, 'base_salary': 420000},
        {'position': '施設長', 'grade': 5, 'step': 1, 'base_salary': 450000},
        {'position': '施設長', 'grade': 5, 'step': 10, 'base_salary': 550000},
    ]
    
    wage_count = 0
    for wt_data in wage_tables_data:
        pos = position_objects[wt_data['position']]
        wt, created = WageTable.objects.get_or_create(
            position=pos,
            grade=wt_data['grade'],
            step=wt_data['step'],
            defaults={
                'base_salary': wt_data['base_salary'],
                'min_salary': wt_data['base_salary'],
                'max_salary': wt_data['base_salary'] + 50000
            }
        )
        if created:
            wage_count += 1
    print(f"  ✓ {wage_count}件の賃金テーブルを作成")
    
    # 7. 職員の作成
    print("\n[7] 職員を作成中...")
    staff_data = [
        # 管理職
        {'name': '山田 次郎', 'position': '施設長', 'hire_date': date(2005, 4, 1), 'grade': 5, 'step': 8},
        {'name': '佐藤 花子', 'position': '副施設長', 'hire_date': date(2010, 4, 1), 'grade': 4, 'step': 6},
        # 介護職員
        {'name': '鈴木 一郎', 'position': 'フロアリーダー', 'hire_date': date(2015, 4, 1), 'grade': 3, 'step': 5},
        {'name': '田中 美咲', 'position': 'フロアリーダー', 'hire_date': date(2016, 4, 1), 'grade': 3, 'step': 4},
        {'name': '高橋 健太', 'position': '主任介護職員', 'hire_date': date(2018, 4, 1), 'grade': 2, 'step': 3},
        {'name': '伊藤 さくら', 'position': '主任介護職員', 'hire_date': date(2019, 4, 1), 'grade': 2, 'step': 2},
        {'name': '渡辺 大輔', 'position': '介護職員', 'hire_date': date(2021, 4, 1), 'grade': 1, 'step': 5},
        {'name': '山本 愛', 'position': '介護職員', 'hire_date': date(2022, 4, 1), 'grade': 1, 'step': 3},
        {'name': '中村 優希', 'position': '介護職員', 'hire_date': date(2023, 4, 1), 'grade': 1, 'step': 2},
        {'name': '小林 翔太', 'position': '介護職員', 'hire_date': date(2024, 4, 1), 'grade': 1, 'step': 1},
        # 看護職員
        {'name': '加藤 恵子', 'position': '看護師長', 'hire_date': date(2012, 4, 1), 'grade': 3, 'step': 7},
        {'name': '吉田 真由美', 'position': '看護師', 'hire_date': date(2019, 4, 1), 'grade': 1, 'step': 5},
        {'name': '山口 陽子', 'position': '看護師', 'hire_date': date(2021, 4, 1), 'grade': 1, 'step': 3},
        # 生活相談員
        {'name': '松本 拓也', 'position': '主任生活相談員', 'hire_date': date(2016, 4, 1), 'grade': 2, 'step': 6},
        {'name': '井上 美穂', 'position': '生活相談員', 'hire_date': date(2020, 4, 1), 'grade': 1, 'step': 4},
    ]
    
    for staff in staff_data:
        pos = position_objects[staff['position']]
        
        # 賃金テーブルから基本給を取得
        wage_table = WageTable.objects.filter(
            position=pos,
            grade=staff['grade'],
            step=staff['step']
        ).first()
        
        base_salary = wage_table.base_salary if wage_table else 200000
        
        sm, created = StaffMember.objects.get_or_create(
            name=staff['name'],
            facility=facility,
            defaults={
                'employee_id': f"T{date.today().year}{StaffMember.objects.count() + 1:04d}",
                'position': pos,
                'hire_date': staff['hire_date'],
                'current_grade': staff['grade'],
                'current_step': staff['step'],
                'base_salary': base_salary,
                'qualifications': '介護福祉士' if '介護' in staff['position'] else '正看護師' if '看護' in staff['position'] else '社会福祉士',
                'status': 'active'
            }
        )
        if created:
            print(f"  ✓ {sm.name} ({pos.name})")
    
    # 8. キャリアパス要件Ⅰの作成
    print("\n[8] キャリアパス要件Ⅰを作成中...")
    req1_data = [
        {
            'position': '介護職員',
            'required_qualifications': '介護職員初任者研修以上',
            'required_experience_years': 0,
            'job_description': '入居者の日常生活支援、身体介護、レクリエーション活動の支援',
            'salary_range_min': 180000,
            'salary_range_max': 210000
        },
        {
            'position': '主任介護職員',
            'required_qualifications': '介護福祉士',
            'required_experience_years': 3,
            'job_description': 'チームリーダーとして介護職員の指導、入居者ケアの統括',
            'salary_range_min': 220000,
            'salary_range_max': 260000
        },
        {
            'position': 'フロアリーダー',
            'required_qualifications': '介護福祉士 + リーダー研修修了',
            'required_experience_years': 5,
            'job_description': 'フロア全体の管理、職員育成、ケアプラン作成支援',
            'salary_range_min': 270000,
            'salary_range_max': 320000
        },
    ]
    
    for req_data in req1_data:
        pos = position_objects[req_data['position']]
        req1, created = CareerPathRequirement1.objects.get_or_create(
            facility=facility,
            position=pos,
            defaults=req_data
        )
        if created:
            print(f"  ✓ {pos.name}の要件を作成")
    
    # 9. キャリアパス要件Ⅱの作成
    print("\n[9] キャリアパス要件Ⅱを作成中...")
    req2_data = [
        {
            'training_name': '新入職員研修',
            'target_position': '介護職員',
            'training_hours': 16,
            'training_content': '施設概要、介護の基本、感染症対策、緊急時対応',
            'training_type': 'OJT',
            'is_mandatory': True,
            'frequency': '入職時'
        },
        {
            'training_name': '介護技術向上研修',
            'target_position': '介護職員',
            'training_hours': 8,
            'training_content': '移乗介助、排泄介助、食事介助の技術向上',
            'training_type': 'OFF_JT',
            'is_mandatory': True,
            'frequency': '年2回'
        },
        {
            'training_name': 'リーダー養成研修',
            'target_position': '主任介護職員',
            'training_hours': 24,
            'training_content': 'チームマネジメント、職員指導、問題解決技法',
            'training_type': 'EXTERNAL',
            'is_mandatory': True,
            'frequency': '昇格時'
        },
        {
            'training_name': '認知症ケア研修',
            'target_position': 'フロアリーダー',
            'training_hours': 16,
            'training_content': '認知症の理解、BPSDへの対応、パーソンセンタードケア',
            'training_type': 'EXTERNAL',
            'is_mandatory': True,
            'frequency': '年1回'
        },
    ]
    
    for req_data in req2_data:
        pos = position_objects[req_data['target_position']]
        req2, created = CareerPathRequirement2.objects.get_or_create(
            facility=facility,
            training_name=req_data['training_name'],
            defaults={**req_data, 'target_position': pos}
        )
        if created:
            print(f"  ✓ {req_data['training_name']}")
    
    # 10. キャリアパス要件Ⅲの作成
    print("\n[10] キャリアパス要件Ⅲを作成中...")
    req3, created = CareerPathRequirement3.objects.get_or_create(
        facility=facility,
        defaults={
            'regular_raise_system': '毎年4月に定期昇給を実施。昇給額は評価に基づき1号俸～3号俸',
            'special_raise_criteria': '特別な功績、資格取得、業務改善提案の実現による特別昇給制度あり',
            'promotion_criteria': '経験年数、保有資格、評価点数、面接により総合的に判断',
            'evaluation_system': '年2回（4月・10月）の人事評価。能力評価、成果評価、行動評価の3軸で評価',
            'raise_amount_range_min': 2000,
            'raise_amount_range_max': 10000,
            'raise_frequency': '年1回（4月）',
            'has_special_raise': True,
            'has_promotion_system': True
        }
    )
    if created:
        print(f"  ✓ 昇給制度を作成")
    
    # 11. 処遇改善計画書の作成
    print("\n[11] 処遇改善計画書を作成中...")
    plan, created = ImprovementPlan.objects.get_or_create(
        provider=provider,
        fiscal_year=2025,
        defaults={
            'target_facility': facility,
            'grant_category': '処遇改善加算Ⅰ',
            'has_requirement_1': True,
            'has_requirement_2': True,
            'has_requirement_3': True,
            'has_requirement_4': False,
            'has_requirement_5': False,
            'estimated_grant_amount': Decimal('12500000'),
            'grant_category_calculated': '処遇改善加算Ⅰ',
            'status': 'draft'
        }
    )
    
    if created:
        print(f"  ✓ 処遇改善計画書を作成")
        
        # 職場環境等要件を選択（14項目から3つ）
        initiatives = WorkplaceInitiative.objects.filter(
            item_number__in=['1-1', '2-1', '3-1']
        )
        plan.selected_initiatives.set(initiatives)
        print(f"  ✓ 職場環境等要件を3つ選択")
    
    print("\n" + "=" * 60)
    print("サンプルデータ作成完了！")
    print("=" * 60)
    print(f"\n事業者: {provider.name}")
    print(f"事業所: {facility.name}")
    print(f"職員数: {StaffMember.objects.filter(facility=facility).count()}名")
    print(f"処遇改善計画書: 1件作成")
    print("\n管理画面から確認できます:")
    print("https://shogu-kaizen-system.onrender.com/admin/")

if __name__ == '__main__':
    create_sample_data()
