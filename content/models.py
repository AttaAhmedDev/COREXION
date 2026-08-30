from django.db import models
from django_cleanup import cleanup


# Cleanup is handled by content.signals instead, which refuses to delete a file
# that is still referenced by another section.
@cleanup.ignore
class PageSection(models.Model):
    page_slug = models.SlugField(
        help_text='Identifies which page this section belongs to (e.g. "home").',
    )
    section_key = models.CharField(
        max_length=100,
        help_text='Identifies the section within the page (e.g. "hero").',
    )
    heading = models.CharField(max_length=255, blank=True, null=True)
    paragraph = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to="sections/",
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional. Leave empty for text-only sections.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "page section"
        verbose_name_plural = "page sections"
        ordering = ["page_slug", "section_key"]
        unique_together = ("page_slug", "section_key")

    def __str__(self):
        return f"{self.page_slug}:{self.section_key}"

    @classmethod
    def get_section(cls, page_slug, section_key):
        return cls.objects.filter(page_slug=page_slug, section_key=section_key).first()
