from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


@login_required
def index(request):
    from apps.stock.models import Material, Lot
    from apps.production.models import ProductionBatch, QCCheck
    from apps.purchase.models import PurchaseOrder, StockShortage
    from apps.sales.models import SalesOrder
    from apps.rnd.models import Product
    from apps.regulatory.models import SafetyReport

    expiry_threshold = timezone.now().date() + timedelta(
        days=getattr(settings, 'EXPIRY_ALERT_DAYS', 30))

    low_stock = [m for m in Material.objects.filter(is_active=True) if m.is_low_stock]
    expiring = Lot.objects.filter(
        expiry_date__lte=expiry_threshold,
        expiry_date__gte=timezone.now().date(),
        is_active=True, current_quantity__gt=0
    ).count()
    failed_qc = QCCheck.objects.filter(result='fail').count()
    pending_regulatory = SafetyReport.objects.filter(
        expiry_date__lte=expiry_threshold,
        expiry_date__gte=timezone.now().date()
    ).count()

    # ── المنقوصات غير المحلولة ──
    active_shortages = StockShortage.objects.filter(
        is_resolved=False
    ).select_related('order').order_by('-created_at')

    context = {
        'total_products': Product.objects.count(),
        'products_approved': Product.objects.filter(status='approved').count(),
        'batches_in_progress': ProductionBatch.objects.filter(status='in_progress').count(),
        'batches_completed': ProductionBatch.objects.filter(status='completed').count(),
        'failed_qc': failed_qc,
        'low_stock_count': len(low_stock),
        'expiring_count': expiring,
        'low_stock_items': low_stock[:5],
        'pending_orders': PurchaseOrder.objects.filter(status__in=['sent', 'confirmed']).count(),
        'pending_sales': SalesOrder.objects.filter(status='confirmed').count(),
        'orders_this_month': SalesOrder.objects.filter(
            order_date__month=timezone.now().month).count(),
        'pending_regulatory': pending_regulatory,
        'recent_batches': ProductionBatch.objects.order_by('-created_at')[:5],
        'recent_sales': SalesOrder.objects.order_by('-created_at')[:5],
        # ── جديد ──
        'active_shortages': active_shortages,
        'shortages_count': active_shortages.count(),
    }
    return render(request, 'dashboard/index.html', context)