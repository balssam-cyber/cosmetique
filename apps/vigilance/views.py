from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Complaint
from apps.stock.models import Lot
from apps.sales.models import Customer
import datetime

@login_required
def complaint_list(request):
    q = request.GET.get('q', '')
    stat = request.GET.get('status', '')
    complaints = Complaint.objects.all().select_related('customer', 'lot')
    
    if q:
        complaints = complaints.filter(Q(reference__icontains=q) | Q(customer__name__icontains=q) | Q(description__icontains=q))
    if stat:
        complaints = complaints.filter(status=stat)
        
    return render(request, 'vigilance/complaint_list.html', {
        'complaints': complaints, 
        'q': q, 
        'stat': stat,
        'status_choices': Complaint.STATUS_CHOICES
    })

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    return render(request, 'vigilance/complaint_detail.html', {'complaint': complaint})

@login_required
def complaint_form(request, pk=None):
    complaint = get_object_or_404(Complaint, pk=pk) if pk else None
    customers = Customer.objects.filter(is_active=True).order_by('name')
    # Les lots de produits finis uniquement
    lots = Lot.objects.filter(is_active=True).order_by('-production_date')
    
    if request.method == 'POST':
        data = request.POST
        c_id = data.get('customer')
        l_id = data.get('lot')
        
        c = get_object_or_404(Customer, pk=c_id) if c_id else None
        l = get_object_or_404(Lot, pk=l_id) if l_id else None
        
        if complaint:
            complaint.customer = c
            complaint.lot = l
            complaint.date_received = data['date_received']
            complaint.severity = data['severity']
            complaint.status = data['status']
            complaint.description = data['description']
            complaint.action_taken = data['action_taken']
            complaint.save()
            messages.success(request, "Incident mis à jour avec succès.")
        else:
            # Generate ref
            timestamp = datetime.datetime.now().strftime('%y%m%d%H%M')
            ref = f"VIG-{timestamp}"
            
            complaint = Complaint.objects.create(
                reference=ref,
                customer=c,
                lot=l,
                date_received=data['date_received'],
                severity=data['severity'],
                status=data['status'],
                description=data['description'],
                action_taken=data.get('action_taken', ''),
                recorded_by=request.user
            )
            messages.success(request, f"Incident {ref} déclaré avec succès.")
            
        return redirect('vigilance:complaint_detail', pk=complaint.pk)
        
    return render(request, 'vigilance/complaint_form.html', {
        'complaint': complaint,
        'customers': customers,
        'lots': lots,
        'severity_choices': Complaint.SEVERITY_CHOICES,
        'status_choices': Complaint.STATUS_CHOICES
    })
