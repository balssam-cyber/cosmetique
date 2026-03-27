from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import MaterialCategory, Material, Lot, StockMovement
from .serializers import (MaterialCategorySerializer, MaterialSerializer, MaterialListSerializer,
                           LotSerializer, StockMovementSerializer)


class MaterialCategoryViewSet(viewsets.ModelViewSet):
    queryset = MaterialCategory.objects.all()
    serializer_class = MaterialCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['material_type', 'category', 'is_active']
    search_fields = ['code', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return MaterialListSerializer
        return MaterialSerializer

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        materials = [m for m in Material.objects.filter(is_active=True) if m.is_low_stock]
        serializer = MaterialListSerializer(materials, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        days = getattr(settings, 'EXPIRY_ALERT_DAYS', 30)
        threshold = timezone.now().date() + timedelta(days=days)
        lots = Lot.objects.filter(
            expiry_date__lte=threshold,
            expiry_date__gte=timezone.now().date(),
            is_active=True,
            current_quantity__gt=0
        )
        serializer = LotSerializer(lots, many=True)
        return Response(serializer.data)


class LotViewSet(viewsets.ModelViewSet):
    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['material', 'is_active']
    search_fields = ['lot_number', 'material__name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['movement_type', 'lot__material']

    def perform_create(self, serializer):
        movement = serializer.save(performed_by=self.request.user)
        # Update lot quantity
        lot = movement.lot
        lot.current_quantity += movement.quantity
        lot.save()
