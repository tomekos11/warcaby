"""
ASGI config for warcaby project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from . import consumers 
from django.urls import path, re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '.settings')

asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": URLRouter(
        [
            path('ws/game', consumers.YourConsumer.as_asgi())
            # Dodaj więcej ścieżek WebSocket według potrzeb
        ]
    ),
    
})
