"""
Management command to populate CosmoERP with rich, realistic sample data.
Run: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Creates highly realistic and voluminous sample data for CosmoERP'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating rich sample data... This might take a few seconds.')
        now = timezone.now()
        today = now.date()

        # Helper to generate random past dates
        def random_date(min_days_ago, max_days_ago):
            days = random.randint(min_days_ago, max_days_ago)
            return today - timedelta(days=days)

        # --- 1. Users ---
        users_data = [
            ('admin', 'admin2026', 'Directeur', 'General', 'admin@cosmo.tn', True),
            ('ceo1', 'cosmo2024', 'Karim', 'Belhaj', 'ceo@cosmo.tn', False),
            ('scientist1', 'cosmo2024', 'Ahmed', 'Benali', 'scientist@cosmo.tn', False),
            ('scientist2', 'cosmo2024', 'Nour', 'El Houda', 'nour@cosmo.tn', False),
            ('lab_manager1', 'cosmo2024', 'Sonia', 'Mansour', 'lab@cosmo.tn', False),
            ('operator1', 'cosmo2024', 'Mohamed', 'Trabelsi', 'operator1@cosmo.tn', False),
            ('operator2', 'cosmo2024', 'Sami', 'Feki', 'operator2@cosmo.tn', False),
            ('operator3', 'cosmo2024', 'Ali', 'Jebali', 'operator3@cosmo.tn', False),
            ('warehouse1', 'cosmo2024', 'Rania', 'Chahed', 'warehouse@cosmo.tn', False),
            ('warehouse2', 'cosmo2024', 'Anis', 'Kamel', 'warehouse2@cosmo.tn', False),
            ('purchase1', 'cosmo2024', 'Farouk', 'Saad', 'purchase@cosmo.tn', False),
            ('regulatory1', 'cosmo2024', 'Leila', 'Bouaziz', 'regulatory@cosmo.tn', False),
            ('qc1', 'cosmo2024', 'Amira', 'Khelifi', 'qc@cosmo.tn', False),
            ('qc2', 'cosmo2024', 'Hela', 'Masmoudi', 'qc2@cosmo.tn', False),
        ]
        users = {}
        for username, password, first, last, email, is_super in users_data:
            u, created = User.objects.get_or_create(username=username)
            u.set_password(password)
            u.first_name = first
            u.last_name = last
            u.email = email
            if is_super:
                u.is_superuser = True
                u.is_staff = True
            u.save()
            users[username] = u

        # --- 2. Roles ---
        from apps.rnd.models import RndRole
        from apps.production.models import ProductionRole
        from apps.stock.models import StockRole
        from apps.dashboard.models import DashboardRole

        roles_rnd = [('admin','viewer'), ('ceo1','viewer'), ('scientist1','scientist'), ('scientist2','scientist'), ('lab_manager1','lab_manager'), ('regulatory1','regulatory')]
        for username, role in roles_rnd:
            RndRole.objects.update_or_create(user=users[username], defaults={'role': role})

        roles_prod = [('admin','viewer'), ('lab_manager1','lab_manager'), ('operator1','operator'), ('operator2','operator'), ('operator3','operator'), ('qc1','qc_technician'), ('qc2','qc_technician')]
        for username, role in roles_prod:
            ProductionRole.objects.update_or_create(user=users[username], defaults={'role': role})

        roles_stock = [('admin','viewer'), ('warehouse1','warehouse_manager'), ('warehouse2','warehouse_manager'), ('purchase1','purchase_officer'), ('lab_manager1','production_manager')]
        for username, role in roles_stock:
            StockRole.objects.update_or_create(user=users[username], defaults={'role': role})

        roles_dash = [('admin','ceo'), ('ceo1','ceo'), ('lab_manager1','lab_manager'), ('warehouse1','warehouse_manager')]
        for username, role in roles_dash:
            DashboardRole.objects.update_or_create(user=users[username], defaults={'role': role})

        # --- 3. Material Categories ---
        from apps.stock.models import MaterialCategory, Material, Lot
        from apps.rnd.models import Ingredient
        
        cat_names = ['Actifs', 'Emollients', 'Emulsifiants', 'Conservateurs', 'Solvants', 'Vitamines', 'Parfums', 'Emballage primaire', 'Emballage secondaire']
        cats = {}
        for name in cat_names:
            c, _ = MaterialCategory.objects.get_or_create(name=name)
            cats[name] = c

        # --- 4. Ingredients & Materials ---
        items_data = [
            # Name, INCI, CAS, MaterialType, CatName, Unit, MinStock, Cost, MaxConc, Func
            ('Acide Hyaluronique', 'Sodium Hyaluronate', '9067-32-7', 'raw_material', 'Actifs', 'kg', 5, 120.0, 5.0, 'Hydratant'),
            ('Glycerine Végétale', 'Glycerin', '56-81-5', 'raw_material', 'Solvants', 'kg', 50, 4.0, 20.0, 'Humectant'),
            ('Beurre de Karité', 'Butyrospermum Parkii Butter', '194043-92-0', 'raw_material', 'Emollients', 'kg', 20, 15.0, 30.0, 'Nourrissant'),
            ('Huile de Jojoba', 'Simmondsia Chinensis Seed Oil', '90045-98-0', 'raw_material', 'Emollients', 'L', 15, 25.0, 100.0, 'Emollient'),
            ('Vitamine C', 'Ascorbic Acid', '50-81-7', 'raw_material', 'Vitamines', 'kg', 2, 80.0, 15.0, 'Anti-oxydant'),
            ('Niacinamide', 'Niacinamide', '98-92-0', 'raw_material', 'Vitamines', 'kg', 5, 40.0, 10.0, 'Eclaircissant'),
            ('Cetearyl Alcohol', 'Cetearyl Alcohol', '67762-27-0', 'raw_material', 'Emulsifiants', 'kg', 20, 8.0, 10.0, 'Emulsifiant'),
            ('Phenoxyethanol', 'Phenoxyethanol', '122-99-6', 'raw_material', 'Conservateurs', 'kg', 10, 12.0, 1.0, 'Conservateur'),
            ('Eau Purifiée', 'Aqua', '7732-18-5', 'raw_material', 'Solvants', 'L', 500, 0.2, 100.0, 'Solvant'),
            ('Acide Salicylique', 'Salicylic Acid', '69-72-7', 'raw_material', 'Actifs', 'kg', 3, 50.0, 2.0, 'Exfoliant'),
            ('Huile Essentielle Lavande', 'Lavandula Angustifolia Oil', '8000-28-0', 'raw_material', 'Parfums', 'L', 2, 150.0, 2.0, 'Parfum'),
            
            # Packaging
            ('Flacon Airless 50ml', '', '', 'packaging', 'Emballage primaire', 'pcs', 1000, 0.45, None, None),
            ('Flacon Pipette 30ml', '', '', 'packaging', 'Emballage primaire', 'pcs', 1000, 0.55, None, None),
            ('Tube Plastique 100ml', '', '', 'packaging', 'Emballage primaire', 'pcs', 2000, 0.20, None, None),
            ('Etui Carton 50ml Standard', '', '', 'packaging', 'Emballage secondaire', 'pcs', 1000, 0.15, None, None),
            ('Etui Carton 30ml Premium', '', '', 'packaging', 'Emballage secondaire', 'pcs', 1000, 0.25, None, None),
            
            # Finished Products
            ('Crème Anti-Âge Nuit 50ml', '', '', 'finished_product', 'Emballage primaire', 'pcs', 200, 8.50, None, None),
            ('Sérum Éclat Vitamine C 30ml', '', '', 'finished_product', 'Emballage primaire', 'pcs', 150, 6.20, None, None),
            ('Lotion Exfoliante BHA 100ml', '', '', 'finished_product', 'Emballage primaire', 'pcs', 300, 4.80, None, None),
            ('Baume Réparateur Karité 100ml', '', '', 'finished_product', 'Emballage primaire', 'pcs', 250, 5.10, None, None),
        ]

        ingredients = {}
        materials = {}
        idx = 1
        for name, inci, cas, mtype, cat_name, unit, min_stock, cost, max_conc, func in items_data:
            code = f"{mtype[:2].upper()}{str(idx).zfill(3)}"
            idx += 1
            
            # Create Ingredient if raw_material
            ing = None
            if mtype == 'raw_material':
                ing, _ = Ingredient.objects.get_or_create(name=name, defaults={
                    'inci_name': inci, 'cas_number': cas, 'category': 'active' if cat_name=='Actifs' else 'solvent',
                    'supplier': 'Multiple', 'max_concentration': max_conc
                })
                ingredients[name] = ing

            # Create Material
            mat, _ = Material.objects.get_or_create(code=code, defaults={
                'name': name, 'material_type': mtype, 'unit': unit,
                'minimum_stock': min_stock, 'reorder_quantity': min_stock*2,
                'category': cats.get(cat_name), 'ingredient': ing
            })
            materials[name] = mat

        # --- 5. Lots Generation ---
        # Generate 2-3 lots per material (excluding finished for now) to show stock diversity
        suppliers_list = ['BioActive Lab', 'ChemPlus', 'NatureExtracts', 'PackPro Int.', 'GlassTech TN']
        for name, mat in materials.items():
            if mat.material_type != 'finished_product':
                for i in range(random.randint(2, 4)): # 2 to 4 lots per material
                    lot_num = f"LOT-{mat.code}-{2024}-{str(i+1).zfill(2)}"
                    qty = random.uniform(mat.minimum_stock, mat.minimum_stock * 5)
                    # Some lots close to expiry for dashboard alerts
                    days_to_expiry = random.randint(10, 500)
                    Lot.objects.get_or_create(lot_number=lot_num, defaults={
                        'material': mat, 'supplier': random.choice(suppliers_list),
                        'initial_quantity': qty * 1.2, 'current_quantity': qty,
                        'expiry_date': today + timedelta(days=days_to_expiry),
                        'unit_cost': mat.minimum_stock * 0.1 + random.uniform(-1, 2) if mat.minimum_stock else 1.0,
                        'created_by': users['warehouse1']
                    })

        # --- 6. Products & Formulations ---
        from apps.rnd.models import Product, Formulation, FormulationIngredient
        
        prod_data = [
            ('Crème Anti-Âge Nuit', 'skincare', 'Crème Anti-Âge Nuit 50ml', [
                ('Eau Purifiée', 'A', 65.0), ('Glycerine Végétale', 'A', 5.0), 
                ('Beurre de Karité', 'B', 15.0), ('Cetearyl Alcohol', 'B', 6.0),
                ('Acide Hyaluronique', 'C', 1.0), ('Niacinamide', 'C', 7.0), 
                ('Phenoxyethanol', 'C', 0.8), ('Huile Essentielle Lavande', 'C', 0.2)
            ]),
            ('Sérum Éclat Vitamine C', 'skincare', 'Sérum Éclat Vitamine C 30ml', [
                ('Eau Purifiée', 'A', 75.0), ('Glycerine Végétale', 'A', 10.0),
                ('Vitamine C', 'B', 14.0), ('Phenoxyethanol', 'C', 1.0)
            ]),
            ('Lotion Exfoliante BHA', 'skincare', 'Lotion Exfoliante BHA 100ml', [
                ('Eau Purifiée', 'A', 88.0), ('Glycerine Végétale', 'A', 8.0),
                ('Acide Salicylique', 'B', 2.0), ('Phenoxyethanol', 'C', 1.0),
                ('Huile de Jojoba', 'D', 1.0)
            ]),
            ('Baume Réparateur', 'bodycare', 'Baume Réparateur Karité 100ml', [
                ('Beurre de Karité', 'A', 70.0), ('Huile de Jojoba', 'A', 28.0),
                ('Vitamine C', 'B', 1.0), ('Phenoxyethanol', 'C', 1.0)
            ])
        ]

        rnd_products = {}
        forms = {}
        idx = 1
        for p_name, p_cat, mat_name, f_ingrs in prod_data:
            ref = f"PRD2024-00{idx}"
            idx += 1
            prod, _ = Product.objects.get_or_create(reference=ref, defaults={
                'name': p_name, 'category': p_cat, 'status': 'approved',
                'created_by': users['scientist1']
            })
            rnd_products[p_name] = prod
            
            form, _ = Formulation.objects.get_or_create(product=prod, version='1.0', defaults={
                'status': 'approved', 'batch_size': 100.0, 'ph_min': 5.0, 'ph_max': 6.5,
                'appearance': 'Conforme au standard',
                'created_by': users['scientist1'], 'approved_by': users['lab_manager1']
            })
            forms[mat_name] = form
            
            # Clear old and create ingredients
            form.ingredients.all().delete()
            for i, (ing_n, phase, pct) in enumerate(f_ingrs):
                FormulationIngredient.objects.create(
                    formulation=form, ingredient=ingredients[ing_n],
                    phase=phase, percentage=pct, function='Actif', order=i
                )

        # --- 7. Production Batches & QC ---
        from apps.production.models import ProductionBatch, QCCheck
        batch_statuses = ['completed'] * 12 + ['in_progress'] * 3 + ['planned'] * 5
        
        batch_idx = 1
        for i, status in enumerate(batch_statuses):
            mat_name = random.choice(list(forms.keys()))
            form = forms[mat_name]
            fp_mat = materials[mat_name]
            
            # Spread production dates realistically
            p_date = random_date(1, 90) if status == 'completed' else (today if status == 'in_progress' else random_date(-15, -1))
            
            qty = random.choice([50.0, 100.0, 250.0])
            b_num = f"BATCH-{str(p_date.year)}-{str(p_date.month).zfill(2)}-{str(batch_idx).zfill(3)}"
            batch_idx += 1
            
            batch, _ = ProductionBatch.objects.get_or_create(batch_number=b_num, defaults={
                'formulation': form, 'planned_quantity': qty, 
                'actual_quantity': qty * random.uniform(0.95, 1.0) if status == 'completed' else 0,
                'production_date': p_date, 'status': status,
                'responsible': users['lab_manager1'], 
                'operator': random.choice([users['operator1'], users['operator2'], users['operator3']])
            })

            # Create Finished product lot if completed
            if status == 'completed' and not batch.finished_lot:
                lot_qty = int(batch.actual_quantity * (10 if '30ml' in mat_name else 5 if '50ml' in mat_name else 10))
                fp_lot, _ = Lot.objects.get_or_create(lot_number=b_num, material=fp_mat, defaults={
                    'initial_quantity': lot_qty, 'current_quantity': int(lot_qty * random.uniform(0.1, 0.8)),
                    'expiry_date': p_date + timedelta(days=365*2),
                    'unit_cost': fp_mat.minimum_stock * 0.05 if fp_mat.minimum_stock else 5.0,
                    'created_by': users['operator1']
                })
                batch.finished_lot = fp_lot
                batch.save()
                
                # Create QC Checks for completed
                QCCheck.objects.get_or_create(batch=batch, test_name='pH', defaults={
                    'specification': 'Conforme', 'measured_value': str(round(random.uniform(5.2, 6.2), 2)),
                    'result': 'pass', 'performed_by': users['qc1'], 'performed_at': now
                })
                QCCheck.objects.get_or_create(batch=batch, test_name='Aspect Visuel', defaults={
                    'specification': 'Conforme', 'measured_value': 'OK',
                    'result': 'pass', 'performed_by': users['qc2'], 'performed_at': now
                })

        # --- 8. Suppliers & Purchase Orders ---
        from apps.purchase.models import Supplier, PurchaseOrder, PurchaseOrderLine
        suppliers_data = [
            ('SUP01', 'BioActive Europe', 'contact@bioactive.eu', 'France'),
            ('SUP02', 'ChemPlus Tunisie', 'tunis@chemplus.com', 'Tunisie'),
            ('SUP03', 'NatureExtracts SA', 'info@nature-ex.ma', 'Maroc'),
            ('SUP04', 'PackPro International', 'sales@packpro.cn', 'Chine'),
            ('SUP05', 'GlassTech TN', 'contact@glasstech.tn', 'Tunisie'),
        ]
        sups = []
        for code, name, email, country in suppliers_data:
            s, _ = Supplier.objects.get_or_create(code=code, defaults={'name': name, 'email': email, 'country': country})
            sups.append(s)

        # 30 Purchase Orders over 6 months
        raw_mats = [m for m in materials.values() if m.material_type in ['raw_material', 'packaging']]
        for i in range(1, 31):
            s = random.choice(sups)
            o_date = random_date(5, 180)
            status = 'received' if o_date < today - timedelta(days=15) else random.choice(['draft', 'confirmed', 'shipped'])
            
            po, _ = PurchaseOrder.objects.get_or_create(order_number=f"PO-{o_date.year}-{str(i).zfill(3)}", defaults={
                'supplier': s, 'status': status, 'order_date': o_date,
                'expected_delivery': o_date + timedelta(days=15),
                'actual_delivery': o_date + timedelta(days=14) if status == 'received' else None,
                'created_by': users['purchase1']
            })
            
            # Add 2-5 lines
            num_lines = random.randint(2, 5)
            for m in random.sample(raw_mats, num_lines):
                qty = random.uniform(10, 500)
                price = m.minimum_stock * 0.1 if m.minimum_stock else 10.0
                PurchaseOrderLine.objects.get_or_create(order=po, material=m, defaults={
                    'quantity': qty, 'unit_price': price,
                    'received_quantity': qty if status == 'received' else 0
                })

        # --- 9. Customers & Sales Orders ---
        from apps.sales.models import Customer, SalesOrder, SalesOrderLine
        customers_data = [
            ('CLT01', 'Pharmacie Principale', 'Tunis, Tunisie'), ('CLT02', 'Parapharmacie Sfax', 'Sfax, Tunisie'),
            ('CLT03', 'BeautyShop Paris', 'Paris, France'), ('CLT04', 'Cosmetiques d\'Alger', 'Alger, Algérie'),
            ('CLT05', 'Para Sousse', 'Sousse, Tunisie'), ('CLT06', 'PharmaCare', 'Dakar, Sénégal'),
            ('CLT07', 'Para Djerba', 'Djerba, Tunisie'), ('CLT08', 'Grosiste Beauty TN', 'Bizerte, Tunisie'),
            ('CLT09', 'Natura Shop', 'Lyon, France'), ('CLT10', 'Health & Beauty', 'Casablanca, Maroc')
        ]
        custs = []
        for code, name, city in customers_data:
            c, _ = Customer.objects.get_or_create(code=code, defaults={'name': name, 'country': city})
            custs.append(c)

        # 50 Sales Orders over 6 months
        fin_mats = [m for m in materials.values() if m.material_type == 'finished_product']
        for i in range(1, 51):
            c = random.choice(custs)
            o_date = random_date(2, 180)
            status = random.choices(['draft', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'], 
                                   weights=[5, 10, 15, 20, 45, 5])[0]
            if o_date > today - timedelta(days=10) and status == 'delivered':
                status = 'processing'
                
            so, _ = SalesOrder.objects.get_or_create(order_number=f"SO-{o_date.year}-{str(i).zfill(3)}", defaults={
                'customer': c, 'status': status, 'order_date': o_date,
                'delivery_date': o_date + timedelta(days=7),
                'created_by': users['ceo1']
            })
            
            # Add 1-4 lines
            num_lines = random.randint(1, min(len(fin_mats), 4))
            for m in random.sample(fin_mats, num_lines):
                qty = random.randint(10, 200)
                price = (m.minimum_stock * 0.05 + 5.0) if m.minimum_stock else 12.0
                loc_lot = Lot.objects.filter(material=m).first()
                SalesOrderLine.objects.get_or_create(order=so, material=m, defaults={
                    'quantity': qty, 'unit_price': price,
                    'shipped_quantity': qty if status in ['shipped', 'delivered'] else 0,
                    'lot': loc_lot if status in ['shipped', 'delivered'] else None
                })

        # --- 10. Regulatory ---
        from apps.regulatory.models import ProductCompliance, SafetyReport, CPNPNotification
        for p in rnd_products.values():
            ProductCompliance.objects.get_or_create(product=p, defaults={
                'status': random.choice(['compliant', 'in_review']), 
                'eu_regulation': True, 'responsible_person': 'Leila Bouaziz',
                'last_review_date': today - timedelta(days=random.randint(10, 300)),
                'next_review_date': today + timedelta(days=random.randint(30, 365)),
                'updated_by': users['regulatory1']
            })

        self.stdout.write(self.style.SUCCESS('\n========================================='))
        self.stdout.write(self.style.SUCCESS('✨ RICH SAMPLE DATA CREATED SUCCESSFULLY! ✨'))
        self.stdout.write(self.style.SUCCESS('=========================================\n'))
        
        self.stdout.write('🔑 Accounts Ready:')
        self.stdout.write('  Super Admin : admin      // Password: admin2026')
        self.stdout.write('  CEO/Manager : ceo1       // Password: cosmo2024')
        self.stdout.write('  Scientist   : scientist1 // Password: cosmo2024')
        self.stdout.write('  Warehouse   : warehouse1 // Password: cosmo2024')
        
        self.stdout.write('\n📊 Generated Items:')
        self.stdout.write(f'  - {len(materials)} Materials & Ingredients')
        self.stdout.write(f'  - {len(rnd_products)} Formulations')
        self.stdout.write(f'  - {len(batch_statuses)} Production Batches')
        self.stdout.write(f'  - 30 Purchase Orders (Suppliers)')
        self.stdout.write(f'  - 50 Sales Orders (Customers)')
        self.stdout.write('\n🚀 Demo is ready to showcase!')
