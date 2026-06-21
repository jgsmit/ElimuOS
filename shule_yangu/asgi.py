"""ASGI config for Shule Yangu."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shule_yangu.settings')
application = get_asgi_application()
