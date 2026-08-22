import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("strategy", "0006_backfill_cadre_strategique"),
    ]

    operations = [
        migrations.AlterField(
            model_name="typeniveau",
            name="cadre_strategique",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="types_niveaux",
                to="strategy.cadrestrategique",
            ),
        ),
    ]
