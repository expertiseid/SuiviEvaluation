from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.beneficiaries.models import ParticipationProjet
from apps.core.permissions import HasGlobalVisibilityOrAssigned
from apps.indicators.models import Indicateur
from apps.indicators.services import palier_pour_taux, paliers_pour, valeur_realisee_totale, taux_realisation
from apps.notifications.services import lister_echeances
from apps.projects.models import Projet
from apps.projects.queryset_filters import visible_projets_ids


def _indicateurs_pour_projets(projet_ids):
    return Indicateur.objects.filter(
        Q(projet__id__in=projet_ids)
        | Q(objectif_general__projet__id__in=projet_ids)
        | Q(objectif_specifique__objectif_general__projet__id__in=projet_ids)
        | Q(activite__objectif_specifique__objectif_general__projet__id__in=projet_ids)
    ).distinct()


def _resume_indicateurs(indicateurs):
    """
    Chaque indicateur suit la palette de SON projet (elles peuvent différer
    d'un projet à l'autre) — les compteurs sont donc regroupés par
    (libellé, couleur) du palier atteint plutôt que par 3 statuts fixes.
    """
    compteurs = {}
    for indicateur in indicateurs:
        taux = taux_realisation(valeur_realisee_totale(indicateur), indicateur.valeur_cible)
        palier = palier_pour_taux(taux, paliers_pour(indicateur=indicateur, projet=indicateur.projet_rattache))
        if palier is None:
            continue
        cle = (palier.libelle, palier.couleur)
        compteurs[cle] = compteurs.get(cle, 0) + 1
    return sorted(
        [{"libelle": libelle, "couleur": couleur, "count": count} for (libelle, couleur), count in compteurs.items()],
        key=lambda r: r["libelle"],
    )


@api_view(["GET"])
@permission_classes([HasGlobalVisibilityOrAssigned])
def dashboard_consolide(request):
    ids = list(visible_projets_ids(request.user))
    projets = Projet.objects.filter(id__in=ids)
    indicateurs = _indicateurs_pour_projets(ids)
    nombre_beneficiaires = (
        ParticipationProjet.objects.filter(projet__id__in=ids).values("beneficiaire").distinct().count()
    )

    return Response(
        {
            "nombre_projets": projets.count(),
            "budget_total": sum((p.budget_total for p in projets), start=0),
            "nombre_beneficiaires": nombre_beneficiaires,
            "indicateurs_par_statut": _resume_indicateurs(indicateurs),
            "projets": [
                {"id": p.id, "code": p.code, "nom": p.nom, "statut": p.statut, "budget_total": p.budget_total}
                for p in projets
            ],
        }
    )


@api_view(["GET"])
@permission_classes([HasGlobalVisibilityOrAssigned])
def dashboard_echeances(request):
    """
    Activités, sous-activités et projets (parmi ceux visibles par l'utilisateur) en retard ou dont
    l'échéance approche — alimente le bandeau défilant du tableau de bord.
    """
    ids = list(visible_projets_ids(request.user))
    return Response(lister_echeances(ids))


@api_view(["GET"])
@permission_classes([HasGlobalVisibilityOrAssigned])
def dashboard_projet(request, projet_id):
    ids = list(visible_projets_ids(request.user))
    projet = Projet.objects.filter(id__in=ids, id=projet_id).first()
    if projet is None:
        return Response({"detail": "Projet introuvable ou non accessible."}, status=404)

    indicateurs = _indicateurs_pour_projets([projet_id])
    nombre_beneficiaires = (
        ParticipationProjet.objects.filter(projet=projet).values("beneficiaire").distinct().count()
    )

    indicateurs_detail = []
    for indicateur in indicateurs:
        taux = taux_realisation(valeur_realisee_totale(indicateur), indicateur.valeur_cible)
        palier = palier_pour_taux(taux, paliers_pour(indicateur=indicateur, projet=projet))
        indicateurs_detail.append(
            {
                "id": indicateur.id,
                "libelle": indicateur.libelle,
                "taux_realisation": taux,
                "palier_actuel": (
                    {"libelle": palier.libelle, "couleur": palier.couleur} if palier else None
                ),
            }
        )

    return Response(
        {
            "projet": {"id": projet.id, "code": projet.code, "nom": projet.nom, "statut": projet.statut},
            "nombre_objectifs_generaux": 1 if hasattr(projet, "objectif_general") else 0,
            "nombre_beneficiaires": nombre_beneficiaires,
            "indicateurs": indicateurs_detail,
            "indicateurs_par_statut": _resume_indicateurs(indicateurs),
        }
    )
