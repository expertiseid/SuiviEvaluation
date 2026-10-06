from django.db.models import ProtectedError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdmin

from .models import User
from .serializers import UserSerializer, UserWriteSerializer


class UserViewSet(viewsets.ModelViewSet):
    """CRUD des utilisateurs — réservé à l'Administrateur, sauf /me/."""

    queryset = User.objects.all().order_by("username")
    filterset_fields = ("role", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return UserWriteSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ("me", "list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAdmin()]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        if instance == self.request.user:
            raise ValidationError({"detail": "Impossible de supprimer ton propre compte."})
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                {
                    "detail": "Impossible de supprimer cet utilisateur : il a déjà des données rattachées "
                    "(valeurs saisies, documents, points de suivi...). Désactive-le plutôt (Actif = Non)."
                }
            )
