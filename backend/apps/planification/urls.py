from django.urls import path

from . import views

urlpatterns = [
    path("planification/modele-import/", views.modele_import_complet, name="planification-modele-import"),
    path("planification/importer/", views.importer_complet, name="planification-importer"),
]
