from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_form, name='customer_add'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_form, name='customer_edit'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.order_form, name='order_add'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.order_form, name='order_edit'),
    path('orders/<int:pk>/ship/', views.order_ship, name='order_ship'),
    path('orders/<int:pk>/invoice/', views.order_invoice_pdf, name='order_invoice'),
    path('reports/', views.report_view, name='reports'),
    # Nouveaux exports
    path('reports/excel/', views.sales_report_excel, name='report_excel'),
    path('batches/<int:pk>/pdf/', views.batch_pdf, name='batch_pdf'),
]

