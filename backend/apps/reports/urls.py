from rest_framework.routers import DefaultRouter

from .views import RapportSuiviViewSet

router = DefaultRouter()
router.register("rapports", RapportSuiviViewSet, basename="rapport")

urlpatterns = router.urls
