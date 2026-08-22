from rest_framework.routers import DefaultRouter

from .views import (
    ActiviteViewSet,
    EquipeViewSet,
    ObjectifGeneralViewSet,
    ObjectifSpecifiqueViewSet,
    ProjetViewSet,
    SousActiviteViewSet,
)

router = DefaultRouter()
router.register("projets", ProjetViewSet, basename="projet")
router.register("objectifs-generaux", ObjectifGeneralViewSet, basename="objectif-general")
router.register("objectifs-specifiques", ObjectifSpecifiqueViewSet, basename="objectif-specifique")
router.register("activites", ActiviteViewSet, basename="activite")
router.register("sous-activites", SousActiviteViewSet, basename="sous-activite")
router.register("equipes", EquipeViewSet, basename="equipe")

urlpatterns = router.urls
