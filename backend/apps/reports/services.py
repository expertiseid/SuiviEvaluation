"""
Calculs agrégés exposés par le rapport de suivi — jamais stockés, toujours
recalculés à la volée pour éviter toute désynchronisation.
"""
SEUIL_STATUT_ATTEINT = 80


def taux_execution_physique_global(projet):
    """Moyenne des taux de réalisation des activités du projet (ignore celles sans quantité prévue)."""
    from apps.projects.models import Activite

    activites = Activite.objects.filter(
        objectif_specifique__objectif_general__projet=projet, quantite_prevue__isnull=False
    )
    taux = [a.taux_realisation for a in activites if a.taux_realisation is not None]
    return round(sum(taux) / len(taux), 1) if taux else None


def taux_execution_financiere_global(projet):
    """Σ budget_realise / Σ budget_planifie sur toutes les activités du projet."""
    from django.db.models import Sum

    from apps.projects.models import Activite

    totaux = Activite.objects.filter(objectif_specifique__objectif_general__projet=projet).aggregate(
        realise=Sum("budget_realise"), planifie=Sum("budget_alloue")
    )
    planifie = totaux["planifie"] or 0
    if not planifie:
        return None
    return round(float(totaux["realise"] or 0) / float(planifie) * 100, 1)


def statut_global(projet):
    from apps.projects.models import Activite

    taux_phys = taux_execution_physique_global(projet)
    taux_fin = taux_execution_financiere_global(projet)

    en_retard = Activite.objects.filter(
        objectif_specifique__objectif_general__projet=projet
    ).exclude(statut=Activite.Statut.REALISEE).filter(date_fin__isnull=False)
    if any(a.alerte_retard for a in en_retard):
        return "EN_RETARD"

    if taux_phys is not None and taux_fin is not None and taux_phys >= SEUIL_STATUT_ATTEINT and taux_fin >= SEUIL_STATUT_ATTEINT:
        return "ATTEINT"
    return "EN_COURS"


def statistiques_zones(projet):
    from apps.beneficiaries.models import ParticipationProjet

    compteurs = {}
    for participation in ParticipationProjet.objects.filter(projet=projet).select_related("beneficiaire__zone"):
        zone = participation.beneficiaire.zone
        if zone:
            compteurs[zone.nom] = compteurs.get(zone.nom, 0) + 1
    return compteurs


def statistiques_beneficiaires(projet):
    from apps.beneficiaries.models import ParticipationProjet, SignalementDoublon

    beneficiaire_ids = list(
        ParticipationProjet.objects.filter(projet=projet).values_list("beneficiaire_id", flat=True).distinct()
    )
    doublons = SignalementDoublon.objects.filter(
        beneficiaire_1_id__in=beneficiaire_ids, beneficiaire_2_id__in=beneficiaire_ids
    ).count()
    return {"nombre_beneficiaires_uniques": len(beneficiaire_ids), "doublons_detectes": doublons}
