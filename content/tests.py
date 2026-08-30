import os
import shutil
import tempfile
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings

from config.database import database_from_env, database_from_url
from .models import PageSection

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
    b"\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class DatabaseUrlTests(TestCase):
    def test_parses_neon_style_url(self):
        config = database_from_url(
            "postgres://app:p%40ss@ep-host.neon.tech:5432/corexion?sslmode=require"
        )
        self.assertEqual(config["NAME"], "corexion")
        self.assertEqual(config["USER"], "app")
        self.assertEqual(config["PASSWORD"], "p@ss")
        self.assertEqual(config["HOST"], "ep-host.neon.tech")
        self.assertEqual(config["OPTIONS"]["sslmode"], "require")

    def test_vercel_without_database_url_uses_sqlite(self):
        with patch.dict(
            os.environ,
            {"VERCEL": "1", "DATABASE_URL": "", "POSTGRES_HOST": ""},
        ):
            config = database_from_env()
        self.assertEqual(config["ENGINE"], "django.db.backends.sqlite3")

    def test_postgres_url_alias_and_pgbouncer(self):
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "",
                "POSTGRES_URL": (
                    "postgres://app:secret@db.example:6432/corexion"
                    "?sslmode=require&pgbouncer=true"
                ),
            },
        ):
            config = database_from_env()
        self.assertTrue(config["DISABLE_SERVER_SIDE_CURSORS"])
        self.assertEqual(config["PORT"], "6432")


class SectionApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        PageSection.objects.create(
            page_slug="home", section_key="hero", heading="Home hero"
        )
        PageSection.objects.create(
            page_slug="home", section_key="expertise_title", heading="Home expertise"
        )
        PageSection.objects.create(
            page_slug="contact", section_key="hero", heading="Contact hero"
        )

    def test_list_returns_every_section(self):
        response = self.client.get("/api/sections/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_page_slug_filter_narrows_results(self):
        response = self.client.get("/api/sections/?page_slug=home")
        self.assertEqual(response.status_code, 200)
        slugs = {section["page_slug"] for section in response.json()}
        self.assertEqual(slugs, {"home"})

    def test_section_key_filter_narrows_results(self):
        response = self.client.get("/api/sections/?page_slug=home&section_key=hero")
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["heading"], "Home hero")

    def test_unknown_page_slug_returns_empty_list(self):
        response = self.client.get("/api/sections/?page_slug=does-not-exist")
        self.assertEqual(response.json(), [])

    def test_writes_are_rejected(self):
        response = self.client.post("/api/sections/", {"page_slug": "home"})
        self.assertEqual(response.status_code, 405)

    def test_cors_preflight_is_allowed(self):
        response = self.client.options(
            "/api/sections/",
            HTTP_ORIGIN="http://localhost:5500",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )
        self.assertEqual(response.status_code, 200)
        # CORS_ALLOW_ALL_ORIGINS answers with a wildcard rather than the origin.
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")


class ServerRenderedContentTests(TestCase):
    """The response body must already carry the stored copy, with the design as
    fallback, so crawlers and no-JS clients see the real content."""

    def setUp(self):
        # Never let a test write into the real media folder.
        media_dir = tempfile.mkdtemp(prefix="corexion-test-media-")
        override = override_settings(MEDIA_ROOT=media_dir)
        override.enable()
        self.addCleanup(shutil.rmtree, media_dir, True)
        self.addCleanup(override.disable)

    def test_stored_heading_replaces_the_design_copy(self):
        PageSection.objects.create(
            page_slug="home", section_key="hero", heading="RAISING THE BAR"
        )
        response = self.client.get("/")
        self.assertContains(response, "RAISING THE BAR")
        self.assertNotContains(response, "WE RAISE<br>STANDARDS")

    def test_design_copy_is_kept_when_no_section_exists(self):
        response = self.client.get("/")
        self.assertContains(response, "WE RAISE<br>STANDARDS")

    def test_design_copy_is_kept_when_section_field_is_blank(self):
        PageSection.objects.create(page_slug="home", section_key="hero", heading="")
        response = self.client.get("/")
        self.assertContains(response, "WE RAISE<br>STANDARDS")

    def test_no_template_tags_leak_into_the_response(self):
        response = self.client.get("/about/leadership")
        self.assertNotContains(response, "{%")

    def test_uploaded_image_is_used(self):
        section = PageSection.objects.create(page_slug="contact", section_key="hero")
        section.image.save("contact-hero.png", ContentFile(PNG_BYTES), save=True)
        self.addCleanup(section.image.delete, save=False)

        response = self.client.get("/contact")
        self.assertContains(response, section.image.url)

    def test_missing_upload_falls_back_to_the_design_image(self):
        PageSection.objects.create(
            page_slug="contact", section_key="hero", image="sections/gone.png"
        )
        response = self.client.get("/contact")
        self.assertNotContains(response, "sections/gone.png")
        self.assertContains(response, "assets/images/15_Global_City_Office.png")

    def test_page_without_any_sections_still_renders(self):
        response = self.client.get("/expertise")
        self.assertEqual(response.status_code, 200)


class CleanUrlTests(TestCase):
    def test_home_is_served_at_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_page_is_served_without_html_extension(self):
        response = self.client.get("/expertise/cost-management")
        self.assertEqual(response.status_code, 200)

    def test_legacy_html_url_redirects_permanently(self):
        response = self.client.get("/pages/contact.html")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/contact")

    def test_unknown_page_returns_404(self):
        response = self.client.get("/no-such-page")
        self.assertEqual(response.status_code, 404)

    def test_cms_path_without_slash_redirects_to_admin(self):
        from django.conf import settings as django_settings

        prefix = django_settings.ADMIN_URL.strip("/")
        response = self.client.get("/" + prefix)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/" + django_settings.ADMIN_URL)

    def test_cms_login_is_reachable(self):
        from django.conf import settings as django_settings

        response = self.client.get("/" + django_settings.ADMIN_URL + "login/")
        self.assertEqual(response.status_code, 200)

    def test_design_css_is_served(self):
        response = self.client.get("/assets/css/base.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/css", response["Content-Type"])

    def test_home_is_not_redirected_to_double_slash(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.get("Location", ""), "//")

    def test_uploaded_media_is_served(self):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        folder = os.path.join(root, "sections")
        os.makedirs(folder)
        with open(os.path.join(folder, "hero.png"), "wb") as handle:
            handle.write(PNG_BYTES)
        with override_settings(MEDIA_ROOT=root):
            response = self.client.get("/media/sections/hero.png")
        self.assertEqual(response.status_code, 200)
