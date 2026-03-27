from django.contrib import admin
from .models import DashboardRole, Alert


@admin.register(DashboardRole)
class DashboardRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'alert_type', 'severity', 'title', 'is_resolved']
    list_filter = ['alert_type', 'severity', 'is_resolved']
