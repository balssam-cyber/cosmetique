from django.contrib import admin
from .models import StockRole, MaterialCategory, Material, Lot, StockMovement


@admin.register(StockRole)
class StockRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


class LotInline(admin.TabularInline):
    model = Lot
    extra = 0
    readonly_fields = ['current_quantity']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'material_type', 'unit', 'minimum_stock', 'total_quantity', 'is_low_stock']
    list_filter = ['material_type', 'category', 'is_active']
    search_fields = ['code', 'name']
    inlines = [LotInline]

    @admin.display(description='Quantité totale', boolean=False)
    def total_quantity(self, obj):
        return obj.total_quantity

    @admin.display(description='Stock faible', boolean=True)
    def is_low_stock(self, obj):
        return obj.is_low_stock


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ['lot_number', 'material', 'current_quantity', 'reception_date', 'expiry_date', 'is_active']
    list_filter = ['material__material_type', 'is_active']
    search_fields = ['lot_number', 'material__name']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'lot', 'movement_type', 'quantity', 'reference', 'performed_by']
    list_filter = ['movement_type']
    readonly_fields = ['created_at']
