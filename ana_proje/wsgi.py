"""
WSGI config for ana_proje project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ana_proje.settings')

django.setup()  # Bu satır, Django'nun ayarlarını yükler ve uygulamanın düzgün çalışmasını sağlar

application = get_wsgi_application()


