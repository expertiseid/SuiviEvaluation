from django.db import models

from apps.core.models import TimestampedModel


class Partenaire(TimestampedModel):
    class TypePartenaire(models.TextChoices):
        BAILLEUR = "BAILLEUR", "Bailleur"
        MISE_EN_OEUVRE = "MISE_EN_OEUVRE", "Partenaire de mise en œuvre"

    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TypePartenaire.choices)
    contact = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ("nom",)

    def __str__(self):
        return self.nom


class Bailleur(TimestampedModel):
    """
    Entité dédiée aux bailleurs (distincte de Partenaire), pour porter le
    montant financé par projet via Financement — Partenaire.type=BAILLEUR
    reste utilisable pour la compatibilité, mais Bailleur est le modèle
    recommandé pour tout nouveau financement multi-bailleurs.
    """

    class TypeBailleur(models.TextChoices):
        INSTITUTIONNEL = "INSTITUTIONNEL", "Institutionnel"
        FONDATION = "FONDATION", "Fondation"
        COOPERATION_BILATERALE = "COOPERATION_BILATERALE", "Coopération bilatérale"
        AUTRE = "AUTRE", "Autre"

    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=30, choices=TypeBailleur.choices, default=TypeBailleur.AUTRE)
    contact = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ("nom",)

    def __str__(self):
        return self.nom


class Financement(TimestampedModel):
    """Table de jonction Projet-Bailleur portant le montant financé."""

    projet = models.ForeignKey("projects.Projet", on_delete=models.CASCADE, related_name="financements")
    bailleur = models.ForeignKey(Bailleur, on_delete=models.PROTECT, related_name="financements")
    montant_finance = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("projet", "bailleur"), name="financement_projet_bailleur_unique")
        ]

    def __str__(self):
        return f"{self.bailleur} → {self.projet} : {self.montant_finance}"
