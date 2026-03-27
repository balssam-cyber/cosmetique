from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db.models import Sum, Count, Q


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    from apps.stock.models import Material, Lot
    from apps.production.models import ProductionBatch, QCCheck
    from apps.purchase.models import PurchaseOrder
    from apps.sales.models import SalesOrder
    from apps.rnd.models import Product, Formulation
    from apps.regulatory.models import SafetyReport, CPNPNotification

    expiry_threshold = timezone.now().date() + timedelta(
        days=getattr(settings, 'EXPIRY_ALERT_DAYS', 30))

    data = {
        'rnd': {
            'total_products': Product.objects.count(),
            'products_in_development': Product.objects.filter(status='development').count(),
            'products_approved': Product.objects.filter(status='approved').count(),
            'formulations': Formulation.objects.count(),
        },
        'production': {
            'batches_planned': ProductionBatch.objects.filter(status='planned').count(),
            'batches_in_progress': ProductionBatch.objects.filter(status='in_progress').count(),
            'batches_completed_this_month': ProductionBatch.objects.filter(
                status='completed',
                production_date__month=timezone.now().month
            ).count(),
            'failed_qc_checks': QCCheck.objects.filter(result='fail').count(),
        },
        'stock': {
            'total_raw_materials': Material.objects.filter(material_type='raw_material', is_active=True).count(),
            'low_stock_items': sum(
                1 for m in Material.objects.filter(is_active=True) if m.is_low_stock
            ),
            'expiring_lots': Lot.objects.filter(
                expiry_date__lte=expiry_threshold,
                expiry_date__gte=timezone.now().date(),
                is_active=True,
                current_quantity__gt=0
            ).count(),
            'expired_lots': Lot.objects.filter(
                expiry_date__lt=timezone.now().date(),
                is_active=True,
                current_quantity__gt=0
            ).count(),
        },
        'purchase': {
            'pending_orders': PurchaseOrder.objects.filter(
                status__in=['sent', 'confirmed']
            ).count(),
            'orders_this_month': PurchaseOrder.objects.filter(
                order_date__month=timezone.now().month
            ).count(),
        },
        'sales': {
            'orders_this_month': SalesOrder.objects.filter(
                order_date__month=timezone.now().month
            ).count(),
            'pending_shipments': SalesOrder.objects.filter(status='confirmed').count(),
        },
        'regulatory': {
            'expiring_reports': SafetyReport.objects.filter(
                expiry_date__lte=expiry_threshold,
                expiry_date__gte=timezone.now().date()
            ).count(),
            'pending_cpnp': CPNPNotification.objects.filter(status='pending').count(),
        },
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alerts_list(request):
    from apps.stock.models import Material, Lot
    from apps.production.models import QCCheck
    from apps.regulatory.models import SafetyReport

    alerts = []
    expiry_threshold = timezone.now().date() + timedelta(
        days=getattr(settings, 'EXPIRY_ALERT_DAYS', 30))

    # Low stock alerts
    for material in Material.objects.filter(is_active=True):
        if material.is_low_stock:
            alerts.append({
                'type': 'low_stock',
                'severity': 'critical' if material.total_quantity == 0 else 'warning',
                'title': f'Stock faible: {material.name}',
                'message': f'Quantité disponible: {material.total_quantity} {material.unit} '
                           f'(minimum: {material.minimum_stock})',
                'url': f'/stock/materials/{material.id}/'
            })

    # Expiring lots
    for lot in Lot.objects.filter(
        expiry_date__lte=expiry_threshold,
        expiry_date__gte=timezone.now().date(),
        is_active=True,
        current_quantity__gt=0
    ):
        alerts.append({
            'type': 'expiry',
            'severity': 'warning',
            'title': f'Expiration proche: {lot.material.name}',
            'message': f'Lot {lot.lot_number} expire le {lot.expiry_date}. '
                       f'Quantité restante: {lot.current_quantity}',
            'url': f'/stock/lots/{lot.id}/'
        })

    # Failed QC
    for qc in QCCheck.objects.filter(result='fail').select_related('batch'):
        alerts.append({
            'type': 'qc_fail',
            'severity': 'critical',
            'title': f'Échec CQ: {qc.test_name}',
            'message': f'Lot {qc.batch.batch_number} - {qc.notes}',
            'url': f'/production/batches/{qc.batch.id}/'
        })

    # Regulatory deadlines
    for report in SafetyReport.objects.filter(
        expiry_date__lte=expiry_threshold,
        expiry_date__gte=timezone.now().date()
    ):
        alerts.append({
            'type': 'regulatory_deadline',
            'severity': 'warning',
            'title': f'RSP expirant: {report.product.name}',
            'message': f'Rapport {report.report_number} expire le {report.expiry_date}',
            'url': f'/regulatory/safety-reports/{report.id}/'
        })

    return Response(alerts)


# ─── Nouvelles vues API ───────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kpi_dashboard(request):
    """
    GET /api/dashboard/kpis/
    Retourne les KPIs complets : CA, croissance, QC, stock, top produits, tendances.
    Résultats mis en cache 5 minutes.
    """
    from .analytics import get_kpi_summary
    use_cache = request.GET.get('refresh', '0') != '1'
    data = get_kpi_summary(use_cache=use_cache)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_view(request):
    """
    GET /api/dashboard/search/?q=<query>
    Recherche globale dans tous les modules ERP.
    Minimum 2 caractères requis.
    """
    from .search import global_search
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return Response({'query': query, 'results': {}, 'total': 0})
    results = global_search(query, request.user)
    total = sum(len(v) for v in results.values())
    return Response({'query': query, 'results': results, 'total': total})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_assistant_api(request):
    """
    POST /api/dashboard/ai/
    Body : {"question": "Analysez les alertes stock"}
    Réponse : {"response": "...", "question": "..."}
    """
    from .ai_assistant import ask_ai_assistant
    question = request.data.get('question', '').strip()
    if not question:
        return Response({'error': 'La question est requise'}, status=400)
    if len(question) > 800:
        return Response({'error': 'Question trop longue (max 800 caractères)'}, status=400)
    response_text = ask_ai_assistant(question)
    return Response({'response': response_text, 'question': question})
