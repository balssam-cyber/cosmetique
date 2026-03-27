"""
Analytics KPI pour le Dashboard CosmoERP.
Fournit get_kpi_summary() avec métriques complètes : CA, QC, stock, top produits, tendances.
"""
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta


def get_kpi_summary(use_cache=True):
    """
    Retourne tous les KPIs pour le dashboard.
    Résultat mis en cache 5 minutes pour les performances.
    """
    cache_key = 'cosmoerp_kpi_summary'
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    # Import ici pour éviter les imports circulaires
    from apps.sales.models import SalesOrder, SalesOrderLine
    from apps.production.models import QCCheck, ProductionBatch
    from apps.stock.models import Lot, Material

    today = timezone.now().date()
    month_start = today.replace(day=1)
    last_month_end = month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    # ── CA mensuel vs mois précédent ──────────────────────────────────────────
    def _sum_sales(qs):
        total = 0
        for order in qs:
            total += order.total_ttc
        return total

    this_month_orders = SalesOrder.objects.filter(
        order_date__gte=month_start,
        status__in=['shipped', 'invoiced']
    ).prefetch_related('lines')

    last_month_orders = SalesOrder.objects.filter(
        order_date__gte=last_month_start,
        order_date__lte=last_month_end,
        status__in=['shipped', 'invoiced']
    ).prefetch_related('lines')

    ca_this_month = sum(float(o.total_ttc) for o in this_month_orders)
    ca_last_month = sum(float(o.total_ttc) for o in last_month_orders)

    if ca_last_month > 0:
        ca_growth = round(((ca_this_month - ca_last_month) / ca_last_month) * 100, 1)
    else:
        ca_growth = 0.0

    # ── Taux de conformité qualité (mois en cours) ───────────────────────────
    total_qc = QCCheck.objects.filter(
        performed_at__date__gte=month_start
    ).count()
    passed_qc = QCCheck.objects.filter(
        performed_at__date__gte=month_start,
        result='pass'
    ).count()
    qc_rate = round((passed_qc / total_qc * 100) if total_qc > 0 else 100.0, 1)

    # ── Valeur totale du stock ─────────────────────────────────────────────────
    stock_value = 0.0
    for lot in Lot.objects.filter(is_active=True, current_quantity__gt=0).select_related('material'):
        if lot.material and lot.material.unit_price:
            stock_value += float(lot.current_quantity) * float(lot.material.unit_price)

    # ── Top 5 produits (chiffre d'affaires ce mois) ──────────────────────────
    top_products = list(
        SalesOrderLine.objects
        .filter(order__order_date__gte=month_start)
        .values('material__name', 'material__code')
        .annotate(
            total_qty=Sum('shipped_quantity'),
            total_revenue=Sum(F('shipped_quantity') * F('unit_price'))
        )
        .order_by('-total_revenue')[:5]
    )
    # Sérialiser les Decimal → float
    top_products = [
        {
            'nom': p['material__name'] or '—',
            'code': p['material__code'] or '—',
            'total_qty': float(p['total_qty'] or 0),
            'total_revenue': float(p['total_revenue'] or 0),
        }
        for p in top_products
    ]

    # ── Évolution CA 6 derniers mois ──────────────────────────────────────────
    six_months_ago = today - timedelta(days=180)
    monthly_orders = SalesOrder.objects.filter(
        order_date__gte=six_months_ago,
        status__in=['shipped', 'invoiced']
    ).order_by('order_date')

    # Grouper manuellement par mois
    monthly_map = {}
    for order in monthly_orders.prefetch_related('lines'):
        key = order.order_date.strftime('%b %Y')
        if key not in monthly_map:
            monthly_map[key] = {'ca': 0.0, 'nb_commandes': 0}
        monthly_map[key]['ca'] += float(order.total_ttc)
        monthly_map[key]['nb_commandes'] += 1

    monthly_trend = [
        {'month': k, 'ca': v['ca'], 'nb_commandes': v['nb_commandes']}
        for k, v in monthly_map.items()
    ]

    # ── Alertes ───────────────────────────────────────────────────────────────
    low_stock_materials = [m for m in Material.objects.filter(is_active=True) if m.is_low_stock]
    stock_critique = len(low_stock_materials)

    lots_expirant_7j = Lot.objects.filter(
        expiry_date__lte=today + timedelta(days=7),
        expiry_date__gte=today,
        is_active=True,
        current_quantity__gt=0
    ).count()

    commandes_retard = SalesOrder.objects.filter(
        status='confirmed',
        delivery_date__lt=today
    ).count()

    batches_en_cours = ProductionBatch.objects.filter(status='in_progress').count()

    result = {
        'ca_this_month': ca_this_month,
        'ca_last_month': ca_last_month,
        'ca_growth_percent': ca_growth,
        'qc_rate': qc_rate,
        'qc_total': total_qc,
        'qc_passed': passed_qc,
        'stock_value': stock_value,
        'top_products': top_products,
        'monthly_trend': monthly_trend,
        'alerts': {
            'stock_critique': stock_critique,
            'lots_expirant_7j': lots_expirant_7j,
            'commandes_retard': commandes_retard,
            'batches_en_cours': batches_en_cours,
        }
    }

    if use_cache:
        cache.set(cache_key, result, timeout=300)  # Cache 5 minutes

    return result
