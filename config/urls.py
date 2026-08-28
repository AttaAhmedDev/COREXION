"""
URL configuration for config project.

Marketing pages are rendered server side from config.pages: the HTML files in
pages/ are Django templates, and the sections stored for that page are passed in
so the response already contains the final copy. Legacy ".html" URLs redirect to
their extensionless equivalent.
"""

from django.conf import settings
from django.contrib import admin
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

from content.models import PageSection

from .pages import SLUG_FOR_URL, TEMPLATE_FOR_URL, URL_FOR_TEMPLATE

ADMIN_PATH = "staff-portal-fa2026/"


def serve_page(request, page=""):
    key = page.strip("/")
    template_name = TEMPLATE_FOR_URL.get(key)
    if template_name is None:
        raise Http404("Unknown page")

    page_slug = SLUG_FOR_URL[key]
    sections = {
        section.section_key: section
        for section in PageSection.objects.filter(page_slug=page_slug)
    }
    return render(
        request,
        template_name,
        {"page_slug": page_slug, "sections": sections},
    )


def redirect_legacy_html(request, path):
    clean_url = URL_FOR_TEMPLATE.get(path)
    if clean_url is None:
        raise Http404("Unknown page")
    return HttpResponsePermanentRedirect("/" + clean_url)


urlpatterns = [
    path(ADMIN_PATH, admin.site.urls),
    path("api/", include("content.urls")),
    re_path(
        r"^assets/(?P<path>.*)$",
        static_serve,
        {"document_root": settings.BASE_DIR / "assets"},
    ),
    re_path(
        r"^media/(?P<path>.*)$",
        static_serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
    re_path(r"^(?P<path>index\.html|pages/.+\.html)$", redirect_legacy_html),
    re_path(r"^(?P<page>[\w./-]*)/?$", serve_page),
]
