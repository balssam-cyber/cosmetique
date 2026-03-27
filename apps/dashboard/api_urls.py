from django.urls import path
from .api_views import dashboard_summary, alerts_list, kpi_dashboard, search_view, ai_assistant_api

urlpatterns = [
    path('summary/', dashboard_summary, name='dashboard-summary'),
    path('alerts/', alerts_list, name='dashboard-alerts'),
    # Nouveaux endpoints
    path('kpis/', kpi_dashboard, name='dashboard-kpis'),
    path('search/', search_view, name='dashboard-search'),
    path('ai/', ai_assistant_api, name='dashboard-ai'),
]
