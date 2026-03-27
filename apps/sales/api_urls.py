from rest_framework.routers import DefaultRouter
from .api_views import CustomerViewSet, SalesOrderViewSet, ShipmentViewSet

router = DefaultRouter()
router.register('customers', CustomerViewSet)
router.register('orders', SalesOrderViewSet)
router.register('shipments', ShipmentViewSet)

urlpatterns = router.urls
