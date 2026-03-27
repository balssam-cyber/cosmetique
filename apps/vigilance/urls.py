from django.urls import path
from . import views

app_name = 'vigilance'

urlpatterns = [
    path('', views.complaint_list, name='complaint_list'),
    path('add/', views.complaint_form, name='complaint_add'),
    path('<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('<int:pk>/edit/', views.complaint_form, name='complaint_edit'),
]
