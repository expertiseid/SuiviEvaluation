from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TimestampedModel


class StatutParticulier(TimestampedModel):
    """Référentiel extensible (PDI, Jeune, Femme, Personne handicapée, ...)."""

    code = models.CharField(max_length=50, unique=True)
    libelle = models.CharField(max_length=100)

    def __str__(self):
        return self.libelle


class Beneficiaire(TimestampedModel):
    class Sexe(models.TextChoices):
        FEMININ = "F", "Féminin"
        MASCULIN = "M", "Masculin"

    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    sexe = models.CharField(max_length=1, choices=Sexe.choices)
    date_naissance = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=30, blank=True, db_index=True)
    numero_piece_identite = models.CharField(max_length=50, blank=True, db_index=True)
    type_piece = models.CharField(max_length=50, blank=True)
    pays = models.CharField(
        max_length=2, blank=True, help_text="Code ISO 3166-1 alpha-2 du pays (ex : BF, ML, NE)."
    )
    zone = models.ForeignKey("geo.Zone", null=True, blank=True, on_delete=models.PROTECT, related_name="beneficiaires")
    statuts_particuliers = models.ManyToManyField(StatutParticulier, blank=True, related_name="beneficiaires")

    history = HistoricalRecords()

    class Meta:
        ordering = ("nom", "prenom")

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class ParticipationProjet(TimestampedModel):
    """
    Table de jonction explicite (plutôt qu'un simple M2M implicite) : c'est
    elle qui permet de suivre un même bénéficiaire à travers plusieurs
    projets/cycles dans la durée.
    """

    beneficiaire = models.ForeignKey(Beneficiaire, on_delete=models.PROTECT, related_name="participations")
    projet = models.ForeignKey("projects.Projet", on_delete=models.PROTECT, related_name="participations")
    date_inscription = models.DateField()
    role_dans_projet = models.CharField(max_length=150, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Participation à un projet"
        verbose_name_plural = "Participations aux projets"
        ordering = ("-date_inscription",)

    def __str__(self):
        return f"{self.beneficiaire} — {self.projet}"


class SignalementDoublon(TimestampedModel):
    class Statut(models.TextChoices):
        SIGNALE = "SIGNALE", "Signalé"
        ECARTE = "ECARTE", "Écarté (faux positif)"
        FUSIONNE = "FUSIONNE", "Fusionné"

    class Methode(models.TextChoices):
        PIECE_IDENTITE = "PIECE_IDENTITE", "Correspondance exacte pièce d'identité"
        SIMILARITE = "SIMILARITE", "Similarité nom/téléphone"

    beneficiaire_1 = models.ForeignKey(
        Beneficiaire, on_delete=models.PROTECT, related_name="signalements_comme_beneficiaire_1"
    )
    beneficiaire_2 = models.ForeignKey(
        Beneficiaire, on_delete=models.PROTECT, related_name="signalements_comme_beneficiaire_2"
    )
    score = models.DecimalField(max_digits=4, decimal_places=3, null=True, blank=True)
    methode = models.CharField(max_length=20, choices=Methode.choices)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.SIGNALE)
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="doublons_traites"
    )
    date_traitement = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Doublon potentiel : {self.beneficiaire_1} / {self.beneficiaire_2}"
