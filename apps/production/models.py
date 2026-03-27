from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.rnd.models import Formulation, Product
from apps.stock.models import Material, Lot, StockMovement


class ProductionRole(models.Model):
    ROLE_CHOICES = [
        ('lab_manager', 'Responsable Laboratoire'),
        ('operator', 'Opérateur'),
        ('qc_technician', 'Technicien CQ'),
        ('viewer', 'Visiteur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='production_role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = "Rôle Production"
        verbose_name_plural = "Rôles Production"


class ProductionBatch(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planifié'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('on_hold', 'En attente'),
    ]
    batch_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de lot")
    formulation = models.ForeignKey(Formulation, on_delete=models.PROTECT,
                                     related_name='production_batches')
    planned_quantity = models.DecimalField(max_digits=10, decimal_places=2,
                                           verbose_name="Quantité planifiée (kg)")
    actual_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          verbose_name="Quantité réelle (kg)")
    production_date = models.DateField(default=timezone.now, verbose_name="Date de production")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                     related_name='managed_batches')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='operated_batches')
    notes = models.TextField(blank=True)
    # Linked finished product lot
    finished_lot = models.OneToOneField(Lot, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='from_batch')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lot {self.batch_number} - {self.formulation.product.name}"

    @property
    def qc_passed(self):
        checks = self.qc_checks.all()
        if not checks:
            return None
        return all(c.result == 'pass' for c in checks)

    class Meta:
        verbose_name = "Lot de production"
        verbose_name_plural = "Lots de production"
        ordering = ['-production_date']


class BatchRawMaterial(models.Model):
    batch = models.ForeignKey(ProductionBatch, on_delete=models.CASCADE,
                               related_name='raw_materials')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, null=True, blank=True)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT, null=True, blank=True)
    # Stored from formulation at creation time
    ingredient_name = models.CharField(max_length=200, blank=True, verbose_name="Ingrédient")
    ingredient_percentage = models.DecimalField(max_digits=8, decimal_places=4,
                                                 null=True, blank=True, verbose_name="% formulation")
    required_quantity = models.DecimalField(max_digits=10, decimal_places=4,
                                             verbose_name="Quantité requise")
    actual_quantity = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True,
                                          verbose_name="Quantité réelle utilisée")

    def __str__(self):
        name = self.material.name if self.material else self.ingredient_name
        return f"{name} - {self.required_quantity}"

    @property
    def display_name(self):
        return self.material.name if self.material else self.ingredient_name or "?"

    @property
    def available_stock(self):
        if self.material:
            return self.material.total_quantity
        return None

    @property
    def stock_ok(self):
        if self.material:
            return self.material.total_quantity >= self.required_quantity
        return None

    class Meta:
        verbose_name = "Matière première du lot"
        verbose_name_plural = "Matières premières du lot"


class QCCheck(models.Model):
    RESULT_CHOICES = [
        ('pass', 'Conforme'),
        ('fail', 'Non conforme'),
        ('pending', 'En attente'),
    ]
    batch = models.ForeignKey(ProductionBatch, on_delete=models.CASCADE, related_name='qc_checks')
    test_name = models.CharField(max_length=200, verbose_name="Nom du test")
    specification = models.CharField(max_length=200, blank=True, verbose_name="Spécification")
    measured_value = models.CharField(max_length=100, blank=True, verbose_name="Valeur mesurée")
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pending')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                      related_name='performed_qc')
    performed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date/heure")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.test_name} - {self.batch.batch_number} - {self.get_result_display()}"

    class Meta:
        verbose_name = "Contrôle qualité"
        verbose_name_plural = "Contrôles qualité"


class Equipment(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la machine")
    serial_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro de série")
    description = models.TextField(blank=True)
    purchase_date = models.DateField(null=True, blank=True, verbose_name="Date d'achat")
    last_maintenance = models.DateField(null=True, blank=True, verbose_name="Dernière maintenance")
    next_maintenance = models.DateField(null=True, blank=True, verbose_name="Prochaine maintenance prévue")
    is_active = models.BooleanField(default=True, verbose_name="En service")
    
    class Meta:
        verbose_name = "Équipement (GMAO)"
        verbose_name_plural = "Équipements (GMAO)"
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name}" + (f" ({self.serial_number})" if self.serial_number else "")

class MaintenanceLog(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(default=timezone.now, verbose_name="Date d'intervention")
    description = models.TextField(verbose_name="Détails de la maintenance")
    performed_by = models.CharField(max_length=150, verbose_name="Effectué par (Technicien ou externe)")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Coût estimé")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Intervention de maintenance"
        verbose_name_plural = "Interventions de maintenance"
        ordering = ['-date']

class BatchTimeLog(models.Model):
    batch = models.ForeignKey(ProductionBatch, on_delete=models.CASCADE, related_name='time_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Employé / Opérateur")
    date = models.DateField(default=timezone.now, verbose_name="Date de travail")
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Heures travaillées")
    hourly_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Coût horaire")
    
    class Meta:
        verbose_name = "Suivi Main d'Œuvre"
        verbose_name_plural = "Suivis Main d'Œuvre"
        ordering = ['-date']

