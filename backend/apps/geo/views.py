from rest_framework import viewsets

from apps.core.permissions import IsAdminOrCreateForAuthenticated, IsAdminOrReadOnly

from .models import NiveauAdministratif, Zone
from .serializers import NiveauAdministratifSerializer, ZoneSerializer


class NiveauAdministratifViewSet(viewsets.ModelViewSet):
    queryset = NiveauAdministratif.objects.select_related("niveau_parent").all()
    serializer_class = NiveauAdministratifSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_fields = ("pays",)


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.select_related("niveau_administratif", "parent").all()
    serializer_class = ZoneSerializer
    permission_classes = (IsAdminOrCreateForAuthenticated,)
    filterset_fields = ("niveau_administratif", "parent")
    search_fields = ("nom",)

    def get_queryset(self):
        qs = super().get_queryset()
        pays = self.request.query_params.get("pays")
        if pays:
            qs = qs.filter(niveau_administratif__pays=pays)
        return qs
