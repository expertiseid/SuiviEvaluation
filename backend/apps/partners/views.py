from django.db.models import Sum
from rest_framework import viewsets

from apps.core.permissions import HasGlobalVisibilityOrAssigned, IsAdminOrCreateForAuthenticated

from .models import Bailleur, Financement, Partenaire
from .serializers import BailleurSerializer, FinancementSerializer, PartenaireSerializer


def _synchroniser_budget_total(projet):
    """
    Maintient l'invariant documenté sur Projet.budget_total (« Coût total =
    fonds propres + financements bailleurs ») à chaque ajout/modification/
    suppression d'un financement — sans ça, le coût total affiché restait
    figé à sa valeur de création du projet et ne reflétait jamais les
    financements bailleurs ajoutés ensuite.
    """
    total_financements = projet.financements.aggregate(total=Sum("montant_finance"))["total"] or 0
    projet.budget_total = projet.fonds_propres + total_financements
    projet.save(update_fields=["budget_total"])


class PartenaireViewSet(viewsets.ModelViewSet):
    queryset = Partenaire.objects.all()
    serializer_class = PartenaireSerializer
    permission_classes = (IsAdminOrCreateForAuthenticated,)
    filterset_fields = ("type",)
    search_fields = ("nom",)


class BailleurViewSet(viewsets.ModelViewSet):
    queryset = Bailleur.objects.all()
    serializer_class = BailleurSerializer
    permission_classes = (IsAdminOrCreateForAuthenticated,)
    filterset_fields = ("type",)
    search_fields = ("nom",)


class FinancementViewSet(viewsets.ModelViewSet):
    queryset = Financement.objects.select_related("bailleur", "projet")
    serializer_class = FinancementSerializer
    permission_classes = (HasGlobalVisibilityOrAssigned,)
    filterset_fields = ("projet", "bailleur")

    def perform_create(self, serializer):
        super().perform_create(serializer)
        _synchroniser_budget_total(serializer.instance.projet)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        _synchroniser_budget_total(serializer.instance.projet)

    def perform_destroy(self, instance):
        projet = instance.projet
        super().perform_destroy(instance)
        _synchroniser_budget_total(projet)
