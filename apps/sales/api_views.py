from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from apps.stock.models import Lot, StockMovement
from .models import Customer, SalesOrder, SalesOrderLine, Shipment, ShipmentLine
from .serializers import (CustomerSerializer, SalesOrderSerializer, SalesOrderLineSerializer,
                           ShipmentSerializer, ShipmentLineSerializer)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'code']
    filterset_fields = ['is_active', 'country']


class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'customer']
    search_fields = ['order_number']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """Ship order and reduce finished product stock."""
        order = self.get_object()
        lines_data = request.data.get('lines', [])

        shipment = Shipment.objects.create(
            order=order,
            shipment_date=request.data.get('shipment_date'),
            tracking_number=request.data.get('tracking_number', ''),
            notes=request.data.get('notes', ''),
            shipped_by=request.user
        )

        for line_data in lines_data:
            order_line = SalesOrderLine.objects.get(id=line_data['order_line_id'])
            lot = Lot.objects.get(id=line_data['lot_id'])
            qty = float(line_data['quantity'])

            # Check stock
            if lot.current_quantity < qty:
                return Response(
                    {'error': f"Stock insuffisant pour lot {lot.lot_number}: "
                              f"disponible {lot.current_quantity}, requis {qty}"},
                    status=400
                )

            # Reduce stock
            lot.current_quantity -= qty
            lot.save()
            movement = StockMovement.objects.create(
                lot=lot,
                movement_type='sale',
                quantity=-qty,
                reference=f"CV-{order.order_number}",
                performed_by=request.user
            )
            ShipmentLine.objects.create(
                shipment=shipment,
                order_line=order_line,
                lot=lot,
                quantity=qty,
                created_lot_movement=movement
            )
            order_line.shipped_quantity += qty
            order_line.save()

        order.status = 'shipped'
        order.save()
        return Response({'status': 'Expédition créée, stock mis à jour.', 'shipment_id': shipment.id})

    @action(detail=False, methods=['get'])
    def report_by_product(self, request):
        from django.db.models import Sum
        data = (
            SalesOrderLine.objects
            .values('material__name', 'material__code')
            .annotate(
                total_quantity=Sum('shipped_quantity'),
                total_revenue=Sum(F('shipped_quantity') * F('unit_price'))
            )
            .order_by('-total_revenue')
        )
        return Response(list(data))

    @action(detail=False, methods=['get'])
    def report_by_customer(self, request):
        from django.db.models import Sum, Count
        data = (
            SalesOrder.objects
            .filter(status__in=['shipped', 'invoiced'])
            .values('customer__name', 'customer__code')
            .annotate(order_count=Count('id'))
            .order_by('-order_count')
        )
        return Response(list(data))


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['order']
