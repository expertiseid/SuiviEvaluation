"""
Suppression en cascade d'un Projet — les FK de la hiérarchie sont en
PROTECT (choix délibéré, pour ne jamais perdre une arborescence par
accident via un autre chemin de code), donc la suppression volontaire d'un
projet doit désimbriquer manuellement, des feuilles vers la racine, dans
une transaction.
"""
from django.db import transaction
from django.db.models import Q


def supprimer_projet_cascade(projet):
    from apps.beneficiaries.models import ParticipationProjet
    from apps.indicators.models import Indicateur, ValeurIndicateur
    from apps.reports.models import RapportSuivi
    from apps.suivi.models import PointSuivi

    from .models import Activite, ObjectifGeneral, ObjectifSpecifique, SousActivite

    with transaction.atomic():
        objectifs_generaux = ObjectifGeneral.objects.filter(projet=projet)
        objectifs_specifiques = ObjectifSpecifique.objects.filter(objectif_general__in=objectifs_generaux)
        activites = Activite.objects.filter(objectif_specifique__in=objectifs_specifiques)
        sous_activites = SousActivite.objects.filter(activite__in=activites)

        indicateurs = Indicateur.objects.filter(
            Q(projet=projet)
            | Q(objectif_general__in=objectifs_generaux)
            | Q(objectif_specifique__in=objectifs_specifiques)
            | Q(activite__in=activites)
        )

        ValeurIndicateur.objects.filter(indicateur__in=indicateurs).delete()
        indicateurs.delete()

        PointSuivi.objects.filter(Q(activite__in=activites) | Q(sous_activite__in=sous_activites)).delete()
        sous_activites.delete()
        activites.delete()
        objectifs_specifiques.delete()
        objectifs_generaux.delete()

        ParticipationProjet.objects.filter(projet=projet).delete()
        RapportSuivi.objects.filter(projet=projet).delete()

        # Documents/Dossiers/Financements sont déjà en CASCADE sur Projet,
        # supprimés automatiquement par le projet.delete() ci-dessous.
        projet.delete()


def supprimer_objectif_general_cascade(objectif_general):
    from apps.indicators.models import Indicateur, ValeurIndicateur
    from apps.suivi.models import PointSuivi

    from .models import Activite, ObjectifSpecifique, SousActivite

    with transaction.atomic():
        objectifs_specifiques = ObjectifSpecifique.objects.filter(objectif_general=objectif_general)
        activites = Activite.objects.filter(objectif_specifique__in=objectifs_specifiques)
        sous_activites = SousActivite.objects.filter(activite__in=activites)

        indicateurs = Indicateur.objects.filter(
            Q(objectif_general=objectif_general)
            | Q(objectif_specifique__in=objectifs_specifiques)
            | Q(activite__in=activites)
        )
        ValeurIndicateur.objects.filter(indicateur__in=indicateurs).delete()
        indicateurs.delete()

        PointSuivi.objects.filter(Q(activite__in=activites) | Q(sous_activite__in=sous_activites)).delete()
        sous_activites.delete()
        activites.delete()
        objectifs_specifiques.delete()
        objectif_general.delete()


def supprimer_objectif_specifique_cascade(objectif_specifique):
    from apps.indicators.models import Indicateur, ValeurIndicateur
    from apps.suivi.models import PointSuivi

    from .models import Activite, SousActivite

    with transaction.atomic():
        activites = Activite.objects.filter(objectif_specifique=objectif_specifique)
        sous_activites = SousActivite.objects.filter(activite__in=activites)
        indicateurs = Indicateur.objects.filter(
            Q(objectif_specifique=objectif_specifique) | Q(activite__in=activites)
        )
        ValeurIndicateur.objects.filter(indicateur__in=indicateurs).delete()
        indicateurs.delete()

        PointSuivi.objects.filter(Q(activite__in=activites) | Q(sous_activite__in=sous_activites)).delete()
        sous_activites.delete()
        activites.delete()
        objectif_specifique.delete()


def synchroniser_projets_associes_equipe(equipe):
    for activite in equipe.activites.all():
        synchroniser_projets_associes_activite(activite)


def synchroniser_projets_associes_activite(activite):
    """
    Un intervenant référencé comme responsable d'une activité, ou comme
    membre de son équipe responsable, doit apparaître dans l'onglet
    « Équipe de projet » du projet concerné sans geste manuel supplémentaire.
    """
    projet = activite.objectif_specifique.objectif_general.projet
    intervenants = list(activite.responsables.all())
    if activite.equipe_responsable_id:
        intervenants += list(activite.equipe_responsable.membres.all())
    for intervenant in intervenants:
        intervenant.projets_associes.add(projet)


def supprimer_activite_cascade(activite):
    from apps.indicators.models import Indicateur, ValeurIndicateur
    from apps.suivi.models import PointSuivi

    from .models import SousActivite

    with transaction.atomic():
        indicateurs = Indicateur.objects.filter(activite=activite)
        ValeurIndicateur.objects.filter(indicateur__in=indicateurs).delete()
        indicateurs.delete()

        sous_activites = SousActivite.objects.filter(activite=activite)
        PointSuivi.objects.filter(Q(activite=activite) | Q(sous_activite__in=sous_activites)).delete()
        sous_activites.delete()
        activite.delete()


def supprimer_sous_activite_cascade(sous_activite):
    from apps.suivi.models import PointSuivi

    with transaction.atomic():
        PointSuivi.objects.filter(sous_activite=sous_activite).delete()
        sous_activite.delete()
