from rest_framework import serializers

from .models import PointSuivi


class PointSuiviSerializer(serializers.ModelSerializer):
    """
    validators = [] : sans ça, DRF détecte les UniqueConstraint conditionnelles
    du modèle (activite+période, sous_activite+période — chacune valide
    seulement quand son FK est non-nul) et force à tort `activite` ET
    `sous_activite` en `required=True` tous les deux, alors qu'ils sont
    mutuellement exclusifs. La vérification d'unicité est donc refaite à la
    main dans validate() ci-dessous.
    """

    activite_libelle = serializers.StringRelatedField(source="activite", read_only=True)
    sous_activite_libelle = serializers.StringRelatedField(source="sous_activite", read_only=True)
    saisi_par_nom = serializers.StringRelatedField(source="saisi_par", read_only=True)

    class Meta:
        model = PointSuivi
        validators = []
        fields = (
            "id",
            "activite",
            "activite_libelle",
            "sous_activite",
            "sous_activite_libelle",
            "periode_debut",
            "periode_fin",
            "quantite_realisee",
            "budget_realise",
            "statut",
            "commentaire",
            "saisi_par",
            "saisi_par_nom",
            "date_saisie",
        )
        read_only_fields = ("saisi_par", "date_saisie")

    def validate(self, attrs):
        activite = attrs.get("activite") or getattr(self.instance, "activite", None)
        sous_activite = attrs.get("sous_activite") or getattr(self.instance, "sous_activite", None)
        if bool(activite) == bool(sous_activite):
            raise serializers.ValidationError(
                "Un point de suivi doit être rattaché soit à une activité, soit à une sous-activité "
                "(jamais les deux, jamais aucune)."
            )

        periode_debut = attrs.get("periode_debut") or getattr(self.instance, "periode_debut", None)
        periode_fin = attrs.get("periode_fin") or getattr(self.instance, "periode_fin", None)
        doublon = PointSuivi.objects.filter(
            activite=activite, sous_activite=sous_activite, periode_debut=periode_debut, periode_fin=periode_fin
        )
        if self.instance:
            doublon = doublon.exclude(pk=self.instance.pk)
        if doublon.exists():
            raise serializers.ValidationError(
                "Un point de suivi existe déjà pour cette période sur cette cible."
            )
        return attrs

    def create(self, validated_data):
        validated_data["saisi_par"] = self.context["request"].user
        return super().create(validated_data)
