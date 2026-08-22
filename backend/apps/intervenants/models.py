from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class Intervenant(TimestampedModel):
    """
    Équipe/responsable de mise en œuvre — entité distincte de User pour
    couvrir les intervenants qui n'ont pas de compte sur la plateforme
    (ex: technicien d'un partenaire de mise en œuvre), tout en pouvant être
    lié à un compte utilisateur quand il en a un.
    """

    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    fonction = models.CharField(max_length=150, blank=True, help_text="Ex : Chef de projet, Animateur…")
    contact = models.CharField(max_length=150, blank=True)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="intervenant_profil",
    )
    projets_associes = models.ManyToManyField("projects.Projet", blank=True, related_name="intervenants")
    activites_associees = models.ManyToManyField("projects.Activite", blank=True, related_name="intervenants")

    class Meta:
        ordering = ("nom", "prenom")

    def __str__(self):
        return f"{self.nom} {self.prenom}"
