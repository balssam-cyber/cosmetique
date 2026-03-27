from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from apps.stock.models import Lot, StockMovement
from .models import ProductionRole, ProductionBatch, BatchRawMaterial, QCCheck
from .serializers import (ProductionBatchSerializer, ProductionBatchListSerializer,
                           BatchRawMaterialSerializer, QCCheckSerializer)


class ProductionBatchViewSet(viewsets.ModelViewSet):
    queryset = ProductionBatch.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'formulation']
    search_fields = ['batch_number']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductionBatchListSerializer
        return ProductionBatchSerializer

    @action(detail=True, methods=['post'])
    def start_production(self, request, pk=None):
        """Start production: check stock availability, deduct raw materials."""
        batch = self.get_object()
        if batch.status != 'planned':
            return Response({'error': 'Ce lot n\'est pas en état planifié.'}, status=400)

        # Check stock for each raw material
        errors = []
        for rm in batch.raw_materials.all():
            available = rm.material.total_quantity
            if available < rm.required_quantity:
                errors.append(
                    f"{rm.material.name}: disponible {available} {rm.material.unit}, "
                    f"requis {rm.required_quantity} {rm.material.unit}"
                )
        if errors:
            return Response({'error': 'Stock insuffisant', 'details': errors}, status=400)

        # Deduct raw materials from stock (FIFO)
        for rm in batch.raw_materials.all():
            remaining = rm.required_quantity
            for lot in rm.material.lots.filter(is_active=True, current_quantity__gt=0).order_by('expiry_date', 'reception_date'):
                if remaining <= 0:
                    break
                deduct = min(lot.current_quantity, remaining)
                lot.current_quantity -= deduct
                lot.save()
                StockMovement.objects.create(
                    lot=lot,
                    movement_type='production_use',
                    quantity=-deduct,
                    reference=f"LOT-{batch.batch_number}",
                    performed_by=request.user
                )
                remaining -= deduct
                rm.actual_quantity = (rm.actual_quantity or 0) + deduct
            rm.save()

        batch.status = 'in_progress'
        batch.save()
        return Response({'status': 'Production démarrée, matières déduites du stock.'})

    @action(detail=True, methods=['post'])
    def complete_production(self, request, pk=None):
        """Complete production and add finished product to stock."""
        batch = self.get_object()
        if batch.status != 'in_progress':
            return Response({'error': 'La production n\'est pas en cours.'}, status=400)

        actual_qty = request.data.get('actual_quantity', batch.planned_quantity)
        batch.actual_quantity = actual_qty
        batch.status = 'completed'
        batch.save()

        # Add finished product to stock
        product = batch.formulation.product
        from apps.stock.models import Material
        try:
            finished_material = Material.objects.get(
                name__icontains=product.name,
                material_type='finished_product'
            )
        except Material.DoesNotExist:
            finished_material = None

        if finished_material:
            lot = Lot.objects.create(
                material=finished_material,
                lot_number=batch.batch_number,
                initial_quantity=actual_qty,
                current_quantity=actual_qty,
                unit_cost=0,
                created_by=request.user
            )
            batch.finished_lot = lot
            batch.save()
            StockMovement.objects.create(
                lot=lot,
                movement_type='production_output',
                quantity=actual_qty,
                reference=f"LOT-{batch.batch_number}",
                performed_by=request.user
            )

        return Response({'status': 'Production complétée, produit fini ajouté au stock.'})


class BatchRawMaterialViewSet(viewsets.ModelViewSet):
    queryset = BatchRawMaterial.objects.all()
    serializer_class = BatchRawMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['batch', 'material']


class QCCheckViewSet(viewsets.ModelViewSet):
    queryset = QCCheck.objects.all()
    serializer_class = QCCheckSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['batch', 'result']

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user, performed_at=timezone.now())
