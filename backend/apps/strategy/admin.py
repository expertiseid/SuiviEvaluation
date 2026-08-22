from django.contrib import admin

from .models import CadreStrategique, ElementStrategique, TypeNiveau


@admin.register(CadreStrategique)
class CadreStrategiqueAdmin(admin.ModelAdmin):
    list_display = ("nom", "created_at")


@admin.register(TypeNiveau)
class TypeNiveauAdmin(admin.ModelAdmin):
    list_display = ("cadre_strategique", "ordre", "nom_niveau", "niveau_parent", "saut_niveau_autorise")
    list_filter = ("cadre_strategique",)
    ordering = ("cadre_strategique", "ordre")


@admin.register(ElementStrategique)
class ElementStrategiqueAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "type_niveau", "element_parent")
    list_filter = ("type_niveau",)
