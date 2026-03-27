from rest_framework import serializers
from .models import PurchaseRole, Supplier, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, GoodsReceiptLine


class PurchaseRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRole
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrderLine
        fields = '__all__'


class PurchaseOrderSerializer(serializers.ModelSerializer):
    lines = PurchaseOrderLineSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'


class GoodsReceiptLineSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='order_line.material.name', read_only=True)

    class Meta:
        model = GoodsReceiptLine
        fields = '__all__'


class GoodsReceiptSerializer(serializers.ModelSerializer):
    lines = GoodsReceiptLineSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = GoodsReceipt
        fields = '__all__'
