from django.urls import path
from . import views

app_name = 'purchase'

urlpatterns = [
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_form, name='supplier_add'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_form, name='supplier_edit'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.order_form, name='order_add'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.order_form, name='order_edit'),
    path('orders/<int:order_pk>/receive/', views.receipt_form, name='receipt_add'),
    path('orders/<int:pk>/quick-receive/', views.quick_receive, name='quick_receive'),
    path('shortages/<int:pk>/resolve/', views.resolve_shortage, name='resolve_shortage'),
]
