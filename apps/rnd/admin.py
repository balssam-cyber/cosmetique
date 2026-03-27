from django.contrib import admin
from .models import RndRole, Ingredient, Product, Formulation, FormulationIngredient, StabilityTest


@admin.register(RndRole)
class RndRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'inci_name', 'cas_number', 'category', 'supplier', 'is_restricted']
    list_filter = ['category', 'is_restricted']
    search_fields = ['name', 'inci_name', 'cas_number']


class FormulationIngredientInline(admin.TabularInline):
    model = FormulationIngredient
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['reference', 'name', 'category', 'status', 'created_by', 'created_at']
    list_filter = ['category', 'status']
    search_fields = ['name', 'reference']


@admin.register(Formulation)
class FormulationAdmin(admin.ModelAdmin):
    list_display = ['product', 'version', 'status', 'batch_size', 'created_by', 'created_at']
    list_filter = ['status']
    inlines = [FormulationIngredientInline]


@admin.register(StabilityTest)
class StabilityTestAdmin(admin.ModelAdmin):
    list_display = ['formulation', 'condition', 'duration_weeks', 'start_date', 'result']
    list_filter = ['condition', 'result']
