from rest_framework import serializers
from .models import ProductionRole, ProductionBatch, BatchRawMaterial, QCCheck


class ProductionRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionRole
        fields = '__all__'


class BatchRawMaterialSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    material_unit = serializers.CharField(source='material.unit', read_only=True)

    class Meta:
        model = BatchRawMaterial
        fields = '__all__'


class QCCheckSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model = QCCheck
        fields = '__all__'


class ProductionBatchSerializer(serializers.ModelSerializer):
    raw_materials = BatchRawMaterialSerializer(many=True, read_only=True)
    qc_checks = QCCheckSerializer(many=True, read_only=True)
    qc_passed = serializers.BooleanField(read_only=True)
    formulation_name = serializers.CharField(source='formulation.__str__', read_only=True)
    product_name = serializers.CharField(source='formulation.product.name', read_only=True)

    class Meta:
        model = ProductionBatch
        fields = '__all__'


class ProductionBatchListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='formulation.product.name', read_only=True)
    qc_passed = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductionBatch
        fields = ['id', 'batch_number', 'product_name', 'planned_quantity', 'actual_quantity',
                  'production_date', 'status', 'qc_passed']
