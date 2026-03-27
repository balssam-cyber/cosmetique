"""
Assistant IA intégré pour CosmoERP.
Utilise l'API Claude d'Anthropic avec contexte ERP injecté dynamiquement.

Configuration requise dans .env :
    ANTHROPIC_API_KEY=sk-ant-...

Usage :
    from apps.dashboard.ai_assistant import ask_ai_assistant
    response = ask_ai_assistant("Analysez les alertes stock actuelles")
"""
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def get_erp_context() -> str:
    """
    Collecte les métriques ERP en temps réel pour enrichir le contexte IA.
    Retourne une chaîne de texte décrivant l'état actuel du système.
    """
    try:
        from apps.stock.models import Material, Lot
        from apps.sales.models import SalesOrder
        from apps.production.models import ProductionBatch, QCCheck
        from apps.purchase.models import PurchaseOrder
        from datetime import timedelta

        today = timezone.now().date()
        low_stock_count = sum(1 for m in Material.objects.filter(is_active=True) if m.is_low_stock)
        lots_expiring = Lot.objects.filter(
            expiry_date__lte=today + timedelta(days=7),
            expiry_date__gte=today,
            is_active=True,
            current_quantity__gt=0
        ).count()
        pending_orders = SalesOrder.objects.filter(status='confirmed').count()
        active_batches = ProductionBatch.objects.filter(status='in_progress').count()
        failed_qc = QCCheck.objects.filter(result='fail').count()
        pending_purchase = PurchaseOrder.objects.filter(status__in=['sent', 'confirmed']).count()

        return f"""Tu es un expert ERP spécialisé en industrie cosmétique (Tunisie).
Tu analyses les données du système CosmoERP en temps réel.

État actuel du système (mis à jour : {today.strftime('%d/%m/%Y')}) :
- 🔴 Articles en stock critique (sous seuil d'alerte) : {low_stock_count}
- ⚠️ Lots expirant dans 7 jours : {lots_expiring}
- 📦 Commandes ventes en attente de livraison : {pending_orders}
- 🏭 Lots de production en cours : {active_batches}
- ❌ Contrôles qualité échoués : {failed_qc}
- 🛒 Bons de commande achat en cours : {pending_purchase}

Réponds toujours en français, de manière concise et actionnable.
Formule des recommandations concrètes basées sur les données fournies.
Si on te pose une question hors ERP cosmétique, rappelle poliment ton rôle."""

    except Exception as e:
        return f"""Tu es un expert ERP spécialisé en industrie cosmétique (Tunisie).
Réponds en français, de manière concise et actionnable.
(Note : données ERP temporairement indisponibles — {str(e)})"""


def ask_ai_assistant(user_question: str) -> str:
    """
    Pose une question à l'assistant Claude avec le contexte ERP injecté.
    Retourne le texte de la réponse.
    Lève une exception si ANTHROPIC_API_KEY n'est pas configurée.
    """
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        return (
            "⚙️ L'assistant IA n'est pas encore configuré.\n"
            "Ajoutez votre clé API Anthropic dans le fichier .env :\n"
            "ANTHROPIC_API_KEY=sk-ant-votre-clé"
        )

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=get_erp_context(),
            messages=[{"role": "user", "content": user_question}]
        )
        return message.content[0].text
    except ImportError:
        return "❌ Package 'anthropic' non installé. Exécutez : pip install anthropic"
    except Exception as e:
        return f"❌ Erreur IA : {str(e)}"


# ─── Vue Django ───────────────────────────────────────────────────────────────

@login_required
@require_POST
def ai_assistant_view(request):
    """
    POST /api/dashboard/ai/
    Body JSON : {"question": "..."}
    Réponse : {"response": "...", "question": "..."}
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Corps JSON invalide'}, status=400)

    question = data.get('question', '').strip()

    if not question:
        return JsonResponse({'error': 'La question ne peut pas être vide'}, status=400)

    if len(question) > 800:
        return JsonResponse({'error': 'Question trop longue (max 800 caractères)'}, status=400)

    response_text = ask_ai_assistant(question)
    return JsonResponse({
        'response': response_text,
        'question': question,
    })
