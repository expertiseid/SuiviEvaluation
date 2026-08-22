import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0005_migrer_zones_bf_vers_niveaux"),
    ]

    operations = [
        migrations.AlterField(
            model_name="zone",
            name="niveau_administratif",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="zones",
                to="geo.niveauadministratif",
            ),
        ),
        migrations.RemoveField(
            model_name="zone",
            name="type",
        ),
        migrations.AlterModelOptions(
            name="zone",
            options={
                "ordering": ("niveau_administratif__ordre", "nom"),
                "verbose_name": "Zone d'intervention",
                "verbose_name_plural": "Zones d'intervention",
            },
        ),
    ]
