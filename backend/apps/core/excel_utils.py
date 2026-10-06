"""
Utilitaires Excel partagés entre tous les générateurs de modèles
d'import/export de la plateforme.
"""
from openpyxl.styles import Border, Side

# Bordure fine sur toutes les cellules d'un tableau, y compris les cellules
# vides — sans ça, un tableau à colonnes fixes dont beaucoup de cellules
# restent vides (feuille clé-valeur, hiérarchie à une colonne par niveau)
# donne une impression de décalage aléatoire au lieu d'un vrai tableau.
BORDURE_TABLEAU = Border(
    left=Side(style="thin", color="B0B0B0"),
    right=Side(style="thin", color="B0B0B0"),
    top=Side(style="thin", color="B0B0B0"),
    bottom=Side(style="thin", color="B0B0B0"),
)


def quadriller(feuille, *, min_row=1, max_row=None, min_col=1, max_col):
    """Applique BORDURE_TABLEAU à toute une plage rectangulaire de cellules."""
    max_row = max_row or feuille.max_row
    for ligne in feuille.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col):
        for cellule in ligne:
            cellule.border = BORDURE_TABLEAU


def figer_entete(feuille, ligne_entete=1):
    """
    Fige la ligne d'en-tête (colonnes figées comprises) pour qu'elle reste
    visible lors du défilement d'un tableau à beaucoup de lignes — facilite
    la saisie sur les modèles d'import.
    """
    feuille.freeze_panes = feuille.cell(row=ligne_entete + 1, column=1).coordinate
