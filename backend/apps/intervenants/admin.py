from django.contrib import admin

from .models import Intervenant


@admin.register(Intervenant)
class IntervenantAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "fonction", "contact", "utilisateur")
    search_fields = ("nom", "prenom")
    filter_horizontal = ("projets_associes", "activites_associees")
