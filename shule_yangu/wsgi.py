"""WSGI config for Shule Yangu."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shule_yangu.settings')
application = get_wsgi_application()
