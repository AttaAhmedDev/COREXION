"""Database settings that work locally and on Vercel (Neon DATABASE_URL)."""

import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

_REPO_ROOT = Path(__file__).resolve().parent.parent


def database_from_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    sslmode = (query.get("sslmode") or ["require"])[0]
    pgbouncer = (query.get("pgbouncer") or [""])[0].lower() in ("true", "1")
    config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote((parsed.path or "/").lstrip("/").split("?")[0]),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or "5432"),
        "CONN_MAX_AGE": 0,
        "OPTIONS": {"sslmode": sslmode},
    }
    if pgbouncer or "-pooler." in (parsed.hostname or ""):
        config["DISABLE_SERVER_SIDE_CURSORS"] = True
    return config


def _hosted_postgres_url():
    for key in (
        "DATABASE_URL",
        "POSTGRES_URL",
        "POSTGRES_URL_NON_POOLING",
        "DATABASE_URL_UNPOOLED",
    ):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return ""


def database_from_env():
    url = _hosted_postgres_url()
    if url:
        return database_from_url(url)
    # Vercel has no local Postgres. Until Neon sets DATABASE_URL, use SQLite
    # in the project tree so migrate-at-build can ship an empty schema.
    if os.environ.get("VERCEL") == "1" and not os.environ.get("POSTGRES_HOST"):
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(_REPO_ROOT / "db.sqlite3"),
        }
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DATABASE")
        or os.environ.get("POSTGRES_DB", "corexion"),
        "USER": os.environ.get("POSTGRES_USER") or os.environ.get("PGUSER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD")
        or os.environ.get("PGPASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST") or os.environ.get("PGHOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT") or os.environ.get("PGPORT", "5432"),
        "CONN_MAX_AGE": 0,
    }
