from django.contrib import admin

from .models import Bailleur, Financement, Partenaire


@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ("nom", "type", "contact", "email", "telephone")
    list_filter = ("type",)
    search_fields = ("nom",)


class FinancementInline(admin.TabularInline):
    model = Financement
    extra = 0


@admin.register(Bailleur)
class BailleurAdmin(admin.ModelAdmin):
    list_display = ("nom", "type", "contact")
    list_filter = ("type",)
    search_fields = ("nom",)
    inlines = [FinancementInline]


@admin.register(Financement)
class FinancementAdmin(admin.ModelAdmin):
    list_display = ("projet", "bailleur", "montant_finance")
    list_filter = ("bailleur",)
