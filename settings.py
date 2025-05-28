import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

# Percorso base progetto
BASE_DIR = Path(__file__).resolve().parent.parent

# Chiave segreta (usa variabili ambiente in produzione)
SECRET_KEY = 'django-insecure-INSERT-YOUR-KEY-HERE'

# Debug attivo
DEBUG = True

# Hosts permessi
ALLOWED_HOSTS = ['*']

# App installate
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'real_estate',
    'pratiche',
    'django.contrib.sitemaps',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL principale
ROOT_URLCONF = 'fglegis_platform.urls'

# Template engine
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'fglegis_platform.wsgi.application'

# Database (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fglegis',
        'USER': 'fglegis_user',
        'PASSWORD': 'WtsuUyBvICG6QcWMWPQQWt0f6fLUUlo4',
        'HOST': 'dpg-d0rcunmmcj7s7385udt0-a.frankfurt-postgres.render.com',
        'PORT': '5432',
    }
}



# Validatori password
AUTH_PASSWORD_VALIDATORS = []

# Lingua e fuso orario
LANGUAGE_CODE = 'it-it'
TIME_ZONE = 'Europe/Rome'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirect login/logout
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/area-personale/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Trusted origins per CSRF (per Replit)
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',
    'https://*.replit.app',
]

# Email SMTP (Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@fglegis.com' 
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = 'FG LEGIS <noreply@fglegis.com>'
