import logging
import os
import warnings
from datetime import timedelta
from pathlib import Path

import dj_database_url
import environ

BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env(DEBUG=(bool, False))

DEFAULT_ENV_FILE = BASE_DIR / ".envs" / "local" / ".env.local"
ENV_FILE = Path(os.environ.get("DJANGO_ENV_FILE", DEFAULT_ENV_FILE))

if ENV_FILE.exists():
    environ.Env.read_env(str(ENV_FILE), overwrite=True)
else:
    environ.Env.read_env(os.path.join(BASE_DIR, ".env"), overwrite=True)


SECRET_KEY = env("SECRET_KEY")


DEBUG = env("DEBUG")

_db_url = env("DATABASE_URL", default="")
if DEBUG and any(
    host in _db_url for host in ("supabase.com", "supabase.co", "amazonaws.com", "render.com")
):
    warnings.warn(
        "ATENÇÃO: DEBUG=True com uma URL de banco de dados de produção detectada. "
        "Isso pode expor informações sensíveis via páginas de erro do Django.",
        RuntimeWarning,
        stacklevel=1,
    )


ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


LOCAL_APPS = [
    "accounts",
    "core",
    "omr",
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "corsheaders",
] + LOCAL_APPS


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "provscan-cache",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.UserRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {
        "user": "60/minute",
        "scan": "30/minute",
    },
}


SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}


SPECTACULAR_SETTINGS = {
    "TITLE": "ProvScan API",
    "DESCRIPTION": "API para leitura automática de gabaritos.",
    "VERSION": "1.0.0",
}


CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "scan_api.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "scan_api.wsgi.application"


DATABASES = {"default": dj_database_url.config(default=env("DATABASE_URL"))}


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


LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Recife"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"


# ---------------------------------------------------------------------------
# Logging estruturado
# ---------------------------------------------------------------------------

try:
    import pythonjsonlogger  # noqa: F401

    _has_json_logger = True
except ImportError:
    _has_json_logger = False

_log_formatter = "json" if (not DEBUG and _has_json_logger) else "verbose"

_formatters: dict = {
    "verbose": {
        "format": "[{levelname}] {asctime} {name} {module}:{lineno} — {message}",
        "style": "{",
    },
}

if _has_json_logger:
    _formatters["json"] = {
        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d",
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": _formatters,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": _log_formatter,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "omr": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# ---------------------------------------------------------------------------
# Sentry — monitoramento de erros em produção (opcional via env var)
# ---------------------------------------------------------------------------

_sentry_dsn = env("SENTRY_DSN", default="")
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(
                level=logging.WARNING,
                event_level=logging.ERROR,
            ),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment="production" if not DEBUG else "development",
    )
