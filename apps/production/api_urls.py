from rest_framework.routers import DefaultRouter
from .api_views import ProductionBatchViewSet, BatchRawMaterialViewSet, QCCheckViewSet

router = DefaultRouter()
router.register('batches', ProductionBatchViewSet)
router.register('raw-materials', BatchRawMaterialViewSet)
router.register('qc-checks', QCCheckViewSet)

urlpatterns = router.urls
