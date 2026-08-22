from django.contrib import admin

from .models import PointSuivi


@admin.register(PointSuivi)
class PointSuiviAdmin(admin.ModelAdmin):
    list_display = ("__str__", "quantite_realisee", "budget_realise", "statut", "saisi_par")
    list_filter = ("statut",)
