from rest_framework import viewsets

from apps.core.permissions import HasGlobalVisibilityOrAssigned, has_global_visibility
from apps.projects.queryset_filters import visible_projets_ids

from .models import Intervenant
from .serializers import IntervenantSerializer


class IntervenantViewSet(viewsets.ModelViewSet):
    serializer_class = IntervenantSerializer
    permission_classes = (HasGlobalVisibilityOrAssigned,)
    filterset_fields = ("projets_associes",)
    search_fields = ("nom", "prenom", "fonction")

    def get_queryset(self):
        qs = Intervenant.objects.prefetch_related("projets_associes", "activites_associees")
        if has_global_visibility(self.request.user):
            return qs
        return qs.filter(projets_associes__id__in=visible_projets_ids(self.request.user)).distinct()
