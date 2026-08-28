from django.contrib import admin

from .models import PageSection


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ("page_slug", "section_key", "heading", "updated_at")
    list_filter = ("page_slug",)
    search_fields = ("page_slug", "section_key", "heading", "paragraph")
