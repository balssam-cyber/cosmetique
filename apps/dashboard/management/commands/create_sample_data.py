"""
Management command to populate CosmoERP with sample data.
Run: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Creates sample data for all ERP apps'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # --- Users ---
        users_data = [
            ('scientist1', 'cosmo2024', 'Ahmed', 'Benali', 'scientist@cosmo.tn'),
            ('lab_manager1', 'cosmo2024', 'Sonia', 'Mansour', 'lab@cosmo.tn'),
            ('operator1', 'cosmo2024', 'Mohamed', 'Trabelsi', 'operator@cosmo.tn'),
            ('warehouse1', 'cosmo2024', 'Rania', 'Chahed', 'warehouse@cosmo.tn'),
            ('purchase1', 'cosmo2024', 'Farouk', 'Saad', 'purchase@cosmo.tn'),
            ('regulatory1', 'cosmo2024', 'Leila', 'Bouaziz', 'regulatory@cosmo.tn'),
            ('ceo1', 'cosmo2024', 'Karim', 'Belhaj', 'ceo@cosmo.tn'),
            ('qc1', 'cosmo2024', 'Amira', 'Khelifi', 'qc@cosmo.tn'),
        ]
        users = {}
        for username, password, first, last, email in users_data:
            u, created = User.objects.get_or_create(username=username)
            u.set_password(password)
            u.first_name = first
            u.last_name = last
            u.email = email
            u.save()
            users[username] = u
            if created:
                self.stdout.write(f'  Created user: {username}')

        # --- RnD Roles ---
        from apps.rnd.models import RndRole
        roles_rnd = [
            ('scientist1', 'scientist'),
            ('lab_manager1', 'lab_manager'),
            ('regulatory1', 'regulatory'),
            ('ceo1', 'viewer'),
        ]
        for username, role in roles_rnd:
            RndRole.objects.update_or_create(user=users[username], defaults={'role': role})

        # --- Production Roles ---
        from apps.production.models import ProductionRole
        roles_prod = [
            ('lab_manager1', 'lab_manager'),
            ('operator1', 'operator'),
            ('qc1', 'qc_technician'),
        ]
        for username, role in roles_prod:
            ProductionRole.objects.update_or_create(user=users[username], defaults={'role': role})

        # --- Stock Roles ---
        from apps.stock.models import StockRole
        roles_stock = [
            ('warehouse1', 'warehouse_manager'),
            ('purchase1', 'purchase_officer'),
            ('lab_manager1', 'production_manager'),
        ]
        for username, role in roles_stock:
            StockRole.objects.update_or_create(user=users[username], defaults={'role': role})

        # --- Dashboard Roles ---
        from apps.dashboard.models import DashboardRole
        DashboardRole.objects.update_or_create(user=users['ceo1'], defaults={'role': 'ceo'})
        DashboardRole.objects.update_or_create(user=users['lab_manager1'], defaults={'role': 'lab_manager'})
        DashboardRole.objects.update_or_create(user=users['warehouse1'], defaults={'role': 'warehouse_manager'})

        # --- Material Categories ---
        from apps.stock.models import MaterialCategory, Material, Lot, StockMovement
        cats = {}
        for name in ['Actifs', 'Emollients', 'Emulsifiants', 'Conservateurs', 'Emballage primaire', 'Emballage secondaire']:
            c, _ = MaterialCategory.objects.get_or_create(name=name)
            cats[name] = c

        # --- Ingredients ---
        from apps.rnd.models import Ingredient
        ingredients_data = [
            ('Acide hyaluronique', 'Sodium Hyaluronate', '9067-32-7', 'active', 'BioActive Lab', 2.0),
            ('Glycerine', 'Glycerin', '56-81-5', 'solvent', 'ChemPlus', 10.0),
            ('Cetearyl Alcohol', 'Cetearyl Alcohol', '67762-27-0', 'emulsifier', 'Oleochem TN', 5.0),
            ('Phenoxyethanol', 'Phenoxyethanol', '122-99-6', 'preservative', 'PreservCo', 1.0),
            ('Niacinamide', 'Niacinamide', '98-92-0', 'active', 'VitaActif', 10.0),
            ('Aloe Vera', 'Aloe Barbadensis Leaf Juice', '85507-69-3', 'active', 'Natura TN', 15.0),
            ('Eau purifiee', 'Aqua', None, 'solvent', 'AquaPure', 100.0),
        ]
        ingredients = {}
        for name, inci, cas, cat, supplier, max_conc in ingredients_data:
            ing, _ = Ingredient.objects.get_or_create(name=name, defaults={
                'inci_name': inci, 'cas_number': cas or '', 'category': cat,
                'supplier': supplier, 'max_concentration': max_conc
            })
            ingredients[name] = ing

        # --- Materials (Stock) ---
        materials_data = [
            ('MP001', 'Acide hyaluronique', 'raw_material', 'kg', 2.0, 5.0, 'Actifs'),
            ('MP002', 'Glycerine', 'raw_material', 'kg', 10.0, 20.0, 'Emollients'),
            ('MP003', 'Cetearyl Alcohol', 'raw_material', 'kg', 5.0, 15.0, 'Emulsifiants'),
            ('MP004', 'Phenoxyethanol', 'raw_material', 'kg', 2.0, 5.0, 'Conservateurs'),
            ('MP005', 'Niacinamide', 'raw_material', 'kg', 1.0, 3.0, 'Actifs'),
            ('MP006', 'Aloe Vera', 'raw_material', 'kg', 5.0, 10.0, 'Actifs'),
            ('MP007', 'Eau purifiee', 'raw_material', 'L', 20.0, 50.0, 'Actifs'),
            ('PF001', 'Creme Hydratante - Flacon 50ml', 'finished_product', 'pcs', 50, 100, None),
            ('PF002', 'Serum Eclat - Flacon 30ml', 'finished_product', 'pcs', 30, 80, None),
            ('EM001', 'Flacon pompe 50ml', 'packaging', 'pcs', 100, 200, 'Emballage primaire'),
            ('EM002', 'Etui carton 50ml', 'packaging', 'pcs', 100, 200, 'Emballage secondaire'),
        ]
        materials = {}
        for code, name, mtype, unit, min_stock, reorder, cat_name in materials_data:
            mat, _ = Material.objects.get_or_create(code=code, defaults={
                'name': name, 'material_type': mtype, 'unit': unit,
                'minimum_stock': min_stock, 'reorder_quantity': reorder,
                'category': cats.get(cat_name)
            })
            materials[code] = mat

        # --- Lots ---
        lots_data = [
            ('MP001', 'LOT-AH-2024-01', 'BioActive Lab', 5.0, date(2025, 12, 31), 120.0),
            ('MP002', 'LOT-GL-2024-01', 'ChemPlus', 25.0, date(2026, 6, 30), 3.5),
            ('MP003', 'LOT-CA-2024-01', 'Oleochem TN', 20.0, date(2026, 3, 31), 8.0),
            ('MP004', 'LOT-PH-2024-01', 'PreservCo', 3.0, date(2025, 9, 30), 45.0),
            ('MP005', 'LOT-NIA-2024-01', 'VitaActif', 8.0, date(2026, 1, 31), 80.0),
            ('MP006', 'LOT-AV-2024-01', 'Natura TN', 15.0, date(2025, 8, 31), 12.0),
            ('MP007', 'LOT-EAU-2024-01', 'AquaPure', 100.0, None, 0.5),
            ('EM001', 'LOT-FL-2024-01', 'PackPro', 500.0, None, 0.15),
            ('EM002', 'LOT-ET-2024-01', 'PackPro', 500.0, None, 0.08),
        ]
        lots = {}
        for code, lot_num, supplier, qty, expiry, cost in lots_data:
            lot, _ = Lot.objects.get_or_create(lot_number=lot_num, defaults={
                'material': materials[code], 'supplier': supplier,
                'initial_quantity': qty, 'current_quantity': qty,
                'expiry_date': expiry, 'unit_cost': cost,
                'created_by': users['warehouse1']
            })
            lots[lot_num] = lot

        # --- Products ---
        from apps.rnd.models import Product, Formulation, FormulationIngredient
        products_data = [
            ('PROD001', 'Creme Hydratante Intensive', 'skincare', 'approved'),
            ('PROD002', 'Serum Eclat Niacinamide 10%', 'skincare', 'approved'),
            ('PROD003', 'Huile Corps Aloe Vera', 'bodycare', 'testing'),
            ('PROD004', 'Creme Solaire SPF50', 'suncare', 'development'),
        ]
        rnd_products = {}
        for ref, name, cat, status in products_data:
            prod, _ = Product.objects.get_or_create(reference=ref, defaults={
                'name': name, 'category': cat, 'status': status,
                'created_by': users['scientist1']
            })
            rnd_products[ref] = prod

        # --- Formulations ---
        form1, _ = Formulation.objects.get_or_create(product=rnd_products['PROD001'], version='1.0', defaults={
            'status': 'approved', 'batch_size': 50.0, 'ph_min': 5.5, 'ph_max': 6.5,
            'appearance': 'Creme blanche onctueuse',
            'created_by': users['scientist1'], 'approved_by': users['lab_manager1']
        })
        form2, _ = Formulation.objects.get_or_create(product=rnd_products['PROD002'], version='1.0', defaults={
            'status': 'approved', 'batch_size': 30.0, 'ph_min': 5.0, 'ph_max': 6.0,
            'appearance': 'Serum transparent leger',
            'created_by': users['scientist1'], 'approved_by': users['lab_manager1']
        })

        # Formulation ingredients
        fi_data = [
            (form1, 'Eau purifiee', 'A', 70.0, 'Solvant'),
            (form1, 'Glycerine', 'A', 5.0, 'Humectant'),
            (form1, 'Cetearyl Alcohol', 'B', 5.0, 'Emulsifiant'),
            (form1, 'Acide hyaluronique', 'C', 0.5, 'Actif hydratant'),
            (form1, 'Phenoxyethanol', 'C', 0.9, 'Conservateur'),
            (form2, 'Eau purifiee', 'A', 80.0, 'Solvant'),
            (form2, 'Glycerine', 'A', 5.0, 'Humectant'),
            (form2, 'Niacinamide', 'B', 10.0, 'Actif eclaircissant'),
            (form2, 'Phenoxyethanol', 'C', 0.9, 'Conservateur'),
        ]
        for i, (form, ing_name, phase, pct, func) in enumerate(fi_data):
            FormulationIngredient.objects.get_or_create(
                formulation=form, ingredient=ingredients[ing_name],
                defaults={'phase': phase, 'percentage': pct, 'function': func, 'order': i}
            )

        # --- Production Batches ---
        from apps.production.models import ProductionBatch, BatchRawMaterial, QCCheck
        batch1, _ = ProductionBatch.objects.get_or_create(batch_number='LOT-2024-001', defaults={
            'formulation': form1, 'planned_quantity': 50.0, 'actual_quantity': 48.5,
            'production_date': date(2024, 10, 15), 'status': 'completed',
            'responsible': users['lab_manager1'], 'operator': users['operator1']
        })
        batch2, _ = ProductionBatch.objects.get_or_create(batch_number='LOT-2024-002', defaults={
            'formulation': form2, 'planned_quantity': 30.0,
            'production_date': date(2024, 11, 1), 'status': 'in_progress',
            'responsible': users['lab_manager1'], 'operator': users['operator1']
        })
        batch3, _ = ProductionBatch.objects.get_or_create(batch_number='LOT-2024-003', defaults={
            'formulation': form1, 'planned_quantity': 100.0,
            'production_date': date(2024, 11, 20), 'status': 'planned',
            'responsible': users['lab_manager1']
        })

        # QC Checks
        QCCheck.objects.get_or_create(batch=batch1, test_name='pH', defaults={
            'specification': '5.5 - 6.5', 'measured_value': '5.9', 'result': 'pass',
            'performed_by': users['qc1'], 'performed_at': timezone.now()
        })
        QCCheck.objects.get_or_create(batch=batch1, test_name='Aspect', defaults={
            'specification': 'Blanc, onctueux, homogene', 'measured_value': 'Conforme', 'result': 'pass',
            'performed_by': users['qc1'], 'performed_at': timezone.now()
        })
        QCCheck.objects.get_or_create(batch=batch1, test_name='Viscosité', defaults={
            'specification': '20000 - 40000 cPs', 'measured_value': '28500 cPs', 'result': 'pass',
            'performed_by': users['qc1'], 'performed_at': timezone.now()
        })

        # Finished product lot
        fp_lot, _ = Lot.objects.get_or_create(lot_number='LOT-2024-001', material=materials['PF001'], defaults={
            'initial_quantity': 480, 'current_quantity': 350,
            'created_by': users['operator1'], 'unit_cost': 3.5
        })
        if not batch1.finished_lot:
            batch1.finished_lot = fp_lot
            batch1.save()

        # --- Suppliers ---
        from apps.purchase.models import Supplier, PurchaseOrder, PurchaseOrderLine
        suppliers_data = [
            ('FOURN001', 'BioActive Lab', 'Dr. Hassan Slim', 'hslim@bioactive.tn', '+216 71 234 567', 'Tunisie'),
            ('FOURN002', 'ChemPlus International', 'Marie Dupont', 'mdupont@chemplus.fr', '+33 1 234 567', 'France'),
            ('FOURN003', 'PackPro Tunisia', 'Ali Rezgui', 'arezgui@packpro.tn', '+216 73 456 789', 'Tunisie'),
        ]
        suppliers = {}
        for code, name, contact, email, phone, country in suppliers_data:
            sup, _ = Supplier.objects.get_or_create(code=code, defaults={
                'name': name, 'contact_name': contact, 'email': email, 'phone': phone, 'country': country
            })
            suppliers[code] = sup

        # Purchase Order
        po1, _ = PurchaseOrder.objects.get_or_create(order_number='2024-001', defaults={
            'supplier': suppliers['FOURN001'], 'status': 'received',
            'order_date': date(2024, 9, 1), 'expected_delivery': date(2024, 9, 15),
            'actual_delivery': date(2024, 9, 14), 'created_by': users['purchase1']
        })
        PurchaseOrderLine.objects.get_or_create(order=po1, material=materials['MP001'], defaults={
            'quantity': 5.0, 'unit_price': 120.0, 'received_quantity': 5.0
        })
        po2, _ = PurchaseOrder.objects.get_or_create(order_number='2024-002', defaults={
            'supplier': suppliers['FOURN002'], 'status': 'confirmed',
            'order_date': date(2024, 11, 5), 'expected_delivery': date(2024, 11, 25),
            'created_by': users['purchase1']
        })
        PurchaseOrderLine.objects.get_or_create(order=po2, material=materials['MP002'], defaults={
            'quantity': 25.0, 'unit_price': 3.5, 'received_quantity': 0
        })
        PurchaseOrderLine.objects.get_or_create(order=po2, material=materials['MP004'], defaults={
            'quantity': 5.0, 'unit_price': 45.0, 'received_quantity': 0
        })

        # --- Customers ---
        from apps.sales.models import Customer, SalesOrder, SalesOrderLine
        customers_data = [
            ('CLT001', 'Pharmacie Al Amal', 'Mme Zahra Ben Salem', 'zahra@alamal.tn', 'Tunisie'),
            ('CLT002', 'Parapharmacie Centrale Tunis', 'M. Rachid Farhat', 'rfarhat@pct.tn', 'Tunisie'),
            ('CLT003', 'BeautyShop Export SARL', 'Sophie Martin', 'smartin@beautyshop.fr', 'France'),
        ]
        customers = {}
        for code, name, contact, email, country in customers_data:
            cust, _ = Customer.objects.get_or_create(code=code, defaults={
                'name': name, 'contact_name': contact, 'email': email, 'country': country
            })
            customers[code] = cust

        # Sales Orders
        so1, _ = SalesOrder.objects.get_or_create(order_number='2024-001', defaults={
            'customer': customers['CLT001'], 'status': 'shipped',
            'order_date': date(2024, 10, 20), 'delivery_date': date(2024, 10, 28),
            'created_by': users['lab_manager1']
        })
        SalesOrderLine.objects.get_or_create(order=so1, material=materials['PF001'], defaults={
            'quantity': 100, 'unit_price': 8.5, 'shipped_quantity': 100, 'lot': fp_lot
        })
        so2, _ = SalesOrder.objects.get_or_create(order_number='2024-002', defaults={
            'customer': customers['CLT003'], 'status': 'confirmed',
            'order_date': date(2024, 11, 10), 'delivery_date': date(2024, 11, 30),
            'created_by': users['lab_manager1']
        })
        SalesOrderLine.objects.get_or_create(order=so2, material=materials['PF001'], defaults={
            'quantity': 200, 'unit_price': 7.5, 'shipped_quantity': 0
        })

        # --- Regulatory ---
        from apps.regulatory.models import ProductCompliance, SafetyReport, CPNPNotification

        ProductCompliance.objects.get_or_create(product=rnd_products['PROD001'], defaults={
            'status': 'compliant', 'eu_regulation': True,
            'responsible_person': 'Sonia Mansour', 'last_review_date': date(2024, 1, 15),
            'next_review_date': date(2025, 1, 15), 'updated_by': users['regulatory1']
        })
        ProductCompliance.objects.get_or_create(product=rnd_products['PROD002'], defaults={
            'status': 'in_review', 'eu_regulation': False,
            'responsible_person': 'Sonia Mansour', 'updated_by': users['regulatory1']
        })

        SafetyReport.objects.get_or_create(report_number='RSP-2024-001', defaults={
            'product': rnd_products['PROD001'], 'formulation': form1,
            'status': 'approved', 'safety_assessor': 'Dr. Amira Khelifi',
            'issue_date': date(2024, 2, 1), 'expiry_date': date(2025, 2, 1),
            'conclusion': 'Le produit est juge sur sans risque pour la sante dans des conditions normales ou raisonnablement previsibles d utilisation.',
            'created_by': users['regulatory1']
        })

        CPNPNotification.objects.get_or_create(notification_number='CPNP-2024-TN-001', defaults={
            'product': rnd_products['PROD001'], 'status': 'accepted',
            'submission_date': date(2024, 3, 1), 'acceptance_date': date(2024, 3, 15),
            'market': 'UE', 'created_by': users['regulatory1']
        })

        # Link Stock Materials to R&D Ingredients
        ingredient_material_links = [
            ('Acide hyaluronique', 'MP001'),
            ('Glycerine', 'MP002'),
            ('Cetearyl Alcohol', 'MP003'),
            ('Phenoxyethanol', 'MP004'),
            ('Niacinamide', 'MP005'),
            ('Aloe Vera', 'MP006'),
            ('Eau purifiee', 'MP007'),
        ]
        for ing_name, mat_code in ingredient_material_links:
            try:
                ing = Ingredient.objects.get(name=ing_name)
                mat = Material.objects.get(code=mat_code)
                if not mat.ingredient:
                    mat.ingredient = ing
                    mat.save()
                    self.stdout.write(f'  Linked: {ing_name} → {mat_code}')
            except (Ingredient.DoesNotExist, Material.DoesNotExist):
                pass

        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write('\nUsers created (password: cosmo2024):')
        self.stdout.write('  scientist1, lab_manager1, operator1, warehouse1, purchase1, regulatory1, qc1, ceo1')
        self.stdout.write('\nAccess admin at: http://127.0.0.1:8000/admin/')
        self.stdout.write('Create superuser: python manage.py createsuperuser')
