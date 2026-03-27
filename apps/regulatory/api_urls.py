from rest_framework.routers import DefaultRouter
from .api_views import ProductComplianceViewSet, SafetyReportViewSet, BPFDeclarationViewSet, CPNPNotificationViewSet, ProductLabelViewSet

router = DefaultRouter()
router.register('compliance', ProductComplianceViewSet)
router.register('safety-reports', SafetyReportViewSet)
router.register('bpf-declarations', BPFDeclarationViewSet)
router.register('cpnp-notifications', CPNPNotificationViewSet)
router.register('labels', ProductLabelViewSet)

urlpatterns = router.urls
