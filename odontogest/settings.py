"""
Configuracion principal de OdontoGest.
Multi-tenant por schema (django-tenants) + PostgreSQL + Render.
"""

from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Seguridad basica
# ---------------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-cambiar-en-produccion')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Render coloca la app detras de un proxy, esto es necesario para HTTPS correcto
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------------------------------------------------------------------------
# Apps: separadas entre "publicas" (schema compartido) y "tenant"
# (se replican dentro de cada consultorio)
# ---------------------------------------------------------------------------
SHARED_APPS = [
    'django_tenants',           # debe ir primero
    'core',                     # Consultorio (tenant), Plan, Suscripcion, Pago, Cupon

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cuentas',                  # Usuario personalizado (compartido: login unico)
    'landing',                  # Pagina publica de mercadeo/registro
]

TENANT_APPS = [
    'django.contrib.contenttypes',

    'clientes',                 # Pacientes, citas, cotizaciones, odontograma, etc.
]

INSTALLED_APPS = list(dict.fromkeys(SHARED_APPS + TENANT_APPS))

TENANT_MODEL = "core.Consultorio"
TENANT_DOMAIN_MODEL = "core.Dominio"

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',  # debe ir primero
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'odontogest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.marca_consultorio',
            ],
        },
    },
]

WSGI_APPLICATION = 'odontogest.wsgi.application'

# ---------------------------------------------------------------------------
# Base de datos: PostgreSQL con router de django-tenants
# ---------------------------------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgres://postgres:postgres@localhost:5432/odontogest'),
        engine='django_tenants.postgresql_backend',
    )
}
DATABASES['default']['ENGINE'] = 'django_tenants.postgresql_backend'

DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)

# ---------------------------------------------------------------------------
# Usuario personalizado
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = 'cuentas.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'cuentas:login'
LOGIN_REDIRECT_URL = 'clientes:dashboard'
LOGOUT_REDIRECT_URL = 'landing:home'

# ---------------------------------------------------------------------------
# Internacionalizacion - Venezuela
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Archivos estaticos y media
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Si se configura almacenamiento externo (Cloudflare R2 / S3), se activa
# automaticamente cuando estas variables existen.
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='')

if AWS_ACCESS_KEY_ID and AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Paleta de colores de la marca (usada en templates via context processor)
# Azul clarito sutil + gris + fondo blanco
# ---------------------------------------------------------------------------
MARCA_APP_NOMBRE = config('MARCA_APP_NOMBRE', default='OdontoGest')
MARCA_COLOR_FONDO = '#FFFFFF'
MARCA_COLOR_AZUL_SUAVE = '#EAF2FA'
MARCA_COLOR_AZUL_ACENTO = '#5B9BD5'
MARCA_COLOR_GRIS_TEXTO = '#6B7280'
MARCA_COLOR_GRIS_CLARO = '#F3F4F6'
