import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv
import pymysql
pymysql.install_as_MySQLdb()
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'management_app.middleware.SessionTimeoutMiddleware',
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

# Media Dosyaları (Avatar, Proje Dosyaları)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SESSION_COOKIE_AGE = 1800  #Burayı 1209600 saniye yapan Ali'ye selamlarımı gönderiyorum, olsun denedin -hazal  #selamını aldım ama  keşke saniye olarak kalsaydı be
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  #sakın deneme
SESSION_COOKIE_SECURE = True

AUTH_USER_MODEL = 'management_app.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'



# E-Posta ayarlarını dış dosyadan çekiyoruz
try:
    from .email_settings import *
except ImportError:
    print("Uyarı: email_settings.py dosyası bulunamadı!")