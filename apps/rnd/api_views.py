from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RndRole, Ingredient, Product, Formulation, FormulationIngredient, StabilityTest
from .serializers import (IngredientSerializer, ProductSerializer, ProductListSerializer,
                           FormulationSerializer, FormulationIngredientSerializer,
                           StabilityTestSerializer)


def get_user_rnd_role(user):
    try:
        return user.rnd_role.role
    except Exception:
        return None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'inci_name', 'cas_number']
    filterset_fields = ['category', 'is_restricted']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            role = get_user_rnd_role(self.request.user)
            if role not in ['scientist', 'lab_manager'] and not self.request.user.is_staff:
                self.permission_denied(self.request)
        return super().get_permissions()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'status']
    search_fields = ['name', 'reference']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FormulationViewSet(viewsets.ModelViewSet):
    queryset = Formulation.objects.all()
    serializer_class = FormulationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'product']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        formulation = self.get_object()
        role = get_user_rnd_role(request.user)
        if role not in ['lab_manager'] and not request.user.is_staff:
            return Response({'error': 'Permission refusée.'}, status=403)
        formulation.status = 'approved'
        formulation.approved_by = request.user
        formulation.save()
        return Response({'status': 'Formulation approuvée'})


class FormulationIngredientViewSet(viewsets.ModelViewSet):
    queryset = FormulationIngredient.objects.all()
    serializer_class = FormulationIngredientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['formulation', 'ingredient']


class StabilityTestViewSet(viewsets.ModelViewSet):
    queryset = StabilityTest.objects.all()
    serializer_class = StabilityTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['formulation', 'result', 'condition']

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)
