from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("beneficiaries", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="beneficiaire",
            name="pays",
            field=models.CharField(
                blank=True, help_text="Code ISO 3166-1 alpha-2 du pays (ex : BF, ML, NE).", max_length=2
            ),
        ),
    ]
