from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.stock.models import Material, Lot, StockMovement


class PurchaseRole(models.Model):
    ROLE_CHOICES = [
        ('purchase_officer', 'Responsable Achats'),
        ('warehouse_manager', 'Responsable Entrepôt'),
        ('viewer', 'Visiteur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='purchase_role')
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = "Rôle Achats"
        verbose_name_plural = "Rôles Achats"


class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code fournisseur")
    contact_name = models.CharField(max_length=200, blank=True, verbose_name="Contact")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    country = models.CharField(max_length=100, blank=True, verbose_name="Pays")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['name']


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyé'),
        ('confirmed', 'Confirmé'),
        ('partially_received', 'Partiellement reçu'),
        ('received', 'Reçu'),
        ('cancelled', 'Annulé'),
    ]
    CURRENCY_CHOICES = [
        ('TND', 'Dinar Tunisien'),
        ('EUR', 'Euro'),
        ('USD', 'Dollar US'),
        ('GBP', 'Livre Sterling'),
    ]
    currency = models.CharField(
    max_length=3, choices=CURRENCY_CHOICES, default='TND',
    verbose_name="Devise"
)
    exchange_rate = models.DecimalField(
    max_digits=10, decimal_places=4, default=1,
    verbose_name="Taux de change vers TND"
)
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de commande")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField(default=timezone.now, verbose_name="Date de commande")
    expected_delivery = models.DateField(null=True, blank=True, verbose_name="Livraison prévue")
    actual_delivery = models.DateField(null=True, blank=True, verbose_name="Livraison réelle")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='created_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
       return f"BC-{self.order_number} - {self.supplier.name}"

    @property
    def total_amount(self):
        return sum(line.total_price for line in self.lines.all())

    @property
    def total_amount_tnd(self):
        return self.total_amount * self.exchange_rate

    class Meta:
        verbose_name = "Bon de commande"
        verbose_name_plural = "Bons de commande"
        ordering = ['-order_date']


class PurchaseOrderLine(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Prix unitaire")
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                             verbose_name="Quantité reçue")
    notes = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.material.name} - {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"


class GoodsReceipt(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='receipts')
    receipt_date = models.DateField(default=timezone.now, verbose_name="Date de réception")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence BL")
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BR-{self.id} - {self.order.order_number}"

    class Meta:
        verbose_name = "Bon de réception"
        verbose_name_plural = "Bons de réception"


class GoodsReceiptLine(models.Model):
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='lines')
    order_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT)
    lot_number = models.CharField(max_length=100, verbose_name="Numéro de lot fournisseur")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité reçue")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Date expiration")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    # Created stock lot
    created_lot = models.OneToOneField(Lot, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='purchase_receipt_line')

    def __str__(self):
        return f"{self.order_line.material.name} - {self.quantity}"

    class Meta:
        verbose_name = "Ligne de réception"
        verbose_name_plural = "Lignes de réception"
class StockShortage(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='shortages')
    material_name = models.CharField(max_length=200, verbose_name="Matière manquante")
    expected_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.TextField(blank=True, verbose_name="Note")
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Manque : {self.material_name} — BC-{self.order.order_number}"

    class Meta:
        verbose_name = "Manque stock"
        verbose_name_plural = "Manques stock"
        ordering = ['-created_at']
