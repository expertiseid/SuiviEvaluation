import io

from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.accounts.constants import ROLES_VALIDATION_RAPPORT
from apps.core.permissions import CanValidateReport, HasGlobalVisibilityOrAssigned
from apps.notifications.models import Notification
from apps.notifications.services import notifier, notifier_par_role
from apps.projects.queryset_filters import visible_projets_ids

from .models import RapportSuivi
from .serializers import RapportSuiviSerializer


class RapportSuiviViewSet(viewsets.ModelViewSet):
    serializer_class = RapportSuiviSerializer
    permission_classes = (HasGlobalVisibilityOrAssigned,)
    filterset_fields = ("projet", "statut", "type_rapport")

    def get_queryset(self):
        return RapportSuivi.objects.select_related("projet", "redige_par", "valide_par").filter(
            projet__id__in=visible_projets_ids(self.request.user)
        )

    @action(detail=True, methods=["post"])
    def soumettre(self, request, pk=None):
        rapport = self.get_object()
        if rapport.statut != RapportSuivi.Statut.BROUILLON:
            raise PermissionDenied("Seul un rapport en brouillon peut être soumis.")
        rapport.statut = RapportSuivi.Statut.SOUMIS
        rapport.save(update_fields=["statut"])
        notifier_par_role(
            ROLES_VALIDATION_RAPPORT,
            Notification.Type.RAPPORT_SOUMIS,
            f"Rapport à valider : {rapport.projet.nom}",
            message=f"Rapport {rapport.get_type_rapport_display()} soumis par {rapport.redige_par}.",
            lien="/rapports",
            exclure=request.user,
        )
        return Response(self.get_serializer(rapport).data)

    @action(detail=True, methods=["post"], permission_classes=[CanValidateReport])
    def valider(self, request, pk=None):
        rapport = self.get_object()
        if rapport.statut != RapportSuivi.Statut.SOUMIS:
            raise PermissionDenied("Seul un rapport soumis peut être validé.")
        rapport.statut = RapportSuivi.Statut.VALIDE
        rapport.valide_par = request.user
        rapport.date_validation = timezone.now()
        rapport.save(update_fields=["statut", "valide_par", "date_validation"])
        notifier(
            [rapport.redige_par],
            Notification.Type.RAPPORT_VALIDE,
            f"Rapport validé : {rapport.projet.nom}",
            message=f"Votre rapport {rapport.get_type_rapport_display()} a été validé par {request.user}.",
            lien="/rapports",
        )
        return Response(self.get_serializer(rapport).data)

    @action(detail=True, methods=["get"], url_path="export/excel")
    def export_excel(self, request, pk=None):
        rapport = self.get_object()
        wb = Workbook()
        ws = wb.active
        ws.title = "Rapport de suivi"
        ws.append(["Projet", str(rapport.projet)])
        ws.append(["Type", rapport.get_type_rapport_display()])
        ws.append(["Période", f"{rapport.periode_debut} au {rapport.periode_fin}"])
        ws.append(["Statut", rapport.get_statut_display()])
        ws.append(["Rédigé par", str(rapport.redige_par)])
        ws.append([])
        ws.append(["Contenu"])
        ws.append([rapport.contenu])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename=rapport_{rapport.pk}.xlsx"
        return response

    @action(detail=True, methods=["get"], url_path="export/pdf")
    def export_pdf(self, request, pk=None):
        from weasyprint import HTML

        rapport = self.get_object()
        html_content = f"""
        <html><body style="font-family: sans-serif;">
        <h1>Rapport de suivi — {rapport.projet}</h1>
        <p><strong>Type :</strong> {rapport.get_type_rapport_display()}</p>
        <p><strong>Période :</strong> {rapport.periode_debut} au {rapport.periode_fin}</p>
        <p><strong>Statut :</strong> {rapport.get_statut_display()}</p>
        <p><strong>Rédigé par :</strong> {rapport.redige_par}</p>
        <h2>Contenu</h2>
        <p>{rapport.contenu}</p>
        </body></html>
        """
        pdf_bytes = HTML(string=html_content).write_pdf()
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename=rapport_{rapport.pk}.pdf"
        return response
