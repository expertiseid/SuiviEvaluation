from django.apps import apps as django_apps
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.core.permissions import HasGlobalVisibilityOrAssigned


@api_view(["GET"])
@permission_classes([HasGlobalVisibilityOrAssigned])
def historique_generique(request, app_label, model_name, object_id):
    """
    Historique générique pour n'importe quel modèle suivi par
    django-simple-history, réutilisable côté frontend sans dupliquer la
    logique par entité : GET /api/v1/audit/{app}/{model}/{id}/historique/
    """
    model = django_apps.get_model(app_label, model_name)
    instance = get_object_or_404(model, pk=object_id)

    if not hasattr(instance, "history"):
        return Response({"detail": "Ce modèle n'a pas d'historique."}, status=400)

    records = list(instance.history.order_by("-history_date"))
    entries = []
    for i, record in enumerate(records):
        changements = []
        if i + 1 < len(records):
            delta = record.diff_against(records[i + 1])
            changements = [
                {"champ": c.field, "ancienne_valeur": c.old, "nouvelle_valeur": c.new} for c in delta.changes
            ]
        entries.append(
            {
                "date": record.history_date,
                "utilisateur": str(record.history_user) if record.history_user else None,
                "type": record.get_history_type_display(),
                "changements": changements,
            }
        )
    return Response(entries)
