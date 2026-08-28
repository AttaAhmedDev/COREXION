from rest_framework.routers import DefaultRouter

from .views import PageSectionViewSet

router = DefaultRouter()
router.register("sections", PageSectionViewSet, basename="pagesection")

urlpatterns = router.urls
