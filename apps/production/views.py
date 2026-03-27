from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
from .models import ProductionBatch, BatchRawMaterial, QCCheck
from apps.rnd.models import Formulation, FormulationIngredient
from apps.stock.models import Material, Lot, StockMovement


@login_required
def batch_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    batches = ProductionBatch.objects.select_related('formulation__product').all()
    if q:
        batches = batches.filter(batch_number__icontains=q)
    if status:
        batches = batches.filter(status=status)
    return render(request, 'production/batch_list.html', {
        'batches': batches, 'q': q, 'status': status,
        'status_choices': ProductionBatch.STATUS_CHOICES
    })


@login_required  # ✅ ERREUR 1 : manquait @login_required + def
def batch_detail(request, pk):
    batch = get_object_or_404(ProductionBatch, pk=pk)
    raw_materials = batch.raw_materials.select_related('material', 'lot').all()
    qc_checks = batch.qc_checks.all()
    time_logs = batch.time_logs.all()    
    return render(request, 'production/batch_detail.html', {
        'batch': batch, 'raw_materials': raw_materials, 'qc_checks': qc_checks, 'time_logs': time_logs
    })


@login_required
def batch_form(request, pk=None):
    batch = get_object_or_404(ProductionBatch, pk=pk) if pk else None
    formulations = Formulation.objects.filter(status='approved').select_related('product')

    presel_form_pk = request.GET.get('formulation')
    presel_formulation = None
    ingredients_preview = []

    if presel_form_pk:
        try:
            presel_formulation = Formulation.objects.get(pk=presel_form_pk, status='approved')
            ingredients_preview = presel_formulation.formulation_ingredients.select_related('ingredient').all()
        except Formulation.DoesNotExist:
            presel_formulation = None

    if batch and batch.planned_quantity:
        planned_value = batch.planned_quantity
    elif presel_formulation:
        planned_value = presel_formulation.batch_size
    else:
        planned_value = ""

    if request.method == 'POST':  # ✅ ERREUR 2 : supprimé le "@login_required\nd" parasite
        data = request.POST
        formulation_id = data.get('formulation')

        try:  # ✅ ERREUR 3 : planned_qty peut être vide, sécurisé
            planned_qty = Decimal(data.get('planned_quantity') or 0)
        except Exception:
            messages.error(request, "Quantité invalide.")
            return redirect('production:batch_add')

        try:
            formulation = Formulation.objects.get(pk=formulation_id, status='approved')
        except Formulation.DoesNotExist:
            messages.error(request, "Formulation invalide ou non approuvée.")
            return redirect('production:batch_add')

        if batch:
            batch.batch_number = data.get('batch_number', batch.batch_number)  # ✅ ERREUR 4 : .get() sécurisé
            batch.formulation = formulation
            batch.planned_quantity = planned_qty
            batch.production_date = data.get('production_date', batch.production_date)  # ✅ ERREUR 5 : .get() sécurisé
            batch.status = data.get('status', batch.status)
            batch.notes = data.get('notes', '')
            batch.save()
            messages.success(request, "Lot modifié.")
        else:
            batch_number = data.get('batch_number', '').strip()
            production_date = data.get('production_date', '').strip()

            if not batch_number or not production_date:  # ✅ ERREUR 6 : validation champs obligatoires
                messages.error(request, "Numéro de lot et date de production sont obligatoires.")
                return render(request, 'production/batch_form.html', {
                    'batch': None,
                    'formulations': formulations,
                    'status_choices': ProductionBatch.STATUS_CHOICES,
                    'presel_formulation': presel_formulation,
                    'ingredients_preview': ingredients_preview,
                    'planned_value': planned_qty,
                })

            batch = ProductionBatch.objects.create(
                batch_number=batch_number,
                formulation=formulation,
                planned_quantity=planned_qty,
                production_date=production_date,
                status='planned',
                responsible=request.user,
                notes=data.get('notes', '')
            )

            for fi in formulation.formulation_ingredients.select_related('ingredient').all():
                required_qty = (fi.percentage / Decimal('100')) * planned_qty
                material = getattr(fi.ingredient, 'stock_material', None)
                if not material:
                    material = Material.objects.filter(
                        name__icontains=fi.ingredient.name, is_active=True
                    ).first()
                BatchRawMaterial.objects.create(
                    batch=batch,
                    material=material,
                    ingredient_name=fi.ingredient.name,
                    ingredient_percentage=fi.percentage,
                    required_quantity=required_qty.quantize(Decimal('0.0001')),
                )

            messages.success(request,
                f"Lot {batch.batch_number} créé. "
                f"{batch.raw_materials.count()} matières calculées automatiquement depuis la formulation."
            )

        return redirect('production:batch_detail', pk=batch.pk)

    return render(request, 'production/batch_form.html', {
        'batch': batch,
        'formulations': formulations,
        'status_choices': ProductionBatch.STATUS_CHOICES,
        'presel_formulation': presel_formulation,
        'ingredients_preview': ingredients_preview,
        'planned_value': planned_value,
    })


@login_required
def batch_start(request, pk):
    batch = get_object_or_404(ProductionBatch, pk=pk)
    if batch.status != 'planned':
        messages.warning(request, "Ce lot n'est pas en statut Planifié.")
        return redirect('production:batch_detail', pk=pk)

    raw_materials = batch.raw_materials.select_related('material').all()
    errors = []

    for rm in raw_materials:
        if rm.material is None:
            errors.append("Matière introuvable dans le stock pour cet ingrédient.")
            continue
        available = rm.material.total_quantity
        if available < rm.required_quantity:
            errors.append(
                f"Stock insuffisant : {rm.material.name} — "
                f"Requis : {rm.required_quantity} {rm.material.unit} | "
                f"Disponible : {available} {rm.material.unit}"
            )

    if errors:
        for e in errors:
            messages.error(request, e)
        return redirect('production:batch_detail', pk=pk)

    for rm in raw_materials:
        if rm.material is None:
            continue
        to_deduct = rm.required_quantity
        lots_fifo = Lot.objects.filter(
            material=rm.material, is_active=True, current_quantity__gt=0
        ).order_by('expiry_date', 'reception_date')

        lot_used = None
        for lot in lots_fifo:
            if to_deduct <= 0:
                break
            take = min(lot.current_quantity, to_deduct)
            lot.current_quantity -= take
            lot.save()
            to_deduct -= take
            lot_used = lot
            StockMovement.objects.create(
                lot=lot,
                movement_type='production_use',
                quantity=-take,
                reference=f"LOT-PROD-{batch.batch_number}",
                performed_by=request.user
            )

        if lot_used:
            rm.lot = lot_used
            rm.actual_quantity = rm.required_quantity
            rm.save()

    batch.status = 'in_progress'
    batch.save()
    messages.success(request, f"Production lancée ! Stock déduit pour {raw_materials.count()} matières.")
    return redirect('production:batch_detail', pk=pk)


@login_required
def batch_complete(request, pk):
    batch = get_object_or_404(ProductionBatch, pk=pk)
    if request.method == 'POST':
        actual_qty = Decimal(request.POST.get('actual_quantity') or batch.planned_quantity)  # ✅ ERREUR 7 : sécurisé
        finished_lot_number = request.POST.get('finished_lot_number', f"PF-{batch.batch_number}")

        finished_material = Material.objects.filter(
            name__icontains=batch.formulation.product.name,
            material_type='finished_product',
            is_active=True
        ).first()

        if finished_material:
            from datetime import timedelta  # ✅ ERREUR 8 : import inutilisé déplacé ici pour propreté
            fin_lot = Lot.objects.create(
                material=finished_material,
                lot_number=finished_lot_number,
                initial_quantity=actual_qty,
                current_quantity=actual_qty,
                reception_date=batch.production_date,
                created_by=request.user,
                notes=f"Produit par lot de production {batch.batch_number}"
            )
            StockMovement.objects.create(
                lot=fin_lot,
                movement_type='production_output',
                quantity=actual_qty,
                reference=f"LOT-PROD-{batch.batch_number}",
                performed_by=request.user
            )
            batch.finished_lot = fin_lot
            messages.success(request,
                f"Produit fini ajouté en stock : {actual_qty} {finished_material.unit} — Lot {finished_lot_number}"
            )
        else:
            messages.warning(request,
                "Produit fini non trouvé dans le stock. "
                "Créez une matière de type 'Produit fini' avec le même nom que le produit R&D."
            )

        batch.actual_quantity = actual_qty
        batch.status = 'completed'
        batch.save()
        messages.success(request, f"Lot {batch.batch_number} marqué comme terminé.")

    return redirect('production:batch_detail', pk=pk)


@login_required
def qc_check_form(request, batch_pk):
    batch = get_object_or_404(ProductionBatch, pk=batch_pk)
    if request.method == 'POST':
        data = request.POST
        QCCheck.objects.create(
            batch=batch,
            test_name=data.get('test_name', ''),  # ✅ ERREUR 9 : .get() sécurisé au lieu de [] qui crash si manquant
            specification=data.get('specification', ''),
            measured_value=data.get('measured_value', ''),
            result=data.get('result', ''),
            performed_by=request.user,
            performed_at=timezone.now(),
            notes=data.get('notes', '')
        )
        messages.success(request, "Contrôle qualité ajouté.")
        return redirect('production:batch_detail', pk=batch_pk)
    return render(request, 'production/qc_check_form.html', {
        'batch': batch, 'result_choices': QCCheck.RESULT_CHOICES
    })

@login_required
def equipment_list(request):
    from .models import Equipment
    equipments = Equipment.objects.all()
    return render(request, 'production/equipment_list.html', {'equipments': equipments})

@login_required
def equipment_detail(request, pk):
    from .models import Equipment
    equipment = get_object_or_404(Equipment, pk=pk)
    logs = equipment.logs.all()
    return render(request, 'production/equipment_detail.html', {'equipment': equipment, 'logs': logs})

@login_required
def equipment_form(request, pk=None):
    from .models import Equipment
    equipment = get_object_or_404(Equipment, pk=pk) if pk else None
    if request.method == 'POST':
        data = request.POST
        if equipment:
            equipment.name = data.get('name') or equipment.name
            equipment.serial_number = data.get('serial_number', '')
            equipment.description = data.get('description', '')
            equipment.purchase_date = data.get('purchase_date') or None
            equipment.is_active = data.get('is_active') == 'on'
            equipment.save()
            messages.success(request, "Équipement modifié avec succès.")
        else:
            equipment = Equipment.objects.create(
                name=data.get('name'),
                serial_number=data.get('serial_number', ''),
                description=data.get('description', ''),
                purchase_date=data.get('purchase_date') or None,
                is_active=data.get('is_active') == 'on'
            )
            messages.success(request, "Équipement créé avec succès.")
        return redirect('production:equipment_detail', pk=equipment.pk)
    return render(request, 'production/equipment_form.html', {'equipment': equipment})

@login_required
def maintenance_add(request, equipment_pk):
    from .models import Equipment, MaintenanceLog
    equipment = get_object_or_404(Equipment, pk=equipment_pk)
    if request.method == 'POST':
        data = request.POST
        MaintenanceLog.objects.create(
            equipment=equipment,
            date=data.get('date'),
            description=data.get('description'),
            performed_by=data.get('performed_by'),
            cost=data.get('cost') or 0
        )
        equipment.last_maintenance = data.get('date')
        if data.get('next_maintenance'):
            equipment.next_maintenance = data.get('next_maintenance')
        equipment.save()
        messages.success(request, "Intervention enregistrée avec succès.")
    return redirect('production:equipment_detail', pk=equipment.pk)

@login_required
def batch_time_log_add(request, batch_pk):
    from .models import BatchTimeLog
    batch = get_object_or_404(ProductionBatch, pk=batch_pk)
    if request.method == 'POST':
        data = request.POST
        BatchTimeLog.objects.create(
            batch=batch,
            user=request.user,
            date=data.get('date'),
            duration_hours=data.get('duration_hours'),
            hourly_cost=data.get('hourly_cost') or 0
        )
        messages.success(request, "Heures de travail ajoutées au lot avec succès.")
    return redirect('production:batch_detail', pk=batch.pk)


# ─── PDF Fiche de Lot (depuis production) ─────────────────────────────────────

@login_required
def batch_pdf_view(request, pk):
    """
    GET /production/batches/<pk>/pdf/
    Redirige vers la vue PDF partagée dans sales.
    """
    from apps.sales.views import batch_pdf
    return batch_pdf(request, pk)