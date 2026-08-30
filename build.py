"""Run on Vercel after install, before the function is published."""

import os


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    from django.core.management import call_command

    has_database = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_HOST")
    if not has_database:
        print("No DATABASE_URL; skipping migrate. Add Neon, then redeploy.")
        return

    call_command("migrate", interactive=False)


if __name__ == "__main__":
    main()
