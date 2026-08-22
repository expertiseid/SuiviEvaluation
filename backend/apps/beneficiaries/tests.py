import pytest

from .models import Beneficiaire
from .services.duplicate_detection import rechercher_doublons


@pytest.mark.django_db
def test_doublon_detecte_par_piece_identite_exacte():
    b1 = Beneficiaire.objects.create(nom="Traore", prenom="Awa", sexe="F", numero_piece_identite="CNIB123")
    b2 = Beneficiaire.objects.create(nom="Traore", prenom="Awa", sexe="F", numero_piece_identite="CNIB123")

    resultats = rechercher_doublons(b2)

    assert any(r["candidat"].pk == b1.pk and r["methode"] == "PIECE_IDENTITE" for r in resultats)


@pytest.mark.django_db
def test_beneficiaires_distincts_ne_sont_pas_signales():
    Beneficiaire.objects.create(nom="Sawadogo", prenom="Issa", sexe="M", numero_piece_identite="CNIB999")
    autre = Beneficiaire.objects.create(nom="Ouedraogo", prenom="Fatou", sexe="F", numero_piece_identite="CNIB111")

    resultats = rechercher_doublons(autre)

    assert resultats == []
