from django.db import migrations


def creer_cadre_par_defaut(apps, schema_editor):
    CadreStrategique = apps.get_model("strategy", "CadreStrategique")
    TypeNiveau = apps.get_model("strategy", "TypeNiveau")

    if TypeNiveau.objects.filter(cadre_strategique__isnull=True).exists():
        cadre = CadreStrategique.objects.create(nom="Cadre stratégique", description="")
        TypeNiveau.objects.filter(cadre_strategique__isnull=True).update(cadre_strategique=cadre)


def inverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("strategy", "0005_cadrestrategique_alter_typeniveau_options_and_more"),
    ]

    operations = [
        migrations.RunPython(creer_cadre_par_defaut, inverse_noop),
    ]
