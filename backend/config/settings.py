"""
Django settings for AgriVigil AI — config du backend MVP.
"""
import dj_database_url
import copy
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

from django.template.context import BaseContext


def _patched_basecontext_copy(self):
    duplicate = object.__new__(self.__class__)
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate

BaseContext.__copy__ = _patched_basecontext_copy

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-CHANGE-ME-IN-PRODUCTION")

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")


INSTALLED_APPS = [
    'corsheaders',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',

    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",

    "core.apps.CoreConfig",
]

try:
    import whitenoise.middleware  # noqa: F401
except ImportError:  # pragma: no cover - dépendance optionnelle selon l’environnement
    WHITENOISE_MIDDLEWARE = []
else:
    WHITENOISE_MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    "django.middleware.security.SecurityMiddleware",
    *WHITENOISE_MIDDLEWARE,
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

ROOT_URLCONF = "config.urls"

CSRF_TRUSTED_ORIGINS = [
    "https://agrivigil-ai-production.up.railway.app",
    "https://agrivigil-ai.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

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

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------------
# Base de données
# ---------------------------------------------------------------------------
# SQLite par défaut pour lancer le MVP immédiatement sans installation.
# Pour la version finale (PostGIS + requêtes spatiales), remplacer par :
#
# DATABASES = {
#     "default": {
#         "ENGINE": "django.contrib.gis.db.backends.postgis",
#         "NAME": os.environ.get("DB_NAME", "agrivigil"),
#         "USER": os.environ.get("DB_USER", "postgres"),
#         "PASSWORD": os.environ.get("DB_PASSWORD", ""),
#         "HOST": os.environ.get("DB_HOST", "localhost"),
#         "PORT": os.environ.get("DB_PORT", "5432"),
#     }
# }

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True if os.environ.get('DATABASE_URL', '').startswith('postgres') else False
    )
}
AUTH_USER_MODEL = "core.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "fr"
LANGUAGES = [
    ("fr", "Français"),
]
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Django REST Framework + JWT
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------------------------------------------------------------
# CORS — le frontend Vite tourne par défaut sur localhost:5173
# ---------------------------------------------------------------------------

# Force en dur pour tester
CORS_ALLOWED_ORIGINS = [
    "https://agrivigil-ai.vercel.app",
    "http://localhost:5173",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

# ---------------------------------------------------------------------------
# Clés d'intégration futures (Gemini, Africa's Talking...) — voir README.md
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
AFRICAS_TALKING_API_KEY = os.environ.get("AFRICAS_TALKING_API_KEY", "")
AFRICAS_TALKING_USERNAME = os.environ.get("AFRICAS_TALKING_USERNAME", "")
HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN", "")
HUGGINGFACE_TTS_MODEL = os.environ.get("HUGGINGFACE_TTS_MODEL", "microsoft/speecht5_tts")

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY", ""),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET", ""),
}
cloudinary_enabled = bool(os.environ.get("CLOUDINARY_URL", "")) or all([
    CLOUDINARY_STORAGE["CLOUD_NAME"],
    CLOUDINARY_STORAGE["API_KEY"],
    CLOUDINARY_STORAGE["API_SECRET"],
])

if cloudinary_enabled:
    STORAGES["default"] = {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    }
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    MEDIA_URL = f"https://res.cloudinary.com/{CLOUDINARY_STORAGE['CLOUD_NAME']}/"
else:
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = "/media/"
    MEDIA_URL = '/media/'
    