from rest_framework import serializers

from .models import Beneficiaire, ParticipationProjet, SignalementDoublon, StatutParticulier


class StatutParticulierSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatutParticulier
        fields = ("id", "code", "libelle")


class ParticipationProjetSerializer(serializers.ModelSerializer):
    projet_nom = serializers.StringRelatedField(source="projet", read_only=True)

    class Meta:
        model = ParticipationProjet
        fields = ("id", "beneficiaire", "projet", "projet_nom", "date_inscription", "role_dans_projet")


class BeneficiaireSerializer(serializers.ModelSerializer):
    zone_nom = serializers.StringRelatedField(source="zone", read_only=True)
    participations = ParticipationProjetSerializer(many=True, read_only=True)

    class Meta:
        model = Beneficiaire
        fields = (
            "id",
            "nom",
            "prenom",
            "sexe",
            "date_naissance",
            "telephone",
            "numero_piece_identite",
            "type_piece",
            "pays",
            "zone",
            "zone_nom",
            "statuts_particuliers",
            "participations",
        )


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
