from rest_framework import serializers

from .models import Bailleur, Financement, Partenaire


class PartenaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partenaire
        fields = ("id", "nom", "type", "contact", "email", "telephone")


class BailleurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bailleur
        fields = ("id", "nom", "type", "contact")


class FinancementSerializer(serializers.ModelSerializer):
    bailleur_nom = serializers.StringRelatedField(source="bailleur", read_only=True)

    class Meta:
        model = Financement
        fields = ("id", "projet", "bailleur", "bailleur_nom", "montant_finance")
