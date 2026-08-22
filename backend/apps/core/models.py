from django.db import models


class TimestampedModel(models.Model):
    """Ajoute created_at/updated_at à tout modèle qui en hérite."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
