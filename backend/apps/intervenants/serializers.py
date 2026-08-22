from rest_framework import serializers

from .models import Intervenant


class IntervenantSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.StringRelatedField(source="utilisateur", read_only=True)

    class Meta:
        model = Intervenant
        fields = (
            "id",
            "nom",
            "prenom",
            "fonction",
            "contact",
            "utilisateur",
            "utilisateur_nom",
            "projets_associes",
            "activites_associees",
        )
