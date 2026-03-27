"""
Recherche globale unifiée dans tous les modules CosmoERP.
global_search(query) → dict avec résultats par module.
"""
from django.db.models import Q


def global_search(query: str, user=None) -> dict:
    """
    Recherche dans tous les modules ERP en une seule fonction.
    Retourne un dict groupé par module avec max 5 résultats chacun.
    Requiert au minimum 2 caractères.
    """
    if not query or len(query.strip()) < 2:
        return {}

    query = query.strip()
    results = {}

    # ── Produits R&D ──────────────────────────────────────────────────────────
    try:
        from apps.rnd.models import Product
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query) | Q(description__icontains=query)
        )[:5]
        if products.exists():
            results['products'] = [
                {
                    'id': p.id,
                    'label': f"{p.code} — {p.name}",
                    'sub': p.get_status_display() if hasattr(p, 'get_status_display') else '',
                    'url': f'/rnd/products/{p.id}/',
                    'module': 'R&D',
                    'icon': 'bi-flask',
                }
                for p in products
            ]
    except Exception:
        pass

    # ── Lots de production ─────────────────────────────────────────────────────
    try:
        from apps.production.models import ProductionBatch
        batches = ProductionBatch.objects.filter(
            Q(batch_number__icontains=query) | Q(formulation__product__name__icontains=query)
        ).select_related('formulation__product')[:5]
        if batches.exists():
            results['batches'] = [
                {
                    'id': b.id,
                    'label': f"Lot {b.batch_number}",
                    'sub': b.formulation.product.name if b.formulation else '—',
                    'url': f'/production/batches/{b.id}/',
                    'module': 'Production',
                    'icon': 'bi-gear',
                }
                for b in batches
            ]
    except Exception:
        pass

    # ── Clients ───────────────────────────────────────────────────────────────
    try:
        from apps.sales.models import Customer
        customers = Customer.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query) | Q(email__icontains=query)
        )[:5]
        if customers.exists():
            results['customers'] = [
                {
                    'id': c.id,
                    'label': f"{c.code} — {c.name}",
                    'sub': c.email or c.country or '',
                    'url': f'/sales/customers/{c.id}/',
                    'module': 'Ventes',
                    'icon': 'bi-people',
                }
                for c in customers
            ]
    except Exception:
        pass

    # ── Commandes ventes ──────────────────────────────────────────────────────
    try:
        from apps.sales.models import SalesOrder
        orders = SalesOrder.objects.filter(
            Q(order_number__icontains=query) | Q(customer__name__icontains=query)
        ).select_related('customer')[:5]
        if orders.exists():
            results['sales_orders'] = [
                {
                    'id': o.id,
                    'label': f"CV-{o.order_number}",
                    'sub': o.customer.name,
                    'url': f'/sales/orders/{o.id}/',
                    'module': 'Ventes',
                    'icon': 'bi-cart',
                }
                for o in orders
            ]
    except Exception:
        pass

    # ── Fournisseurs / Achats ─────────────────────────────────────────────────
    try:
        from apps.purchase.models import Supplier
        suppliers = Supplier.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query) | Q(email__icontains=query)
        )[:5]
        if suppliers.exists():
            results['suppliers'] = [
                {
                    'id': s.id,
                    'label': s.name,
                    'sub': s.email or '',
                    'url': f'/purchase/suppliers/{s.id}/',
                    'module': 'Achats',
                    'icon': 'bi-truck',
                }
                for s in suppliers
            ]
    except Exception:
        pass

    # ── Matières stock ────────────────────────────────────────────────────────
    try:
        from apps.stock.models import Material
        materials = Material.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )[:5]
        if materials.exists():
            results['materials'] = [
                {
                    'id': m.id,
                    'label': f"{m.code} — {m.name}",
                    'sub': m.get_material_type_display() if hasattr(m, 'get_material_type_display') else '',
                    'url': f'/stock/materials/{m.id}/',
                    'module': 'Stock',
                    'icon': 'bi-box-seam',
                }
                for m in materials
            ]
    except Exception:
        pass

    return results
