from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.stock.models import Lot, StockMovement
from .models import Supplier, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, GoodsReceiptLine
from .serializers import (SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderLineSerializer,
                           GoodsReceiptSerializer, GoodsReceiptLineSerializer)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'code']
    filterset_fields = ['is_active', 'country']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'supplier']
    search_fields = ['order_number']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Create a goods receipt and update stock."""
        order = self.get_object()
        receipt_data = request.data
        lines_data = receipt_data.get('lines', [])

        receipt = GoodsReceipt.objects.create(
            order=order,
            receipt_date=receipt_data.get('receipt_date'),
            reference=receipt_data.get('reference', ''),
            notes=receipt_data.get('notes', ''),
            received_by=request.user
        )

        for line_data in lines_data:
            order_line = PurchaseOrderLine.objects.get(id=line_data['order_line_id'])
            qty = float(line_data['quantity'])

            # Create stock lot
            lot = Lot.objects.create(
                material=order_line.material,
                lot_number=line_data.get('lot_number', f"LOT-{receipt.id}"),
                supplier=order.supplier.name,
                initial_quantity=qty,
                current_quantity=qty,
                expiry_date=line_data.get('expiry_date'),
                unit_cost=order_line.unit_price,
                created_by=request.user
            )
            StockMovement.objects.create(
                lot=lot,
                movement_type='reception',
                quantity=qty,
                reference=f"BC-{order.order_number}",
                performed_by=request.user
            )
            GoodsReceiptLine.objects.create(
                receipt=receipt,
                order_line=order_line,
                lot_number=line_data.get('lot_number', ''),
                quantity=qty,
                expiry_date=line_data.get('expiry_date'),
                unit_cost=order_line.unit_price,
                created_lot=lot
            )
            order_line.received_quantity += qty
            order_line.save()

        # Update order status
        all_received = all(
            l.received_quantity >= l.quantity for l in order.lines.all()
        )
        order.status = 'received' if all_received else 'partially_received'
        order.save()

        return Response({'status': 'Réception créée et stock mis à jour.', 'receipt_id': receipt.id})


class GoodsReceiptViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceipt.objects.all()
    serializer_class = GoodsReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['order']
