#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shogu_kaizen_system.settings')
django.setup()

from facility_management.models import Provider, Facility
from career_management.models import JobCategory, Position, WageTable, StaffMember

def create_sample_data():
    print("サンプルデータを投入しています...")
    
    provider, _ = Provider.objects.get_or_create(
        name="社会福祉法人さくら会",
        defaults={'address': '東京都港区六本木1-2-3', 'phone': '03-1234-5678'}
    )
    
    facility, _ = Facility.objects.get_or_create(
        facility_number='1370100001',
        defaults={
            'provider': provider,
            'name': 'さくら介護ホーム',
            'service_type': 'special_nursing_home',
            'address': '東京都港区六本木1-2-3',
            'capacity': 50,
            'staff_count': 30
        }
    )
    
    care_category, _ = JobCategory.objects.get_or_create(
        category_code='care',
        defaults={'category_name': '介護職員'}
    )
    
    positions_data = [
        {'level': 1, 'name': '介護職員', 'exp_months': 0},
        {'level': 2, 'name': '介護職員（経験者）', 'exp_months': 12},
        {'level': 3, 'name': '主任介護職員', 'exp_months': 36},
    ]
    
    for pos_data in positions_data:
        position, created = Position.objects.get_or_create(
            facility=facility,
            job_category=care_category,
            level=pos_data['level'],
            defaults={
                'position_name': pos_data['name'],
                'required_experience_months': pos_data['exp_months'],
            }
        )
        
        if created and not hasattr(position, 'wage_table'):
            WageTable.objects.create(
                position=position,
                base_salary_start=220000 + (pos_data['level'] - 1) * 30000,
                step_raise_amount=2000,
                max_steps=30,
                qualification_allowance=5000 * pos_data['level'],
                position_allowance=0
            )
    
    print("✅ サンプルデータの投入が完了しました！")
    print(f"事業所ID: {facility.id}")
    print("賃金テーブル: http://127.0.0.1:8000/career/facility/{}/wage-table-builder/".format(facility.id))

if __name__ == '__main__':
    create_sample_data()
