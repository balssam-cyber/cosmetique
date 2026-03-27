from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count
from django.utils import timezone
from datetime import timedelta
import json

from apps.sales.models import SalesOrder, SalesOrderLine
from apps.purchase.models import PurchaseOrder, GoodsReceiptLine

@login_required
def dashboard(request):
    # ==========================================
    # 1. KPIs Généraux (Chiffre d'Affaires & Achats)
    # ==========================================
    
    # Chiffre d'Affaires total (Ventes expédiées ou facturées)
    shipped_sales = SalesOrder.objects.filter(status__in=['shipped', 'invoiced'])
    total_revenue = sum(order.total_amount for order in shipped_sales)
    
    # Achats totaux (Basé sur les réceptions réelles)
    receipt_lines = GoodsReceiptLine.objects.all()
    total_purchases = sum(float(line.quantity) * float(line.unit_cost) for line in receipt_lines if line.unit_cost)
    
    # Bénéfice Brut Estimmé
    gross_profit = float(total_revenue) - total_purchases
    
    # ==========================================
    # 2. Analyse Temporelle (Exemple : 6 derniers mois)
    # ==========================================
    # Pour la démo, on aggrège simplement par mois les commandes
    import datetime
    today = datetime.date.today()
    six_months_ago = today - datetime.timedelta(days=180)
    
    recent_sales = SalesOrder.objects.filter(
        status__in=['shipped', 'invoiced'],
        order_date__gte=six_months_ago
    )
    
    # Construction des séries temporelles (très simple)
    months_data = {}
    for i in range(5, -1, -1):
        dt = today - datetime.timedelta(days=30*i)
        key = dt.strftime("%Y-%m")
        months_data[key] = {'revenue': 0, 'purchases': 0}
        
    for order in recent_sales:
        key = order.order_date.strftime("%Y-%m")
        if key in months_data:
            months_data[key]['revenue'] += float(order.total_amount)
            
    recent_purchases = PurchaseOrder.objects.filter(
        status__in=['received', 'partially_received'],
        order_date__gte=six_months_ago
    )
    for purchase in recent_purchases:
        key = purchase.order_date.strftime("%Y-%m")
        if key in months_data:
            months_data[key]['purchases'] += float(purchase.total_amount_tnd)
            
    labels = list(months_data.keys())
    revenue_series = [months_data[k]['revenue'] for k in labels]
    purchases_series = [months_data[k]['purchases'] for k in labels]
    
    # ==========================================
    # 3. Top Produits (Pareto - 80/20)
    # ==========================================
    top_products = (
        SalesOrderLine.objects
        .filter(order__status__in=['shipped', 'invoiced'])
        .values('material__name')
        .annotate(total_qty=Sum('shipped_quantity'))
        .order_by('-total_qty')[:5]
    )
    prod_labels = [p['material__name'] for p in top_products]
    prod_data = [float(p['total_qty']) for p in top_products]

    context = {
        'total_revenue': total_revenue,
        'total_purchases': total_purchases,
        'gross_profit': gross_profit,
        
        # Données JSON pour Chart.js
        'chart_labels': json.dumps(labels),
        'revenue_series': json.dumps(revenue_series),
        'purchases_series': json.dumps(purchases_series),
        'prod_labels': json.dumps(prod_labels),
        'prod_data': json.dumps(prod_data),
    }
    
    return render(request, 'analytics/dashboard.html', context)
