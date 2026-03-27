from rest_framework import serializers
from .models import Customer, SalesOrder, SalesOrderLine, Shipment, ShipmentLine


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class SalesOrderLineSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SalesOrderLine
        fields = '__all__'


class SalesOrderSerializer(serializers.ModelSerializer):
    lines = SalesOrderLineSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = SalesOrder
        fields = '__all__'


class ShipmentLineSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='order_line.material.name', read_only=True)

    class Meta:
        model = ShipmentLine
        fields = '__all__'


class ShipmentSerializer(serializers.ModelSerializer):
    lines = ShipmentLineSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Shipment
        fields = '__all__'
