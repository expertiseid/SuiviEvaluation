"""
Exports avancés pour interopérabilité avec les outils de collecte (XLSForm,
pour KoboToolbox/ODK Collect) et d'analyse statistique (SPSS .sav).
"""
import io
import re
import tempfile

from openpyxl import Workbook

from .services import indicateurs_pour_projet


def _slug(texte: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_]", "_", texte.strip().lower())
    return re.sub(r"_+", "_", slug).strip("_")[:60]


def generer_xlsform(projet) -> bytes:
    """
    Génère un formulaire XLSForm (.xlsx) reprenant les indicateurs du projet,
    importable directement dans KoboToolbox/ODK Build pour la collecte
    mobile — sert de pont entre la plateforme et la collecte hors-ligne
    recommandée par le cahier des charges (KoboToolbox plutôt que du natif).
    """
    indicateurs = indicateurs_pour_projet(projet.id).order_by("libelle")

    wb = Workbook()
    survey = wb.active
    survey.title = "survey"
    survey.append(["type", "name", "label", "hint"])
    survey.append(["text", "periode", f"Période de collecte — {projet.nom}", ""])

    noms_utilises = set()
    for indicateur in indicateurs:
        nom = _slug(indicateur.libelle) or f"indicateur_{indicateur.id}"
        while nom in noms_utilises:
            nom = f"{nom}_{indicateur.id}"
        noms_utilises.add(nom)
        survey.append(["decimal", nom, indicateur.libelle, f"Unité : {indicateur.unite}"])

    choices = wb.create_sheet("choices")
    choices.append(["list_name", "name", "label"])

    settings_sheet = wb.create_sheet("settings")
    settings_sheet.append(["form_title", "form_id"])
    settings_sheet.append([f"Suivi {projet.nom}", f"suivi_{projet.code.lower()}"])

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def generer_spss(projet) -> bytes:
    """
    Exporte les valeurs d'indicateurs du projet en fichier SPSS .sav, pour
    analyse statistique externe — répond à l'exigence d'export ouvert et
    interopérable (pas de format propriétaire fermé).
    """
    import pandas as pd
    import pyreadstat

    indicateurs = indicateurs_pour_projet(projet.id)
    lignes = []
    for indicateur in indicateurs:
        for valeur in indicateur.valeurs.all():
            lignes.append(
                {
                    "indicateur": indicateur.libelle[:80],
                    "unite": indicateur.unite,
                    "periode_debut": str(valeur.periode_debut),
                    "periode_fin": str(valeur.periode_fin),
                    "valeur_realisee": float(valeur.valeur_realisee),
                    "valeur_cible": float(indicateur.valeur_cible),
                    "saisi_par": str(valeur.saisi_par),
                }
            )

    if not lignes:
        lignes = [
            {
                "indicateur": "",
                "unite": "",
                "periode_debut": "",
                "periode_fin": "",
                "valeur_realisee": None,
                "valeur_cible": None,
                "saisi_par": "",
            }
        ]

    df = pd.DataFrame(lignes)

    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        pyreadstat.write_sav(df, tmp.name, file_label=projet.nom[:80])
        tmp.seek(0)
        return tmp.read()
