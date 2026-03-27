from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import (
    ProductCompliance, SafetyReport, BPFDeclaration,
    CPNPNotification, ProductLabel, RegulatoryDocument,
)
from apps.rnd.models import Product, Formulation


@login_required
def compliance_list(request):
    compliances = ProductCompliance.objects.select_related('product').all()
    return render(request, 'regulatory/compliance_list.html', {'compliances': compliances})


@login_required
def compliance_detail(request, pk):
    compliance = get_object_or_404(ProductCompliance, pk=pk)
    return render(request, 'regulatory/compliance_detail.html', {'compliance': compliance})


@login_required
def safety_report_list(request):
    reports = SafetyReport.objects.select_related('product').all()
    return render(request, 'regulatory/safety_report_list.html', {'reports': reports})


@login_required
def safety_report_detail(request, pk):
    report = get_object_or_404(SafetyReport, pk=pk)
    return render(request, 'regulatory/safety_report_detail.html', {'report': report})


@login_required
def safety_report_form(request, pk=None):
    report = get_object_or_404(SafetyReport, pk=pk) if pk else None
    products = Product.objects.all()
    formulations = Formulation.objects.filter(status='approved')
    if request.method == 'POST':
        data = request.POST
        if report:
            report.product_id = data['product']
            report.formulation_id = data.get('formulation') or None
            report.report_number = data['report_number']
            report.status = data['status']
            report.safety_assessor = data['safety_assessor']
            report.issue_date = data.get('issue_date') or None
            report.expiry_date = data.get('expiry_date') or None
            report.conclusion = data.get('conclusion', '')
            report.save()
            messages.success(request, "Rapport modifié.")
        else:
            report = SafetyReport.objects.create(
                product_id=data['product'],
                formulation_id=data.get('formulation') or None,
                report_number=data['report_number'],
                status=data.get('status', 'draft'),
                safety_assessor=data['safety_assessor'],
                issue_date=data.get('issue_date') or None,
                expiry_date=data.get('expiry_date') or None,
                conclusion=data.get('conclusion', ''),
                created_by=request.user
            )
            messages.success(request, "Rapport créé.")
        return redirect('regulatory:safety_report_detail', pk=report.pk)
    return render(request, 'regulatory/safety_report_form.html', {
        'report': report, 'products': products, 'formulations': formulations,
        'status_choices': SafetyReport.STATUS_CHOICES
    })


@login_required
def cpnp_list(request):
    notifications = CPNPNotification.objects.select_related('product').all()
    return render(request, 'regulatory/cpnp_list.html', {'notifications': notifications})


@login_required
def bpf_list(request):
    declarations = BPFDeclaration.objects.select_related('product').all()
    return render(request, 'regulatory/bpf_list.html', {'declarations': declarations})


@login_required
def label_list(request):
    labels = ProductLabel.objects.select_related('product').all()
    return render(request, 'regulatory/label_list.html', {'labels': labels})


# ── Documents réglementaires multi-pays ──

@login_required
def regulatory_doc_list(request):
    country = request.GET.get('country', '')
    doc_type = request.GET.get('doc_type', '')
    status = request.GET.get('status', '')

    docs = RegulatoryDocument.objects.select_related('product').all()
    if country:
        docs = docs.filter(country__icontains=country)
    if doc_type:
        docs = docs.filter(doc_type=doc_type)
    if status:
        docs = docs.filter(status=status)

    # ── Alertes expiration ──
    threshold = timezone.now().date() + timedelta(days=30)
    expiring_soon = RegulatoryDocument.objects.filter(
        expiry_date__lte=threshold,
        expiry_date__gte=timezone.now().date(),
        status='valid'
    ).count()

    return render(request, 'regulatory/regulatory_doc_list.html', {
        'docs': docs,
        'country': country,
        'doc_type': doc_type,
        'status': status,
        'expiring_soon': expiring_soon,
        'doc_type_choices': RegulatoryDocument.DOC_TYPE_CHOICES,
        'status_choices': RegulatoryDocument.STATUS_CHOICES,
    })


@login_required
def regulatory_doc_detail(request, pk):
    doc = get_object_or_404(RegulatoryDocument, pk=pk)
    return render(request, 'regulatory/regulatory_doc_detail.html', {'doc': doc})


@login_required
def regulatory_doc_form(request, pk=None, product_pk=None):
    doc = get_object_or_404(RegulatoryDocument, pk=pk) if pk else None
    products = Product.objects.all()
    presel_product = get_object_or_404(Product, pk=product_pk) if product_pk else None

    if request.method == 'POST':
        data = request.POST
        file = request.FILES.get('document_file')

        if doc:
            doc.product_id  = data['product']
            doc.country     = data['country']
            doc.authority   = data.get('authority', '')
            doc.doc_type    = data['doc_type']
            doc.reference   = data.get('reference', '')
            doc.status      = data.get('status', 'pending')
            doc.issue_date  = data.get('issue_date') or None
            doc.expiry_date = data.get('expiry_date') or None
            doc.notes       = data.get('notes', '')
            if file:
                doc.document_file = file
            doc.save()
            messages.success(request, "Document modifié.")
        else:
            doc = RegulatoryDocument.objects.create(
                product_id  = data['product'],
                country     = data['country'],
                authority   = data.get('authority', ''),
                doc_type    = data['doc_type'],
                reference   = data.get('reference', ''),
                status      = data.get('status', 'pending'),
                issue_date  = data.get('issue_date') or None,
                expiry_date = data.get('expiry_date') or None,
                notes       = data.get('notes', ''),
                document_file = file,
                created_by  = request.user,
            )
            messages.success(request, "Document ajouté.")
        return redirect('regulatory:doc_detail', pk=doc.pk)

    return render(request, 'regulatory/regulatory_doc_form.html', {
        'doc': doc,
        'products': products,
        'presel_product': presel_product,
        'doc_type_choices': RegulatoryDocument.DOC_TYPE_CHOICES,
        'status_choices': RegulatoryDocument.STATUS_CHOICES,
    })


@login_required
def regulatory_doc_delete(request, pk):
    doc = get_object_or_404(RegulatoryDocument, pk=pk)
    doc.delete()
    messages.success(request, "Document supprimé.")
    return redirect('regulatory:doc_list')
