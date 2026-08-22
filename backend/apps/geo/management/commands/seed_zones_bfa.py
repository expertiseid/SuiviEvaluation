import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.geo.models import NiveauAdministratif, Zone

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "bfa_regions_provinces.json"


class Command(BaseCommand):
    help = (
        "Charge les niveaux administratifs (Région > Province > Commune > Village) et les 17 régions / 47 "
        "provinces du Burkina Faso (source : limites administratives officielles) — communes et villages "
        "restent à ajouter librement au fil de la saisie."
    )

    def handle(self, *args, **options):
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

        region_niveau, _ = NiveauAdministratif.objects.get_or_create(
            pays="BF", nom_niveau="Région", defaults={"ordre": 1, "niveau_parent": None}
        )
        province_niveau, _ = NiveauAdministratif.objects.get_or_create(
            pays="BF", nom_niveau="Province", defaults={"ordre": 2, "niveau_parent": region_niveau}
        )
        NiveauAdministratif.objects.get_or_create(
            pays="BF", nom_niveau="Commune", defaults={"ordre": 3, "niveau_parent": province_niveau}
        )

        region_par_code = {}
        crees = 0
        for code, nom in data["regions"]:
            zone, cree = Zone.objects.get_or_create(
                code=code, niveau_administratif=region_niveau, defaults={"nom": nom}
            )
            region_par_code[code] = zone
            crees += int(cree)

        for code, nom, region_code in data["provinces"]:
            _, cree = Zone.objects.get_or_create(
                code=code,
                niveau_administratif=province_niveau,
                defaults={"nom": nom, "parent": region_par_code[region_code]},
            )
            crees += int(cree)

        total = len(data["regions"]) + len(data["provinces"])
        self.stdout.write(self.style.SUCCESS(f"{crees} zone(s) créée(s) sur {total} (régions + provinces)."))
