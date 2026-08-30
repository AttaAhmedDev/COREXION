"""Run on Vercel after install, before the function is published."""

import os
import shutil
from pathlib import Path


def _publish_assets():
    """Copy design files into public/ so Vercel CDN serves /assets/..."""
    root = Path(__file__).resolve().parent
    source = root / "assets"
    dest = root / "public" / "assets"
    if not source.is_dir():
        return
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    from django.core.management import call_command
    from django.db.utils import DatabaseError

    _publish_assets()

    try:
        call_command("migrate", interactive=False)
    except DatabaseError as exc:
        print(f"migrate failed: {exc}")


if __name__ == "__main__":
    main()
