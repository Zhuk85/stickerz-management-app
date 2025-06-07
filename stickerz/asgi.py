"""
ASGI config for stickerz project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickerz.settings')

# Инициализируем ASGI приложение
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Django's ASGI application для обработки HTTP запросов
    "http": django_asgi_app,
    
    # WebSocket обработчик с аутентификацией и проверкой хостов
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
