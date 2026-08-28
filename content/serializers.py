from rest_framework import serializers

from .models import PageSection


class PageSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSection
        fields = (
            "id",
            "page_slug",
            "section_key",
            "heading",
            "paragraph",
            "image",
            "updated_at",
        )
        read_only_fields = fields
