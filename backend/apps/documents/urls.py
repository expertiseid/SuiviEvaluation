from rest_framework.routers import DefaultRouter

from .views import DocumentViewSet, DossierViewSet, PieceJustificativeViewSet

router = DefaultRouter()
router.register("pieces-justificatives", PieceJustificativeViewSet, basename="piece-justificative")
router.register("dossiers", DossierViewSet, basename="dossier")
router.register("documents", DocumentViewSet, basename="document")

urlpatterns = router.urls
