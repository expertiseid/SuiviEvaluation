from django.db import migrations


def backfill_cadre_strategique(apps, schema_editor):
    Projet = apps.get_model("projects", "Projet")
    CadreStrategique = apps.get_model("strategy", "CadreStrategique")
    cadre_defaut = CadreStrategique.objects.order_by("id").first()
    if cadre_defaut is None:
        return
    Projet.objects.filter(cadre_strategique__isnull=True).update(cadre_strategique=cadre_defaut)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0006_projet_cadre_strategique_step1"),
        ("strategy", "0007_typeniveau_cadre_strategique_required"),
    ]

    operations = [
        migrations.RunPython(backfill_cadre_strategique, noop),
    ]
