"""Rate limit tests.

SimpleRateThrottle.THROTTLE_RATES is read from the DRF settings once, when the
class is first imported, so override_settings(REST_FRAMEWORK=...) has no effect
on it. The rates are therefore patched directly on the throttle class.
"""

from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from rest_framework.throttling import ScopedRateThrottle

from .models import PageSection

TEST_RATES = {"anon": "1000/min", "user": "1000/min", "sections": "3/min"}


class SectionThrottleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        PageSection.objects.create(
            page_slug="home", section_key="hero", heading="Home hero"
        )

    def setUp(self):
        # Throttle history lives in the cache and would otherwise leak between tests.
        cache.clear()
        self.addCleanup(cache.clear)
        patcher = mock.patch.object(ScopedRateThrottle, "THROTTLE_RATES", TEST_RATES)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_requests_within_the_limit_succeed(self):
        for _ in range(3):
            response = self.client.get("/api/sections/?page_slug=home")
            self.assertEqual(response.status_code, 200)

    def test_requests_are_throttled_past_the_limit(self):
        for _ in range(3):
            self.client.get("/api/sections/?page_slug=home")
        response = self.client.get("/api/sections/?page_slug=home")
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response)

    def test_separate_clients_get_separate_budgets(self):
        for _ in range(4):
            self.client.get("/api/sections/?page_slug=home", REMOTE_ADDR="10.0.0.1")
        blocked = self.client.get(
            "/api/sections/?page_slug=home", REMOTE_ADDR="10.0.0.1"
        )
        other_client = self.client.get(
            "/api/sections/?page_slug=home", REMOTE_ADDR="10.0.0.2"
        )
        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(other_client.status_code, 200)

    def test_static_pages_are_not_throttled(self):
        for _ in range(10):
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
