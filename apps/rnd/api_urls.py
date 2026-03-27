from rest_framework.routers import DefaultRouter
from .api_views import IngredientViewSet, ProductViewSet, FormulationViewSet, FormulationIngredientViewSet, StabilityTestViewSet

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('products', ProductViewSet)
router.register('formulations', FormulationViewSet)
router.register('formulation-ingredients', FormulationIngredientViewSet)
router.register('stability-tests', StabilityTestViewSet)

urlpatterns = router.urls
