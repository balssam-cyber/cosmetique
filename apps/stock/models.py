from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


class StockRole(models.Model):
    ROLE_CHOICES = [
        ('warehouse_manager', 'Responsable Entrepôt'),
        ('purchase_officer', 'Responsable Achats'),
        ('production_manager', 'Responsable Production'),
        ('viewer', 'Visiteur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stock_role')
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = "Rôle Stock"
        verbose_name_plural = "Rôles Stock"


class MaterialCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Catégorie")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Catégorie matière"
        verbose_name_plural = "Catégories matières"


class Material(models.Model):
    TYPE_CHOICES = [
        ('raw_material', 'Matière première'),
        ('packaging', 'Emballage'),
        ('finished_product', 'Produit fini'),
        ('laboratory', 'Matériel laboratoire'),
    ]
    UNIT_CHOICES = [
        ('kg', 'Kilogramme'),
        ('g', 'Gramme'),
        ('L', 'Litre'),
        ('mL', 'Millilitre'),
        ('pcs', 'Pièce'),
        ('box', 'Boîte'),
    ]
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    name = models.CharField(max_length=200, verbose_name="Nom")
    material_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.ForeignKey(MaterialCategory, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        verbose_name="Stock minimum")
    reorder_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                           verbose_name="Quantité de commande")
    order_cost = models.DecimalField(
    max_digits=10, decimal_places=2, default=0,
    verbose_name="Coût par commande (DT)"
)
    holding_cost = models.DecimalField(
    max_digits=10, decimal_places=2, default=0,
    verbose_name="Coût de stockage/unité/mois (DT)"
)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    # Link to R&D ingredient (optional) - text ref for manual matching
    ingredient_ref = models.CharField(max_length=200, blank=True, verbose_name="Réf. ingrédient")
    # Direct FK to R&D Ingredient for automatic stock calculation in production
    ingredient = models.OneToOneField(
        'rnd.Ingredient', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='stock_material',
        verbose_name="Ingrédient R&D lié"
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def total_quantity(self):
        return self.lots.filter(is_active=True).aggregate(
            total=models.Sum('current_quantity'))['total'] or 0

    @property
    def is_low_stock(self):
        return self.total_quantity <= self.minimum_stock
    @property
    def eoq(self):
        import math
        from django.utils import timezone
        from datetime import timedelta
        last_month = timezone.now() - timedelta(days=30)
        consumed = StockMovement.objects.filter(
        lot__material=self,
        movement_type='production_use',
        created_at__gte=last_month
    ).aggregate(total=models.Sum('quantity'))['total'] or 0
        D = abs(float(consumed))
        S = float(self.order_cost)
        H = float(self.holding_cost)
        if H > 0 and D > 0 and S > 0:
            return round(math.sqrt((2 * D * S) / H), 2)
        return None
    
    class Meta:
        verbose_name = "Matière / Produit"
        verbose_name_plural = "Matières / Produits"
        ordering = ['name']


class Lot(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='lots')
    lot_number = models.CharField(max_length=100, unique=True, verbose_name="Numéro de lot")
    supplier = models.CharField(max_length=200, blank=True, verbose_name="Fournisseur (Supplier)")
    initial_quantity = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Quantité initiale")
    current_quantity = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Quantité actuelle")
    reception_date = models.DateField(default=timezone.now, verbose_name="Date de réception / production")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Date d'expiration")
    location = models.CharField(max_length=100, blank=True, verbose_name="Emplacement géographique")
    
    QC_CHOICES = [
        ('quarantine', 'En Quarantaine'),
        ('approved', 'Approuvé (Conforme)'),
        ('rejected', 'Rejeté (Non Conforme)'),
    ]
    qc_status = models.CharField(max_length=20, choices=QC_CHOICES, default='quarantine', verbose_name="Statut Qualité")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name="Coût unitaire")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Lot"
        verbose_name_plural = "Lots"
        ordering = ['-reception_date']

    def __str__(self):
        return f"{self.lot_number} ({self.material.name}) - {self.current_quantity}{self.material.unit}"
        
    def get_qr_code_base64(self):
        import qrcode
        from io import BytesIO
        import base64
        
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        data = f"LOT: {self.lot_number}\nPROD: {self.material.name}\nQTE: {self.current_quantity} {self.material.get_unit_display()}"
        if self.expiry_date:
            data += f"\nEXP: {self.expiry_date.strftime('%Y-%m-%d')}"
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#0d1b3e", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    @property
    def is_expiring_soon(self):
        if self.expiry_date:
            threshold = timezone.now().date() + timedelta(
                days=getattr(settings, 'EXPIRY_ALERT_DAYS', 30))
            return self.expiry_date <= threshold
        return False

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    class Meta:
        verbose_name = "Lot"
        verbose_name_plural = "Lots"
        ordering = ['-reception_date']


class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('reception', 'Réception'),
        ('production_use', 'Utilisation production'),
        ('production_output', 'Sortie production'),
        ('sale', 'Vente'),
        ('adjustment', 'Ajustement'),
        ('return', 'Retour'),
        ('loss', 'Perte'),
    ]
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2,
                                    verbose_name="Quantité (+ entrée / - sortie)")
    reference = models.CharField(max_length=200, blank=True, verbose_name="Référence")
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.lot} - {self.quantity}"

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-created_at']
