from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import IndicateurViewSet, ParametresAlerteView, ValeurIndicateurViewSet, paliers_alerte

router = DefaultRouter()
router.register("indicateurs", IndicateurViewSet, basename="indicateur")
router.register("valeurs-indicateurs", ValeurIndicateurViewSet, basename="valeur-indicateur")

urlpatterns = router.urls + [
    path("parametres-alerte/", ParametresAlerteView.as_view(), name="parametres-alerte"),
    path("paliers-alerte/", paliers_alerte, name="paliers-alerte"),
]
