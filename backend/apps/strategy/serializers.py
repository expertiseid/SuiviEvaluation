from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import CadreStrategique, ElementStrategique, TypeNiveau


class CadreStrategiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CadreStrategique
        fields = ("id", "nom", "description", "created_at")


class TypeNiveauSerializer(serializers.ModelSerializer):
    niveau_parent_nom = serializers.StringRelatedField(source="niveau_parent", read_only=True)

    class Meta:
        model = TypeNiveau
        fields = (
            "id",
            "cadre_strategique",
            "nom_niveau",
            "ordre",
            "niveau_parent",
            "niveau_parent_nom",
            "saut_niveau_autorise",
            "aide_code",
        )


class ElementStrategiqueSerializer(serializers.ModelSerializer):
    type_niveau_nom = serializers.StringRelatedField(source="type_niveau", read_only=True)
    element_parent_nom = serializers.StringRelatedField(source="element_parent", read_only=True)

    class Meta:
        model = ElementStrategique
        fields = (
            "id",
            "type_niveau",
            "type_niveau_nom",
            "element_parent",
            "element_parent_nom",
            "code",
            "nom",
            "description",
        )

    def validate(self, attrs):
        instance = ElementStrategique(
            id=getattr(self.instance, "id", None),
            type_niveau=attrs.get("type_niveau", getattr(self.instance, "type_niveau", None)),
            element_parent=attrs.get("element_parent", getattr(self.instance, "element_parent", None)),
        )
        try:
            instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return attrs
