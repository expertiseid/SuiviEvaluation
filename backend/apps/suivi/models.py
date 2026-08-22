from django.conf import settings
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint

from apps.core.models import TimestampedModel


class PointSuivi(TimestampedModel):
    """
    Saisie périodique de suivi pour une activité OU une sous-activité
    (jamais les deux) — la quantité et le budget réalisés sont ce qui a été
    accompli PENDANT cette période précise (un delta), pas un total cumulé :
    on additionne toutes les périodes d'une même activité/sous-activité pour
    obtenir le total réalisé à comparer à la cible (voir
    apps.suivi.services.synchroniser_activite_depuis_suivi).

    Sépare ce qui était jusqu'ici un simple instantané figé sur
    Activite/SousActivite (quantite_realisee/budget_realise/statut) en un
    historique complet, pour permettre au module Suivi d'afficher une
    évolution dans le temps — Activite/SousActivite restent synchronisés
    automatiquement sur la somme des points saisis (apps.suivi.services).
    """

    activite = models.ForeignKey(
        "projects.Activite", null=True, blank=True, on_delete=models.PROTECT, related_name="points_suivi"
    )
    sous_activite = models.ForeignKey(
        "projects.SousActivite", null=True, blank=True, on_delete=models.PROTECT, related_name="points_suivi"
    )
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    quantite_realisee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_realise = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Uniquement pertinent pour une activité — les sous-activités n'ont pas de budget propre.",
    )
    statut = models.CharField(max_length=20, blank=True, help_text="Statut au moment de cette saisie (facultatif).")
    commentaire = models.TextField(blank=True)
    saisi_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="points_suivi_saisis"
    )
    date_saisie = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Point de suivi"
        verbose_name_plural = "Points de suivi"
        ordering = ("-periode_fin",)
        constraints = [
            CheckConstraint(
                check=(
                    Q(activite__isnull=False, sous_activite__isnull=True)
                    | Q(activite__isnull=True, sous_activite__isnull=False)
                ),
                name="point_suivi_rattachement_unique",
            ),
            UniqueConstraint(
                fields=("activite", "periode_debut", "periode_fin"),
                name="point_suivi_activite_periode_unique",
                condition=Q(activite__isnull=False),
            ),
            UniqueConstraint(
                fields=("sous_activite", "periode_debut", "periode_fin"),
                name="point_suivi_sous_activite_periode_unique",
                condition=Q(sous_activite__isnull=False),
            ),
        ]

    def __str__(self):
        cible = self.activite or self.sous_activite
        return f"{cible} — {self.periode_debut} au {self.periode_fin}"
