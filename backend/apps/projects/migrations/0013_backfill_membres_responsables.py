from django.db import migrations


def resoudre_intervenant(Intervenant, cache, nom_saisi):
    cle = nom_saisi.strip().lower()
    if cle in cache:
        return cache[cle]
    intervenant = Intervenant.objects.filter(nom__iexact=nom_saisi.strip()).first()
    if intervenant is None:
        intervenant = Intervenant.objects.create(nom=nom_saisi.strip(), prenom="")
    cache[cle] = intervenant
    return intervenant


def backfill(apps, schema_editor):
    Intervenant = apps.get_model("intervenants", "Intervenant")
    Equipe = apps.get_model("projects", "Equipe")
    Activite = apps.get_model("projects", "Activite")

    cache = {}

    for equipe in Equipe.objects.exclude(membres_noms=[]):
        for nom in equipe.membres_noms:
            if not nom.strip():
                continue
            equipe.membres.add(resoudre_intervenant(Intervenant, cache, nom))

    for activite in Activite.objects.exclude(responsables_noms=[]):
        for nom in activite.responsables_noms:
            if not nom.strip():
                continue
            activite.responsables.add(resoudre_intervenant(Intervenant, cache, nom))


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0012_add_membres_responsables_m2m"),
    ]

    operations = [
        migrations.RunPython(backfill, noop),
    ]
