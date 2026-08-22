from rest_framework.routers import DefaultRouter

from .views import BailleurViewSet, FinancementViewSet, PartenaireViewSet

router = DefaultRouter()
router.register("partenaires", PartenaireViewSet, basename="partenaire")
router.register("bailleurs", BailleurViewSet, basename="bailleur")
router.register("financements", FinancementViewSet, basename="financement")

urlpatterns = router.urls
