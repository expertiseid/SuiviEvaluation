from django.contrib import admin

from .models import RapportSuivi


@admin.register(RapportSuivi)
class RapportSuiviAdmin(admin.ModelAdmin):
    list_display = ("projet", "type_rapport", "periode_debut", "periode_fin", "statut", "redige_par", "valide_par")
    list_filter = ("statut", "type_rapport", "projet")
