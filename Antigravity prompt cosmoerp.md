# 🚀 ANTIGRAVITY PROMPT — CosmoERP Full Deployment & Enhancement Plan

> **Contexte du projet :** CosmoERP est un système ERP Django complet pour une entreprise de fabrication cosmétique tunisienne. Il inclut 7 modules : R&D, Production, Stock, Achats, Ventes, Réglementaire, Dashboard + une API REST complète.

---

## 🎯 MISSION PRINCIPALE

Tu vas effectuer **3 grandes transformations** sur ce projet Django :

1. **Migration vers Supabase** (PostgreSQL managé) comme base de données principale
2. **Déploiement gratuit complet** sur Railway (backend) + Supabase (DB) + WhiteNoise (static)
3. **Améliorations fonctionnelles** : nouvelles features, UI modernisée, performance

---

## PARTIE 1 — MIGRATION SUPABASE (Base de données PostgreSQL)

### 1.1 — Configuration `settings.py`

Remplace la configuration SQLite actuelle par Supabase PostgreSQL :

```python
# cosmo_erp/settings.py

import os
from decouple import config

# REMPLACE la config DB existante par :
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('SUPABASE_DB_NAME', default='postgres'),
        'USER': config('SUPABASE_DB_USER', default='postgres'),
        'PASSWORD': config('SUPABASE_DB_PASSWORD'),
        'HOST': config('SUPABASE_DB_HOST'),  # db.xxxxxxxxxxxx.supabase.co
        'PORT': config('SUPABASE_DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 60,
    }
}
```

### 1.2 — Fichier `.env` (modèle complet)

Crée/remplace le fichier `.env` avec ces variables :

```env
# Django
SECRET_KEY=your-super-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app,localhost,127.0.0.1

# Supabase PostgreSQL
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-supabase-db-password
SUPABASE_DB_HOST=db.xxxxxxxxxxxxxxxxxx.supabase.co
SUPABASE_DB_PORT=5432

# Supabase API (optionnel - pour fonctionnalités avancées)
SUPABASE_URL=https://xxxxxxxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Email (Gmail SMTP gratuit)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS (si API consommée par frontend externe)
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### 1.3 — Mise à jour `requirements.txt`

Remplace le fichier `requirements.txt` complet par :

```txt
# Framework
Django>=4.2,<5.0
djangorestframework>=3.14
django-filter>=23.0

# Database
psycopg2-binary>=2.9.9

# Configuration
python-decouple>=3.8

# Images
Pillow>=10.0

# Static files (WhiteNoise pour Railway)
whitenoise>=6.6.0

# CORS
django-cors-headers>=4.3.0

# Supabase Python SDK (optionnel mais recommandé)
supabase>=2.4.0

# Caching & Performance
django-redis>=5.4.0

# Monitoring
sentry-sdk>=1.39.0

# Export Excel/PDF (nouvelles features)
openpyxl>=3.1.2
reportlab>=4.1.0
```

### 1.4 — Configuration WhiteNoise pour les fichiers statiques

Dans `settings.py`, ajoute/modifie :

```python
# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Dans MIDDLEWARE, ajoute APRÈS SecurityMiddleware :
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← AJOUTER ICI
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ← AJOUTER (CORS)
    # ... reste du middleware
]

# INSTALLED_APPS — ajouter :
INSTALLED_APPS = [
    # ... apps existantes ...
    'corsheaders',
    'whitenoise.runserver_nostatic',
]

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')

# Security pour production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

---

## PARTIE 2 — DÉPLOIEMENT RAILWAY (Gratuit, 500h/mois)

### 2.1 — Fichier `Procfile` (CRÉER à la racine)

```
web: gunicorn cosmo_erp.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
release: python manage.py migrate --no-input && python manage.py collectstatic --no-input
```

### 2.2 — Fichier `railway.toml` (CRÉER à la racine)

```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt && python manage.py collectstatic --no-input"

[deploy]
startCommand = "gunicorn cosmo_erp.wsgi:application --bind 0.0.0.0:$PORT --workers 2"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[environments.production.variables]
DJANGO_SETTINGS_MODULE = "cosmo_erp.settings"
PYTHONUNBUFFERED = "1"
```

### 2.3 — Fichier `runtime.txt` (CRÉER à la racine)

```
python-3.11.7
```

### 2.4 — Mise à jour `requirements.txt` — ajouter gunicorn

```txt
gunicorn>=21.2.0
```

### 2.5 — Instructions de déploiement Railway (étape par étape)

```
ÉTAPES DE DÉPLOIEMENT :

1. Créer compte Railway.app (gratuit, 500h/mois, aucune CB requise)

2. Créer compte Supabase.com (gratuit, 2 projets, 500MB DB)

3. Sur Supabase :
   - New Project → Nom: cosmo-erp → Région: EU West
   - Copier: Host, Password depuis Settings > Database

4. Sur Railway :
   - New Project → Deploy from GitHub Repo
   - Lier le repo GitHub du projet
   - Add Variables → coller toutes les variables du .env
   - Le déploiement est automatique à chaque git push

5. Domaine gratuit Railway :
   - Settings > Networking > Generate Domain
   - Format: your-app.up.railway.app

6. Initialiser la DB (1 seule fois) :
   - Railway Console → python manage.py migrate
   - Railway Console → python manage.py create_sample_data
```

---

## PARTIE 3 — AMÉLIORATIONS FONCTIONNELLES REMARQUABLES

### 3.1 — 🔔 Système de Notifications en Temps Réel (Django Channels + Supabase Realtime)

**Fichier : `apps/dashboard/consumers.py`** (CRÉER)

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.group_name = f"alerts_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_alert(self, event):
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'title': event['title'],
            'message': event['message'],
            'severity': event['severity'],  # 'danger', 'warning', 'info'
            'module': event['module'],
        }))
```

**Utilisation dans les signals :**

```python
# apps/stock/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=StockLot)
def check_stock_low(sender, instance, **kwargs):
    if instance.quantite <= instance.material.seuil_alerte:
        channel_layer = get_channel_layer()
        # Notifier tous les responsables entrepôt
        for user in get_warehouse_users():
            async_to_sync(channel_layer.group_send)(
                f"alerts_{user.id}",
                {
                    "type": "send_alert",
                    "title": "⚠️ Stock Critique",
                    "message": f"{instance.material.nom} : {instance.quantite} {instance.material.unite} restants",
                    "severity": "danger",
                    "module": "stock",
                }
            )
```

---

### 3.2 — 📊 Export Excel/PDF des Rapports

**Fichier : `apps/sales/views.py`** (AJOUTER ces vues)

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


class SalesReportExcelView(LoginRequiredMixin, View):
    """Export rapport ventes en Excel professionnel"""
    
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Rapport Ventes"
        
        # En-tête stylisé
        header_font = Font(bold=True, color="FFFFFF", size=12)
        header_fill = PatternFill("solid", fgColor="1B4F72")  # Bleu marine
        
        headers = ['Date', 'Client', 'Produit', 'Quantité', 'Prix Unitaire', 'Total TTC', 'Statut']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
        
        # Données
        orders = SalesOrder.objects.select_related('client').prefetch_related('lines__product')
        for row_idx, order in enumerate(orders, 2):
            for line in order.lines.all():
                ws.append([
                    order.date.strftime('%d/%m/%Y'),
                    order.client.nom,
                    line.product.nom,
                    line.quantite,
                    float(line.prix_unitaire),
                    float(line.total_ttc),
                    order.get_statut_display(),
                ])
        
        # Auto-largeur colonnes
        for column in ws.columns:
            max_length = max(len(str(cell.value or '')) for cell in column)
            ws.column_dimensions[column[0].column_letter].width = min(max_length + 2, 40)
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="rapport_ventes_cosmo.xlsx"'
        wb.save(response)
        return response


class ProductionBatchPDFView(LoginRequiredMixin, View):
    """Fiche de lot de production en PDF"""
    
    def get(self, request, pk, *args, **kwargs):
        batch = get_object_or_404(ProductionBatch, pk=pk)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="lot_{batch.numero}.pdf"'
        
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        
        # Logo / En-tête
        p.setFillColorRGB(0.1, 0.3, 0.6)
        p.rect(0, height - 80, width, 80, fill=True)
        p.setFillColorRGB(1, 1, 1)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(40, height - 45, "CosmoERP — Fiche de Lot")
        
        # Informations lot
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(40, height - 120, f"Lot N° : {batch.numero}")
        p.setFont("Helvetica", 12)
        p.drawString(40, height - 145, f"Produit : {batch.product.nom}")
        p.drawString(40, height - 165, f"Quantité : {batch.quantite} {batch.product.unite}")
        p.drawString(40, height - 185, f"Date fabrication : {batch.date_fabrication.strftime('%d/%m/%Y')}")
        p.drawString(40, height - 205, f"Date expiration : {batch.date_expiration.strftime('%d/%m/%Y')}")
        p.drawString(40, height - 225, f"Statut : {batch.get_statut_display()}")
        
        p.showPage()
        p.save()
        return response
```

**Ajouter aux URLs :**

```python
# apps/sales/urls.py
path('reports/excel/', SalesReportExcelView.as_view(), name='sales-report-excel'),

# apps/production/urls.py  
path('batches/<int:pk>/pdf/', ProductionBatchPDFView.as_view(), name='batch-pdf'),
```

---

### 3.3 — 🤖 Assistant IA Intégré (Analyse des données ERP)

**Fichier : `apps/dashboard/ai_assistant.py`** (CRÉER)

```python
"""
Assistant IA pour analyses ERP — utilise l'API Claude d'Anthropic
Nécessite : pip install anthropic
Variable env : ANTHROPIC_API_KEY=sk-ant-...
"""
import anthropic
from django.conf import settings
from apps.stock.models import StockLot, StockMaterial
from apps.sales.models import SalesOrder
from apps.production.models import ProductionBatch


def get_erp_context():
    """Collecte les métriques ERP actuelles pour le contexte IA"""
    stock_alerts = StockLot.objects.filter(
        quantite__lte=models.F('material__seuil_alerte')
    ).count()
    
    pending_orders = SalesOrder.objects.filter(statut='pending').count()
    active_batches = ProductionBatch.objects.filter(statut='in_progress').count()
    
    return f"""
    Contexte ERP CosmoERP (cosmétiques):
    - Alertes stock actives: {stock_alerts}
    - Commandes ventes en attente: {pending_orders}
    - Lots de production en cours: {active_batches}
    Tu es un expert ERP spécialisé en industrie cosmétique. 
    Réponds en français, de manière concise et actionnable.
    """


def ask_ai_assistant(user_question: str) -> str:
    """Pose une question à l'assistant IA avec contexte ERP"""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=get_erp_context(),
        messages=[{"role": "user", "content": user_question}]
    )
    return message.content[0].text


# Vue Django pour l'assistant
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json

@login_required
@require_POST
def ai_assistant_view(request):
    data = json.loads(request.body)
    question = data.get('question', '').strip()
    
    if not question:
        return JsonResponse({'error': 'Question vide'}, status=400)
    
    if len(question) > 500:
        return JsonResponse({'error': 'Question trop longue (max 500 chars)'}, status=400)
    
    try:
        response = ask_ai_assistant(question)
        return JsonResponse({'response': response})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

**Ajouter en .env :**
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

### 3.4 — 📈 Dashboard Analytics Avancé (KPIs visuels)

**Fichier : `apps/dashboard/analytics.py`** (CRÉER)

```python
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta


def get_kpi_summary():
    """Retourne tous les KPIs pour le dashboard"""
    today = timezone.now().date()
    month_start = today.replace(day=1)
    last_month = (month_start - timedelta(days=1)).replace(day=1)
    
    # CA mensuel vs mois précédent
    ca_this_month = SalesOrder.objects.filter(
        date__gte=month_start, statut='completed'
    ).aggregate(total=Sum('total_ttc'))['total'] or 0
    
    ca_last_month = SalesOrder.objects.filter(
        date__gte=last_month, date__lt=month_start, statut='completed'
    ).aggregate(total=Sum('total_ttc'))['total'] or 1
    
    ca_growth = round(((ca_this_month - ca_last_month) / ca_last_month) * 100, 1)
    
    # Taux de conformité qualité
    total_qc = QCCheck.objects.filter(date__gte=month_start).count()
    passed_qc = QCCheck.objects.filter(date__gte=month_start, resultat='pass').count()
    qc_rate = round((passed_qc / total_qc * 100) if total_qc > 0 else 100, 1)
    
    # Taux de rotation des stocks
    stock_value = StockLot.objects.aggregate(
        total=Sum(F('quantite') * F('material__prix_unitaire'))
    )['total'] or 0
    
    # Top 5 produits vendus
    top_products = SalesOrderLine.objects.filter(
        order__date__gte=month_start
    ).values('product__nom').annotate(
        total_qty=Sum('quantite'),
        total_revenue=Sum('total_ttc')
    ).order_by('-total_revenue')[:5]
    
    # Évolution CA 6 derniers mois
    monthly_trend = SalesOrder.objects.filter(
        date__gte=today - timedelta(days=180),
        statut='completed'
    ).annotate(month=TruncMonth('date')).values('month').annotate(
        ca=Sum('total_ttc'),
        nb_commandes=Count('id')
    ).order_by('month')
    
    return {
        'ca_this_month': float(ca_this_month),
        'ca_growth_percent': ca_growth,
        'qc_rate': qc_rate,
        'stock_value': float(stock_value),
        'top_products': list(top_products),
        'monthly_trend': [
            {
                'month': item['month'].strftime('%b %Y'),
                'ca': float(item['ca']),
                'nb_commandes': item['nb_commandes']
            }
            for item in monthly_trend
        ],
        'alerts': {
            'stock_critique': StockLot.objects.filter(
                quantite__lte=F('material__seuil_alerte')
            ).count(),
            'lots_expirant_7j': StockLot.objects.filter(
                date_expiration__lte=today + timedelta(days=7),
                date_expiration__gte=today
            ).count(),
            'commandes_retard': SalesOrder.objects.filter(
                statut='confirmed',
                date_livraison_prevue__lt=today
            ).count(),
        }
    }
```

**Vue API pour le dashboard :**

```python
# apps/dashboard/views.py — AJOUTER
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .analytics import get_kpi_summary

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kpi_dashboard(request):
    data = get_kpi_summary()
    return Response(data)
```

---

### 3.5 — 🔍 Recherche Globale (Global Search)

**Fichier : `apps/dashboard/search.py`** (CRÉER)

```python
from django.db.models import Q
from apps.rnd.models import Product, Ingredient
from apps.production.models import ProductionBatch
from apps.stock.models import StockMaterial, StockLot
from apps.purchase.models import PurchaseOrder, Supplier
from apps.sales.models import SalesOrder, Customer


def global_search(query: str, user=None) -> dict:
    """Recherche unifiée dans tous les modules ERP"""
    if len(query) < 2:
        return {}
    
    results = {}
    
    # Produits R&D
    products = Product.objects.filter(
        Q(nom__icontains=query) | Q(code__icontains=query) | Q(description__icontains=query)
    )[:5]
    if products:
        results['products'] = [{'id': p.id, 'nom': p.nom, 'code': p.code, 'url': f'/rnd/products/{p.id}/'} for p in products]
    
    # Lots de production
    batches = ProductionBatch.objects.filter(
        Q(numero__icontains=query) | Q(product__nom__icontains=query)
    ).select_related('product')[:5]
    if batches:
        results['batches'] = [{'id': b.id, 'numero': b.numero, 'product': b.product.nom, 'url': f'/production/batches/{b.id}/'} for b in batches]
    
    # Clients
    customers = Customer.objects.filter(
        Q(nom__icontains=query) | Q(email__icontains=query) | Q(code_client__icontains=query)
    )[:5]
    if customers:
        results['customers'] = [{'id': c.id, 'nom': c.nom, 'email': c.email, 'url': f'/sales/customers/{c.id}/'} for c in customers]
    
    # Fournisseurs
    suppliers = Supplier.objects.filter(
        Q(nom__icontains=query) | Q(email__icontains=query)
    )[:5]
    if suppliers:
        results['suppliers'] = [{'id': s.id, 'nom': s.nom, 'url': f'/purchase/suppliers/{s.id}/'} for s in suppliers]
    
    return results


# Vue API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_view(request):
    query = request.GET.get('q', '').strip()
    results = global_search(query, request.user)
    return Response({'query': query, 'results': results, 'total': sum(len(v) for v in results.values())})
```

---

### 3.6 — 📅 Planificateur de Production (Nouveau module)

**Fichier : `apps/production/scheduler.py`** (CRÉER)

```python
"""
Planificateur intelligent de production :
- Vérifie la disponibilité des matières premières avant de planifier
- Calcule la capacité de production réelle
- Génère un planning optimisé (FIFO)
- Envoie des alertes si stock insuffisant
"""
from django.db.models import Sum, F
from apps.stock.models import StockLot
from apps.production.models import ProductionBatch, BOMLine  # Bill of Materials


def check_production_feasibility(product_id: int, quantity: float) -> dict:
    """
    Vérifie si on peut produire `quantity` unités du produit.
    Retourne les matières disponibles/manquantes.
    """
    bom_lines = BOMLine.objects.filter(
        formulation__product_id=product_id,
        formulation__is_active=True
    ).select_related('ingredient')
    
    feasibility = {
        'can_produce': True,
        'missing_materials': [],
        'available_materials': [],
    }
    
    for line in bom_lines:
        required_qty = line.quantite * quantity
        available = StockLot.objects.filter(
            material__ingredient=line.ingredient,
            date_expiration__gt=timezone.now().date()
        ).aggregate(total=Sum('quantite'))['total'] or 0
        
        if available < required_qty:
            feasibility['can_produce'] = False
            feasibility['missing_materials'].append({
                'ingredient': line.ingredient.nom,
                'required': required_qty,
                'available': available,
                'shortage': required_qty - available,
                'unit': line.ingredient.unite,
            })
        else:
            feasibility['available_materials'].append({
                'ingredient': line.ingredient.nom,
                'required': required_qty,
                'available': available,
            })
    
    return feasibility


def auto_deduct_stock_fifo(batch: 'ProductionBatch') -> list:
    """
    Déduit automatiquement les stocks (FIFO par date d'expiration).
    Retourne la liste des lots consommés.
    """
    consumed = []
    bom_lines = BOMLine.objects.filter(
        formulation__product=batch.product,
        formulation__is_active=True
    )
    
    for line in bom_lines:
        needed = line.quantite * batch.quantite
        lots = StockLot.objects.filter(
            material__ingredient=line.ingredient,
            date_expiration__gt=timezone.now().date(),
            quantite__gt=0
        ).order_by('date_expiration')  # FIFO = expiration la plus proche en premier
        
        for lot in lots:
            if needed <= 0:
                break
            consumed_from_lot = min(lot.quantite, needed)
            lot.quantite -= consumed_from_lot
            lot.save()
            needed -= consumed_from_lot
            consumed.append({
                'lot': lot.numero,
                'ingredient': line.ingredient.nom,
                'consumed': consumed_from_lot,
            })
    
    return consumed
```

---

### 3.7 — 🌐 Interface Multilingue (FR/AR/EN)

**Fichier : `cosmo_erp/settings.py`** — Activer i18n

```python
# Dans settings.py
USE_I18N = True
USE_L10N = True

LANGUAGE_CODE = 'fr'

LANGUAGES = [
    ('fr', 'Français'),
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

MIDDLEWARE += ['django.middleware.locale.LocaleMiddleware']
```

**Créer les fichiers de traduction :**

```bash
# Commandes à exécuter :
django-admin makemessages -l ar
django-admin makemessages -l en
# Editer locale/ar/LC_MESSAGES/django.po
# Puis compiler :
django-admin compilemessages
```

---

### 3.8 — 🔐 Authentification JWT pour l'API REST

**Dans `requirements.txt` — ajouter :**

```txt
djangorestframework-simplejwt>=5.3.0
```

**Dans `settings.py` :**

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}
```

**Dans `urls.py` — ajouter :**

```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns += [
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

---

## PARTIE 4 — OPTIMISATIONS PERFORMANCES

### 4.1 — Cache Redis (via Upstash, gratuit)

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config('REDIS_URL', default='redis://localhost:6379/0'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "cosmoerp"
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

**Utilisation dans les vues critiques :**

```python
from django.core.cache import cache

def get_dashboard_summary(request):
    cache_key = f"dashboard_summary_{request.user.id}"
    data = cache.get(cache_key)
    
    if not data:
        data = get_kpi_summary()  # Calcul coûteux
        cache.set(cache_key, data, timeout=300)  # Cache 5 minutes
    
    return JsonResponse(data)
```

### 4.2 — Optimisation des Requêtes Django ORM

```python
# ❌ AVANT (N+1 queries) :
orders = SalesOrder.objects.all()
for order in orders:
    print(order.client.nom)  # 1 query par order !

# ✅ APRÈS (1 seule query) :
orders = SalesOrder.objects.select_related('client').prefetch_related(
    'lines__product'
).filter(statut='pending').order_by('-date')[:50]
```

---

## RÉCAPITULATIF FINAL — STACK TECHNOLOGIQUE GRATUITE

| Composant | Service | Coût |
|-----------|---------|------|
| Backend Django | Railway.app | Gratuit (500h/mois) |
| Base de données | Supabase PostgreSQL | Gratuit (500MB) |
| Fichiers statiques | WhiteNoise (intégré) | Gratuit |
| Cache | Upstash Redis | Gratuit (10K req/jour) |
| Monitoring | Sentry | Gratuit (5K events/mois) |
| Email | Gmail SMTP | Gratuit |
| Domaine | Railway subdomain | Gratuit |
| **TOTAL** | | **0 DT/mois** |

---

## ORDRE D'EXÉCUTION RECOMMANDÉ

```
1. Créer projet Supabase → copier credentials DB
2. Mettre à jour requirements.txt
3. Mettre à jour settings.py (DB + WhiteNoise + CORS + Security)
4. Créer Procfile + railway.toml + runtime.txt
5. Créer/mettre à jour .env
6. Tester en local : python manage.py migrate
7. Push sur GitHub
8. Créer projet Railway → lier repo → ajouter variables
9. Déploiement automatique ✅
10. Appliquer les améliorations par ordre de priorité
```

---

*Prompt créé pour Antigravity — Projet CosmoERP Django | Mars 2026*
