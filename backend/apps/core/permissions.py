"""
Permissions DRF basées sur le champ `role` de l'utilisateur plutôt que sur
les Groups/Permissions Django natifs : les 5 rôles métier correspondent à
des niveaux d'accès fonctionnels transversaux (lecture seule / saisie /
validation / administration) qui ne collent pas à la sémantique CRUD
standard add/change/delete/view.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.constants import (
    ROLE_ADMIN,
    ROLES_VALIDATION_RAPPORT,
    ROLES_VISIBILITE_GLOBALE,
)


class IsAdmin(BasePermission):
    """Réservé au rôle Administrateur."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == ROLE_ADMIN)


class IsAdminOrReadOnly(BasePermission):
    """Lecture pour tout utilisateur authentifié, écriture réservée à l'Administrateur."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == ROLE_ADMIN


class IsAdminOrCreateForAuthenticated(BasePermission):
    """
    Lecture et création (POST) ouvertes à tout utilisateur authentifié — pour
    les référentiels légers créables « à la volée » depuis un autre
    formulaire (ex : nouvelle commune, nouveau bailleur saisi en tapant son
    nom) — modification et suppression réservées à l'Administrateur.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in (*SAFE_METHODS, "POST"):
            return True
        return request.user.role == ROLE_ADMIN


class HasGlobalVisibilityOrAssigned(BasePermission):
    """
    Autorise l'accès en lecture à tout utilisateur authentifié ; le filtrage
    fin par affectation (zones/projets) se fait dans get_queryset() de
    chaque viewset via has_global_visibility(request.user), pas ici.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanValidateReport(BasePermission):
    """Rôles habilités à faire passer un rapport de SOUMIS à VALIDE."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ROLES_VALIDATION_RAPPORT
        )


def has_global_visibility(user) -> bool:
    return user.role in ROLES_VISIBILITE_GLOBALE
