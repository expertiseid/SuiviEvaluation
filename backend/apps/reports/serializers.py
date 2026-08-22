from rest_framework import serializers

from .models import RapportSuivi
from .services import (
    statistiques_beneficiaires,
    statistiques_zones,
    statut_global,
    taux_execution_financiere_global,
    taux_execution_physique_global,
)


class RapportSuiviSerializer(serializers.ModelSerializer):
    projet_nom = serializers.StringRelatedField(source="projet", read_only=True)
    redige_par_nom = serializers.StringRelatedField(source="redige_par", read_only=True)
    valide_par_nom = serializers.StringRelatedField(source="valide_par", read_only=True)
    taux_execution_physique_global = serializers.SerializerMethodField()
    taux_execution_financiere_global = serializers.SerializerMethodField()
    statut_global = serializers.SerializerMethodField()
    statistiques_zones = serializers.SerializerMethodField()
    statistiques_beneficiaires = serializers.SerializerMethodField()

    class Meta:
        model = RapportSuivi
        fields = (
            "id",
            "projet",
            "projet_nom",
            "periode_debut",
            "periode_fin",
            "type_rapport",
            "redige_par",
            "redige_par_nom",
            "contenu",
            "statut",
            "date_validation",
            "valide_par",
            "valide_par_nom",
            "taux_execution_physique_global",
            "taux_execution_financiere_global",
            "statut_global",
            "statistiques_zones",
            "statistiques_beneficiaires",
        )
        read_only_fields = ("statut", "date_validation", "valide_par", "redige_par")

    def get_taux_execution_physique_global(self, obj):
        return taux_execution_physique_global(obj.projet)

    def get_taux_execution_financiere_global(self, obj):
        return taux_execution_financiere_global(obj.projet)

    def get_statut_global(self, obj):
        return statut_global(obj.projet)

    def get_statistiques_zones(self, obj):
        return statistiques_zones(obj.projet)

    def get_statistiques_beneficiaires(self, obj):
        return statistiques_beneficiaires(obj.projet)

    def create(self, validated_data):
        validated_data["redige_par"] = self.context["request"].user
        return super().create(validated_data)
