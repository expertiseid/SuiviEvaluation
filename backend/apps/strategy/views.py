from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly

from .models import CadreStrategique, ElementStrategique, TypeNiveau
from .serializers import CadreStrategiqueSerializer, ElementStrategiqueSerializer, TypeNiveauSerializer
from .services import (
    exporter_structuration,
    generer_modele_import,
    importer_structuration,
    supprimer_cadre_strategique_cascade,
)


class CadreStrategiqueViewSet(viewsets.ModelViewSet):
    queryset = CadreStrategique.objects.all()
    serializer_class = CadreStrategiqueSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def perform_destroy(self, instance):
        supprimer_cadre_strategique_cascade(instance)

    @action(detail=True, methods=["get"], url_path="export")
    def export_structuration(self, request, pk=None):
        cadre = self.get_object()
        contenu = exporter_structuration(cadre)
        response = HttpResponse(
            contenu, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f"attachment; filename=plan_strategique_{cadre.id}.xlsx"
        return response


class TypeNiveauViewSet(viewsets.ModelViewSet):
    queryset = TypeNiveau.objects.select_related("niveau_parent", "cadre_strategique")
    serializer_class = TypeNiveauSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_fields = ("cadre_strategique",)


class ElementStrategiqueViewSet(viewsets.ModelViewSet):
    serializer_class = ElementStrategiqueSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_fields = ("type_niveau", "element_parent")

    def get_queryset(self):
        qs = ElementStrategique.objects.select_related("type_niveau", "element_parent")
        cadre_id = self.request.query_params.get("cadre_strategique")
        if cadre_id:
            qs = qs.filter(type_niveau__cadre_strategique_id=cadre_id)
        return qs

    @action(detail=False, methods=["get"], url_path="modele-import")
    def modele_import(self, request):
        cadre_id = request.query_params.get("cadre_strategique")
        if not cadre_id:
            raise ValidationError({"cadre_strategique": "Paramètre requis."})
        cadre = get_object_or_404(CadreStrategique, pk=cadre_id)
        contenu = generer_modele_import(cadre)
        response = HttpResponse(
            contenu, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=modele_import_structuration.xlsx"
        return response

    @action(
        detail=False,
        methods=["post"],
        url_path="importer",
        parser_classes=[MultiPartParser, FormParser],
    )
    def importer(self, request):
        fichier = request.data.get("fichier")
        cadre_id = request.data.get("cadre_strategique")
        if not cadre_id:
            raise ValidationError({"cadre_strategique": "Paramètre requis."})
        cadre = get_object_or_404(CadreStrategique, pk=cadre_id)
        if not fichier:
            raise ValidationError({"fichier": "Un fichier Excel (.xlsx) est requis."})
        try:
            resultat = importer_structuration(fichier, cadre)
        except Exception as exc:  # fichier corrompu, mauvais format, etc.
            raise ValidationError({"fichier": f"Impossible de lire ce fichier : {exc}"})
        return Response(resultat)
