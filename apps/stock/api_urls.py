from rest_framework.routers import DefaultRouter
from .api_views import MaterialCategoryViewSet, MaterialViewSet, LotViewSet, StockMovementViewSet

router = DefaultRouter()
router.register('categories', MaterialCategoryViewSet)
router.register('materials', MaterialViewSet)
router.register('lots', LotViewSet)
router.register('movements', StockMovementViewSet)

urlpatterns = router.urls
