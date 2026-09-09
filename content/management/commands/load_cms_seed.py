"""Copy bundled CMS images onto the media volume and load section rows once."""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from content.models import PageSection


class Command(BaseCommand):
    help = "Load seed/ CMS rows and images if present (skips data when sections already exist)."

    def handle(self, *args, **options):
        seed = Path(settings.BASE_DIR) / "seed"
        src = seed / "media" / "sections"
        dest = Path(settings.MEDIA_ROOT) / "sections"
        copied = 0
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            for path in src.rglob("*"):
                if not path.is_file():
                    continue
                target = dest / path.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                copied += 1
            self.stdout.write(f"Copied {copied} media file(s) to {dest}")
        else:
            self.stdout.write(f"No seed media at {src}")

        fixture = seed / "pagesections.json"
        if not fixture.is_file():
            self.stdout.write(f"No fixture at {fixture}")
            return
        if PageSection.objects.exists():
            self.stdout.write("PageSection already has rows; skipping loaddata")
            return
        call_command("loaddata", str(fixture), verbosity=1)
        self.stdout.write(
            self.style.SUCCESS(f"Loaded {PageSection.objects.count()} page section(s)")
        )
