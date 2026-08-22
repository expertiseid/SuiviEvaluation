from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("type", "lu")

    def get_queryset(self):
        return Notification.objects.filter(destinataire=self.request.user)

    @action(detail=False, methods=["get"], url_path="non-lues-count")
    def non_lues_count(self, request):
        count = self.get_queryset().filter(lu=False).count()
        return Response({"count": count})

    @action(detail=True, methods=["post"], url_path="marquer-lu")
    def marquer_lu(self, request, pk=None):
        notif = self.get_object()
        if not notif.lu:
            notif.lu = True
            notif.date_lecture = timezone.now()
            notif.save(update_fields=["lu", "date_lecture"])
        return Response(self.get_serializer(notif).data)

    @action(detail=False, methods=["post"], url_path="tout-marquer-lu")
    def tout_marquer_lu(self, request):
        self.get_queryset().filter(lu=False).update(lu=True, date_lecture=timezone.now())
        return Response({"status": "ok"})
