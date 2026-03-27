from rest_framework import viewsets, permissions
from .models import RegulatoryRole, ProductCompliance, SafetyReport, BPFDeclaration, CPNPNotification, ProductLabel
from .serializers import (ProductComplianceSerializer, SafetyReportSerializer,
                           BPFDeclarationSerializer, CPNPNotificationSerializer, ProductLabelSerializer)


class ProductComplianceViewSet(viewsets.ModelViewSet):
    queryset = ProductCompliance.objects.all()
    serializer_class = ProductComplianceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'eu_regulation']

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class SafetyReportViewSet(viewsets.ModelViewSet):
    queryset = SafetyReport.objects.all()
    serializer_class = SafetyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'product']
    search_fields = ['report_number', 'product__name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BPFDeclarationViewSet(viewsets.ModelViewSet):
    queryset = BPFDeclaration.objects.all()
    serializer_class = BPFDeclarationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'product']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CPNPNotificationViewSet(viewsets.ModelViewSet):
    queryset = CPNPNotification.objects.all()
    serializer_class = CPNPNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'market']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProductLabelViewSet(viewsets.ModelViewSet):
    queryset = ProductLabel.objects.all()
    serializer_class = ProductLabelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'product', 'language']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
