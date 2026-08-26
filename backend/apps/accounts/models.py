from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import NIVEAU_ACCES_CHOICES, NIVEAU_ACCES_LECTURE_ECRITURE, ROLE_CHOICES


class User(AbstractUser):
    """
    Utilisateur custom défini dès le premier commit (AUTH_USER_MODEL).
    Le rattachement aux projets se fait dans l'autre sens, via
    Projet.utilisateurs_affectes (voir apps.projects.models), pour éviter
    toute dépendance circulaire de migration entre accounts et projects.
    """

    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    niveau_acces = models.CharField(
        max_length=20,
        choices=NIVEAU_ACCES_CHOICES,
        default=NIVEAU_ACCES_LECTURE_ECRITURE,
        help_text="Lecture seule = consultation uniquement ; Lecture et écriture = peut créer/modifier dans "
        "son périmètre. Un Administrateur a toujours un accès complet, indépendamment de ce champ.",
    )
    telephone = models.CharField(max_length=30, blank=True)
    zones_affectees = models.ManyToManyField(
        "geo.Zone",
        blank=True,
        related_name="utilisateurs_affectes",
        help_text="Zones auxquelles l'utilisateur (ex: animateur de terrain) est restreint.",
    )

    def __str__(self):
        return self.get_full_name() or self.username
