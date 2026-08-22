from decimal import Decimal

from .models import PalierAlerte
from .services import palier_pour_taux, taux_realisation


def test_taux_realisation_calcule_pourcentage():
    assert taux_realisation(Decimal("40"), Decimal("100")) == 40.0
    assert taux_realisation(Decimal("0"), Decimal("100")) == 0.0
    assert taux_realisation(Decimal("50"), Decimal("0")) == 0.0


def _paliers(*bornes_libelles):
    return [
        PalierAlerte(borne_min=borne, libelle=libelle, couleur="#000000") for borne, libelle in bornes_libelles
    ]


def test_palier_pour_taux_applique_les_bornes():
    paliers = _paliers((0, "Critique"), (50, "À risque"), (80, "Conforme"))
    assert palier_pour_taux(40, paliers).libelle == "Critique"
    assert palier_pour_taux(60, paliers).libelle == "À risque"
    assert palier_pour_taux(90, paliers).libelle == "Conforme"
    assert palier_pour_taux(50, paliers).libelle == "À risque"


def test_palier_pour_taux_supporte_un_nombre_quelconque_de_paliers():
    paliers = _paliers((0, "Faible"), (20, "Moyen"), (50, "Bon"), (80, "Excellent"))
    assert palier_pour_taux(10, paliers).libelle == "Faible"
    assert palier_pour_taux(65, paliers).libelle == "Bon"
    assert palier_pour_taux(95, paliers).libelle == "Excellent"


def test_palier_pour_taux_sans_palier_ni_taux():
    assert palier_pour_taux(None, _paliers((0, "Critique"))) is None
    assert palier_pour_taux(50, []) is None
