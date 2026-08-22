from rest_framework.routers import DefaultRouter

from .views import NiveauAdministratifViewSet, ZoneViewSet

router = DefaultRouter()
router.register("zones", ZoneViewSet, basename="zone")
router.register("niveaux-administratifs", NiveauAdministratifViewSet, basename="niveau-administratif")

urlpatterns = router.urls
