from django.contrib import admin
from .models import PurchaseRole, Supplier, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, GoodsReceiptLine


@admin.register(PurchaseRole)
class PurchaseRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_name', 'email', 'country', 'is_active']
    list_filter = ['country', 'is_active']
    search_fields = ['name', 'code']


class PurchaseOrderLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'status', 'order_date', 'expected_delivery', 'total_amount']
    list_filter = ['status', 'supplier']
    search_fields = ['order_number']
    inlines = [PurchaseOrderLineInline]

    @admin.display(description='Montant total')
    def total_amount(self, obj):
        return f"{obj.total_amount:.2f} €"


class GoodsReceiptLineInline(admin.TabularInline):
    model = GoodsReceiptLine
    extra = 1


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'receipt_date', 'reference', 'received_by']
    inlines = [GoodsReceiptLineInline]
