from rest_framework import serializers
from .models import RndRole, Ingredient, Product, Formulation, FormulationIngredient, StabilityTest


class RndRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RndRole
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class FormulationIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_inci = serializers.CharField(source='ingredient.inci_name', read_only=True)

    class Meta:
        model = FormulationIngredient
        fields = '__all__'


class StabilityTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StabilityTest
        fields = '__all__'


class FormulationSerializer(serializers.ModelSerializer):
    formulation_ingredients = FormulationIngredientSerializer(many=True, read_only=True)
    stability_tests = StabilityTestSerializer(many=True, read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Formulation
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    formulations = FormulationSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'reference', 'name', 'category', 'status', 'created_at']
