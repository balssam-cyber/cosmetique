from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from .models import RndRole, Ingredient, Product, Formulation, FormulationIngredient, StabilityTest, IngredientCompatibility


def get_user_role(user):
    try:
        return user.rnd_role.role
    except Exception:
        return 'viewer'


def can_edit(user):
    return get_user_role(user) in ['scientist', 'lab_manager'] or user.is_staff


@login_required
def ingredient_list(request):
    q = request.GET.get('q', '')
    cat = request.GET.get('cat', '')
    ingredients = Ingredient.objects.all()
    if q:
        ingredients = ingredients.filter(Q(name__icontains=q) | Q(inci_name__icontains=q) | Q(cas_number__icontains=q))
    if cat:
        ingredients = ingredients.filter(category=cat)
    return render(request, 'rnd/ingredient_list.html', {
        'ingredients': ingredients, 'q': q, 'cat': cat,
        'category_choices': Ingredient.CATEGORY_CHOICES,
        'can_edit': can_edit(request.user)
    })


@login_required
def ingredient_detail(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    used_in = ingredient.formulationingredient_set.select_related('formulation__product').all()
    return render(request, 'rnd/ingredient_detail.html', {
        'ingredient': ingredient, 'used_in': used_in,
        'can_edit': can_edit(request.user)
    })


@login_required
def ingredient_form(request, pk=None):
    if not can_edit(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('rnd:ingredient_list')
    ingredient = get_object_or_404(Ingredient, pk=pk) if pk else None
    if request.method == 'POST':
        data = request.POST
        fields = {
            'name': data.get('name', ''),
            'inci_name': data.get('inci_name', ''),
            'cas_number': data.get('cas_number', ''),
            'category': data.get('category', 'other'),
            'origin': data.get('origin', ''),
            'aspect': data.get('aspect', ''),
            'certification': data.get('certification', ''),
            'description': data.get('description', ''),
            'applications': data.get('applications', ''),
            'usage_mode': data.get('usage_mode', ''),
            'dosage_min': data.get('dosage_min') or None,
            'dosage_max': data.get('dosage_max') or None,
            'addition_phase': data.get('addition_phase', ''),
            'solubility': data.get('solubility', ''),
            'storage': data.get('storage', ''),
            'max_concentration': data.get('max_concentration') or None,
            'is_restricted': 'is_restricted' in data,
            'notes': data.get('notes', ''),
        }
        if ingredient:
            for k, v in fields.items():
                setattr(ingredient, k, v)
            ingredient.save()
            messages.success(request, "Ingrédient modifié.")
        else:
            ingredient = Ingredient.objects.create(**fields)
            messages.success(request, "Ingrédient créé.")
        return redirect('rnd:ingredient_detail', pk=ingredient.pk)
    return render(request, 'rnd/ingredient_form.html', {
        'ingredient': ingredient,
        'category_choices': Ingredient.CATEGORY_CHOICES,
    })


@login_required
def product_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    products = Product.objects.all()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(reference__icontains=q))
    if status:
        products = products.filter(status=status)
    return render(request, 'rnd/product_list.html', {
        'products': products, 'q': q, 'status': status,
        'status_choices': Product.STATUS_CHOICES,
        'can_edit': can_edit(request.user)
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    formulations = product.formulations.all()
    compliance = getattr(product, 'compliance', None)
    return render(request, 'rnd/product_detail.html', {
        'product': product, 'formulations': formulations,
        'compliance': compliance, 'can_edit': can_edit(request.user)
    })


@login_required
def product_form(request, pk=None):
    if not can_edit(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('rnd:product_list')
    product = get_object_or_404(Product, pk=pk) if pk else None
    if request.method == 'POST':
        data = request.POST
        fields = {
            'name': data['name'],
            'reference': data['reference'],
            'category': data['category'],
            'description': data.get('description', ''),
            'status': data['status'],
        }
        if product:
            for k, v in fields.items():
                setattr(product, k, v)
            product.save()
            messages.success(request, "Produit modifié.")
        else:
            product = Product.objects.create(**fields, created_by=request.user)
            messages.success(request, "Produit créé.")
        return redirect('rnd:product_detail', pk=product.pk)
    return render(request, 'rnd/product_form.html', {
        'product': product,
        'category_choices': Product.CATEGORY_CHOICES,
        'status_choices': Product.STATUS_CHOICES,
    })


@login_required
def formulation_detail(request, pk):
    formulation = get_object_or_404(Formulation, pk=pk)
    ingredients = formulation.formulation_ingredients.select_related('ingredient').all()
    stability_tests = formulation.stability_tests.all()
    total_pct = sum(fi.percentage for fi in ingredients)

    for fi in ingredients:
        fi.qty_kg = (fi.percentage / Decimal('100')) * formulation.batch_size

    return render(request, 'rnd/formulation_detail.html', {
        'formulation': formulation,
        'ingredients': ingredients,
        'stability_tests': stability_tests,
        'total_pct': total_pct,
        'can_edit': can_edit(request.user)
    })


@login_required
def formulation_form(request, product_pk=None, pk=None):
    if not can_edit(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('rnd:product_list')
    formulation = get_object_or_404(Formulation, pk=pk) if pk else None
    product = get_object_or_404(Product, pk=product_pk) if product_pk else (
        formulation.product if formulation else None
    )
    if request.method == 'POST':
        data = request.POST
        fields = {
            'version': data['version'],
            'status': data.get('status', 'draft'),
            'batch_size': data['batch_size'],
            'ph_min': data.get('ph_min') or None,
            'ph_max': data.get('ph_max') or None,
            'viscosity': data.get('viscosity', ''),
            'appearance': data.get('appearance', ''),
            'notes': data.get('notes', ''),
        }
        if formulation:
            for k, v in fields.items():
                setattr(formulation, k, v)
            formulation.save()
            messages.success(request, "Formulation modifiée.")
        else:
            formulation = Formulation.objects.create(
                product=product, created_by=request.user, **fields
            )
            messages.success(request, "Formulation créée. Ajoutez les ingrédients.")
        return redirect('rnd:formulation_detail', pk=formulation.pk)
    return render(request, 'rnd/formulation_form.html', {
        'formulation': formulation, 'product': product,
        'status_choices': Formulation.STATUS_CHOICES,
    })


@login_required
def formulation_ingredient_add(request, formulation_pk):
    if not can_edit(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('rnd:formulation_detail', pk=formulation_pk)
    formulation = get_object_or_404(Formulation, pk=formulation_pk)
    all_ingredients = Ingredient.objects.all().order_by('name')

    if request.method == 'POST':
        data = request.POST
        ingredient_id = data.get('ingredient')
        percentage = data.get('percentage')

        if not ingredient_id or not percentage:
            messages.error(request, "Ingrédient et pourcentage sont obligatoires.")
        else:
            try:
                from django.db.models import Q as DQ
                ingredient = Ingredient.objects.get(pk=ingredient_id)
                pct = Decimal(percentage)

                # ── Check max_concentration ──
                if ingredient.max_concentration and pct > ingredient.max_concentration:
                    messages.error(request,
                        f"⚠ Concentration trop élevée — {ingredient.name} : "
                        f"max autorisé {ingredient.max_concentration}% "
                        f"(vous avez saisi {pct}%)"
                    )
                # ── Check déjà dans la formulation ──
                elif FormulationIngredient.objects.filter(
                    formulation=formulation, ingredient_id=ingredient_id
                ).exists():
                    messages.error(request, "Cet ingrédient est déjà dans la formulation.")
                else:
                    # ── Check incompatibilité ──
                    existing_ingredients = [
                        fi.ingredient for fi in formulation.formulation_ingredients.select_related('ingredient').all()
                    ]
                    incompatible = []
                    caution = []

                    for existing in existing_ingredients:
                        compat = IngredientCompatibility.objects.filter(
                            DQ(ingredient_a=ingredient, ingredient_b=existing) |
                            DQ(ingredient_a=existing, ingredient_b=ingredient)
                        ).first()
                        if compat:
                            if compat.status == 'incompatible':
                                note = f" — {compat.notes}" if compat.notes else ""
                                incompatible.append(f"{existing.name}{note}")
                            elif compat.status == 'caution':
                                note = f" — {compat.notes}" if compat.notes else ""
                                caution.append(f"{existing.name}{note}")

                    if incompatible:
                        messages.error(request,
                            f"❌ Incompatible avec : {', '.join(incompatible)}"
                        )
                    else:
                        fi = FormulationIngredient.objects.create(
                            formulation=formulation,
                            ingredient_id=ingredient_id,
                            percentage=pct,
                            phase=data.get('phase', 'A'),
                            function=data.get('function', ''),
                            order=formulation.formulation_ingredients.count() + 1
                        )
                        if caution:
                            messages.warning(request,
                                f"⚠ {fi.ingredient.name} ajouté avec précaution : {', '.join(caution)}"
                            )
                        else:
                            messages.success(request,
                                f"✅ Ingrédient «{fi.ingredient.name}» ({percentage}%) ajouté."
                            )
                        return redirect('rnd:formulation_detail', pk=formulation_pk)

            except Ingredient.DoesNotExist:
                messages.error(request, "Ingrédient introuvable.")
            except Exception as e:
                messages.error(request, f"Erreur : {e}")

    existing_ids = formulation.formulation_ingredients.values_list('ingredient_id', flat=True)
    available = all_ingredients.exclude(id__in=existing_ids)
    current_total = sum(fi.percentage for fi in formulation.formulation_ingredients.all())

    # ── Compatibilité pour affichage dans le template ──
    from django.db.models import Q as DQ
    existing_ingredient_ids = list(existing_ids)
    compatibility_map = {}
    if existing_ingredient_ids:
        for ing in available:
            compat = IngredientCompatibility.objects.filter(
                DQ(ingredient_a=ing, ingredient_b__in=existing_ingredient_ids) |
                DQ(ingredient_b=ing, ingredient_a__in=existing_ingredient_ids)
            ).values_list('status', flat=True)
            statuses = list(compat)
            if 'incompatible' in statuses:
                compatibility_map[ing.pk] = 'incompatible'
            elif 'caution' in statuses:
                compatibility_map[ing.pk] = 'caution'
            else:
                compatibility_map[ing.pk] = 'compatible'

    return render(request, 'rnd/formulation_ingredient_form.html', {
        'formulation': formulation,
        'available_ingredients': available,
        'current_total': current_total,
        'remaining_pct': Decimal('100') - current_total,
        'phase_choices': FormulationIngredient.PHASE_CHOICES,
        'compatibility_map': compatibility_map,
    })

@login_required
def formulation_ingredient_delete(request, pk):
    fi = get_object_or_404(FormulationIngredient, pk=pk)
    if not can_edit(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('rnd:formulation_detail', pk=fi.formulation.pk)
    formulation_pk = fi.formulation.pk
    name = fi.ingredient.name
    fi.delete()
    messages.success(request, f"Ingrédient «{name}» supprimé.")
    return redirect('rnd:formulation_detail', pk=formulation_pk)


@login_required
def stability_test_list(request):
    tests = StabilityTest.objects.select_related('formulation__product').all()
    return render(request, 'rnd/stability_test_list.html', {
        'tests': tests, 'can_edit': can_edit(request.user)
    })


@login_required
def stability_test_add(request, formulation_pk):
    formulation = get_object_or_404(Formulation, pk=formulation_pk)
    if request.method == 'POST':
        data = request.POST
        StabilityTest.objects.create(
            formulation=formulation,
            condition=data['condition'],
            duration_weeks=data['duration_weeks'],
            start_date=data['start_date'],
            end_date=data.get('end_date') or None,
            result=data.get('result', 'pending'),
            ph_initial=data.get('ph_initial') or None,
            ph_final=data.get('ph_final') or None,
            appearance_ok='appearance_ok' in data,
            odor_ok='odor_ok' in data,
            observations=data.get('observations', ''),
            performed_by=request.user
        )
        messages.success(request, "Test de stabilité ajouté.")
        return redirect('rnd:formulation_detail', pk=formulation_pk)
    return render(request, 'rnd/stability_test_form.html', {
        'formulation': formulation,
        'condition_choices': StabilityTest.CONDITION_CHOICES,
        'result_choices': StabilityTest.RESULT_CHOICES,
    })


@login_required
def formulation_simulate(request, pk):
    formulation = get_object_or_404(Formulation, pk=pk)
    
    # Handle cost parameter updates via POST
    if request.method == 'POST':
        try:
            formulation.packaging_cost = Decimal(request.POST.get('packaging_cost', formulation.packaging_cost))
            formulation.labor_cost = Decimal(request.POST.get('labor_cost', formulation.labor_cost))
            formulation.target_margin = Decimal(request.POST.get('target_margin', formulation.target_margin))
            formulation.save()
            messages.success(request, "Paramètres de coût mis à jour.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour des paramètres : {e}")

    ingredients = formulation.formulation_ingredients.select_related('ingredient').all()
    
    # ── 1. Check Total Percentage ──
    total_pct = sum(fi.percentage for fi in ingredients)
    total_ok = (total_pct == Decimal('100'))

    # ── 2. Category Breakdown & Missing Checks ──
    categories = {}
    for fi in ingredients:
        cat = fi.ingredient.get_category_display()
        categories[cat] = categories.get(cat, Decimal('0')) + fi.percentage

    has_preservative = any(fi.ingredient.category == 'preservative' for fi in ingredients)
    has_water = any('eau' in fi.ingredient.name.lower() or 'water' in fi.ingredient.name.lower() or 'aqua' in fi.ingredient.name.lower() for fi in ingredients)

    # ── 3. Regulatory & Max Concentration Check ──
    concentration_alerts = []
    for fi in ingredients:
        if fi.ingredient.max_concentration and fi.percentage > fi.ingredient.max_concentration:
            concentration_alerts.append({
                'ingredient': fi.ingredient.name,
                'actual': fi.percentage,
                'max': fi.ingredient.max_concentration
            })

    # ── 4. Compatibility Check ──
    from django.db.models import Q as DQ
    compatibility_alerts = []
    ingredient_list = [fi.ingredient for fi in ingredients]
    for i in range(len(ingredient_list)):
        for j in range(i + 1, len(ingredient_list)):
            ing_a = ingredient_list[i]
            ing_b = ingredient_list[j]
            compat = IngredientCompatibility.objects.filter(
                (DQ(ingredient_a=ing_a, ingredient_b=ing_b) | DQ(ingredient_a=ing_b, ingredient_b=ing_a)) &
                DQ(status__in=['incompatible', 'caution'])
            ).first()
            if compat:
                compatibility_alerts.append({
                    'pair': f"{ing_a.name} ↔ {ing_b.name}",
                    'status': compat.get_status_display(),
                    'is_danger': compat.status == 'incompatible',
                    'notes': compat.notes
                })

    # ── 5. AI/Smart Advice Generation ──
    advice = []
    if not total_ok:
        advice.append({'type': 'danger', 'msg': f"Le total de la formule est de {total_pct}%. Il doit être exactement de 100%."})
    if has_water and not has_preservative:
        advice.append({'type': 'warning', 'msg': "La formule contient de l'eau mais aucun conservateur détecté. Risque élevé de prolifération bactérienne."})
    
    active_pct = categories.get('Actif', Decimal('0'))
    if active_pct == 0:
        advice.append({'type': 'info', 'msg': "Aucun actif cosmétique détecté. S'agit-il d'une base simple ?"})
    elif active_pct < Decimal('0.5'):
        advice.append({'type': 'warning', 'msg': f"La concentration totale en actifs ({active_pct}%) semble faible pour revendiquer une efficacité."})
    
    if not concentration_alerts and not compatibility_alerts and total_ok:
        advice.append({'type': 'success', 'msg': "La formule semble parfaitement équilibrée, sûre et conforme aux limites enregistrées."})

    # ── 6. Cost Calculation (Linked with Stock) ──
    from apps.stock.models import Material, Lot
    formula_cost_per_kg = Decimal('0')
    cost_details = []

    for fi in ingredients:
        # Try to find corresponding Material in Stock (via Direct FK or exact name match)
        material = Material.objects.filter(DQ(ingredient=fi.ingredient) | DQ(name__iexact=fi.ingredient.name)).first()
        unit_cost = Decimal('0')
        has_cost_data = False

        if material:
            # Get latest lot cost
            latest_lot = material.lots.order_by('-reception_date', '-created_at').first()
            if latest_lot and latest_lot.unit_cost > 0:
                unit_cost = latest_lot.unit_cost
                has_cost_data = True
        
        # Contribution per kg (percentage / 100 * cost per kg)
        # Assuming unit_cost is per KG (default for materials).
        cost_contribution = (fi.percentage / Decimal('100')) * unit_cost
        formula_cost_per_kg += cost_contribution

        cost_details.append({
            'ingredient': fi.ingredient.name,
            'percentage': fi.percentage,
            'unit_cost': unit_cost,
            'cost_contribution': cost_contribution,
            'has_cost_data': has_cost_data
        })

    # ── 7. Pricing Simulator ──
    # Default assumptions (unit = 100g / 0.1kg usually for cosmetics, we'll parameterize it if possible, defaulting to 1kg here or letting user scale)
    product_cost_1kg = formula_cost_per_kg + formulation.packaging_cost + formulation.labor_cost
    
    # Selling price calculation: Cost / (1 - target_margin) or simply Cost + (Cost * margin)
    # Usually margin represents Gross Margin %: Price = Cost / (1 - Margin/100)
    margin_ratio = formulation.target_margin / Decimal('100')
    if margin_ratio < 1:
        suggested_retail_price = product_cost_1kg / (Decimal('1') - margin_ratio)
    else:
        suggested_retail_price = product_cost_1kg * Decimal('2') # Fallback if margin >= 100% incorrectly entered

    return render(request, 'rnd/formulation_simulate.html', {
        'formulation': formulation,
        'total_pct': total_pct,
        'total_ok': total_ok,
        'categories': categories,
        'concentration_alerts': concentration_alerts,
        'compatibility_alerts': compatibility_alerts,
        'advice': advice,
        'formula_cost_per_kg': formula_cost_per_kg,
        'cost_details': cost_details,
        'product_cost_1kg': product_cost_1kg,
        'suggested_retail_price': suggested_retail_price,
        'potential_profit': suggested_retail_price - product_cost_1kg,
    })