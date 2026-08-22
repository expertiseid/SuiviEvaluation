"""
Rôles métier, isolés dans un module sans dépendance vers models.py
pour pouvoir être importés par apps/core/permissions.py sans risque
d'import circulaire.
"""

ROLE_ADMIN = "ADMIN"
ROLE_COORDO_GENERAL = "COORDO_GENERAL"
ROLE_CHARGE_SE = "CHARGE_SE"
ROLE_CHEF_PROJET = "CHEF_PROJET"
ROLE_CHEF_SERVICE = "CHEF_SERVICE"
ROLE_ANIMATEUR_TERRAIN = "ANIMATEUR_TERRAIN"

ROLE_CHOICES = [
    (ROLE_ADMIN, "Administrateur"),
    (ROLE_COORDO_GENERAL, "Coordonnateur général"),
    (ROLE_CHARGE_SE, "Chargé de Suivi-Évaluation"),
    (ROLE_CHEF_PROJET, "Chef de projet"),
    (ROLE_CHEF_SERVICE, "Chef de service"),
    (ROLE_ANIMATEUR_TERRAIN, "Animateur de terrain"),
]

# Rôles ayant une visibilité globale en lecture (tous les projets/zones)
ROLES_VISIBILITE_GLOBALE = {ROLE_ADMIN, ROLE_COORDO_GENERAL, ROLE_CHARGE_SE}

# Rôles habilités à valider un rapport de suivi
ROLES_VALIDATION_RAPPORT = {ROLE_ADMIN, ROLE_COORDO_GENERAL, ROLE_CHARGE_SE}

# Rôles notifiés lors de la modification d'une activité déjà planifiée
ROLES_NOTIFIEES_MODIFICATION_ACTIVITE = {ROLE_COORDO_GENERAL, ROLE_CHARGE_SE}
