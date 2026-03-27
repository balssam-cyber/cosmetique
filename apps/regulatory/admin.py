from django.contrib import admin
from .models import RegulatoryRole, ProductCompliance, SafetyReport, BPFDeclaration, CPNPNotification, ProductLabel


@admin.register(RegulatoryRole)
class RegulatoryRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']


@admin.register(ProductCompliance)
class ProductComplianceAdmin(admin.ModelAdmin):
    list_display = ['product', 'status', 'eu_regulation', 'last_review_date', 'next_review_date']
    list_filter = ['status', 'eu_regulation']


@admin.register(SafetyReport)
class SafetyReportAdmin(admin.ModelAdmin):
    list_display = ['report_number', 'product', 'status', 'safety_assessor', 'issue_date', 'expiry_date']
    list_filter = ['status']
    search_fields = ['report_number', 'product__name']


@admin.register(BPFDeclaration)
class BPFDeclarationAdmin(admin.ModelAdmin):
    list_display = ['declaration_number', 'product', 'status', 'facility_name', 'issue_date', 'expiry_date']
    list_filter = ['status']


@admin.register(CPNPNotification)
class CPNPNotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_number', 'product', 'status', 'submission_date', 'market']
    list_filter = ['status', 'market']


@admin.register(ProductLabel)
class ProductLabelAdmin(admin.ModelAdmin):
    list_display = ['product', 'version', 'status', 'language', 'created_at']
    list_filter = ['status', 'language']
