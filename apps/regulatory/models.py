from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.rnd.models import Product, Formulation


class RegulatoryRole(models.Model):
    ROLE_CHOICES = [
        ('regulatory_officer', 'Responsable Réglementaire'),
        ('qa_manager', 'Responsable QA'),
        ('viewer', 'Visiteur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='regulatory_role')
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = "Rôle Réglementaire"
        verbose_name_plural = "Rôles Réglementaires"


class ProductCompliance(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('in_review', 'En cours de révision'),
        ('compliant', 'Conforme'),
        ('non_compliant', 'Non conforme'),
        ('exempted', 'Exempté'),
    ]
    product = models.OneToOneField(Product, on_delete=models.CASCADE,
                                    related_name='compliance')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    eu_regulation = models.BooleanField(default=False, verbose_name="Rég. UE 1223/2009")
    responsible_person = models.CharField(max_length=200, blank=True,
                                          verbose_name="Personne responsable")
    responsible_person_address = models.TextField(blank=True, verbose_name="Adresse RP")
    last_review_date = models.DateField(null=True, blank=True, verbose_name="Dernière révision")
    next_review_date = models.DateField(null=True, blank=True, verbose_name="Prochaine révision")
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conformité - {self.product.name}"

    class Meta:
        verbose_name = "Conformité produit"
        verbose_name_plural = "Conformités produits"


class SafetyReport(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('under_review', 'En révision'),
        ('approved', 'Approuvé'),
        ('expired', 'Expiré'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='safety_reports')
    formulation = models.ForeignKey(Formulation, on_delete=models.PROTECT, null=True, blank=True)
    report_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro RSP")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    safety_assessor = models.CharField(max_length=200, verbose_name="Évaluateur sécurité")
    issue_date = models.DateField(null=True, blank=True, verbose_name="Date d'émission")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Date expiration")
    conclusion = models.TextField(blank=True, verbose_name="Conclusion")
    document = models.FileField(upload_to='safety_reports/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RSP {self.report_number} - {self.product.name}"

    class Meta:
        verbose_name = "Rapport de sécurité"
        verbose_name_plural = "Rapports de sécurité"
        ordering = ['-created_at']


class BPFDeclaration(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Non commencé'),
        ('in_progress', 'En cours'),
        ('completed', 'Complété'),
        ('submitted', 'Soumis'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bpf_declarations')
    declaration_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro BPF")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    facility_name = models.CharField(max_length=200, verbose_name="Nom de l'établissement")
    facility_address = models.TextField(verbose_name="Adresse")
    manufacturing_site = models.CharField(max_length=200, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BPF {self.declaration_number} - {self.product.name}"

    class Meta:
        verbose_name = "Déclaration BPF"
        verbose_name_plural = "Déclarations BPF"


class CPNPNotification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('submitted', 'Soumis'),
        ('accepted', 'Accepté'),
        ('rejected', 'Rejeté'),
        ('withdrawn', 'Retiré'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cpnp_notifications')
    notification_number = models.CharField(max_length=100, unique=True,
                                            verbose_name="Numéro CPNP")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submission_date = models.DateField(null=True, blank=True, verbose_name="Date soumission")
    acceptance_date = models.DateField(null=True, blank=True, verbose_name="Date acceptation")
    market = models.CharField(max_length=100, default='UE', verbose_name="Marché")
    product_category = models.CharField(max_length=200, blank=True)
    frame_formulation = models.BooleanField(default=False, verbose_name="Formulation cadre")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CPNP {self.notification_number} - {self.product.name}"

    class Meta:
        verbose_name = "Notification CPNP"
        verbose_name_plural = "Notifications CPNP"


class ProductLabel(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('approved', 'Approuvé'),
        ('obsolete', 'Obsolète'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='labels')
    version = models.CharField(max_length=20, verbose_name="Version")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    language = models.CharField(max_length=50, default='Français', verbose_name="Langue")
    ingredient_list = models.TextField(verbose_name="Liste INCI")
    claims = models.TextField(blank=True, verbose_name="Claims marketing")
    warnings = models.TextField(blank=True, verbose_name="Avertissements")
    net_quantity = models.CharField(max_length=50, blank=True, verbose_name="Contenu net")
    label_file = models.FileField(upload_to='labels/', null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='approved_labels')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='created_labels')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Étiquette {self.product.name} v{self.version} ({self.language})"

    class Meta:
        verbose_name = "Étiquette"
        verbose_name_plural = "Étiquettes"
        unique_together = ['product', 'version', 'language']
class RegulatoryDocument(models.Model):
    STATUS_CHOICES = [
        ('valid', 'Valide'),
        ('pending', 'En attente'),
        ('expired', 'Expiré'),
        ('rejected', 'Rejeté'),
    ]
    DOC_TYPE_CHOICES = [
        ('registration', 'Enregistrement'),
        ('certificate', 'Certificat'),
        ('license', 'Licence / Autorisation'),
        ('analysis', "Certificat d'analyse"),
        ('safety', 'Rapport de sécurité'),
        ('technical', 'Fiche technique'),
        ('label', 'Étiquette approuvée'),
        ('other', 'Autre'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='regulatory_documents'
    )
    # ── Pays libre ──
    country = models.CharField(
        max_length=100, verbose_name="Pays / Marché",
        help_text="Ex: Tunisie, UE, Maroc, UAE..."
    )
    # ── Autorité libre ──
    authority = models.CharField(
        max_length=200, blank=True, verbose_name="Autorité",
        help_text="Ex: INNORPI, Ministère de la Santé, SFDA..."
    )
    doc_type = models.CharField(
        max_length=20, choices=DOC_TYPE_CHOICES, default='certificate',
        verbose_name="Type de document"
    )
    # ── Référence libre ──
    reference = models.CharField(
        max_length=200, blank=True, verbose_name="Numéro / Référence"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending'
    )
    issue_date = models.DateField(
        null=True, blank=True, verbose_name="Date d'émission"
    )
    expiry_date = models.DateField(
        null=True, blank=True, verbose_name="Date d'expiration"
    )
    # ── Fichier PDF ou image ──
    document_file = models.FileField(
        upload_to='regulatory_docs/', null=True, blank=True,
        verbose_name="Fichier (PDF, image...)"
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.country} — {self.get_doc_type_display()} — {self.product.name}"

    @property
    def is_expiring_soon(self):
        if self.expiry_date:
            from datetime import timedelta
            return self.expiry_date <= timezone.now().date() + timedelta(days=30)
        return False

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    class Meta:
        verbose_name = "Document réglementaire"
        verbose_name_plural = "Documents réglementaires"
        ordering = ['-created_at']
