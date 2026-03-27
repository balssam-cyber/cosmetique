from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal, InvalidOperation
import uuid
from .models import Supplier, PurchaseOrder, PurchaseOrderLine, GoodsReceipt
from apps.stock.models import Material


@login_required
def supplier_list(request):
    q = request.GET.get('q', '')
    suppliers = Supplier.objects.filter(is_active=True)
    if q:
        suppliers = suppliers.filter(Q(name__icontains=q) | Q(code__icontains=q))
    return render(request, 'purchase/supplier_list.html', {'suppliers': suppliers, 'q': q})


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    orders = supplier.orders.all().order_by('-order_date')[:20]
    return render(request, 'purchase/supplier_detail.html', {'supplier': supplier, 'orders': orders})


@login_required
def supplier_form(request, pk=None):
    supplier = get_object_or_404(Supplier, pk=pk) if pk else None
    if request.method == 'POST':
        data = request.POST
        if supplier:
            for field in ['name', 'code', 'contact_name', 'email', 'phone', 'address', 'country', 'notes']:
                setattr(supplier, field, data.get(field, ''))
            supplier.save()
            messages.success(request, "Fournisseur modifié.")
        else:
            supplier = Supplier.objects.create(
                name=data['name'], code=data['code'],
                contact_name=data.get('contact_name', ''),
                email=data.get('email', ''), phone=data.get('phone', ''),
                address=data.get('address', ''), country=data.get('country', ''),
            )
            messages.success(request, "Fournisseur créé.")
        return redirect('purchase:supplier_detail', pk=supplier.pk)
    return render(request, 'purchase/supplier_form.html', {'supplier': supplier})


@login_required
def order_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    orders = PurchaseOrder.objects.select_related('supplier').all()
    if q:
        orders = orders.filter(Q(order_number__icontains=q) | Q(supplier__name__icontains=q))
    if status:
        orders = orders.filter(status=status)
    return render(request, 'purchase/order_list.html', {
        'orders': orders, 'q': q, 'status': status,
        'status_choices': PurchaseOrder.STATUS_CHOICES
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    receipts = order.receipts.all()
    return render(request, 'purchase/order_detail.html', {'order': order, 'receipts': receipts})


@login_required
def order_form(request, pk=None):
    order = get_object_or_404(PurchaseOrder, pk=pk) if pk else None
    suppliers = Supplier.objects.filter(is_active=True)

    if request.method == 'POST':
        data = request.POST
        order_number = data.get('order_number', '').strip()
        supplier_id  = data.get('supplier', '').strip()
        order_date   = data.get('order_date', '').strip()

        if not order_number or not supplier_id or not order_date:
            messages.error(request, "Numéro, fournisseur et date sont obligatoires.")
            return render(request, 'purchase/order_form.html', {
                'order': order, 'suppliers': suppliers,
                'status_choices': PurchaseOrder.STATUS_CHOICES,
                'currency_choices': PurchaseOrder.CURRENCY_CHOICES,
            })

        if not order and PurchaseOrder.objects.filter(order_number=order_number).exists():
            messages.error(request, f"Le numéro '{order_number}' existe déjà.")
            return render(request, 'purchase/order_form.html', {
                'order': order, 'suppliers': suppliers,
                'status_choices': PurchaseOrder.STATUS_CHOICES,
                'currency_choices': PurchaseOrder.CURRENCY_CHOICES,
            })

        currency      = data.get('currency', 'TND')
        exchange_rate = Decimal(data.get('exchange_rate') or '1')

        if order:
            order.supplier_id       = supplier_id
            order.status            = data.get('status', order.status)
            order.order_date        = order_date
            order.expected_delivery = data.get('expected_delivery') or None
            order.notes             = data.get('notes', '')
            order.currency          = currency
            order.exchange_rate     = exchange_rate
            order.save()
            order.lines.all().delete()
        else:
            order = PurchaseOrder.objects.create(
                order_number      = order_number,
                supplier_id       = supplier_id,
                order_date        = order_date,
                expected_delivery = data.get('expected_delivery') or None,
                notes             = data.get('notes', ''),
                currency          = currency,
                exchange_rate     = exchange_rate,
                created_by        = request.user,
            )

        material_names = data.getlist('material_name[]')
        material_units = data.getlist('material_unit[]')
        quantities     = data.getlist('quantity[]')
        unit_prices    = data.getlist('unit_price[]')

        lines_created = 0
        for name, unit, qty_str, price_str in zip(material_names, material_units, quantities, unit_prices):
            name = name.strip()
            unit = unit.strip() or 'kg'
            if not name or not qty_str:
                continue
            try:
                qty   = Decimal(qty_str)
                price = Decimal(price_str) if price_str else Decimal('0')
            except InvalidOperation:
                continue
            if qty <= 0:
                continue

            material = Material.objects.filter(name__iexact=name, is_active=True).first()
            if not material:
                code = name.upper().replace(' ', '-')[:20]
                if Material.objects.filter(code=code).exists():
                    code = f"{code[:15]}-{str(uuid.uuid4())[:4].upper()}"
                material = Material.objects.create(
                    code          = code,
                    name          = name,
                    unit          = unit if unit in ['kg', 'g', 'L', 'mL', 'pcs', 'box'] else 'kg',
                    is_active     = True,
                    material_type = 'raw_material',
                )

            PurchaseOrderLine.objects.create(
                order      = order,
                material   = material,
                quantity   = qty,
                unit_price = price,
            )
            lines_created += 1

        if lines_created == 0:
            messages.warning(request, "Commande enregistrée mais aucune ligne ajoutée.")
        else:
            messages.success(request,
                f"Bon de commande enregistré — {lines_created} ligne(s) — "
                f"Total : {order.total_amount:.2f} {order.currency} "
                f"({order.total_amount_tnd:.2f} TND)"
            )

        return redirect('purchase:order_detail', pk=order.pk)

    return render(request, 'purchase/order_form.html', {
        'order': order,
        'suppliers': suppliers,
        'status_choices': PurchaseOrder.STATUS_CHOICES,
        'currency_choices': PurchaseOrder.CURRENCY_CHOICES,
    })


@login_required
def receipt_form(request, order_pk):
    order = get_object_or_404(PurchaseOrder, pk=order_pk)
    if request.method == 'POST':
        data = request.POST
        receipt = GoodsReceipt.objects.create(
            order        = order,
            receipt_date = data['receipt_date'],
            reference    = data.get('reference', ''),
            notes        = data.get('notes', ''),
            received_by  = request.user,
        )
        from apps.stock.models import Lot, StockMovement
        from .models import GoodsReceiptLine

        for line in order.lines.all():
            lot_num = data.get(f'lot_{line.pk}', '').strip()
            qty_str = data.get(f'qty_{line.pk}', '0')
            exp     = data.get(f'expiry_{line.pk}') or None
            try:
                qty = Decimal(qty_str) if qty_str else Decimal('0')
            except InvalidOperation:
                qty = Decimal('0')

            if qty <= 0:
                continue

            if not lot_num:
                lot_num = f"AUTO-{order.order_number}-{line.pk}"

            lot = Lot.objects.create(
                material         = line.material,
                lot_number       = lot_num,
                supplier         = order.supplier.name,
                initial_quantity = qty,
                current_quantity = qty,
                expiry_date      = exp,
                unit_cost        = line.unit_price,
                created_by       = request.user,
            )
            StockMovement.objects.create(
                lot           = lot,
                movement_type = 'reception',
                quantity      = qty,
                reference     = f"BC-{order.order_number}",
                performed_by  = request.user,
            )
            GoodsReceiptLine.objects.create(
                receipt     = receipt,
                order_line  = line,
                lot_number  = lot_num,
                quantity    = qty,
                expiry_date = exp,
                unit_cost   = line.unit_price,
                created_lot = lot,
            )
            line.received_quantity += qty
            line.save()

        all_rcvd = all(l.received_quantity >= l.quantity for l in order.lines.all())
        order.status = 'received' if all_rcvd else 'partially_received'
        order.save()
        messages.success(request, "Réception enregistrée, stock mis à jour.")
        return redirect('purchase:order_detail', pk=order_pk)

    return render(request, 'purchase/receipt_form.html', {'order': order})
@login_required
def quick_receive(request, pk):
    """Réceptionner tout en un clic avec possibilité de noter les manques."""
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        from apps.stock.models import Lot, StockMovement
        from .models import GoodsReceiptLine, StockShortage
        from django.utils import timezone

        receipt = GoodsReceipt.objects.create(
            order        = order,
            receipt_date = timezone.now().date(),
            reference    = request.POST.get('reference', ''),
            notes        = request.POST.get('notes', ''),
            received_by  = request.user,
        )

        for line in order.lines.all():
            qty_str  = request.POST.get(f'qty_{line.pk}', str(line.quantity))
            lot_num  = request.POST.get(f'lot_{line.pk}', '').strip()
            exp      = request.POST.get(f'expiry_{line.pk}') or None
            note     = request.POST.get(f'note_{line.pk}', '').strip()

            try:
                qty = Decimal(qty_str) if qty_str else Decimal('0')
            except InvalidOperation:
                qty = Decimal('0')

            # ── Note manque ──
            if qty < line.quantity or note:
                StockShortage.objects.create(
                    order             = order,
                    material_name     = line.material.name,
                    expected_quantity = line.quantity,
                    received_quantity = qty,
                    note              = note,
                    created_by        = request.user,
                )

            if qty <= 0:
                continue

            if not lot_num:
                lot_num = f"AUTO-{order.order_number}-{line.pk}"

            lot = Lot.objects.create(
                material         = line.material,
                lot_number       = lot_num,
                supplier         = order.supplier.name,
                initial_quantity = qty,
                current_quantity = qty,
                expiry_date      = exp,
                unit_cost        = line.unit_price,
                created_by       = request.user,
            )
            StockMovement.objects.create(
                lot           = lot,
                movement_type = 'reception',
                quantity      = qty,
                reference     = f"BC-{order.order_number}",
                performed_by  = request.user,
            )
            GoodsReceiptLine.objects.create(
                receipt     = receipt,
                order_line  = line,
                lot_number  = lot_num,
                quantity    = qty,
                expiry_date = exp,
                unit_cost   = line.unit_price,
                created_lot = lot,
            )
            line.received_quantity += qty
            line.save()

        all_rcvd = all(l.received_quantity >= l.quantity for l in order.lines.all())
        order.status = 'received' if all_rcvd else 'partially_received'
        order.save()
        messages.success(request, "Stock mis à jour !")
        return redirect('purchase:order_detail', pk=pk)

    return render(request, 'purchase/quick_receive.html', {'order': order})


@login_required
def resolve_shortage(request, pk):
    """Marquer un manque comme résolu."""
    from .models import StockShortage
    from django.utils import timezone
    shortage = get_object_or_404(StockShortage, pk=pk)
    shortage.is_resolved = True
    shortage.resolved_at = timezone.now()
    shortage.save()
    messages.success(request, f"Manque '{shortage.material_name}' marqué comme résolu.")
    return redirect('purchase:order_detail', pk=shortage.order.pk)