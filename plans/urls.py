from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('plan-wizard/', views.plan_wizard, name='plan_wizard'),
]
