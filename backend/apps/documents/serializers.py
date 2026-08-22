from rest_framework import serializers

from .models import Document, DocumentVersion, Dossier, PieceJustificative


class PieceJustificativeSerializer(serializers.ModelSerializer):
    uploaded_by_nom = serializers.StringRelatedField(source="uploaded_by", read_only=True)

    class Meta:
        model = PieceJustificative
        fields = (
            "id",
            "fichier",
            "nom",
            "type_document",
            "uploaded_by",
            "uploaded_by_nom",
            "valeur_indicateur",
            "rapport_suivi",
            "created_at",
        )
        read_only_fields = ("uploaded_by", "created_at")

    def validate(self, attrs):
        valeur_indicateur = attrs.get("valeur_indicateur", getattr(self.instance, "valeur_indicateur", None))
        rapport_suivi = attrs.get("rapport_suivi", getattr(self.instance, "rapport_suivi", None))
        if bool(valeur_indicateur) == bool(rapport_suivi):
            raise serializers.ValidationError(
                "Une pièce justificative doit être rattachée à exactement une Valeur d'indicateur OU un Rapport de suivi."
            )
        return attrs

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)


class DossierSerializer(serializers.ModelSerializer):
    cree_par_nom = serializers.StringRelatedField(source="cree_par", read_only=True)

    class Meta:
        model = Dossier
        fields = ("id", "nom", "projet", "parent", "cree_par", "cree_par_nom")
        read_only_fields = ("cree_par",)

    def create(self, validated_data):
        validated_data["cree_par"] = self.context["request"].user
        return super().create(validated_data)


class DocumentVersionSerializer(serializers.ModelSerializer):
    uploaded_by_nom = serializers.StringRelatedField(source="uploaded_by", read_only=True)

    class Meta:
        model = DocumentVersion
        fields = ("id", "document", "fichier", "version", "uploaded_by", "uploaded_by_nom", "commentaire", "created_at")
        read_only_fields = ("version", "uploaded_by", "created_at")


class DocumentSerializer(serializers.ModelSerializer):
    cree_par_nom = serializers.StringRelatedField(source="cree_par", read_only=True)
    derniere_version = DocumentVersionSerializer(read_only=True)
    nombre_versions = serializers.IntegerField(source="versions.count", read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "nom",
            "dossier",
            "projet",
            "activite",
            "type_document",
            "description",
            "cree_par",
            "cree_par_nom",
            "derniere_version",
            "nombre_versions",
            "created_at",
        )
        read_only_fields = ("cree_par", "created_at")
