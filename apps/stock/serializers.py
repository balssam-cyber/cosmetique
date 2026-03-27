from rest_framework import serializers
from .models import StockRole, MaterialCategory, Material, Lot, StockMovement


class StockRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockRole
        fields = '__all__'


class MaterialCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialCategory
        fields = '__all__'


class LotSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Lot
        fields = '__all__'


class StockMovementSerializer(serializers.ModelSerializer):
    lot_info = serializers.CharField(source='lot.__str__', read_only=True)

    class Meta:
        model = StockMovement
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    lots = LotSerializer(many=True, read_only=True)
    total_quantity = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Material
        fields = '__all__'


class MaterialListSerializer(serializers.ModelSerializer):
    total_quantity = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Material
        fields = ['id', 'code', 'name', 'material_type', 'unit', 'minimum_stock',
                  'total_quantity', 'is_low_stock', 'is_active']
