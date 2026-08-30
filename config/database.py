"""Database settings that work locally and on Vercel (Neon DATABASE_URL)."""

import os
from urllib.parse import parse_qs, unquote, urlparse


def database_from_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    sslmode = (query.get("sslmode") or ["require"])[0]
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote((parsed.path or "/").lstrip("/")),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or "5432"),
        "CONN_MAX_AGE": 0,
        "OPTIONS": {"sslmode": sslmode},
    }


def database_from_env():
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return database_from_url(url)
    # Vercel has no local Postgres. Until Neon sets DATABASE_URL, use a
    # throwaway SQLite file so the marketing pages still render (CMS empty).
    if os.environ.get("VERCEL") == "1" and not os.environ.get("POSTGRES_HOST"):
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "/tmp/corexion.sqlite3",
        }
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "corexion"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 0,
    }
