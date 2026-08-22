from django.urls import path

from .views import historique_generique

urlpatterns = [
    path(
        "audit/<str:app_label>/<str:model_name>/<int:object_id>/historique/",
        historique_generique,
        name="audit-historique",
    ),
]
