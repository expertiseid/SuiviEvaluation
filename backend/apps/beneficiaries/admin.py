from django.contrib import admin

from .models import Beneficiaire, ParticipationProjet, SignalementDoublon, StatutParticulier, TypeActiviteBeneficiaire


class ParticipationProjetInline(admin.TabularInline):
    model = ParticipationProjet
    extra = 0


@admin.register(Beneficiaire)
class BeneficiaireAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "sexe", "telephone", "numero_piece_identite", "zone")
    list_filter = ("sexe", "zone", "statuts_particuliers", "types_activite")
    search_fields = ("nom", "prenom", "telephone", "numero_piece_identite")
    filter_horizontal = ("statuts_particuliers", "types_activite")
    inlines = [ParticipationProjetInline]


@admin.register(StatutParticulier)
class StatutParticulierAdmin(admin.ModelAdmin):
    list_display = ("code", "libelle")


@admin.register(TypeActiviteBeneficiaire)
class TypeActiviteBeneficiaireAdmin(admin.ModelAdmin):
    list_display = ("code", "libelle")


@admin.register(SignalementDoublon)
class SignalementDoublonAdmin(admin.ModelAdmin):
    list_display = ("beneficiaire_1", "beneficiaire_2", "methode", "score", "statut", "traite_par")
    list_filter = ("statut", "methode")
