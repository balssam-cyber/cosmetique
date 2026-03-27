from rest_framework.routers import DefaultRouter
from .api_views import SupplierViewSet, PurchaseOrderViewSet, GoodsReceiptViewSet

router = DefaultRouter()
router.register('suppliers', SupplierViewSet)
router.register('orders', PurchaseOrderViewSet)
router.register('receipts', GoodsReceiptViewSet)

urlpatterns = router.urls
