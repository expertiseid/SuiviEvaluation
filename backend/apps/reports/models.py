from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TimestampedModel


class RapportSuivi(TimestampedModel):
    class TypeRapport(models.TextChoices):
        MENSUEL = "MENSUEL", "Mensuel"
        TRIMESTRIEL = "TRIMESTRIEL", "Trimestriel"
        AUTRE = "AUTRE", "Autre"

    class Statut(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon"
        SOUMIS = "SOUMIS", "Soumis"
        VALIDE = "VALIDE", "Validé"

    projet = models.ForeignKey("projects.Projet", on_delete=models.PROTECT, related_name="rapports")
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    type_rapport = models.CharField(max_length=20, choices=TypeRapport.choices)
    redige_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="rapports_rediges"
    )
    contenu = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.BROUILLON)
    date_validation = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rapports_valides",
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ("-periode_fin",)

    def __str__(self):
        return f"Rapport {self.type_rapport} — {self.projet} ({self.periode_debut} au {self.periode_fin})"
