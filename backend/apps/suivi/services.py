"""
Synchronise la "photo actuelle" d'une Activite/SousActivite
(quantite_realisee/budget_realise/statut) sur la SOMME de ses PointSuivi —
même principe que taux_realisation_actuel côté Indicateur, qui dérive du
total des ValeurIndicateur plutôt que d'un champ saisi à part : on garde un
seul historique source de vérité (PointSuivi, une ligne = ce qui a été
accompli PENDANT une période précise), et les champs sur
Activite/SousActivite ne sont qu'une valeur dérivée mise en cache pour les
écrans qui n'ont pas besoin de l'historique complet (Planification,
exports, rapports).
"""
from decimal import Decimal

from django.db.models import Sum


def valeur_attendue_a(date, debut, fin, depart, arrivee):
    """
    Port Python de `valeurAttendueA` (frontend/src/utils/suivi.ts) : valeur
    interpolée linéairement à `date` entre (debut, depart) et (fin, arrivee).
    Doit rester IDENTIQUE à la version frontend — les deux calculent la même
    ligne « progression attendue » et le même « attendu aujourd'hui », côté
    écran pour l'un, côté exports Excel/PDF pour l'autre.
    """
    depart = float(depart)
    arrivee = float(arrivee)
    if not debut or not fin or fin <= debut:
        return arrivee
    t = min(1.0, max(0.0, (date - debut).days / (fin - debut).days))
    return depart + (arrivee - depart) * t


def taux_de(valeur, cible):
    if valeur is None or not cible:
        return None
    return round(float(valeur) / float(cible) * 1000) / 10


def ecart_texte(valeur_reelle, valeur_attendue, unite=""):
    if valeur_reelle is None or valeur_attendue is None:
        return None
    ecart = round((float(valeur_reelle) - float(valeur_attendue)) * 10) / 10
    suffixe = f" {unite}" if unite else ""
    if ecart > 0:
        return f"{ecart}{suffixe} de plus que prévu à cette date"
    if ecart < 0:
        return f"{abs(ecart)}{suffixe} de moins que prévu à cette date"
    return "exactement comme prévu à cette date"


def construire_dashboard_suivi(projet) -> dict:
    """
    Construit le même dict que renvoie l'API `suivi_dashboard_projet` —
    extrait ici pour être réutilisé tel quel par les exports Excel/PDF, qui
    ont besoin de repartir exactement des mêmes chiffres que ceux affichés à
    l'écran (pas de recalcul séparé qui pourrait diverger).
    """
    from apps.indicators.services import (
        indicateurs_pour_projet,
        palier_pour_taux,
        paliers_pour,
        taux_realisation,
        valeur_realisee_totale,
    )
    from apps.projects.models import Activite
    from apps.reports.services import (
        statut_global,
        taux_execution_financiere_global,
        taux_execution_physique_global,
    )

    def _serialiser_palier(palier):
        if palier is None:
            return None
        return {"id": palier.id, "libelle": palier.libelle, "couleur": palier.couleur, "borne_min": palier.borne_min}

    indicateurs_detail = []
    for indicateur in indicateurs_pour_projet(projet.id).select_related("activite"):
        taux = taux_realisation(valeur_realisee_totale(indicateur), indicateur.valeur_cible)
        historique = []
        cumul = Decimal("0")
        for v in indicateur.valeurs.order_by("periode_fin"):
            cumul += v.valeur_realisee
            historique.append(
                {
                    "id": v.id,
                    "periode_debut": v.periode_debut,
                    "periode_fin": v.periode_fin,
                    "valeur_realisee": v.valeur_realisee,
                    "valeur_cumulee": cumul,
                    "commentaire": v.commentaire,
                    "taux": taux_realisation(cumul, indicateur.valeur_cible),
                }
            )
        if indicateur.activite_id and indicateur.activite.date_debut and indicateur.activite.date_fin:
            periode_debut_planifiee = indicateur.activite.date_debut
            periode_fin_planifiee = indicateur.activite.date_fin
        else:
            periode_debut_planifiee = projet.date_debut
            periode_fin_planifiee = projet.date_fin
        palier = palier_pour_taux(taux, paliers_pour(indicateur=indicateur, projet=projet))
        indicateurs_detail.append(
            {
                "id": indicateur.id,
                "libelle": indicateur.libelle,
                "unite": indicateur.unite,
                "valeur_reference": indicateur.valeur_reference,
                "valeur_cible": indicateur.valeur_cible,
                "taux_actuel": taux,
                "palier_actuel": _serialiser_palier(palier),
                "periode_debut_planifiee": periode_debut_planifiee,
                "periode_fin_planifiee": periode_fin_planifiee,
                "historique": historique,
            }
        )

    activites_detail = []
    activites = (
        Activite.objects.filter(objectif_specifique__objectif_general__projet=projet)
        .prefetch_related("sous_activites", "points_suivi", "sous_activites__points_suivi")
    )
    for activite in activites:
        historique = []
        cumul_quantite = Decimal("0")
        cumul_budget = Decimal("0")
        for p in activite.points_suivi.order_by("periode_fin"):
            cumul_quantite += p.quantite_realisee or Decimal("0")
            cumul_budget += p.budget_realise or Decimal("0")
            historique.append(
                {
                    "id": p.id,
                    "periode_debut": p.periode_debut,
                    "periode_fin": p.periode_fin,
                    "quantite_realisee": p.quantite_realisee,
                    "quantite_cumulee": cumul_quantite,
                    "budget_realise": p.budget_realise,
                    "budget_cumule": cumul_budget,
                    "statut": p.statut,
                    "commentaire": p.commentaire,
                }
            )
        sous_activites_detail = []
        for sous_activite in activite.sous_activites.all():
            sous_historique = []
            cumul_sous = Decimal("0")
            for p in sous_activite.points_suivi.order_by("periode_fin"):
                cumul_sous += p.quantite_realisee or Decimal("0")
                sous_historique.append(
                    {
                        "id": p.id,
                        "periode_debut": p.periode_debut,
                        "periode_fin": p.periode_fin,
                        "quantite_realisee": p.quantite_realisee,
                        "quantite_cumulee": cumul_sous,
                        "statut": p.statut,
                        "commentaire": p.commentaire,
                    }
                )
            sous_activites_detail.append(
                {
                    "id": sous_activite.id,
                    "libelle": sous_activite.libelle,
                    "statut": sous_activite.statut,
                    "quantite_prevue": sous_activite.quantite_prevue,
                    "unite_quantite": sous_activite.unite_quantite,
                    "date_debut": sous_activite.date_debut,
                    "date_fin": sous_activite.date_fin,
                    "historique": sous_historique,
                }
            )
        palier_activite = palier_pour_taux(activite.taux_realisation, paliers_pour(activite=activite, projet=projet))
        activites_detail.append(
            {
                "id": activite.id,
                "code_activite": activite.code_activite,
                "libelle": activite.libelle,
                "statut": activite.statut,
                "valeur_reference": activite.valeur_reference,
                "quantite_prevue": activite.quantite_prevue,
                "unite_quantite": activite.unite_quantite,
                "budget_alloue": activite.budget_alloue,
                "date_debut": activite.date_debut,
                "date_fin": activite.date_fin,
                "taux_realisation": activite.taux_realisation,
                "taux_execution_financiere": activite.taux_execution_financiere,
                "palier_actuel": _serialiser_palier(palier_activite),
                "sous_activites": sous_activites_detail,
                "historique": historique,
            }
        )

    return {
        "projet": {"id": projet.id, "code": projet.code, "nom": projet.nom, "statut": projet.statut},
        "taux_execution_physique_global": taux_execution_physique_global(projet),
        "taux_execution_financiere_global": taux_execution_financiere_global(projet),
        "statut_global": statut_global(projet),
        "indicateurs": indicateurs_detail,
        "activites": activites_detail,
    }


def dernier_point_suivi(activite=None, sous_activite=None):
    from .models import PointSuivi

    qs = PointSuivi.objects.filter(activite=activite) if activite else PointSuivi.objects.filter(sous_activite=sous_activite)
    return qs.order_by("-periode_fin").first()


def synchroniser_activite_depuis_suivi(activite):
    from .models import PointSuivi

    points = PointSuivi.objects.filter(activite=activite)
    totaux = points.aggregate(quantite=Sum("quantite_realisee"), budget=Sum("budget_realise"))
    activite.quantite_realisee = totaux["quantite"]
    activite.budget_realise = totaux["budget"]
    dernier = points.order_by("-periode_fin").first()
    if dernier and dernier.statut:
        activite.statut = dernier.statut
    activite.save(update_fields=["quantite_realisee", "budget_realise", "statut", "updated_at"])


def synchroniser_sous_activite_depuis_suivi(sous_activite):
    from .models import PointSuivi

    points = PointSuivi.objects.filter(sous_activite=sous_activite)
    totaux = points.aggregate(quantite=Sum("quantite_realisee"))
    sous_activite.quantite_realisee = totaux["quantite"]
    dernier = points.order_by("-periode_fin").first()
    if dernier and dernier.statut:
        sous_activite.statut = dernier.statut
    sous_activite.save(update_fields=["quantite_realisee", "statut", "updated_at"])
