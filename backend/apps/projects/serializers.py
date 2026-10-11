from rest_framework import serializers

from .models import Activite, Equipe, NiveauActivite, ObjectifGeneral, ObjectifSpecifique, Projet, SousActivite


class NiveauActiviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NiveauActivite
        fields = ("id", "projet", "profondeur", "nom_niveau")


class EquipeSerializer(serializers.ModelSerializer):
    membres_noms = serializers.StringRelatedField(source="membres", many=True, read_only=True)

    class Meta:
        model = Equipe
        fields = ("id", "nom", "membres", "membres_noms", "date_debut_contrat", "date_fin_contrat")


class SousActiviteSerializer(serializers.ModelSerializer):
    """
    quantite_realisee/statut sont en lecture seule ici : ce sont des valeurs
    dérivées, synchronisées automatiquement depuis le dernier PointSuivi
    (apps.suivi) — la planification (ce formulaire) ne fixe que la cible, la
    saisie du réel se fait exclusivement depuis le module Suivi.
    """

    axe_strategique_libelle = serializers.StringRelatedField(source="axe_strategique", read_only=True)

    class Meta:
        model = SousActivite
        fields = (
            "id",
            "activite",
            "libelle",
            "axe_strategique",
            "axe_strategique_libelle",
            "quantite_prevue",
            "quantite_realisee",
            "unite_quantite",
            "date_debut",
            "date_fin",
            "statut",
        )
        read_only_fields = ("quantite_realisee", "statut")

    def validate(self, attrs):
        if "axe_strategique" in attrs and attrs["axe_strategique"] is not None:
            axe = attrs["axe_strategique"]
            activite = attrs.get("activite") or getattr(self.instance, "activite", None)
            cadre_projet = activite.objectif_specifique.objectif_general.projet.cadre_strategique_id
            # Projet sans cadre stratégique choisi : rien à quoi comparer, pas de restriction.
            if cadre_projet is not None and axe.type_niveau.cadre_strategique_id != cadre_projet:
                raise serializers.ValidationError(
                    {"axe_strategique": "Cet élément stratégique n'appartient pas au cadre stratégique du projet."}
                )
        return attrs


class ActiviteSerializer(serializers.ModelSerializer):
    """
    statut/quantite_realisee/budget_realise sont en lecture seule ici : ce
    sont des valeurs dérivées, synchronisées automatiquement depuis le
    dernier PointSuivi (apps.suivi) — la planification (ce formulaire/API)
    ne fixe que la cible, la saisie du réel se fait exclusivement depuis le
    module Suivi (qui, lui, écrit directement sur le modèle, hors de ce
    serializer). date_debut_reelle/date_fin_reelle restent écrivables ici :
    ce sont de simples dates jalons (pas un historique périodique), éditées
    depuis le module Suivi via une requête PATCH ciblée.
    """

    responsable_compte_nom = serializers.StringRelatedField(source="responsable", read_only=True)
    responsables_noms = serializers.StringRelatedField(source="responsables", many=True, read_only=True)
    equipe_responsable_nom = serializers.StringRelatedField(source="equipe_responsable", read_only=True)
    axe_strategique_libelle = serializers.StringRelatedField(source="axe_strategique", read_only=True)
    sous_activites = SousActiviteSerializer(many=True, read_only=True)
    enfants = serializers.SerializerMethodField()
    taux_realisation = serializers.ReadOnlyField()
    taux_execution_financiere = serializers.ReadOnlyField()
    alerte_retard = serializers.ReadOnlyField()

    class Meta:
        model = Activite
        fields = (
            "id",
            "objectif_specifique",
            "activite_parent",
            "code_activite",
            "libelle",
            "statut",
            "commentaire",
            "axe_strategique",
            "axe_strategique_libelle",
            "budget_alloue",
            "budget_realise",
            "valeur_reference",
            "quantite_prevue",
            "quantite_realisee",
            "unite_quantite",
            "date_debut",
            "date_fin",
            "date_debut_reelle",
            "date_fin_reelle",
            "nb_jours_planifies",
            "date_rappel",
            "responsables",
            "responsables_noms",
            "responsable",
            "responsable_compte_nom",
            "equipe_responsable",
            "equipe_responsable_nom",
            "sous_activites",
            "enfants",
            "taux_realisation",
            "taux_execution_financiere",
            "alerte_retard",
        )
        read_only_fields = ("statut", "quantite_realisee", "budget_realise")

    def get_enfants(self, obj):
        # Activités imbriquées sous celle-ci (voir Activite.activite_parent) —
        # même sérialiseur, récursif : chaque enfant peut lui-même avoir des
        # enfants (profondeur illimitée).
        return ActiviteSerializer(obj.enfants.all(), many=True, context=self.context).data

    def validate(self, attrs):
        if "axe_strategique" in attrs and attrs["axe_strategique"] is not None:
            axe = attrs["axe_strategique"]
            objectif_specifique = attrs.get("objectif_specifique") or getattr(self.instance, "objectif_specifique", None)
            cadre_projet = objectif_specifique.objectif_general.projet.cadre_strategique_id
            # Projet sans cadre stratégique choisi : rien à quoi comparer, pas de restriction.
            if cadre_projet is not None and axe.type_niveau.cadre_strategique_id != cadre_projet:
                raise serializers.ValidationError(
                    {"axe_strategique": "Cet élément stratégique n'appartient pas au cadre stratégique du projet."}
                )

        activite_parent = attrs.get("activite_parent") or getattr(self.instance, "activite_parent", None)
        objectif_specifique = attrs.get("objectif_specifique") or getattr(self.instance, "objectif_specifique", None)
        if activite_parent and objectif_specifique and activite_parent.objectif_specifique_id != objectif_specifique.id:
            raise serializers.ValidationError(
                {"activite_parent": "L'activité parente doit être rattachée au même objectif spécifique."}
            )
        return attrs

    def create(self, validated_data):
        # responsables (M2M) doit être retiré avant la création de l'instance
        # (comme le fait ModelSerializer.create() par défaut) — on reproduit
        # ce comportement à la main puisqu'on a besoin d'appeler clean() juste
        # avant le save() pour valider activite_parent.
        responsables = validated_data.pop("responsables", None)
        instance = Activite(**validated_data)
        instance.clean()
        instance.save()
        if responsables is not None:
            instance.responsables.set(responsables)
        return instance

    def update(self, instance, validated_data):
        responsables = validated_data.pop("responsables", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.clean()
        instance.save()
        if responsables is not None:
            instance.responsables.set(responsables)
        return instance


class ObjectifSpecifiqueSerializer(serializers.ModelSerializer):
    # Seulement les activités racines (sans activite_parent) : les activités
    # imbriquées apparaissent via ActiviteSerializer.enfants, pas ici — sinon
    # elles seraient dupliquées (une fois à plat, une fois nichées).
    activites = serializers.SerializerMethodField()

    class Meta:
        model = ObjectifSpecifique
        fields = ("id", "objectif_general", "libelle", "description", "activites")

    def get_activites(self, obj):
        racines = obj.activites.filter(activite_parent__isnull=True)
        return ActiviteSerializer(racines, many=True, context=self.context).data


class ObjectifGeneralSerializer(serializers.ModelSerializer):
    objectifs_specifiques = ObjectifSpecifiqueSerializer(many=True, read_only=True)

    class Meta:
        model = ObjectifGeneral
        fields = ("id", "projet", "libelle", "description", "objectifs_specifiques")

    def validate(self, attrs):
        projet = attrs.get("projet") or getattr(self.instance, "projet", None)
        if projet and not self.instance and ObjectifGeneral.objects.filter(projet=projet).exists():
            raise serializers.ValidationError("Ce projet a déjà un objectif général.")
        return attrs


class ProjetSerializer(serializers.ModelSerializer):
    """Lecture : FK affichées en clair + hiérarchie imbriquée."""

    partenaire_bailleur_nom = serializers.StringRelatedField(source="partenaire_bailleur", read_only=True)
    partenaire_mise_en_oeuvre_nom = serializers.StringRelatedField(source="partenaire_mise_en_oeuvre", read_only=True)
    partenaires_consortium_noms = serializers.StringRelatedField(source="partenaires_consortium", many=True, read_only=True)
    cadre_strategique_nom = serializers.StringRelatedField(source="cadre_strategique", read_only=True)
    objectif_general = serializers.SerializerMethodField()
    financement_bailleurs_total = serializers.ReadOnlyField()

    class Meta:
        model = Projet
        fields = (
            "id",
            "nom",
            "code",
            "pays",
            "partenaire_bailleur",
            "partenaire_bailleur_nom",
            "partenaire_mise_en_oeuvre",
            "partenaire_mise_en_oeuvre_nom",
            "partenaires_consortium",
            "partenaires_consortium_noms",
            "budget_total",
            "fonds_propres",
            "financement_bailleurs_total",
            "date_debut",
            "date_fin",
            "date_rappel",
            "statut",
            "type_mise_en_oeuvre",
            "zones",
            "cadre_strategique",
            "cadre_strategique_nom",
            "chef_de_projet_nom",
            "utilisateurs_affectes",
            "cible_totale",
            "cible_hommes",
            "cible_femmes",
            "cible_jeunes",
            "cible_pdi",
            "elements_capitalisation",
            "objectif_general",
        )

    def get_objectif_general(self, obj):
        og = getattr(obj, "objectif_general", None)
        return ObjectifGeneralSerializer(og).data if og else None


class ProjetWriteSerializer(serializers.ModelSerializer):
    """Écriture : uniquement les IDs en FK/M2M, pas de hiérarchie imbriquée."""

    class Meta:
        model = Projet
        fields = (
            "id",
            "nom",
            "code",
            "pays",
            "partenaire_bailleur",
            "partenaire_mise_en_oeuvre",
            "partenaires_consortium",
            "budget_total",
            "fonds_propres",
            "date_debut",
            "date_fin",
            "date_rappel",
            "statut",
            "type_mise_en_oeuvre",
            "zones",
            "cadre_strategique",
            "chef_de_projet_nom",
            "utilisateurs_affectes",
            "cible_totale",
            "cible_hommes",
            "cible_femmes",
            "cible_jeunes",
            "cible_pdi",
            "elements_capitalisation",
        )
