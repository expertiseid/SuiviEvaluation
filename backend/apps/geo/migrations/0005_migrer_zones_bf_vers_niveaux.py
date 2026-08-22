from django.db import migrations


NIVEAUX_BF = [
    ("REGION", "Région", 1, None),
    ("PROVINCE", "Province", 2, "REGION"),
    ("COMMUNE", "Commune", 3, "PROVINCE"),
    ("VILLAGE", "Village", 4, "COMMUNE"),
]


def migrer_vers_niveaux(apps, schema_editor):
    NiveauAdministratif = apps.get_model("geo", "NiveauAdministratif")
    Zone = apps.get_model("geo", "Zone")

    if not Zone.objects.exists():
        return

    niveau_par_code = {}
    for code, nom, ordre, code_parent in NIVEAUX_BF:
        niveau_par_code[code] = NiveauAdministratif.objects.create(
            pays="BF",
            nom_niveau=nom,
            ordre=ordre,
            niveau_parent=niveau_par_code.get(code_parent) if code_parent else None,
        )

    for zone in Zone.objects.all():
        zone.niveau_administratif = niveau_par_code[zone.type]
        zone.save(update_fields=["niveau_administratif"])


def revenir_en_arriere(apps, schema_editor):
    NiveauAdministratif = apps.get_model("geo", "NiveauAdministratif")
    NiveauAdministratif.objects.filter(pays="BF").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0004_niveauadministratif"),
    ]

    operations = [
        migrations.RunPython(migrer_vers_niveaux, revenir_en_arriere),
    ]
