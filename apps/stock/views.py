from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from .models import MaterialCategory, Material, Lot, StockMovement

try:
    from apps.rnd.models import Ingredient
    RND_AVAILABLE = True
except ImportError:
    RND_AVAILABLE = False


@login_required
def material_list(request):
    q = request.GET.get('q', '')
    mtype = request.GET.get('type', '')
    materials = Material.objects.filter(is_active=True).order_by('name')
    if q:
        materials = materials.filter(Q(name__icontains=q) | Q(code__icontains=q))
    if mtype:
        materials = materials.filter(material_type=mtype)
    for m in materials:
        m.qty = m.total_quantity
        m.low = m.is_low_stock
    return render(request, 'stock/material_list.html', {
        'materials': materials, 'q': q, 'mtype': mtype,
        'type_choices': Material.TYPE_CHOICES
    })


@login_required
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    lots = material.lots.filter(is_active=True).order_by('expiry_date', 'reception_date')
    movements = StockMovement.objects.filter(lot__material=material).order_by('-created_at')[:50]
    return render(request, 'stock/material_detail.html', {
        'material': material, 'lots': lots, 'movements': movements
    })


@login_required
def material_form(request, pk=None):
    material = get_object_or_404(Material, pk=pk) if pk else None
    categories = MaterialCategory.objects.all()
    ingredients = Ingredient.objects.all().order_by('name') if RND_AVAILABLE else []
    if request.method == 'POST':
        data = request.POST
        cat_id = data.get('category')
        cat = MaterialCategory.objects.get(pk=cat_id) if cat_id else None
        # Ingredient FK
        ing_id = data.get('ingredient')
        ingredient = None
        if ing_id and RND_AVAILABLE:
            try:
                ingredient = Ingredient.objects.get(pk=ing_id)
                # Check not already linked to another material
                existing = Material.objects.filter(ingredient=ingredient).exclude(pk=pk).first()
                if existing:
                    messages.error(request, f"Cet ingrédient est déjà lié à '{existing.name}'.")
                    ingredient = None
            except Ingredient.DoesNotExist:
                ingredient = None

        if material:
            material.name = data['name']
            material.code = data['code']
            material.material_type = data['material_type']
            material.unit = data['unit']
            material.minimum_stock = data.get('minimum_stock') or 0
            material.reorder_quantity = data.get('reorder_quantity') or 0
            material.description = data.get('description', '')
            material.category = cat
            material.ingredient = ingredient
            material.save()
            messages.success(request, "Matière modifiée avec succès.")
        else:
            material = Material.objects.create(
                name=data['name'], code=data['code'],
                material_type=data['material_type'], unit=data['unit'],
                minimum_stock=data.get('minimum_stock') or 0,
                reorder_quantity=data.get('reorder_quantity') or 0,
                description=data.get('description', ''), category=cat,
                ingredient=ingredient
            )
            messages.success(request, "Matière créée avec succès.")
        return redirect('stock:material_detail', pk=material.pk)
    return render(request, 'stock/material_form.html', {
        'material': material, 'categories': categories,
        'type_choices': Material.TYPE_CHOICES,
        'unit_choices': Material.UNIT_CHOICES,
        'ingredients': ingredients,
    })


@login_required
def lot_list(request):
    q = request.GET.get('q', '')
    mtype = request.GET.get('type', '')
    lots = Lot.objects.filter(is_active=True).select_related('material').order_by('expiry_date', 'material__name')
    if q:
        lots = lots.filter(Q(lot_number__icontains=q) | Q(material__name__icontains=q))
    if mtype:
        lots = lots.filter(material__material_type=mtype)
    expiry_threshold = timezone.now().date() + timedelta(days=getattr(settings, 'EXPIRY_ALERT_DAYS', 30))
    return render(request, 'stock/lot_list.html', {
        'lots': lots, 'q': q, 'mtype': mtype,
        'expiry_threshold': expiry_threshold,
        'type_choices': Material.TYPE_CHOICES,
    })


@login_required
def lot_detail(request, pk):
    lot = get_object_or_404(Lot, pk=pk)
    movements = lot.movements.order_by('-created_at')
    return render(request, 'stock/lot_detail.html', {'lot': lot, 'movements': movements})


@login_required
def lot_add(request):
    """Add a new lot manually (reception sans bon de commande)."""
    materials = Material.objects.filter(is_active=True).order_by('name')
    if request.method == 'POST':
        data = request.POST
        mat = get_object_or_404(Material, pk=data['material'])
        qty = Decimal(data['quantity'])
        lot = Lot.objects.create(
            material=mat,
            lot_number=data['lot_number'],
            supplier=data.get('supplier', ''),
            initial_quantity=qty,
            current_quantity=qty,
            reception_date=data['reception_date'],
            expiry_date=data.get('expiry_date') or None,
            unit_cost=data.get('unit_cost') or 0,
            location=data.get('location', ''),
            notes=data.get('notes', ''),
            created_by=request.user
        )
        StockMovement.objects.create(
            lot=lot, movement_type='reception', quantity=qty,
            reference=data.get('reference', ''),
            performed_by=request.user
        )
        messages.success(request, f"Lot {lot.lot_number} ajouté au stock ({qty} {mat.unit}).")
        return redirect('stock:material_detail', pk=mat.pk)
    return render(request, 'stock/lot_form.html', {'materials': materials})


@login_required
def movement_list(request):
    mtype = request.GET.get('type', '')
    movements = StockMovement.objects.select_related('lot__material', 'performed_by').order_by('-created_at')[:200]
    if mtype:
        movements = StockMovement.objects.filter(movement_type=mtype).select_related('lot__material').order_by('-created_at')[:200]
    return render(request, 'stock/movement_list.html', {
        'movements': movements, 'mtype': mtype,
        'movement_choices': StockMovement.MOVEMENT_TYPE_CHOICES,
    })


@login_required
def alerts_view(request):
    expiry_threshold = timezone.now().date() + timedelta(days=getattr(settings, 'EXPIRY_ALERT_DAYS', 30))
    low_stock = [m for m in Material.objects.filter(is_active=True) if m.is_low_stock]
    expiring = Lot.objects.filter(
        expiry_date__lte=expiry_threshold,
        expiry_date__gte=timezone.now().date(),
        is_active=True, current_quantity__gt=0
    ).select_related('material')
    expired = Lot.objects.filter(
        expiry_date__lt=timezone.now().date(),
        is_active=True, current_quantity__gt=0
    ).select_related('material')
    return render(request, 'stock/alerts.html', {
        'low_stock': low_stock, 'expiring': expiring, 'expired': expired
    })


@login_required
def qc_dashboard(request):
    lots = Lot.objects.filter(is_active=True, qc_status='quarantine').order_by('production_date')
    return render(request, 'stock/qc_dashboard.html', {'lots': lots})


@login_required
def lot_qc_update(request, pk):
    lot = get_object_or_404(Lot, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            lot.qc_status = 'approved'
            messages.success(request, f"Lot {lot.lot_number} approuvé avec succès.")
        elif action == 'reject':
            lot.qc_status = 'rejected'
            messages.error(request, f"Lot {lot.lot_number} rejeté (Non Conforme).")
        lot.save()
        
        # Rediriger d'où on vient
        next_url = request.POST.get('next', '')
        if next_url:
            return redirect(next_url)
    return redirect('stock:qc_dashboard')
