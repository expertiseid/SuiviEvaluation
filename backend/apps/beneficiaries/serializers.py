from django.utils import timezone
from rest_framework import serializers

from .models import Beneficiaire, ParticipationProjet, SignalementDoublon, StatutParticulier, TypeActiviteBeneficiaire


class StatutParticulierSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatutParticulier
        fields = ("id", "code", "libelle")


class TypeActiviteBeneficiaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeActiviteBeneficiaire
        fields = ("id", "code", "libelle")


def calculer_age(date_naissance):
    if not date_naissance:
        return None
    aujourdhui = timezone.localdate()
    age = aujourdhui.year - date_naissance.year
    if (aujourdhui.month, aujourdhui.day) < (date_naissance.month, date_naissance.day):
        age -= 1
    return age


def tranche_age_de(age):
    """
    Tranches alignées sur la convention déjà utilisée dans l'app pour le
    statut particulier « Jeune » (moins de 35 ans) : 0-17 / 18-35 / 36-59 / 60+.
    """
    if age is None:
        return None
    if age < 18:
        return "0-17 ans"
    if age <= 35:
        return "18-35 ans"
    if age <= 59:
        return "36-59 ans"
    return "60 ans et plus"


class ParticipationProjetSerializer(serializers.ModelSerializer):
    projet_nom = serializers.StringRelatedField(source="projet", read_only=True)
    beneficiaire_nom = serializers.StringRelatedField(source="beneficiaire", read_only=True)
    activite_nom = serializers.StringRelatedField(source="activite", read_only=True)
    sous_activite_nom = serializers.StringRelatedField(source="sous_activite", read_only=True)

    class Meta:
        model = ParticipationProjet
        fields = (
            "id",
            "beneficiaire",
            "beneficiaire_nom",
            "projet",
            "projet_nom",
            "activite",
            "activite_nom",
            "sous_activite",
            "sous_activite_nom",
            "date_inscription",
            "role_dans_projet",
        )


class BeneficiaireSerializer(serializers.ModelSerializer):
    zone_nom = serializers.StringRelatedField(source="zone", read_only=True)
    participations = ParticipationProjetSerializer(many=True, read_only=True)
    age = serializers.SerializerMethodField()
    tranche_age = serializers.SerializerMethodField()

    class Meta:
        model = Beneficiaire
        fields = (
            "id",
            "nom",
            "prenom",
            "sexe",
            "date_naissance",
            "age",
            "tranche_age",
            "telephone",
            "numero_piece_identite",
            "type_piece",
            "pays",
            "zone",
            "zone_nom",
            "statuts_particuliers",
            "types_activite",
            "participations",
        )

    def get_age(self, obj):
        return calculer_age(obj.date_naissance)

    def get_tranche_age(self, obj):
        return tranche_age_de(calculer_age(obj.date_naissance))


class SignalementDoublonSerializer(serializers.ModelSerializer):
    beneficiaire_1_nom = serializers.StringRelatedField(source="beneficiaire_1", read_only=True)
    beneficiaire_2_nom = serializers.StringRelatedField(source="beneficiaire_2", read_only=True)

    class Meta:
        model = SignalementDoublon
        fields = (
            "id",
            "beneficiaire_1",
            "beneficiaire_1_nom",
            "beneficiaire_2",
            "beneficiaire_2_nom",
            "score",
            "methode",
            "statut",
            "traite_par",
            "date_traitement",
        )
        read_only_fields = ("traite_par", "date_traitement")
