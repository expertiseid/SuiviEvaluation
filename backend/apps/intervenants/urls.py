from rest_framework.routers import DefaultRouter

from .views import IntervenantViewSet

router = DefaultRouter()
router.register("intervenants", IntervenantViewSet, basename="intervenant")

urlpatterns = router.urls
