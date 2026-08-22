from django.contrib import admin

from .models import NiveauAdministratif, Zone


@admin.register(NiveauAdministratif)
class NiveauAdministratifAdmin(admin.ModelAdmin):
    list_display = ("pays", "nom_niveau", "ordre", "niveau_parent")
    list_filter = ("pays",)
    search_fields = ("nom_niveau",)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("nom", "niveau_administratif", "parent")
    list_filter = ("niveau_administratif__pays", "niveau_administratif")
    search_fields = ("nom",)
