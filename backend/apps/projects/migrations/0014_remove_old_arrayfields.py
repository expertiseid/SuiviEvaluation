from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0013_backfill_membres_responsables"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="activite",
            name="responsables_noms",
        ),
        migrations.RemoveField(
            model_name="equipe",
            name="membres_noms",
        ),
        migrations.RemoveField(
            model_name="historicalactivite",
            name="responsables_noms",
        ),
        migrations.RemoveField(
            model_name="historicalequipe",
            name="membres_noms",
        ),
    ]
