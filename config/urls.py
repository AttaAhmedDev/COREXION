"""
URL configuration for config project.

Marketing pages are rendered server side from config.pages: the HTML files in
pages/ are Django templates, and the sections stored for that page are passed in
so the response already contains the final copy. Legacy ".html" URLs redirect to
their extensionless equivalent.
"""

from xml.sax.saxutils import escape

from django.conf import settings
from django.contrib import admin
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve as static_serve

from content.models import PageSection

from .pages import PAGES, SLUG_FOR_URL, TEMPLATE_FOR_URL, URL_FOR_TEMPLATE, canonical_url, seo_context


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
    context = {"page_slug": page_slug, "sections": sections}
    context.update(seo_context(key, settings.SITE_URL))
    return render(request, template_name, context)


def redirect_legacy_html(request, path):
    clean_url = URL_FOR_TEMPLATE.get(path)
    if clean_url is None:
        raise Http404("Unknown page")
    return HttpResponsePermanentRedirect("/" + clean_url)


def healthz(_request):
    return HttpResponse("ok")


def robots_txt(_request):
    site = settings.SITE_URL.rstrip("/")
    body = f"User-agent: *\nAllow: /\n\nSitemap: {site}/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


def sitemap_xml(_request):
    site = settings.SITE_URL.rstrip("/")
    entries = []
    for url_key in PAGES:
        loc = escape(canonical_url(url_key, site))
        entries.append(f"    <url>\n        <loc>{loc}</loc>\n    </url>")
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n'
        + "\n\n".join(entries)
        + "\n\n</urlset>\n"
    )
    return HttpResponse(body, content_type="application/xml; charset=utf-8")


urlpatterns = [
    path("healthz", healthz),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
    path("admin/", RedirectView.as_view(url="/" + settings.ADMIN_URL, permanent=False)),
    path("admin", RedirectView.as_view(url="/" + settings.ADMIN_URL, permanent=False)),
    path(
        settings.ADMIN_URL.rstrip("/"),
        RedirectView.as_view(url="/" + settings.ADMIN_URL, permanent=False),
    ),
    path(settings.ADMIN_URL, admin.site.urls),
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
