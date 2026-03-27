from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('materials/', views.material_list, name='material_list'),
    path('materials/add/', views.material_form, name='material_add'),
    path('materials/<int:pk>/', views.material_detail, name='material_detail'),
    path('materials/<int:pk>/edit/', views.material_form, name='material_edit'),

    path('lots/', views.lot_list, name='lot_list'),
    path('lots/<int:pk>/', views.lot_detail, name='lot_detail'),
    path('lots/add/', views.lot_add, name='lot_add'),
    path('lots/<int:pk>/qc/', views.lot_qc_update, name='lot_qc_update'),

    path('movements/', views.movement_list, name='movement_list'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('qc/', views.qc_dashboard, name='qc_dashboard'),
]
