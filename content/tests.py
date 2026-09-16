import shutil
import tempfile

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings

from .models import PageSection

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
    b"\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


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


class SeoTests(TestCase):
    def test_robots_txt_allows_crawlers_and_points_to_sitemap(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response["Content-Type"])
        body = response.content.decode()
        self.assertIn("User-agent: *", body)
        self.assertIn("Allow: /", body)
        self.assertIn("Sitemap: https://corexion.uk/sitemap.xml", body)

    def test_sitemap_lists_every_public_page(self):
        from config.pages import PAGES, canonical_url

        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response["Content-Type"])
        body = response.content.decode()
        for url_key in PAGES:
            self.assertIn(canonical_url(url_key, "https://corexion.uk"), body)

    def test_home_has_unique_title_description_canonical_and_json_ld(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertEqual(html.count("<head>"), 1)
        self.assertContains(response, "<title>COREXION | We Raise Standards</title>", html=False)
        self.assertContains(
            response,
            'meta name="description"',
            html=False,
        )
        self.assertContains(response, 'rel="canonical" href="https://corexion.uk/"')
        self.assertContains(response, 'property="og:url" content="https://corexion.uk/"')
        self.assertContains(response, 'rel="icon"')
        self.assertContains(response, "application/ld+json")
        self.assertContains(response, '"@type": "Organization"')

    def test_inner_page_uses_its_own_canonical_and_title(self):
        response = self.client.get("/contact")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<title>Contact | COREXION</title>", html=False)
        self.assertContains(response, 'rel="canonical" href="https://corexion.uk/contact"')
        self.assertContains(response, 'property="og:url" content="https://corexion.uk/contact"')
