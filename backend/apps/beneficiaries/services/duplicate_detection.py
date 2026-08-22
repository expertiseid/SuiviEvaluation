"""
Détection de doublons bénéficiaires entre projets : jamais de fusion
automatique (trop risqué), uniquement un signalement à valider manuellement.

Deux mécanismes complémentaires :
1. Correspondance exacte sur le numéro de pièce d'identité (doublon quasi certain).
2. Similarité trigram (extension PostgreSQL pg_trgm) sur nom+prénom, croisée
   avec une correspondance de téléphone.
"""
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q

SEUIL_SIMILARITE_NOM = 0.4


def rechercher_doublons(beneficiaire):
    """Retourne une liste de dicts {candidat, score, methode} pour un bénéficiaire donné."""
    from ..models import Beneficiaire

    resultats = []
    autres = Beneficiaire.objects.exclude(pk=beneficiaire.pk)

    if beneficiaire.numero_piece_identite:
        for candidat in autres.filter(numero_piece_identite=beneficiaire.numero_piece_identite):
            resultats.append({"candidat": candidat, "score": 1.0, "methode": "PIECE_IDENTITE"})

    nom_complet = f"{beneficiaire.nom} {beneficiaire.prenom}"
    qs = autres.annotate(
        similarite=TrigramSimilarity("nom", beneficiaire.nom) + TrigramSimilarity("prenom", beneficiaire.prenom)
    ).filter(Q(similarite__gte=SEUIL_SIMILARITE_NOM))

    if beneficiaire.telephone:
        qs = qs.filter(Q(telephone=beneficiaire.telephone) | Q(similarite__gte=SEUIL_SIMILARITE_NOM * 1.5))

    for candidat in qs.exclude(pk__in=[r["candidat"].pk for r in resultats]):
        resultats.append(
            {"candidat": candidat, "score": round(float(candidat.similarite) / 2, 3), "methode": "SIMILARITE"}
        )

    return resultats
