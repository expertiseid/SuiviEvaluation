from rest_framework.routers import DefaultRouter

from .views import (
    BeneficiaireViewSet,
    ParticipationProjetViewSet,
    SignalementDoublonViewSet,
    StatutParticulierViewSet,
)

router = DefaultRouter()
router.register("beneficiaires", BeneficiaireViewSet, basename="beneficiaire")
router.register("participations-projet", ParticipationProjetViewSet, basename="participation-projet")
router.register("statuts-particuliers", StatutParticulierViewSet, basename="statut-particulier")
router.register("signalements-doublons", SignalementDoublonViewSet, basename="signalement-doublon")

urlpatterns = router.urls
