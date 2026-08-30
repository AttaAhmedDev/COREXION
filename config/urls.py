"""
URL configuration for config project.

Marketing pages are rendered server side from config.pages: the HTML files in
pages/ are Django templates, and the sections stored for that page are passed in
so the response already contains the final copy. Legacy ".html" URLs redirect to
their extensionless equivalent.
"""

from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.db import DatabaseError
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

from content.models import PageSection

from .pages import SLUG_FOR_URL, TEMPLATE_FOR_URL, URL_FOR_TEMPLATE


def redirect_admin_index(request):
    return HttpResponsePermanentRedirect("/" + settings.ADMIN_URL)


def serve_page(request, page=""):
    key = page.strip("/")
    admin_prefix = settings.ADMIN_URL.strip("/")
    if key == admin_prefix or key.startswith(admin_prefix + "/"):
        remainder = key[len(admin_prefix) :].lstrip("/")
        target = "/" + settings.ADMIN_URL + remainder
        if remainder and not target.endswith("/"):
            target += "/"
        return HttpResponsePermanentRedirect(target)
    template_name = TEMPLATE_FOR_URL.get(key)
    if template_name is None:
        raise Http404("Unknown page")

    page_slug = SLUG_FOR_URL[key]
    try:
        sections = {
            section.section_key: section
            for section in PageSection.objects.filter(page_slug=page_slug)
        }
    except DatabaseError:
        sections = {}
    return render(
        request,
        template_name,
        {"page_slug": page_slug, "sections": sections},
    )


def serve_design_assets(request, path):
    """Serve /assets/ from collectstatic output, then the repo assets/ folder."""
    roots = []
    static_root = Path(settings.STATIC_ROOT)
    if static_root.is_dir():
        roots.append(static_root)
    roots.append(settings.BASE_DIR / "assets")
    for root in roots:
        full = (root / path).resolve()
        try:
            full.relative_to(root.resolve())
        except ValueError:
            continue
        if full.is_file():
            return static_serve(request, path, document_root=root)
    raise Http404("Asset not found")


def redirect_legacy_html(request, path):
    if path == "index.html":
        return HttpResponsePermanentRedirect("/")
    clean_url = URL_FOR_TEMPLATE.get(path)
    if clean_url is None:
        raise Http404("Unknown page")
    return HttpResponsePermanentRedirect("/" + clean_url)


_admin_prefix = settings.ADMIN_URL.strip("/")
urlpatterns = [
    path("api/", include("content.urls")),
    re_path(r"^assets/(?P<path>.*)$", serve_design_assets),
]
if _admin_prefix:
    urlpatterns = [
        path(_admin_prefix, redirect_admin_index),
        path(settings.ADMIN_URL, admin.site.urls),
        *urlpatterns,
    ]

if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            static_serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

urlpatterns += [
    re_path(r"^(?P<path>index\.html|pages/.+\.html)$", redirect_legacy_html),
    re_path(r"^(?P<page>[\w./-]*)/?$", serve_page),
]
