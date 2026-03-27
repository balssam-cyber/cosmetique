from django.urls import path
from . import views

app_name = 'rnd'

urlpatterns = [
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('ingredients/add/', views.ingredient_form, name='ingredient_add'),
    path('ingredients/<int:pk>/', views.ingredient_detail, name='ingredient_detail'),
    path('ingredients/<int:pk>/edit/', views.ingredient_form, name='ingredient_edit'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_form, name='product_add'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_form, name='product_edit'),
    path('products/<int:product_pk>/formulations/add/', views.formulation_form, name='formulation_add'),
    path('formulations/<int:pk>/', views.formulation_detail, name='formulation_detail'),
    path('formulations/<int:pk>/edit/', views.formulation_form, name='formulation_edit'),
    path('formulations/<int:formulation_pk>/ingredients/add/', views.formulation_ingredient_add, name='fi_add'),
    path('formulation-ingredients/<int:pk>/delete/', views.formulation_ingredient_delete, name='fi_delete'),
    path('stability-tests/', views.stability_test_list, name='stability_test_list'),
    path('formulations/<int:formulation_pk>/stability/add/', views.stability_test_add, name='stability_add'),
    path('formulations/<int:pk>/simulate/', views.formulation_simulate, name='formulation_simulate'),
]
