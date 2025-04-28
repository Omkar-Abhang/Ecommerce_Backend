"""
ASGI config for Ecom_Backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import orders.rauting  # Import orders routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecom_Backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # for HTTP
    "websocket": AuthMiddlewareStack(
        URLRouter(
            orders.rauting.websocket_urlpatterns
        )
    ),
})