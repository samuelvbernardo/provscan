from pathlib import Path
import os
import environ
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = env('SECRET_KEY')


DEBUG = env('DEBUG')


ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')


LOCAL_APPS = [
    'accounts',
    'core',
    'omr',
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'corsheaders',
] + LOCAL_APPS


REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',

    'PAGE_SIZE': 10,    
}


SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
}


SPECTACULAR_SETTINGS = {
    "TITLE": "ProvScan API",
    "DESCRIPTION": "API para leitura automática de gabaritos.",
    "VERSION": "1.0.0",
}


CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'scan_api.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


WSGI_APPLICATION = 'scan_api.wsgi.application'


DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "accounts.validators.StrongPasswordValidator",
    },
]


LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Recife'

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.User"