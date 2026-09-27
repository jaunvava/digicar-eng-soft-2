"""
Django settings for digicar project - Sistema de Ordens de Serviço
Multi-tenant architecture with shared SQLite database.
"""

from pathlib import Path
import os

from .database import criar_configuracao_bancos

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-sfu_t@!q=kx%pmn$g5i^n$90e6-($8hjes!#c@(4_guf-4)+h8'

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# Trusted origins for CSRF - required when behind a reverse proxy (EasyPanel, Nginx, etc.)
_csrf_extra = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    'https://digios-digi-os.evxbqk.easypanel.host',
    'http://digios-digi-os.evxbqk.easypanel.host',
    'https://ap2-digi-os.evxbqk.easypanel.host',
    'http://ap2-digi-os.evxbqk.easypanel.host',
] + [o.strip() for o in _csrf_extra.split(',') if o.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dark_mode_switch',
    # Apps do sistema
    'core',
    'clientes',
    'produtos',
    'financeiro',
    'orcamentos',
    'ordens',
    'relatorios',
    'fornecedores',
    
    # Swagger / DRF
    'rest_framework',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.TenantMiddleware',
    'core.permissions.RolePermissionMiddleware',
]

ROOT_URLCONF = 'digicar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.empresa_context',
            ],
        },
    },
]

DARK_THEME = {
    'cdn': True,  # Use False se preferir servir os arquivos localmente
    'theme_selector': True,  # Mostra o seletor de tema
    'default': 'system',  # Tema padrão: 'light', 'dark' ou 'system'
    'cached': True,  # Cache das preferências
}

WSGI_APPLICATION = 'digicar.wsgi.application'

DATABASES = criar_configuracao_bancos(os.environ, BASE_DIR)

# DB_APP_ROUTES aceita pares app:alias separados por virgula (ex.: core:db2).
DATABASE_APP_ROUTES = {}
for _rota in os.environ.get('DB_APP_ROUTES', '').split(','):
    if _rota.strip():
        _app, _alias = _rota.strip().split(':', 1)
        if _alias not in DATABASES:
            raise ValueError(f"DB_APP_ROUTES referencia alias inexistente: {_alias}")
        DATABASE_APP_ROUTES[_app.strip()] = _alias.strip()
DATABASE_ROUTERS = ['digicar.routers.AppDatabaseRouter']

FILE_STORAGE = os.environ.get('FILE_STORAGE', 'local').lower()
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'digicar')
if FILE_STORAGE == 'mongo':
    STORAGES = {
        'default': {'BACKEND': 'storage.mongo_django.MongoGridFSStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-BR'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
