import pytest
from rest_framework.test import APIClient

from apps.accounts.constants import ROLE_ADMIN, ROLE_ANIMATEUR_TERRAIN
from apps.accounts.models import User
from apps.strategy.models import CadreStrategique

from .models import Projet


@pytest.fixture
def cadre_strategique(db):
    return CadreStrategique.objects.create(nom="Cadre de test")


@pytest.mark.django_db
def test_animateur_non_affecte_ne_voit_aucun_projet(cadre_strategique):
    Projet.objects.create(
        nom="Projet X", code="PX-1", date_debut="2026-01-01", date_fin="2026-12-31",
        cadre_strategique=cadre_strategique,
    )
    animateur = User.objects.create_user(username="animateur1", password="x", role=ROLE_ANIMATEUR_TERRAIN)

    client = APIClient()
    client.force_authenticate(animateur)
    response = client.get("/api/v1/projets/")

    assert response.status_code == 200
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_animateur_affecte_voit_son_projet(cadre_strategique):
    projet = Projet.objects.create(
        nom="Projet Y", code="PY-1", date_debut="2026-01-01", date_fin="2026-12-31",
        cadre_strategique=cadre_strategique,
    )
    animateur = User.objects.create_user(username="animateur2", password="x", role=ROLE_ANIMATEUR_TERRAIN)
    projet.utilisateurs_affectes.add(animateur)

    client = APIClient()
    client.force_authenticate(animateur)
    response = client.get("/api/v1/projets/")

    assert response.status_code == 200
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_admin_voit_tous_les_projets(cadre_strategique):
    Projet.objects.create(
        nom="Projet A", code="PA-1", date_debut="2026-01-01", date_fin="2026-12-31",
        cadre_strategique=cadre_strategique,
    )
    Projet.objects.create(
        nom="Projet B", code="PB-1", date_debut="2026-01-01", date_fin="2026-12-31",
        cadre_strategique=cadre_strategique,
    )
    admin = User.objects.create_user(username="admin_test", password="x", role=ROLE_ADMIN)

    client = APIClient()
    client.force_authenticate(admin)
    response = client.get("/api/v1/projets/")

    assert response.status_code == 200
    assert response.data["count"] == 2
