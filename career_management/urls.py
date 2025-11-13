from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='career_index'),
    path('facility/<int:facility_id>/wage-table-builder/', views.wage_table_builder, name='wage_table_builder'),
    path('facility/<int:facility_id>/staff-list/', views.staff_list, name='staff_list'),
    path('facility/<int:facility_id>/promotion-candidates/', views.promotion_candidates, name='promotion_candidates'),
    path('staff/<int:staff_id>/', views.staff_detail, name='staff_detail'),

# ↓↓↓ ここから追加 ↓↓↓
    
    # キャリアパス要件設計メインメニュー
    path(
        'facility/<int:facility_id>/career-path-requirements/',
        views.career_path_requirements_index,
        name='career_path_requirements_index'
    ),
    
    # 要件Ⅰ：任用要件と賃金体系
    path(
        'facility/<int:facility_id>/requirement-one/',
        views.requirement_one_list,
        name='requirement_one_list'
    ),
    path(
        'facility/<int:facility_id>/requirement-one/position/<int:position_id>/',
        views.requirement_one_edit,
        name='requirement_one_edit'
    ),
    
    # 要件Ⅲ：昇給制度
    path(
        'facility/<int:facility_id>/requirement-three/',
        views.requirement_three_edit,
        name='requirement_three_edit'
    ),
    path(
        'facility/<int:facility_id>/promotion-criteria/',
        views.promotion_criteria_list,
        name='promotion_criteria_list'
    ),
    
    # 要件Ⅱ：研修計画
    path(
        'facility/<int:facility_id>/requirement-two/',
        views.requirement_two_list,
        name='requirement_two_list'
    ),
    path(
        'facility/<int:facility_id>/training-plan/new/',
        views.training_plan_edit,
        name='training_plan_new'
    ),
    path(
        'facility/<int:facility_id>/training-plan/<int:plan_id>/',
        views.training_plan_edit,
        name='training_plan_edit'
    ),
]

