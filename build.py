"""Run on Vercel after install, before the function is published."""

import os


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    from django.core.management import call_command
    from django.db.utils import DatabaseError

    try:
        call_command("migrate", interactive=False)
    except DatabaseError as exc:
        print(f"migrate failed: {exc}")


if __name__ == "__main__":
    main()
