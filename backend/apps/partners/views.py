from rest_framework import viewsets

from apps.core.permissions import HasGlobalVisibilityOrAssigned, IsAdminOrCreateForAuthenticated

from .models import Bailleur, Financement, Partenaire
from .serializers import BailleurSerializer, FinancementSerializer, PartenaireSerializer


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
