"""
Django settings for config project.
"""

import os
from pathlib import Path
from urllib.parse import unquote, urlparse

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(path):
    """Populate os.environ from a KEY=VALUE file, without overriding variables
    that are already set in the real environment."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env_file(BASE_DIR / ".env")

if "DJANGO_DEBUG" in os.environ:
    DEBUG = os.environ.get("DJANGO_DEBUG") == "1"
else:
    DEBUG = not bool(os.environ.get("RAILWAY_ENVIRONMENT"))

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-dev-only-change-me"
    else:
        raise ValueError("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG=0")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]"
    ).split(",")
    if host.strip()
]
for host in (
    os.environ.get("RAILWAY_PUBLIC_DOMAIN", ""),
    os.environ.get("RAILWAY_PRIVATE_DOMAIN", ""),
):
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)
if os.environ.get("RAILWAY_ENVIRONMENT"):
    ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
_public_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
if _public_domain:
    _origin = f"https://{_public_domain}"
    if _origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_origin)

if os.environ.get("RAILWAY_ENVIRONMENT"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

# CMS login path. The production value lives in .env and must not be committed.
_admin = os.environ.get("DJANGO_ADMIN_PATH", "cms").strip().strip("/")
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
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        # The pages in pages/ (and index.html) are the templates, so the project
        # root is the search path. Keeping it as the only entry means no other
        # directory can shadow a page with a same-named file.
        "DIRS": [BASE_DIR],
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

_database_url = os.environ.get("DATABASE_URL", "")
if _database_url:
    _db = urlparse(_database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote((_db.path or "/").lstrip("/")),
            "USER": unquote(_db.username or ""),
            "PASSWORD": unquote(_db.password or ""),
            "HOST": _db.hostname or "",
            "PORT": str(_db.port or "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", os.environ.get("PGDATABASE", "corexion")),
            "USER": os.environ.get("POSTGRES_USER", os.environ.get("PGUSER", "postgres")),
            "PASSWORD": os.environ.get(
                "POSTGRES_PASSWORD", os.environ.get("PGPASSWORD", "")
            ),
            "HOST": os.environ.get("POSTGRES_HOST", os.environ.get("PGHOST", "localhost")),
            "PORT": os.environ.get("POSTGRES_PORT", os.environ.get("PGPORT", "5432")),
        }
    }

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

# Public origin used in canonical URLs, Open Graph tags, robots.txt and sitemap.xml.
SITE_URL = os.environ.get("PUBLIC_SITE_URL", "https://corexion.uk").rstrip("/")

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "assets"]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
_volume = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", "")
MEDIA_ROOT = Path(_volume) if _volume else BASE_DIR / "media"

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
        # Every page view costs one request, so allow comfortable browsing while
        # still stopping scrapers and accidental request loops.
        "anon": os.environ.get("THROTTLE_ANON", "120/min"),
        "user": os.environ.get("THROTTLE_USER", "600/min"),
        "sections": os.environ.get("THROTTLE_SECTIONS", "120/min"),
    },
    # Number of proxies in front of the app, used to pick the real client IP
    # out of X-Forwarded-For. 0 means trust REMOTE_ADDR.
    "NUM_PROXIES": int(os.environ.get("NUM_PROXIES", "0")),
}

# Throttle counters live in the cache. LocMemCache is per-process, which is fine
# for local development; point CACHE_URL at Redis when running more than one
# worker, otherwise each worker enforces its own separate limit.
CACHE_URL = os.environ.get("CACHE_URL", "")
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
