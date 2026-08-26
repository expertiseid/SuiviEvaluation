from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from apps.accounts.constants import ROLES_NOTIFIEES_MODIFICATION_ACTIVITE
from apps.core.permissions import HasGlobalVisibilityOrAssigned, IsAdminOrCreateForAuthenticated
from apps.indicators.exports import generer_xlsform
from apps.notifications.models import Notification
from apps.notifications.services import notifier, notifier_par_role

from .import_excel import generer_modele_import_projet, importer_projet
from .models import Activite, Equipe, ObjectifGeneral, ObjectifSpecifique, Projet, SousActivite
from .queryset_filters import visible_projets_ids
from .serializers import (
    ActiviteSerializer,
    EquipeSerializer,
    ObjectifGeneralSerializer,
    ObjectifSpecifiqueSerializer,
    ProjetSerializer,
    ProjetWriteSerializer,
    SousActiviteSerializer,
)
from .services import (
    supprimer_activite_cascade,
    supprimer_objectif_general_cascade,
    supprimer_objectif_specifique_cascade,
    supprimer_projet_cascade,
    supprimer_sous_activite_cascade,
    synchroniser_projets_associes_activite,
    synchroniser_projets_associes_equipe,
)


class EquipeViewSet(viewsets.ModelViewSet):
    queryset = Equipe.objects.all()
    serializer_class = EquipeSerializer
    permission_classes = (IsAdminOrCreateForAuthenticated,)
    search_fields = ("nom",)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        synchroniser_projets_associes_equipe(serializer.instance)


class ProjetViewSet(viewsets.ModelViewSet):
    permission_classes = (HasGlobalVisibilityOrAssigned,)
    filterset_fields = ("statut", "partenaire_bailleur", "partenaire_mise_en_oeuvre")
    search_fields = ("nom", "code")

    def get_queryset(self):
        return (
            Projet.objects.select_related("partenaire_bailleur", "partenaire_mise_en_oeuvre")
            .prefetch_related("objectif_general__objectifs_specifiques__activites__sous_activites")
            .filter(id__in=visible_projets_ids(self.request.user))
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ProjetWriteSerializer
        return ProjetSerializer

    def perform_destroy(self, instance):
        supprimer_projet_cascade(instance)

    @action(detail=True, methods=["get"], url_path="export/xlsform")
    def export_xlsform(self, request, pk=None):
        projet = self.get_object()
        contenu = generer_xlsform(projet)
        response = HttpResponse(
            contenu, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f"attachment; filename=xlsform_{projet.code}.xlsx"
        return response

    @action(detail=False, methods=["get"], url_path="modele-import")
    def modele_import(self, request):
        contenu = generer_modele_import_projet()
        response = HttpResponse(
            contenu, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=modele_import_projet.xlsx"
        return response

    @action(detail=False, methods=["post"], url_path="importer", parser_classes=[MultiPartParser, FormParser])
    def importer(self, request):
        fichier = request.data.get("fichier")
        if not fichier:
            raise ValidationError({"fichier": "Un fichier Excel (.xlsx) est requis."})
        try:
            resultat = importer_projet(fichier)
        except Exception as exc:  # fichier corrompu, mauvais format, etc.
            raise ValidationError({"fichier": f"Impossible de lire ce fichier : {exc}"})
        return Response(resultat)


class ObjectifGeneralViewSet(viewsets.ModelViewSet):
    serializer_class = ObjectifGeneralSerializer
    permission_classes = (HasGlobalVisibilityOrAssigned,)
    filterset_fields = ("projet",)

    def get_queryset(self):
        return ObjectifGeneral.objects.filter(projet__id__in=visible_projets_ids(self.request.user))

    def perform_destroy(self, instance):
        supprimer_objectif_general_cascade(instance)


class ObjectifSpecifiqueViewSet(viewsets.ModelViewSet):
    serializer_class = ObjectifSpecifiqueSerializer
    permission_classes = (HasGlobalVisibilityOrAssigned,)
    filterset_fields = ("objectif_general",)

    def get_queryset(self):
        return ObjectifSpecifique.objects.filter(
            objectif_general__projet__id__in=visible_projets_ids(self.request.user)
        )

    def perform_destroy(self, instance):
        supprimer_objectif_specifique_cascade(instance)


class ActiviteViewSet(viewsets.ModelViewSet):
    serializer_class = ActiviteSerializer
    permission_classes = (HasGlobalVisibilityOrAssigned,)
    filterset_fields = ("objectif_specifique", "responsable")

    CHAMPS_SURVEILLES = ("date_debut", "date_fin", "budget_alloue", "quantite_prevue", "statut")

    def get_queryset(self):
        return Activite.objects.filter(
            objectif_specifique__objectif_general__projet__id__in=visible_projets_ids(self.request.user)
        )

    def perform_destroy(self, instance):
        supprimer_activite_cascade(instance)

    @action(detail=False, methods=["get"], url_path="pour-projet")
    def pour_projet(self, request):
        """
        Liste allégée (id, libellé), non paginée, des activités d'un projet —
        alimente le sélecteur de grille d'alerte par activité (potentiellement
        des centaines d'activités, une pagination classique serait inutile ici).
        """
        projet_id = request.query_params.get("projet")
        ids = visible_projets_ids(self.request.user)
        if not projet_id or int(projet_id) not in ids:
            return Response([])
        activites = self.get_queryset().filter(
            objectif_specifique__objectif_general__projet__id=projet_id
        ).order_by("libelle")
        return Response([{"id": a.id, "libelle": a.libelle} for a in activites])

    def perform_create(self, serializer):
        super().perform_create(serializer)
        synchroniser_projets_associes_activite(serializer.instance)

    def perform_update(self, serializer):
        instance = serializer.instance
        anciennes_valeurs = {champ: getattr(instance, champ) for champ in self.CHAMPS_SURVEILLES}
        deja_planifiee = anciennes_valeurs["date_debut"] is not None or anciennes_valeurs["date_fin"] is not None

        super().perform_update(serializer)
        synchroniser_projets_associes_activite(serializer.instance)

        activite = serializer.instance
        changements = [
            champ for champ in self.CHAMPS_SURVEILLES if anciennes_valeurs[champ] != getattr(activite, champ)
        ]
        if changements and deja_planifiee:
            projet = activite.objectif_specifique.objectif_general.projet
            titre = f"Activité modifiée : {activite.libelle}"
            message = f"Projet {projet.nom} — champ(s) modifié(s) : {', '.join(changements)}."
            lien = f"/projets/{projet.id}"
            if projet.utilisateurs_affectes.exists():
                notifier(list(projet.utilisateurs_affectes.all()), Notification.Type.ACTIVITE_MODIFIEE, titre, message, lien)
            notifier_par_role(
                ROLES_NOTIFIEES_MODIFICATION_ACTIVITE,
                Notification.Type.ACTIVITE_MODIFIEE,
                titre,
                message,
                lien,
                exclure=self.request.user,
            )


class SousActiviteViewSet(viewsets.ModelViewSet):
    serializer_class = SousActiviteSerializer
    permission_classes = (HasGlobalVisibilityOrAssigned,)
    filterset_fields = ("activite", "statut")

    def get_queryset(self):
        return SousActivite.objects.filter(
            activite__objectif_specifique__objectif_general__projet__id__in=visible_projets_ids(
                self.request.user
            )
        )

    def perform_destroy(self, instance):
        supprimer_sous_activite_cascade(instance)
