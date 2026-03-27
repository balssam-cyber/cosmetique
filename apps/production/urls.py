from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/add/', views.batch_form, name='batch_add'),
    path('batches/<int:pk>/', views.batch_detail, name='batch_detail'),
    path('batches/<int:pk>/edit/', views.batch_form, name='batch_edit'),
    path('batches/<int:pk>/start/', views.batch_start, name='batch_start'),
    path('batches/<int:pk>/complete/', views.batch_complete, name='batch_complete'),
    path('batches/<int:batch_pk>/qc/add/', views.qc_check_form, name='qc_add'),
    path('batches/<int:batch_pk>/time/', views.batch_time_log_add, name='batch_time_log_add'),
    path('batches/<int:pk>/pdf/', views.batch_pdf_view, name='batch_pdf'),   # ← Fiche PDF

    path('equipments/', views.equipment_list, name='equipment_list'),
    path('equipments/add/', views.equipment_form, name='equipment_add'),
    path('equipments/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('equipments/<int:pk>/edit/', views.equipment_form, name='equipment_edit'),
    path('equipments/<int:equipment_pk>/maintenance/', views.maintenance_add, name='maintenance_add'),
]

