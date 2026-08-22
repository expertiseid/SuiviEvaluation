import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0007_backfill_cadre_strategique"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projet",
            name="cadre_strategique",
            field=models.ForeignKey(
                help_text="Cadre stratégique auquel ce projet est rattaché — borne les éléments "
                "stratégiques proposés pour ses activités.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="projets",
                to="strategy.cadrestrategique",
            ),
        ),
        migrations.AlterField(
            model_name="historicalprojet",
            name="cadre_strategique",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Cadre stratégique auquel ce projet est rattaché — borne les éléments "
                "stratégiques proposés pour ses activités.",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="strategy.cadrestrategique",
            ),
        ),
    ]
