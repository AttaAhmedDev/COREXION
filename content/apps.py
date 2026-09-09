from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "content"

    def ready(self):
        from . import signals  # noqa: F401
        self._load_cms_seed_if_needed()

    def _load_cms_seed_if_needed(self):
        import os
        import sys
        from pathlib import Path

        argv0 = Path(sys.argv[0]).name if sys.argv else ""
        if "gunicorn" not in argv0:
            return
        if not os.environ.get("RAILWAY_ENVIRONMENT"):
            return
        from django.core.management import call_command

        call_command("load_cms_seed")
