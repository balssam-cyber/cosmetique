"""
WebSocket Consumer pour les notifications en temps réel — CosmoERP.
Utilise Django Channels (ASGI).

Pour activer :
1. pip install channels channels-redis
2. Configurer CHANNEL_LAYERS dans settings.py (voir ci-dessous)
3. Créer cosmo_erp/asgi.py

Configuration settings.py à ajouter :
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [config('REDIS_URL', default='redis://localhost:6379')]},
        }
    }
"""
import json

try:
    from channels.generic.websocket import AsyncWebsocketConsumer
    CHANNELS_AVAILABLE = True
except ImportError:
    CHANNELS_AVAILABLE = False
    # Fallback si channels n'est pas installé
    class AsyncWebsocketConsumer:
        pass


class AlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer pour les alertes ERP en temps réel.
    Chaque utilisateur reçoit ses alertes dans un groupe dédié.
    """

    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f"alerts_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Envoyer un message de bienvenue
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': f'Connecté aux alertes temps réel, {self.user.first_name or self.user.username}',
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Reçoit des messages du client (ping/pong, ack)."""
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except (json.JSONDecodeError, KeyError):
            pass

    async def send_alert(self, event):
        """Envoie une alerte au client WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'title': event.get('title', ''),
            'message': event.get('message', ''),
            'severity': event.get('severity', 'info'),   # danger | warning | info | success
            'module': event.get('module', ''),
            'url': event.get('url', ''),
        }))


# ─── Helpers pour envoyer des alertes depuis n'importe où ────────────────────

def send_alert_to_user(user_id: int, title: str, message: str,
                        severity: str = 'info', module: str = '', url: str = ''):
    """
    Envoie une alerte WebSocket à un utilisateur spécifique.
    Appel synchrone (utilisable dans les signals Django).

    Exemple :
        send_alert_to_user(
            user_id=3,
            title="⚠️ Stock Critique",
            message="Aspirine : 2 kg restants",
            severity="danger",
            module="stock",
            url="/stock/materials/12/"
        )
    """
    if not CHANNELS_AVAILABLE:
        return  # Silently skip if channels not installed

    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        async_to_sync(channel_layer.group_send)(
            f"alerts_{user_id}",
            {
                "type": "send_alert",
                "title": title,
                "message": message,
                "severity": severity,
                "module": module,
                "url": url,
            }
        )
    except Exception:
        pass  # Ne jamais bloquer le flux principal pour une notification


def send_alert_to_group(group_name: str, title: str, message: str,
                         severity: str = 'info', module: str = '', url: str = ''):
    """
    Envoie une alerte à un groupe (ex: 'warehouse_managers').
    """
    if not CHANNELS_AVAILABLE:
        return

    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_alert",
                "title": title,
                "message": message,
                "severity": severity,
                "module": module,
                "url": url,
            }
        )
    except Exception:
        pass
