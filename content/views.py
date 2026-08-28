from rest_framework import permissions, viewsets
from rest_framework.throttling import ScopedRateThrottle

from .models import PageSection
from .serializers import PageSectionSerializer


class PageSectionViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve marketing page sections. Writes happen in Django admin."""

    queryset = PageSection.objects.all()
    serializer_class = PageSectionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    http_method_names = ["get", "head", "options"]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "sections"

    def get_queryset(self):
        queryset = super().get_queryset()
        page_slug = self.request.query_params.get("page_slug")
        if page_slug:
            queryset = queryset.filter(page_slug=page_slug)
        section_key = self.request.query_params.get("section_key")
        if section_key:
            queryset = queryset.filter(section_key=section_key)
        return queryset
