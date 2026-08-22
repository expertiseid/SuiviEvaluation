from django.db import migrations


def backfill(apps, schema_editor):
    Activite = apps.get_model("projects", "Activite")

    for activite in Activite.objects.select_related(
        "objectif_specifique__objectif_general__projet", "equipe_responsable"
    ).prefetch_related("responsables", "equipe_responsable__membres"):
        projet = activite.objectif_specifique.objectif_general.projet
        intervenants = list(activite.responsables.all())
        if activite.equipe_responsable_id:
            intervenants += list(activite.equipe_responsable.membres.all())
        for intervenant in intervenants:
            intervenant.projets_associes.add(projet)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0014_remove_old_arrayfields"),
    ]

    operations = [
        migrations.RunPython(backfill, noop),
    ]
