from django.db import models
from django.contrib.auth.models import User


class DashboardRole(models.Model):
    ROLE_CHOICES = [
        ('ceo', 'PDG'),
        ('lab_manager', 'Responsable Laboratoire'),
        ('production_manager', 'Responsable Production'),
        ('warehouse_manager', 'Responsable Entrepôt'),
        ('viewer', 'Visiteur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_role')
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = "Rôle Dashboard"
        verbose_name_plural = "Rôles Dashboard"


class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('low_stock', 'Stock faible'),
        ('expiry', 'Expiration proche'),
        ('qc_fail', 'Échec CQ'),
        ('regulatory_deadline', 'Échéance réglementaire'),
        ('info', 'Information'),
    ]
    SEVERITY_CHOICES = [
        ('critical', 'Critique'),
        ('warning', 'Avertissement'),
        ('info', 'Information'),
    ]
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='warning')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"

    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ['-created_at']
