from django.contrib import admin

from .models import Document, DocumentVersion, Dossier, PieceJustificative


@admin.register(PieceJustificative)
class PieceJustificativeAdmin(admin.ModelAdmin):
    list_display = ("nom", "type_document", "uploaded_by", "valeur_indicateur", "rapport_suivi", "created_at")
    list_filter = ("type_document",)


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ("nom", "projet", "parent", "cree_par")
    list_filter = ("projet",)


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ("version", "created_at")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("nom", "dossier", "projet", "type_document", "cree_par")
    list_filter = ("projet", "type_document")
    inlines = [DocumentVersionInline]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("document", "version", "uploaded_by", "created_at")
