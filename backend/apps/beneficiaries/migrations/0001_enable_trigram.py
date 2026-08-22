from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    """
    Active l'extension PostgreSQL pg_trgm, nécessaire à TrigramSimilarity
    utilisé par le service de détection de doublons bénéficiaires.
    Doit rester la toute première migration de cette app.
    """

    initial = True
    dependencies = []
    operations = [TrigramExtension()]
