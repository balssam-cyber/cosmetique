from django.contrib import admin
from .models import Customer, SalesOrder, SalesOrderLine, Shipment, ShipmentLine


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_name', 'email', 'country', 'is_active']
    list_filter = ['country', 'is_active']
    search_fields = ['name', 'code']


class SalesOrderLineInline(admin.TabularInline):
    model = SalesOrderLine
    extra = 1


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'order_date', 'total_amount']
    list_filter = ['status', 'customer']
    search_fields = ['order_number']
    inlines = [SalesOrderLineInline]

    @admin.display(description='Montant total')
    def total_amount(self, obj):
        return f"{obj.total_amount:.2f} €"


class ShipmentLineInline(admin.TabularInline):
    model = ShipmentLine
    extra = 1


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'shipment_date', 'tracking_number', 'shipped_by']
    inlines = [ShipmentLineInline]
