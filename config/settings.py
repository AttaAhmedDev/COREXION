"""
Django settings for config project.
"""

import os
from pathlib import Path

from .database import database_from_env

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(path, override=False):
    """Populate os.environ from a KEY=VALUE file."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        if override or key not in os.environ:
            os.environ[key] = value


load_env_file(BASE_DIR / ".env")
load_env_file(BASE_DIR / ".env.local", override=True)

ON_VERCEL = os.environ.get("VERCEL") == "1"

DEBUG = os.environ.get(
    "DJANGO_DEBUG",
    "0" if ON_VERCEL else "1",
) == "1"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG or ON_VERCEL:
        # Collectstatic imports settings during the Vercel build, before you
        # may have set env vars. Set DJANGO_SECRET_KEY in the project for a
        # stable production secret (admin sessions).
        SECRET_KEY = "django-insecure-set-DJANGO_SECRET_KEY-in-vercel-env"
    else:
        raise ValueError("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG=0")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]"
    ).split(",")
    if host.strip()
]
if ON_VERCEL:
    ALLOWED_HOSTS.extend([".vercel.app", ".now.sh"])
vercel_url = os.environ.get("VERCEL_URL", "").strip()
if vercel_url and vercel_url not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(vercel_url)

# CMS login path. The production value lives in .env and must not be committed.
# An empty DJANGO_ADMIN_PATH would mount the CMS at "" and 301 the homepage to "//".
_admin = os.environ.get("DJANGO_ADMIN_PATH", "cms").strip().strip("/").strip("\"'")
if not _admin:
    _admin = "cms"
ADMIN_URL = _admin + "/"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "content",
    # Must stay last: its signal handlers delete replaced/orphaned media files.
    "django_cleanup.apps.CleanupConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates", BASE_DIR],
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

DATABASES = {"default": database_from_env()}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Pages already request /assets/... so collectstatic publishes there on Vercel.
STATIC_URL = "/assets/"
STATICFILES_DIRS = [BASE_DIR / "assets"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

default_file_backend = (
    "content.storage.VercelBlobStorage"
    if os.environ.get("BLOB_READ_WRITE_TOKEN")
    else "django.core.files.storage.FileSystemStorage"
)
STORAGES = {
    "default": {"BACKEND": default_file_backend},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.environ.get("THROTTLE_ANON", "120/min"),
        "user": os.environ.get("THROTTLE_USER", "600/min"),
        "sections": os.environ.get("THROTTLE_SECTIONS", "120/min"),
    },
    "NUM_PROXIES": int(os.environ.get("NUM_PROXIES", "1" if ON_VERCEL else "0")),
}

CACHE_URL = os.environ.get("CACHE_URL") or os.environ.get("REDIS_URL", "")
if CACHE_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": CACHE_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "corexion-throttling",
        }
    }

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ["GET", "HEAD", "OPTIONS"]

csrf_origins = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
csrf_origins.extend(
    [
        "https://*.vercel.app",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
)
if vercel_url:
    csrf_origins.append("https://" + vercel_url.removeprefix("https://"))
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(csrf_origins))

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
