from django.db import models
from django.contrib.auth.models import User


class RndRole(models.Model):
    ROLE_CHOICES = [
        ('scientist', 'Scientist'),
        ('lab_manager', 'Lab Manager'),
        ('regulatory', 'Regulatory'),
        ('viewer', 'Viewer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rnd_role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = "Rôle R&D"
        verbose_name_plural = "Rôles R&D"


class Ingredient(models.Model):
    CATEGORY_CHOICES = [
        ('active', 'Actif'),
        ('emulsifier', 'Émulsifiant'),
        ('preservative', 'Conservateur'),
        ('fragrance', 'Parfum'),
        ('colorant', 'Colorant'),
        ('solvent', 'Solvant'),
        ('other', 'Autre'),
    ]
    name = models.CharField(max_length=200, verbose_name="Nom")
    inci_name = models.CharField(max_length=200, blank=True, verbose_name="Nom INCI")
    cas_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro CAS")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    supplier = models.CharField(max_length=200, blank=True, verbose_name="Fournisseur")
    max_concentration = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                             verbose_name="Concentration max (%)")
    is_restricted = models.BooleanField(default=False, verbose_name="Restreint")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    # ── Champs étendus utilisés dans le formulaire ──
    origin = models.CharField(max_length=200, blank=True, verbose_name="Origine")
    aspect = models.CharField(max_length=200, blank=True, verbose_name="Aspect physique")
    certification = models.CharField(max_length=200, blank=True, verbose_name="Certifications")
    description = models.TextField(blank=True, verbose_name="Description")
    applications = models.TextField(blank=True, verbose_name="Applications cosmétiques")
    usage_mode = models.CharField(max_length=200, blank=True, verbose_name="Mode d'ajout")
    dosage_min = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                     verbose_name="Dosage min (%)")
    dosage_max = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True,
                                     verbose_name="Dosage max (%)")
    addition_phase = models.CharField(max_length=100, blank=True, verbose_name="Phase d'ajout")
    solubility = models.CharField(max_length=200, blank=True, verbose_name="Solubilité")
    storage = models.CharField(max_length=200, blank=True, verbose_name="Conditions de stockage")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ingrédient"
        verbose_name_plural = "Ingrédients"
        ordering = ['name']


class Product(models.Model):
    STATUS_CHOICES = [
        ('development', 'En développement'),
        ('testing', 'En test'),
        ('approved', 'Approuvé'),
        ('discontinued', 'Arrêté'),
    ]
    CATEGORY_CHOICES = [
        ('skincare', 'Soin peau'),
        ('haircare', 'Soin cheveux'),
        ('makeup', 'Maquillage'),
        ('fragrance', 'Parfum'),
        ('bodycare', 'Soin corps'),
        ('suncare', 'Solaire'),
        ('other', 'Autre'),
    ]
    name = models.CharField(max_length=200, verbose_name="Nom")
    reference = models.CharField(max_length=50, unique=True, verbose_name="Référence")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='skincare')
    description = models.TextField(blank=True, verbose_name="Description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='development')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='created_products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} - {self.name}"

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']


class Formulation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('under_review', 'En révision'),
        ('approved', 'Approuvée'),
        ('obsolete', 'Obsolète'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='formulations')
    version = models.CharField(max_length=20, verbose_name="Version")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    batch_size = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Taille du lot (kg)")
    ph_min = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="pH min")
    ph_max = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="pH max")
    viscosity = models.CharField(max_length=100, blank=True, verbose_name="Viscosité")
    appearance = models.CharField(max_length=200, blank=True, verbose_name="Aspect")
    notes = models.TextField(blank=True, verbose_name="Notes")
    # ── Paramètres de coût ──
    packaging_cost = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Coût d'emballage unitaire (DT)")
    labor_cost = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Coût de la main d'œuvre unitaire (DT)")
    target_margin = models.DecimalField(max_digits=5, decimal_places=2, default=50, verbose_name="Marge ciblée (%)")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='created_formulations')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='approved_formulations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} v{self.version}"

    class Meta:
        verbose_name = "Formulation"
        verbose_name_plural = "Formulations"
        unique_together = ['product', 'version']
        ordering = ['-created_at']


class FormulationIngredient(models.Model):
    PHASE_CHOICES = [
        ('A', 'Phase A'),
        ('B', 'Phase B'),
        ('C', 'Phase C'),
        ('D', 'Phase D'),
        ('other', 'Autre'),
    ]
    formulation = models.ForeignKey(Formulation, on_delete=models.CASCADE, related_name='formulation_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    phase = models.CharField(max_length=10, choices=PHASE_CHOICES, default='A')
    percentage = models.DecimalField(max_digits=8, decimal_places=4, verbose_name="Pourcentage (%)")
    function = models.CharField(max_length=200, blank=True, verbose_name="Fonction")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.ingredient.name} ({self.percentage}%)"

    class Meta:
        verbose_name = "Ingrédient de formulation"
        verbose_name_plural = "Ingrédients de formulation"
        ordering = ['phase', 'order']


class StabilityTest(models.Model):
    CONDITION_CHOICES = [
        ('room_temp', 'Température ambiante (25°C)'),
        ('accelerated', 'Accéléré (40°C/75%RH)'),
        ('freeze_thaw', 'Congélation-décongélation'),
        ('uv', 'Exposition UV'),
        ('cold', 'Froid (4°C)'),
    ]
    RESULT_CHOICES = [
        ('pass', 'Conforme'),
        ('fail', 'Non conforme'),
        ('pending', 'En cours'),
    ]
    formulation = models.ForeignKey(Formulation, on_delete=models.CASCADE, related_name='stability_tests')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    duration_weeks = models.PositiveIntegerField(verbose_name="Durée (semaines)")
    start_date = models.DateField(verbose_name="Date début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date fin")
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pending')
    ph_initial = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    ph_final = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    appearance_ok = models.BooleanField(null=True, blank=True, verbose_name="Aspect OK")
    odor_ok = models.BooleanField(null=True, blank=True, verbose_name="Odeur OK")
    observations = models.TextField(blank=True, verbose_name="Observations")
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.formulation} - {self.get_condition_display()}"

    class Meta:
        verbose_name = "Test de stabilité"
        verbose_name_plural = "Tests de stabilité"
class IngredientCompatibility(models.Model):
    COMPATIBILITY_CHOICES = [
        ('compatible', 'Compatible'),
        ('incompatible', 'Incompatible'),
        ('caution', 'Précaution'),
    ]
    ingredient_a = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='compatibilities'
    )
    ingredient_b = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='compatible_with'
    )
    status = models.CharField(
        max_length=15, choices=COMPATIBILITY_CHOICES, default='compatible'
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['ingredient_a', 'ingredient_b']
        verbose_name = "Compatibilité"
        verbose_name_plural = "Compatibilités"

    def __str__(self):
        return f"{self.ingredient_a.name} ↔ {self.ingredient_b.name} : {self.get_status_display()}"