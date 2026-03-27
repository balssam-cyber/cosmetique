from django.urls import path
from . import views

app_name = 'regulatory'

urlpatterns = [
    path('compliance/', views.compliance_list, name='compliance_list'),
    path('compliance/<int:pk>/', views.compliance_detail, name='compliance_detail'),
    path('safety-reports/', views.safety_report_list, name='safety_report_list'),
    path('safety-reports/add/', views.safety_report_form, name='safety_report_add'),
    path('safety-reports/<int:pk>/', views.safety_report_detail, name='safety_report_detail'),
    path('safety-reports/<int:pk>/edit/', views.safety_report_form, name='safety_report_edit'),
    path('cpnp/', views.cpnp_list, name='cpnp_list'),
    path('bpf/', views.bpf_list, name='bpf_list'),
    path('labels/', views.label_list, name='label_list'),
    # ── Documents réglementaires multi-pays ──
    path('docs/', views.regulatory_doc_list, name='doc_list'),
    path('docs/add/', views.regulatory_doc_form, name='doc_add'),
    path('docs/<int:pk>/', views.regulatory_doc_detail, name='doc_detail'),
    path('docs/<int:pk>/edit/', views.regulatory_doc_form, name='doc_edit'),
    path('docs/<int:pk>/delete/', views.regulatory_doc_delete, name='doc_delete'),
    path('products/<int:product_pk>/docs/add/', views.regulatory_doc_form, name='doc_add_for_product'),
]
