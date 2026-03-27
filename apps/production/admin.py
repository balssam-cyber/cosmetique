from django.contrib import admin
from .models import ProductionRole, ProductionBatch, BatchRawMaterial, QCCheck


@admin.register(ProductionRole)
class ProductionRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']


class BatchRawMaterialInline(admin.TabularInline):
    model = BatchRawMaterial
    extra = 1


class QCCheckInline(admin.TabularInline):
    model = QCCheck
    extra = 1


@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'formulation', 'planned_quantity', 'actual_quantity',
                    'production_date', 'status', 'qc_passed']
    list_filter = ['status']
    search_fields = ['batch_number']
    inlines = [BatchRawMaterialInline, QCCheckInline]

    @admin.display(description='CQ OK', boolean=True)
    def qc_passed(self, obj):
        return obj.qc_passed


@admin.register(QCCheck)
class QCCheckAdmin(admin.ModelAdmin):
    list_display = ['batch', 'test_name', 'specification', 'measured_value', 'result', 'performed_by']
    list_filter = ['result']
