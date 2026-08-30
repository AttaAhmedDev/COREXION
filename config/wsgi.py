"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
app = application


def _apply_migrations():
    """Create tables on cold start. Vercel may not have DATABASE_URL at build."""
    from django.core.management import call_command
    from django.db.utils import DatabaseError

    try:
        call_command("migrate", interactive=False, run_syncdb=True)
    except DatabaseError as exc:
        print(f"migrate failed: {exc}")


_apply_migrations()
