from django.db.models import Q
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.core.permissions import HasGlobalVisibilityOrAssigned
from apps.projects.models import Projet
from apps.projects.queryset_filters import visible_projets_ids

from .export_excel import exporter_suivi_excel
from .export_pdf import exporter_suivi_pdf
from .models import PointSuivi
from .serializers import PointSuiviSerializer
from .services import construire_dashboard_suivi, synchroniser_activite_depuis_suivi, synchroniser_sous_activite_depuis_suivi


class PointSuiviViewSet(viewsets.ModelViewSet):
    serializer_class = PointSuiviSerializer
    permission_classes = (HasGlobalVisibilityOrAssigned,)
    filterset_fields = ("activite", "sous_activite")

    def get_queryset(self):
        ids = visible_projets_ids(self.request.user)
        return (
            PointSuivi.objects.filter(
                Q(activite__objectif_specifique__objectif_general__projet__id__in=ids)
                | Q(sous_activite__activite__objectif_specifique__objectif_general__projet__id__in=ids)
            )
            .select_related("activite", "sous_activite", "saisi_par")
        )

    def _synchroniser(self, instance):
        if instance.activite_id:
            synchroniser_activite_depuis_suivi(instance.activite)
        else:
            synchroniser_sous_activite_depuis_suivi(instance.sous_activite)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._synchroniser(serializer.instance)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._synchroniser(serializer.instance)

    def perform_destroy(self, instance):
        activite, sous_activite = instance.activite, instance.sous_activite
        super().perform_destroy(instance)
        if activite:
            synchroniser_activite_depuis_suivi(activite)
        else:
            synchroniser_sous_activite_depuis_suivi(sous_activite)


def _projet_visible_ou_404(request, projet_id):
    ids = list(visible_projets_ids(request.user))
    return Projet.objects.filter(id__in=ids, id=projet_id).first()


@api_view(["GET"])
@permission_classes([HasGlobalVisibilityOrAssigned])
def suivi_dashboard_projet(request, projet_id):
    projet = _projet_visible_ou_404(request, projet_id)
    if projet is None:
        return Response({"detail": "Projet introuvable ou non accessible."}, status=404)
    return Response(construire_dashboard_suivi(projet))


@api_view(["GET"])
@permission_classes([HasGlobalVisibilityOrAssigned])
def suivi_exporter_excel(request, projet_id):
    projet = _projet_visible_ou_404(request, projet_id)
    if projet is None:
        return Response({"detail": "Projet introuvable ou non accessible."}, status=404)

    contenu = exporter_suivi_excel(projet)
    response = HttpResponse(
        contenu, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f"attachment; filename=suivi_{projet.code}.xlsx"
    return response


@api_view(["GET"])
@permission_classes([HasGlobalVisibilityOrAssigned])
def suivi_exporter_pdf(request, projet_id):
    projet = _projet_visible_ou_404(request, projet_id)
    if projet is None:
        return Response({"detail": "Projet introuvable ou non accessible."}, status=404)

    contenu = exporter_suivi_pdf(projet)
    response = HttpResponse(contenu, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=suivi_{projet.code}.pdf"
    return response
