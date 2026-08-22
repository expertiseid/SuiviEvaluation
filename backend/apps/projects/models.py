from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TimestampedModel


class Projet(TimestampedModel):
    class Statut(models.TextChoices):
        EN_PREPARATION = "EN_PREPARATION", "En préparation"
        EN_COURS = "EN_COURS", "En cours"
        CLOTURE = "CLOTURE", "Clôturé"

    class TypeMiseEnOeuvre(models.TextChoices):
        DIRECT = "DIRECT", "Direct"
        CONSORTIUM = "CONSORTIUM", "En consortium"

    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    pays = ArrayField(
        models.CharField(max_length=2),
        default=list,
        blank=True,
        help_text="Codes ISO 3166-1 alpha-2 des pays d'intervention (ex : BF, ML, NE).",
    )
    partenaire_bailleur = models.ForeignKey(
        "partners.Partenaire",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="projets",
        help_text="Bailleur principal (Partenaire.type=BAILLEUR).",
    )
    partenaire_mise_en_oeuvre = models.ForeignKey(
        "partners.Partenaire",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="projets_mise_en_oeuvre",
        help_text="Partenaire de mise en œuvre principal (Partenaire.type=MISE_EN_OEUVRE).",
    )
    partenaires_consortium = models.ManyToManyField(
        "partners.Partenaire",
        blank=True,
        related_name="projets_consortium",
        help_text="Partenaires du consortium — renseigné quand type_mise_en_oeuvre=CONSORTIUM.",
    )
    cadre_strategique = models.ForeignKey(
        "strategy.CadreStrategique",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="projets",
        help_text="Cadre stratégique auquel ce projet est rattaché — borne les éléments stratégiques "
        "proposés pour ses activités. Fortement recommandé mais pas obligatoire.",
    )
    budget_total = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, help_text="Coût total = fonds propres + financements bailleurs."
    )
    fonds_propres = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_PREPARATION)
    type_mise_en_oeuvre = models.CharField(
        max_length=20, choices=TypeMiseEnOeuvre.choices, default=TypeMiseEnOeuvre.DIRECT
    )
    zones = models.ManyToManyField("geo.Zone", blank=True, related_name="projets")
    chef_de_projet_nom = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nom du chef de projet — texte libre, indépendant d'un compte plateforme. Pour donner accès "
        "à la plateforme, ajoute la personne dans « Utilisateurs affectés » ci-dessous.",
    )
    utilisateurs_affectes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="projets_affectes",
        help_text="Utilisateurs (ex: animateurs, chefs de projet) autorisés sur ce projet.",
    )

    # Cible du projet, ventilée par catégorie de bénéficiaires
    cible_totale = models.PositiveIntegerField(null=True, blank=True)
    cible_hommes = models.PositiveIntegerField(null=True, blank=True)
    cible_femmes = models.PositiveIntegerField(null=True, blank=True)
    cible_jeunes = models.PositiveIntegerField(null=True, blank=True)
    cible_pdi = models.PositiveIntegerField(null=True, blank=True, verbose_name="Cible PDI")

    elements_capitalisation = models.TextField(
        blank=True, help_text="Saisi en fin de projet : leçons apprises, bonnes pratiques."
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ("-date_debut",)

    def __str__(self):
        return f"{self.code} — {self.nom}"

    @property
    def financement_bailleurs_total(self):
        from django.db.models import Sum

        return self.financements.aggregate(total=Sum("montant_finance"))["total"] or 0


class ObjectifGeneral(TimestampedModel):
    projet = models.OneToOneField(Projet, on_delete=models.PROTECT, related_name="objectif_general")
    libelle = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Objectif général"
        verbose_name_plural = "Objectifs généraux"

    def __str__(self):
        return self.libelle


class ObjectifSpecifique(TimestampedModel):
    objectif_general = models.ForeignKey(
        ObjectifGeneral, on_delete=models.PROTECT, related_name="objectifs_specifiques"
    )
    libelle = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Objectif spécifique"
        verbose_name_plural = "Objectifs spécifiques"

    def __str__(self):
        return self.libelle


class Equipe(TimestampedModel):
    nom = models.CharField(max_length=200, unique=True)
    membres = models.ManyToManyField(
        "intervenants.Intervenant",
        blank=True,
        related_name="equipes",
        help_text="Membres de l'équipe — personnes déjà enregistrées (créées à la volée si besoin).",
    )
    date_debut_contrat = models.DateField(null=True, blank=True)
    date_fin_contrat = models.DateField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Équipe"
        verbose_name_plural = "Équipes"

    def __str__(self):
        return self.nom


class Activite(TimestampedModel):
    class Statut(models.TextChoices):
        NON_REALISEE = "NON_REALISEE", "Non réalisée"
        EN_COURS = "EN_COURS", "En cours"
        REALISEE = "REALISEE", "Réalisée"

    objectif_specifique = models.ForeignKey(
        ObjectifSpecifique, on_delete=models.PROTECT, related_name="activites"
    )
    code_activite = models.CharField(
        max_length=30, blank=True, help_text="Codification interne (ex : AI1.1, AI1.1.2)."
    )
    libelle = models.CharField(max_length=300)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.NON_REALISEE)
    axe_strategique = models.ForeignKey(
        "strategy.ElementStrategique", null=True, blank=True, on_delete=models.SET_NULL, related_name="activites"
    )

    budget_alloue = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    budget_realise = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    valeur_reference = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur de base avant le démarrage de l'activité — une activité se suit alors comme un "
        "indicateur (valeur de départ → cible), utile pour tracer la progression attendue dans le temps.",
    )
    quantite_prevue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantite_realisee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unite_quantite = models.CharField(max_length=50, blank=True, help_text="Ex : producteurs, hectares, sessions…")

    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    date_debut_reelle = models.DateField(null=True, blank=True)
    date_fin_reelle = models.DateField(null=True, blank=True)
    nb_jours_planifies = models.PositiveIntegerField(null=True, blank=True)

    responsables = models.ManyToManyField(
        "intervenants.Intervenant",
        blank=True,
        related_name="activites_dont_responsable",
        help_text="Responsables de l'activité — personnes déjà enregistrées (créées à la volée si besoin).",
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="activites_responsable",
        help_text="Compte plateforme lié (optionnel) — nécessaire pour que le responsable reçoive des "
        "notifications.",
    )
    equipe_responsable = models.ForeignKey(
        Equipe, null=True, blank=True, on_delete=models.SET_NULL, related_name="activites"
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.libelle

    @property
    def taux_realisation(self):
        if not self.quantite_prevue:
            return None
        return round(float(self.quantite_realisee or 0) / float(self.quantite_prevue) * 100, 1)

    @property
    def taux_execution_financiere(self):
        if not self.budget_alloue:
            return None
        return round(float(self.budget_realise or 0) / float(self.budget_alloue) * 100, 1)

    @property
    def alerte_retard(self):
        from django.utils import timezone

        return bool(
            self.date_fin and self.date_fin < timezone.localdate() and self.statut != self.Statut.REALISEE
        )


class SousActivite(TimestampedModel):
    class Statut(models.TextChoices):
        PLANIFIEE = "PLANIFIEE", "Planifiée"
        EN_COURS = "EN_COURS", "En cours"
        TERMINEE = "TERMINEE", "Terminée"

    activite = models.ForeignKey(Activite, on_delete=models.PROTECT, related_name="sous_activites")
    libelle = models.CharField(max_length=300)
    axe_strategique = models.ForeignKey(
        "strategy.ElementStrategique", null=True, blank=True, on_delete=models.SET_NULL, related_name="sous_activites"
    )
    quantite_prevue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantite_realisee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    unite_quantite = models.CharField(max_length=50, blank=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.PLANIFIEE)

    history = HistoricalRecords()

    verbose_name = "Sous-activité"

    def __str__(self):
        return self.libelle
