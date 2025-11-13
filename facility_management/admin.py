from django.contrib import admin
from .models import Provider, Facility

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'created_at']
    search_fields = ['name', 'corporate_number']

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'service_type', 'facility_number', 'capacity', 'staff_count']
    list_filter = ['service_type', 'provider']
    search_fields = ['name', 'facility_number']
