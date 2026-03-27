from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', lambda request: redirect('dashboard:index'), name='home'),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('rnd/', include('apps.rnd.urls')),
    path('production/', include('apps.production.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('vigilance/', include('apps.vigilance.urls')),
    path('stock/', include('apps.stock.urls', namespace='stock')),
    path('purchase/', include('apps.purchase.urls', namespace='purchase')),
    path('sales/', include('apps.sales.urls', namespace='sales')),
    path('regulatory/', include('apps.regulatory.urls', namespace='regulatory')),
    # API endpoints
    path('api/rnd/', include('apps.rnd.api_urls')),
    path('api/production/', include('apps.production.api_urls')),
    path('api/stock/', include('apps.stock.api_urls')),
    path('api/purchase/', include('apps.purchase.api_urls')),
    path('api/sales/', include('apps.sales.api_urls')),
    path('api/regulatory/', include('apps.regulatory.api_urls')),
    path('api/dashboard/', include('apps.dashboard.api_urls')),
    path('api-auth/', include('rest_framework.urls')),
    # JWT Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
