from django.utils import timezone
from datetime import timedelta
from apps.stock.models import Material, Lot
from django.conf import settings

def alerts_count(request):
    if not request.user.is_authenticated:
        return {'total_alerts': 0}
        
    expiry_threshold = timezone.now().date() + timedelta(days=getattr(settings, 'EXPIRY_ALERT_DAYS', 30))
    low_stock_count = sum(1 for m in Material.objects.filter(is_active=True) if m.is_low_stock)
    
    expiring_count = Lot.objects.filter(
        expiry_date__lte=expiry_threshold,
        is_active=True, current_quantity__gt=0
    ).count()
    
    quarantine_count = Lot.objects.filter(is_active=True, qc_status='quarantine').count()
    
    return {'total_alerts': low_stock_count + expiring_count + quarantine_count}
