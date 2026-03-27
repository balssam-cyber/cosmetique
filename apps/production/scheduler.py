"""
Planificateur intelligent de production pour CosmoERP.

Fonctions principales :
- check_production_feasibility() → Vérifie la disponibilité des matières avant lancement
- get_production_schedule()      → Retourne un planning estimé
- calculate_completion_date()    → Estime la date de fin de production

Ces fonctions sont utilisées en complément des vues production existantes.
"""
from django.utils import timezone
from django.db.models import Sum, F, Q
from datetime import timedelta


def check_production_feasibility(formulation, planned_quantity: float) -> dict:
    """
    Vérifie si on peut produire `planned_quantity` kg du produit.
    
    Args:
        formulation: Instance de apps.rnd.models.Formulation
        planned_quantity: Quantité à produire (en kg)
    
    Returns:
        dict avec :
            - can_produce (bool)
            - missing_materials (list)
            - available_materials (list)
            - coverage_percent (float) : % de couverture des matières
            - estimated_cost (float)   : Coût matières estimé en DT
    
    Exemple d'utilisation dans une vue :
        from apps.production.scheduler import check_production_feasibility
        feasibility = check_production_feasibility(batch.formulation, batch.planned_quantity)
        if not feasibility['can_produce']:
            for m in feasibility['missing_materials']:
                messages.error(request, f"Manque : {m['ingredient']} - {m['shortage']} {m['unit']}")
    """
    from apps.stock.models import Lot, Material
    from apps.rnd.models import FormulationIngredient
    from decimal import Decimal

    feasibility = {
        'can_produce': True,
        'missing_materials': [],
        'available_materials': [],
        'coverage_percent': 100.0,
        'estimated_cost': 0.0,
        'formulation': formulation.name if formulation else '—',
        'planned_quantity': float(planned_quantity),
    }

    planned_qty = Decimal(str(planned_quantity))

    try:
        ingredients = FormulationIngredient.objects.filter(
            formulation=formulation
        ).select_related('ingredient')
    except Exception:
        return feasibility

    total_required = 0
    total_available_for_required = 0

    for fi in ingredients:
        # Quantité requise = pourcentage × quantité planifiée / 100
        required_qty = (fi.percentage / Decimal('100')) * planned_qty

        # Chercher les matières disponibles via le nom de l'ingrédient
        material = getattr(fi.ingredient, 'stock_material', None)
        if not material:
            material = Material.objects.filter(
                name__icontains=fi.ingredient.name,
                is_active=True
            ).first()

        if material:
            available = material.total_quantity
        else:
            # Chercher dans les lots directement
            available = Lot.objects.filter(
                material__name__icontains=fi.ingredient.name,
                is_active=True,
                current_quantity__gt=0,
                expiry_date__gte=timezone.now().date()
            ).aggregate(total=Sum('current_quantity'))['total'] or Decimal('0')

        available = Decimal(str(available))
        required_qty_f = float(required_qty)
        available_f = float(available)

        # Coût estimé
        unit_price = float(material.unit_price) if material and material.unit_price else 0
        estimated_cost = required_qty_f * unit_price
        feasibility['estimated_cost'] += estimated_cost

        total_required += required_qty_f
        total_available_for_required += min(available_f, required_qty_f)

        entry = {
            'ingredient': fi.ingredient.name,
            'required': required_qty_f,
            'available': available_f,
            'unit': material.unit if material else fi.ingredient.unit if hasattr(fi.ingredient, 'unit') else 'kg',
            'percentage': float(fi.percentage),
        }

        if available < required_qty:
            feasibility['can_produce'] = False
            entry['shortage'] = required_qty_f - available_f
            feasibility['missing_materials'].append(entry)
        else:
            entry['surplus'] = available_f - required_qty_f
            feasibility['available_materials'].append(entry)

    # Coverage %
    if total_required > 0:
        feasibility['coverage_percent'] = round(
            (total_available_for_required / total_required) * 100, 1
        )

    return feasibility


def get_production_schedule(days_ahead: int = 30) -> list:
    """
    Retourne la liste des lots planifiés pour les prochains `days_ahead` jours.
    Vérifie la faisabilité de chaque lot.
    
    Returns:
        list de dict avec infos lot + faisabilité
    """
    from apps.production.models import ProductionBatch

    today = timezone.now().date()
    end_date = today + timedelta(days=days_ahead)

    batches = ProductionBatch.objects.filter(
        status='planned',
        production_date__gte=today,
        production_date__lte=end_date,
    ).select_related('formulation__product', 'responsible').order_by('production_date')

    schedule = []
    for batch in batches:
        feasibility = check_production_feasibility(batch.formulation, batch.planned_quantity)
        schedule.append({
            'batch_number': batch.batch_number,
            'product': batch.formulation.product.name if batch.formulation else '—',
            'formulation': batch.formulation.name if batch.formulation else '—',
            'planned_quantity': float(batch.planned_quantity),
            'production_date': batch.production_date.strftime('%d/%m/%Y'),
            'responsible': batch.responsible.get_full_name() if batch.responsible else '—',
            'can_produce': feasibility['can_produce'],
            'coverage_percent': feasibility['coverage_percent'],
            'missing_count': len(feasibility['missing_materials']),
            'estimated_cost': feasibility['estimated_cost'],
            'batch_id': batch.id,
        })

    return schedule


def auto_deduct_stock_fifo(batch) -> list:
    """
    Déduit automatiquement les stocks selon la méthode FIFO (expiration la plus proche d'abord).
    Retourne la liste détaillée des lots consommés.
    
    Note : Cette logique est déjà implémentée dans production/views.py::batch_start().
    Ce module offre une version standalone réutilisable pour les signaux ou tâches async.
    
    Args:
        batch: Instance de ProductionBatch
    
    Returns:
        list de dict {lot, ingredient, consumed, unit}
    """
    from apps.rnd.models import FormulationIngredient
    from apps.stock.models import Lot, StockMovement
    from decimal import Decimal

    consumed_list = []

    if not batch.formulation:
        return consumed_list

    ingredients = FormulationIngredient.objects.filter(
        formulation=batch.formulation
    ).select_related('ingredient')

    for fi in ingredients:
        needed = (fi.percentage / Decimal('100')) * batch.planned_quantity

        # Chercher les lots disponibles FIFO (plus proche expiration d'abord)
        lots = Lot.objects.filter(
            material__name__icontains=fi.ingredient.name,
            is_active=True,
            current_quantity__gt=0,
            expiry_date__gte=timezone.now().date()
        ).order_by('expiry_date', 'reception_date')

        for lot in lots:
            if needed <= 0:
                break
            take = min(Decimal(str(lot.current_quantity)), needed)
            lot.current_quantity = Decimal(str(lot.current_quantity)) - take
            lot.save(update_fields=['current_quantity'])
            needed -= take
            consumed_list.append({
                'lot': lot.lot_number,
                'ingredient': fi.ingredient.name,
                'consumed': float(take),
                'unit': lot.material.unit if lot.material else 'kg',
            })

    return consumed_list


def get_feasibility_summary_for_batch(batch) -> dict:
    """
    Raccourci pour obtenir la faisabilité d'un lot existant.
    """
    if not batch.formulation:
        return {'can_produce': False, 'missing_materials': [], 'available_materials': [],
                'coverage_percent': 0, 'estimated_cost': 0}
    return check_production_feasibility(batch.formulation, batch.planned_quantity)
