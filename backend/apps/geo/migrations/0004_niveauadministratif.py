from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0003_zone_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="NiveauAdministratif",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("pays", models.CharField(help_text="Code ISO 3166-1 alpha-2 du pays (ex : BF, ML, NE).", max_length=2)),
                ("nom_niveau", models.CharField(help_text="Ex : 'Région', 'Province', 'Commune', 'Village'...", max_length=150)),
                ("ordre", models.PositiveSmallIntegerField(help_text="Position dans la hiérarchie : 1 = niveau le plus élevé.")),
                (
                    "saut_niveau_autorise",
                    models.BooleanField(
                        default=True,
                        help_text="Autorise une zone de ce niveau à avoir une zone parente qui n'est pas du niveau "
                        "immédiatement supérieur — utile car la précision des données de terrain varie (parfois "
                        "seule la région est connue).",
                    ),
                ),
                ("aide_code", models.CharField(blank=True, help_text="Exemple affiché comme aide à la saisie (ex : 'Ex : Kadiogo').", max_length=100)),
                (
                    "niveau_parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="niveaux_enfants",
                        to="geo.niveauadministratif",
                    ),
                ),
            ],
            options={
                "verbose_name": "Niveau administratif",
                "verbose_name_plural": "Niveaux administratifs",
                "ordering": ("pays", "ordre"),
            },
        ),
        migrations.AddField(
            model_name="zone",
            name="niveau_administratif",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="zones",
                to="geo.niveauadministratif",
            ),
        ),
    ]
