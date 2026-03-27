from django.db import models
from django.utils import timezone
from apps.stock.models import Lot
from apps.sales.models import Customer
from django.contrib.auth.models import User

class Complaint(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Faible (Remarque, Packaging)'),
        ('medium', 'Moyenne (Odeur, Texture altérée)'),
        ('high', 'Critique (Réaction allergique, Santé)'),
    ]
    STATUS_CHOICES = [
        ('open', 'Ouvert (Nouvelle)'),
        ('investigating', 'En cours d\'investigation'),
        ('closed', 'Clôturé'),
    ]
    
    reference = models.CharField(max_length=50, unique=True, verbose_name="Référence")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='complaints', verbose_name="Client")
    lot = models.ForeignKey(Lot, on_delete=models.SET_NULL, null=True, related_name='complaints', verbose_name="Lot concerné")
    date_received = models.DateField(default=timezone.now, verbose_name="Date de déclaration")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='low', verbose_name="Gravité")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Statut")
    
    description = models.TextField(verbose_name="Description du problème (Symptômes)")
    action_taken = models.TextField(blank=True, verbose_name="Action correctrice (CAPA)")
    
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Technicien responsable")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Plainte (Vigilance)"
        verbose_name_plural = "Plaintes (Vigilance)"
        ordering = ['-date_received']
        
    def __str__(self):
        return f"{self.reference} - {self.customer.name}"
