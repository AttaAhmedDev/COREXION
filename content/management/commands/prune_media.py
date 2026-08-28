"""Delete uploaded files that no PageSection references.

Replaced and deleted images are cleaned up automatically by content.signals.
This command exists for files that were orphaned before that was in place, or by
direct database edits that bypass the signals.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from content.models import PageSection

UPLOAD_DIR = "sections"


class Command(BaseCommand):
    help = "List (or delete with --delete) media files that no section uses."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Actually delete the orphaned files. Without it, only reports.",
        )

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        upload_root = media_root / UPLOAD_DIR
        if not upload_root.exists():
            self.stdout.write("No upload directory at %s" % upload_root)
            return

        referenced = set(
            PageSection.objects.exclude(image="")
            .exclude(image=None)
            .values_list("image", flat=True)
        )

        orphans = []
        for path in sorted(upload_root.rglob("*")):
            if not path.is_file():
                continue
            name = path.relative_to(media_root).as_posix()
            if name not in referenced:
                orphans.append((name, path))

        for name, path in orphans:
            size_kb = path.stat().st_size / 1024
            self.stdout.write("%-60s %8.1f KB" % (name, size_kb))

        if not orphans:
            self.stdout.write(self.style.SUCCESS("No orphaned files."))
            return

        if not options["delete"]:
            self.stdout.write(
                "\n%d orphaned file(s). Re-run with --delete to remove them."
                % len(orphans)
            )
            return

        deleted = 0
        for name, path in orphans:
            try:
                path.unlink()
                deleted += 1
            except OSError as error:
                self.stderr.write("Could not delete %s: %s" % (name, error))
        self.stdout.write(self.style.SUCCESS("\nDeleted %d file(s)." % deleted))
