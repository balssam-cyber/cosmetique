from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.stock.models import Material, Lot, StockMovement


class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code client")
    contact_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True, verbose_name="Adresse")
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['name']


class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('shipped', 'Expédié'),
        ('invoiced', 'Facturé'),
        ('cancelled', 'Annulé'),
    ]
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de commande")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField(default=timezone.now, verbose_name="Date commande")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Date livraison")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Remise globale (%)")
    
    invoice_number = models.CharField(max_length=50, blank=True, verbose_name="N° Facture")
    tva_rate = models.DecimalField(max_digits=5, decimal_places=2, default=19.00, verbose_name="TVA (%)")
    PAYMENT_CHOICES = [
        ('unpaid', 'Non payé'),
        ('partial', 'Partiellement payé'),
        ('paid', 'Payé'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='unpaid')
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='created_sales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CV-{self.order_number} - {self.customer.name}"

    @property
    def gross_amount(self):
        """Total avant remise."""
        return sum(line.total_price for line in self.lines.all())

    @property
    def total_amount(self):
        """Total après remise (HT)."""
        gross = self.gross_amount
        return float(gross) * (1.0 - (float(self.discount) / 100.0))

    @property
    def total_tva(self):
        return self.total_amount * (float(self.tva_rate) / 100.0)

    @property
    def total_ttc(self):
        return self.total_amount + self.total_tva

    class Meta:
        verbose_name = "Commande vente"
        verbose_name_plural = "Commandes vente"
        ordering = ['-order_date']


class SalesOrderLine(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='lines')
    material = models.ForeignKey(Material, on_delete=models.PROTECT,
                                  limit_choices_to={'material_type': 'finished_product'})
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Prix unitaire")
    shipped_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                            verbose_name="Quantité expédiée")

    def __str__(self):
        return f"{self.material.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    class Meta:
        verbose_name = "Ligne de vente"
        verbose_name_plural = "Lignes de vente"


class Shipment(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='shipments')
    shipment_date = models.DateField(default=timezone.now, verbose_name="Date expédition")
    tracking_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    shipped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EXP-{self.id} - {self.order.order_number}"

    class Meta:
        verbose_name = "Expédition"
        verbose_name_plural = "Expéditions"


class ShipmentLine(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='lines')
    order_line = models.ForeignKey(SalesOrderLine, on_delete=models.PROTECT)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    created_lot_movement = models.OneToOneField('stock.StockMovement', on_delete=models.SET_NULL,
                                                  null=True, blank=True)

    def __str__(self):
        return f"{self.order_line.material.name} - {self.quantity}"

    class Meta:
        verbose_name = "Ligne d'expédition"
        verbose_name_plural = "Lignes d'expédition"
