from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("intervenants", "0001_initial"),
        ("projects", "0011_activite_zones_responsables_multiples"),
    ]

    operations = [
        migrations.AddField(
            model_name="activite",
            name="responsables",
            field=models.ManyToManyField(
                blank=True,
                help_text="Responsables de l'activité — personnes déjà enregistrées (créées à la volée si besoin).",
                related_name="activites_dont_responsable",
                to="intervenants.intervenant",
            ),
        ),
        migrations.AddField(
            model_name="equipe",
            name="membres",
            field=models.ManyToManyField(
                blank=True,
                help_text="Membres de l'équipe — personnes déjà enregistrées (créées à la volée si besoin).",
                related_name="equipes",
                to="intervenants.intervenant",
            ),
        ),
    ]
