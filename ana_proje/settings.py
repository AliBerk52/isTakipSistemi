import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını sisteme yükler
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!mf_ssqa4^whr&5819@4-)*_$35un!(&f9q^@ebeyko6w)z!0f'

DEBUG = True

ALLOWED_HOSTS = [
    '.vercel.app',     
    '127.0.0.1',
    'localhost',
    '*', # Her yerden erişime şimdilik izin veriyoruz
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'management_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ana_proje.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'front'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ana_proje.wsgi.application'

# ---> İŞTE DÜZELTİLMİŞ VE TEK OLAN VERİTABANI AYARIN <---
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'mysql://root:qfvMLttpvQhFpkFsfBQlXTHTlrUJlqzh@turntable.proxy.rlwy.net:24805/railway'),
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

STATICFILES_DIRS = [BASE_DIR / 'front']
STATIC_URL = '/static/'
# Vercel için bu satır şart!
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

SESSION_COOKIE_AGE = 1209600  # Varsayılan süreyi 14 güne (saniye cinsinden) çıkardık
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Kontrolü "Beni Hatırla" kutucuğuna bıraktık
SESSION_COOKIE_SECURE = False # Şimdilik local testler için False kalmalı

AUTH_USER_MODEL = 'management_app.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'



# E-Posta ayarlarını dış dosyadan çekiyoruz
try:
    from .email_settings import *
except ImportError:
    print("Uyarı: email_settings.py dosyası bulunamadı!")