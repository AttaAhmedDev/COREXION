"""Media cleanup tests.

These use TransactionTestCase because cleanup runs in transaction.on_commit
callbacks, which never fire inside the rolled back transaction of a TestCase.

Every test redirects MEDIA_ROOT to a throwaway directory. The test database is
empty, so anything that scans MEDIA_ROOT for unreferenced files would treat the
real uploads as orphans and delete them.
"""

import shutil
import tempfile
from io import StringIO

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TransactionTestCase, override_settings

from .models import PageSection

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
    b"\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _storage():
    return PageSection._meta.get_field("image").storage


class MediaCleanupTests(TransactionTestCase):
    def setUp(self):
        media_dir = tempfile.mkdtemp(prefix="corexion-test-media-")
        override = override_settings(MEDIA_ROOT=media_dir)
        override.enable()
        # Cleanups run last-registered-first, so the override stays active for
        # any per-file cleanup a test registers later.
        self.addCleanup(shutil.rmtree, media_dir, True)
        self.addCleanup(override.disable)

    def _make_section(self, page_slug, filename):
        section = PageSection.objects.create(page_slug=page_slug, section_key="hero")
        section.image.save(filename, ContentFile(PNG_BYTES), save=True)
        self.addCleanup(self._remove_file, section.image.name)
        return section

    def _remove_file(self, name):
        storage = _storage()
        if name and storage.exists(name):
            storage.delete(name)

    def test_replaced_image_is_deleted(self):
        section = self._make_section("home", "old.png")
        old_name = section.image.name

        section.image.save("new.png", ContentFile(PNG_BYTES), save=True)
        self.addCleanup(self._remove_file, section.image.name)

        self.assertFalse(
            _storage().exists(old_name), "replaced image was left on disk"
        )
        self.assertTrue(_storage().exists(section.image.name))

    def test_image_is_deleted_when_section_is_deleted(self):
        section = self._make_section("home", "only.png")
        name = section.image.name

        section.delete()

        self.assertFalse(_storage().exists(name))

    def test_shared_image_survives_deleting_one_section(self):
        first = self._make_section("home", "shared.png")
        shared_name = first.image.name
        second = PageSection.objects.create(page_slug="contact", section_key="hero")
        second.image.name = shared_name
        second.save()

        first.delete()

        self.assertTrue(
            _storage().exists(shared_name),
            "shared image was deleted while another section still uses it",
        )

    def test_prune_media_only_removes_unreferenced_files(self):
        section = self._make_section("home", "kept.png")
        kept_name = section.image.name

        storage = _storage()
        orphan_name = storage.save("sections/orphan.png", ContentFile(PNG_BYTES))
        self.addCleanup(self._remove_file, orphan_name)

        output = StringIO()
        call_command("prune_media", stdout=output)
        self.assertIn(orphan_name, output.getvalue())
        self.assertTrue(storage.exists(orphan_name), "dry run deleted a file")

        call_command("prune_media", "--delete", stdout=StringIO())
        self.assertFalse(storage.exists(orphan_name))
        self.assertTrue(storage.exists(kept_name), "referenced file was deleted")

    def test_shared_image_survives_when_one_section_swaps_it(self):
        first = self._make_section("home", "shared-swap.png")
        shared_name = first.image.name
        second = PageSection.objects.create(page_slug="contact", section_key="hero")
        second.image.name = shared_name
        second.save()

        second.image.save("replacement.png", ContentFile(PNG_BYTES), save=True)
        self.addCleanup(self._remove_file, second.image.name)

        self.assertTrue(
            _storage().exists(shared_name),
            "shared image was deleted while another section still uses it",
        )
