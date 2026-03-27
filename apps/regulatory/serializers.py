from rest_framework import serializers
from .models import RegulatoryRole, ProductCompliance, SafetyReport, BPFDeclaration, CPNPNotification, ProductLabel


class RegulatoryRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulatoryRole
        fields = '__all__'


class ProductComplianceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductCompliance
        fields = '__all__'


class SafetyReportSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SafetyReport
        fields = '__all__'


class BPFDeclarationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = BPFDeclaration
        fields = '__all__'


class CPNPNotificationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = CPNPNotification
        fields = '__all__'


class ProductLabelSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductLabel
        fields = '__all__'
