"""
Import d'un projet complet (fiche + planification Objectif général > Objectif
spécifique > Activité > Sous-activité) depuis un classeur Excel — même
philosophie « best-effort » que l'import de structuration stratégique
(apps.strategy.services) : une ligne en erreur est ignorée sans bloquer
l'import des autres, tout est rapporté au client.
"""
import datetime
import io
import unicodedata

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

from apps.core.excel_utils import figer_entete, quadriller


def _normaliser_entete(texte: str) -> str:
    """
    Compare les en-têtes en ignorant accents/casse/tirets-vs-espaces/espaces
    en trop (ex : « Sous-activité » == « sous   activite ») — pour tolérer
    les petites variations de saisie d'un en-tête sans risquer de confondre
    une colonne avec une autre (comparaison toujours à un nom précis, jamais
    une déduction depuis le contenu des lignes).
    """
    sans_accents = "".join(c for c in unicodedata.normalize("NFD", texte) if unicodedata.category(c) != "Mn")
    return " ".join(sans_accents.replace("-", " ").lower().split())

CHAMPS_PROJET = [
    ("Nom du projet", "Programme d'appui à la résilience communautaire"),
    ("Code du projet", "PRJ-2026-001"),
    ("Cadre stratégique", "Nom exact d'un cadre stratégique déjà créé (laisser vide si aucun)"),
    ("Pays (codes ISO séparés par ;)", "BF"),
    ("Budget total (FCFA)", 100000000),
    ("Fonds propres (FCFA)", 10000000),
    ("Date de début (AAAA-MM-JJ)", "2026-01-01"),
    ("Date de fin (AAAA-MM-JJ)", "2027-12-31"),
    ("Statut (EN_PREPARATION/EN_COURS/CLOTURE)", "EN_PREPARATION"),
    ("Type de mise en œuvre (DIRECT/CONSORTIUM)", "DIRECT"),
    ("Bailleur", "Fondation Grameen"),
    ("Partenaire de mise en œuvre", "ONG Sahel Solidarité"),
    ("Partenaires du consortium (séparés par ;)", ""),
    ("Chef de projet", "OUEDRAOGO Fatimata"),
    ("Utilisateurs affectés — identifiants séparés par ; (accès plateforme)", ""),
    ("Cible totale", 1000),
    ("Cible hommes", 400),
    ("Cible femmes", 600),
    ("Cible jeunes", 300),
    ("Cible PDI", 100),
]

COLONNES_PLANIFICATION = [
    "Objectif général",
    "Objectif spécifique",
    "Code activité",
    "Activité",
    "Sous-activité",
    "Valeur de base",
    "Budget alloué (FCFA)",
    "Quantité prévue",
    "Unité",
    "Date début (AAAA-MM-JJ)",
    "Date fin (AAAA-MM-JJ)",
    "Commentaire",
]

LIGNES_EXEMPLE_PLANIFICATION = [
    ["Améliorer la sécurité alimentaire des ménages vulnérables", "", "", "", "", "", "", "", "", "", "", ""],
    ["", "Renforcer les capacités techniques des producteurs", "", "", "", "", "", "", "", "", "", ""],
    [
        "",
        "",
        "A1.1",
        "Former les producteurs aux techniques agroécologiques",
        "",
        0,
        2000000,
        300,
        "producteurs",
        "2026-02-01",
        "2026-06-30",
        "",
    ],
    ["", "", "", "", "Session de formation en zone rurale", "", "", 100, "producteurs", "2026-02-01", "2026-03-31", ""],
]


def generer_feuille_projet(wb):
    feuille = wb.active
    feuille.title = "Projet"
    for cle, exemple in CHAMPS_PROJET:
        feuille.append([cle, exemple])
    for ligne in feuille.iter_rows(min_col=1, max_col=1):
        ligne[0].font = Font(bold=True)
    quadriller(feuille, max_col=2)
    feuille.column_dimensions["A"].width = 42
    feuille.column_dimensions["B"].width = 48
    return feuille


def generer_feuille_planification(wb, avec_exemple=True):
    feuille = wb.create_sheet("Planification")
    nb_colonnes = len(COLONNES_PLANIFICATION)
    feuille.append(COLONNES_PLANIFICATION)
    for cellule in feuille[1]:
        cellule.font = Font(bold=True)
    if avec_exemple:
        for ligne in LIGNES_EXEMPLE_PLANIFICATION:
            feuille.append(ligne)

    # Lignes vides supplémentaires déjà quadrillées, pour que la saisie
    # manuelle qui suit les exemples reste visuellement dans le tableau au
    # lieu de flotter sans repère de colonnes.
    lignes_vides_supplementaires = 20
    for _ in range(lignes_vides_supplementaires):
        feuille.append([""] * nb_colonnes)

    quadriller(feuille, max_col=nb_colonnes)
    figer_entete(feuille)

    largeurs = {"A": 34, "B": 34, "C": 14, "D": 40, "E": 34, "F": 14, "G": 16, "H": 14, "I": 14, "J": 16, "K": 16}
    for colonne, largeur in largeurs.items():
        feuille.column_dimensions[colonne].width = largeur

    return feuille


def generer_modele_import_projet() -> bytes:
    from apps.indicators.import_excel import generer_feuille_paliers_alerte

    wb = Workbook()
    generer_feuille_projet(wb)
    generer_feuille_planification(wb)
    generer_feuille_paliers_alerte(wb)

    instructions = wb.create_sheet("Instructions")
    instructions.append(["Consignes"])
    instructions.append(["- Feuille « Projet » : une ligne = un champ (colonne A = nom du champ, colonne B = valeur)."])
    instructions.append(["- Nom du projet, Code du projet, Date de début et Date de fin sont obligatoires."])
    instructions.append(["- Le code du projet doit être unique — l'import est refusé s'il existe déjà."])
    instructions.append([
        "- « Utilisateurs affectés » : identifiants (username) de comptes déjà créés sur la plateforme, séparés "
        "par « ; ». C'est ce qui donne réellement accès au projet une fois connecté — le champ « Chef de "
        "projet » n'est qu'un intitulé affiché, il ne donne aucun accès à lui seul. Un identifiant inconnu "
        "est ignoré avec un avertissement, sans bloquer le reste de l'import."
    ])
    instructions.append([
        "- Feuille « Planification » : une colonne = un niveau (Objectif général → Objectif spécifique → "
        "Activité → Sous-activité). Sur chaque ligne, remplis UNE SEULE de ces colonnes de niveau : son "
        "rattachement est déduit automatiquement (le dernier élément de niveau immédiatement supérieur "
        "renseigné au-dessus)."
    ])
    instructions.append([
        "- Tu peux insérer d'AUTRES colonnes de niveau entre « Objectif spécifique » et « Sous-activité », "
        "nommées comme tu veux (ex : « Résultat »), pour imbriquer un niveau de plus — le nom de la colonne "
        "devient le nom affiché de ce niveau. Attention : toute colonne placée dans cette zone devient un "
        "niveau, y compris une colonne qui n'en est pas censée être un (une note ponctuelle par ex.) — place "
        "ce genre de colonne avant « Objectif général » ou après « Date fin » pour éviter ça."
    ])
    instructions.append([
        "- Les colonnes Code activité / Valeur de base / Budget alloué / Quantité prévue / Unité / Date début / "
        "Date fin / Commentaire s'appliquent à la ligne d'Activité (à n'importe quel niveau imbriqué) ou de "
        "Sous-activité correspondante (Code activité, Valeur de base, Budget alloué et Commentaire uniquement "
        "pour une Activité) — toujours sur LA MÊME LIGNE que le niveau concerné, jamais sur une ligne à part."
    ])
    instructions.append([
        "- Valeur de base : niveau avant le démarrage de l'activité (comme la Valeur de référence d'un "
        "indicateur) — permet de tracer la progression attendue dans le temps, pas seulement 0 → cible."
    ])
    instructions.append(["- Réimporter le même fichier met à jour les éléments déjà importés (même nom, même position)."])
    instructions.append([
        "- Feuille « Grilles d'alerte » (facultative) : pour donner au projet, ou à une activité précise "
        "(par son libellé exact) créée dans la feuille « Planification » ci-dessus, sa propre grille de "
        "paliers plutôt que d'hériter de la grille globale — une ligne par palier, plusieurs lignes pour la "
        "même portée forment sa grille complète."
    ])

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def _texte(champs, cle, defaut=""):
    v = champs.get(cle)
    return str(v).strip() if v not in (None, "") else defaut


def _nombre(champs, cle, defaut=0):
    v = champs.get(cle)
    if v in (None, ""):
        return defaut
    try:
        return float(v)
    except (TypeError, ValueError):
        return defaut


def _entier_ou_none(champs, cle):
    v = champs.get(cle)
    if v in (None, ""):
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _date(champs, cle):
    v = champs.get(cle)
    if not v:
        return None
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.date() if isinstance(v, datetime.datetime) else v
    try:
        return datetime.datetime.strptime(str(v).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _resoudre_partenaire(nom, type_):
    from apps.partners.models import Partenaire

    nom = (nom or "").strip()
    if not nom:
        return None
    existant = Partenaire.objects.filter(nom__iexact=nom, type=type_).first()
    return existant or Partenaire.objects.create(nom=nom, type=type_)


def _lire_champs_cle_valeur(feuille) -> dict:
    champs = {}
    for row in feuille.iter_rows(min_row=1, values_only=True):
        if not row or not row[0]:
            continue
        cle = str(row[0]).strip()
        champs[cle] = row[1] if len(row) > 1 else None
    return champs


def importer_planification(feuille, projet) -> dict:
    """
    Importe la feuille « Planification » (Objectif général > Objectif
    spécifique > [niveaux d'Activité imbriqués, en nombre libre] >
    Sous-activité) dans la hiérarchie du projet donné.

    Les colonnes entre « Objectif spécifique » et « Sous-activité » forment
    une chaîne de niveaux d'Activité imbriqués (via Activite.activite_parent)
    — une seule colonne (« Activité ») par défaut dans le modèle téléchargé,
    mais rien n'empêche d'en insérer d'autres, librement nommées (ex :
    « Résultat » puis « Activité »), comme pour l'import de structuration
    stratégique. Le nom de chaque colonne devient le libellé affiché de ce
    niveau pour ce projet (voir NiveauActivite), déduit automatiquement au
    premier import.
    """
    from .models import Activite, NiveauActivite, ObjectifGeneral, ObjectifSpecifique, SousActivite

    resultat = {
        "objectifs_generaux": 0,
        "objectifs_specifiques_crees": 0,
        "activites_creees": 0,
        "sous_activites_creees": 0,
        "erreurs": [],
    }

    lignes = list(feuille.iter_rows(min_row=1, values_only=True))
    if not lignes:
        return resultat

    entetes = [str(c).strip() if c else "" for c in lignes[0]]

    entetes_normalises = [_normaliser_entete(e) for e in entetes]

    def index(nom):
        nom_normalise = _normaliser_entete(nom)
        return entetes_normalises.index(nom_normalise) if nom_normalise in entetes_normalises else None

    idx_og = index("Objectif général")
    idx_os = index("Objectif spécifique")
    idx_sa = index("Sous-activité")
    idx_code = index("Code activité")
    idx_valeur_ref = index("Valeur de base")
    idx_budget = index("Budget alloué (FCFA)")
    idx_qte = index("Quantité prévue")
    idx_unite = index("Unité")
    idx_debut = index("Date début (AAAA-MM-JJ)")
    idx_fin = index("Date fin (AAAA-MM-JJ)")
    idx_commentaire = index("Commentaire")

    colonnes_fixes = {
        i
        for i in (
            idx_og,
            idx_os,
            idx_sa,
            idx_code,
            idx_valeur_ref,
            idx_budget,
            idx_qte,
            idx_unite,
            idx_debut,
            idx_fin,
            idx_commentaire,
        )
        if i is not None
    }
    borne_fin = idx_sa if idx_sa is not None else len(entetes)
    debut_recherche = (idx_os + 1) if idx_os is not None else 0
    # Une colonne = un niveau, sans exception ni devinette sur son contenu —
    # même principe que l'import de structuration stratégique : toute colonne
    # nommée entre Objectif spécifique et Sous-activité (ou la fin si pas de
    # Sous-activité) devient un niveau d'Activité imbriqué. Ajouter une
    # colonne dans cette zone qu'on ne veut PAS voir comme un niveau (une
    # note, un suivi ponctuel...) la fait donc devenir un niveau — à l'auteur
    # du fichier de la placer plutôt avant « Objectif général » ou après
    # « Date fin » si ce n'est pas l'effet voulu.
    idx_activite_niveaux = [
        i
        for i in range(debut_recherche, borne_fin)
        if i not in colonnes_fixes and entetes[i] and not entetes_normalises[i].startswith("code")
    ]

    if idx_og is None and idx_os is None and not idx_activite_niveaux and idx_sa is None:
        resultat["erreurs"].append({"ligne": 1, "message": "Aucune colonne de planification reconnue."})
        return resultat

    # Mémorise le nom de chaque colonne « niveau d'activité » rencontrée pour
    # CE projet (affichage uniquement) — crée les niveaux manquants, ne
    # renomme jamais un niveau déjà nommé par un import précédent.
    profondeurs_existantes = set(
        NiveauActivite.objects.filter(projet=projet).values_list("profondeur", flat=True)
    )
    for profondeur, idx in enumerate(idx_activite_niveaux):
        if profondeur not in profondeurs_existantes:
            NiveauActivite.objects.create(projet=projet, profondeur=profondeur, nom_niveau=entetes[idx])

    def valeur(ligne, idx):
        if idx is None or idx >= len(ligne):
            return None
        return ligne[idx]

    def date_cellule(ligne, idx):
        v = valeur(ligne, idx)
        if not v:
            return None
        if isinstance(v, (datetime.date, datetime.datetime)):
            return v.date() if isinstance(v, datetime.datetime) else v
        try:
            return datetime.datetime.strptime(str(v).strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    og_actuel = ObjectifGeneral.objects.filter(projet=projet).first()
    os_actuel = None
    dernier_par_niveau: list = [None] * len(idx_activite_niveaux)

    for numero, ligne in enumerate(lignes[1:], start=2):
        if not any(ligne):
            continue

        if idx_og is not None and valeur(ligne, idx_og):
            nom = str(valeur(ligne, idx_og)).strip()
            if og_actuel:
                og_actuel.libelle = nom
                og_actuel.save(update_fields=["libelle"])
            else:
                og_actuel = ObjectifGeneral.objects.create(projet=projet, libelle=nom)
                resultat["objectifs_generaux"] += 1
            os_actuel = None
            dernier_par_niveau = [None] * len(idx_activite_niveaux)
            continue

        if idx_os is not None and valeur(ligne, idx_os):
            if not og_actuel:
                resultat["erreurs"].append(
                    {"ligne": numero, "message": "Aucun objectif général défini au-dessus — ligne ignorée."}
                )
                continue
            nom = str(valeur(ligne, idx_os)).strip()
            existant = ObjectifSpecifique.objects.filter(objectif_general=og_actuel, libelle__iexact=nom).first()
            os_actuel = existant or ObjectifSpecifique.objects.create(objectif_general=og_actuel, libelle=nom)
            if not existant:
                resultat["objectifs_specifiques_crees"] += 1
            dernier_par_niveau = [None] * len(idx_activite_niveaux)
            continue

        profondeurs_remplies = [p for p, idx in enumerate(idx_activite_niveaux) if valeur(ligne, idx)]
        if len(profondeurs_remplies) > 1:
            resultat["erreurs"].append(
                {"ligne": numero, "message": "Une seule colonne de niveau d'activité doit être remplie par ligne — ligne ignorée."}
            )
            continue

        if profondeurs_remplies:
            profondeur = profondeurs_remplies[0]
            idx_colonne = idx_activite_niveaux[profondeur]
            if not os_actuel:
                resultat["erreurs"].append(
                    {"ligne": numero, "message": "Aucun objectif spécifique défini au-dessus — ligne ignorée."}
                )
                continue

            activite_parent = dernier_par_niveau[profondeur - 1] if profondeur > 0 else None
            if profondeur > 0 and activite_parent is None:
                nom_niveau_parent = entetes[idx_activite_niveaux[profondeur - 1]]
                resultat["erreurs"].append(
                    {
                        "ligne": numero,
                        "message": f"Aucun élément « {nom_niveau_parent} » renseigné au-dessus pour rattacher cette ligne — ligne ignorée.",
                    }
                )
                continue

            nom = str(valeur(ligne, idx_colonne)).strip()
            existant = Activite.objects.filter(
                objectif_specifique=os_actuel, activite_parent=activite_parent, libelle__iexact=nom
            ).first()
            act_actuel = existant or Activite(objectif_specifique=os_actuel, activite_parent=activite_parent, libelle=nom)
            act_actuel.libelle = nom
            if valeur(ligne, idx_code):
                act_actuel.code_activite = str(valeur(ligne, idx_code)).strip()
            if valeur(ligne, idx_valeur_ref) not in (None, ""):
                act_actuel.valeur_reference = valeur(ligne, idx_valeur_ref)
            if valeur(ligne, idx_budget) not in (None, ""):
                act_actuel.budget_alloue = valeur(ligne, idx_budget)
            if valeur(ligne, idx_qte) not in (None, ""):
                act_actuel.quantite_prevue = valeur(ligne, idx_qte)
            if valeur(ligne, idx_unite):
                act_actuel.unite_quantite = str(valeur(ligne, idx_unite)).strip()
            date_debut = date_cellule(ligne, idx_debut)
            if date_debut:
                act_actuel.date_debut = date_debut
            date_fin = date_cellule(ligne, idx_fin)
            if date_fin:
                act_actuel.date_fin = date_fin
            if valeur(ligne, idx_commentaire):
                act_actuel.commentaire = str(valeur(ligne, idx_commentaire)).strip()
            try:
                act_actuel.clean()
            except Exception as exc:  # ValidationError du modèle
                resultat["erreurs"].append({"ligne": numero, "message": str(exc)})
                continue
            act_actuel.save()
            if not existant:
                resultat["activites_creees"] += 1

            dernier_par_niveau[profondeur] = act_actuel
            for j in range(profondeur + 1, len(dernier_par_niveau)):
                dernier_par_niveau[j] = None
            continue

        if idx_sa is not None and valeur(ligne, idx_sa):
            act_actuel = next((a for a in reversed(dernier_par_niveau) if a is not None), None)
            if not act_actuel:
                resultat["erreurs"].append(
                    {"ligne": numero, "message": "Aucune activité définie au-dessus — ligne ignorée."}
                )
                continue
            nom = str(valeur(ligne, idx_sa)).strip()
            existant = SousActivite.objects.filter(activite=act_actuel, libelle__iexact=nom).first()
            sa = existant or SousActivite(activite=act_actuel, libelle=nom)
            sa.libelle = nom
            if valeur(ligne, idx_qte) not in (None, ""):
                sa.quantite_prevue = valeur(ligne, idx_qte)
            if valeur(ligne, idx_unite):
                sa.unite_quantite = str(valeur(ligne, idx_unite)).strip()
            date_debut = date_cellule(ligne, idx_debut)
            if date_debut:
                sa.date_debut = date_debut
            date_fin = date_cellule(ligne, idx_fin)
            if date_fin:
                sa.date_fin = date_fin
            sa.save()
            if not existant:
                resultat["sous_activites_creees"] += 1
            continue

    return resultat


def importer_projet(fichier, cadre_strategique_impose=None) -> dict:
    """
    Crée un projet (feuille « Projet ») et sa planification (feuille
    « Planification ») depuis un classeur Excel. `cadre_strategique_impose`
    permet à l'import combiné (apps.planification) d'imposer le cadre
    stratégique qu'il vient de créer, sans passer par la colonne « Cadre
    stratégique » de la feuille.
    """
    from apps.indicators.import_excel import importer_paliers_alerte

    from .models import Activite, Projet

    wb = load_workbook(fichier, data_only=True)
    resultat = importer_projet_depuis_wb(wb, cadre_strategique_impose=cadre_strategique_impose)

    if resultat.get("projet_id") and "Grilles d'alerte" in wb.sheetnames:
        projet = Projet.objects.get(id=resultat["projet_id"])
        activites_par_nom = {
            a.libelle.strip().lower(): a
            for a in Activite.objects.filter(objectif_specifique__objectif_general__projet=projet)
        }
        resultat_paliers = importer_paliers_alerte(
            wb["Grilles d'alerte"], projet=projet, activites_par_nom=activites_par_nom
        )
        resultat["grilles_alerte_creees"] = resultat_paliers["grilles_creees"]
        resultat["erreurs"] += [
            {"ligne": e["ligne"], "message": f"[Grilles d'alerte] {e['message']}"} for e in resultat_paliers["erreurs"]
        ]

    return resultat


def importer_projet_depuis_wb(wb, cadre_strategique_impose=None) -> dict:
    from django.contrib.auth import get_user_model

    from apps.strategy.models import CadreStrategique

    from .models import Projet

    User = get_user_model()

    if "Projet" not in wb.sheetnames:
        return {"projet_id": None, "erreurs": [{"ligne": 0, "message": "Feuille « Projet » introuvable."}], "avertissements": []}

    champs = _lire_champs_cle_valeur(wb["Projet"])
    erreurs = []
    avertissements = []

    nom = _texte(champs, "Nom du projet")
    code = _texte(champs, "Code du projet")
    if not nom or not code:
        erreurs.append({"ligne": 0, "message": "Nom du projet et Code du projet sont obligatoires."})
        return {"projet_id": None, "erreurs": erreurs, "avertissements": avertissements}

    if Projet.objects.filter(code=code).exists():
        erreurs.append({"ligne": 0, "message": f"Un projet avec le code « {code} » existe déjà — import annulé."})
        return {"projet_id": None, "erreurs": erreurs, "avertissements": avertissements}

    date_debut = _date(champs, "Date de début (AAAA-MM-JJ)")
    date_fin = _date(champs, "Date de fin (AAAA-MM-JJ)")
    if not date_debut or not date_fin:
        erreurs.append(
            {"ligne": 0, "message": "Date de début et Date de fin sont obligatoires, au format AAAA-MM-JJ."}
        )
        return {"projet_id": None, "erreurs": erreurs, "avertissements": avertissements}

    cadre = cadre_strategique_impose
    if cadre is None:
        nom_cadre = _texte(champs, "Cadre stratégique")
        if nom_cadre:
            cadre = CadreStrategique.objects.filter(nom__iexact=nom_cadre).first()
            if not cadre:
                avertissements.append(
                    {"ligne": 0, "message": f"Cadre stratégique « {nom_cadre} » introuvable — laissé vide."}
                )

    pays = [c.strip().upper() for c in _texte(champs, "Pays (codes ISO séparés par ;)").split(";") if c.strip()]

    statut_brut = _texte(champs, "Statut (EN_PREPARATION/EN_COURS/CLOTURE)", "EN_PREPARATION").upper()
    statut = statut_brut if statut_brut in dict(Projet.Statut.choices) else Projet.Statut.EN_PREPARATION

    type_brut = _texte(champs, "Type de mise en œuvre (DIRECT/CONSORTIUM)", "DIRECT").upper()
    type_mise_en_oeuvre = (
        type_brut if type_brut in dict(Projet.TypeMiseEnOeuvre.choices) else Projet.TypeMiseEnOeuvre.DIRECT
    )

    bailleur = _resoudre_partenaire(_texte(champs, "Bailleur"), "BAILLEUR")
    partenaire_mise_en_oeuvre = _resoudre_partenaire(_texte(champs, "Partenaire de mise en œuvre"), "MISE_EN_OEUVRE")
    noms_consortium = [c.strip() for c in _texte(champs, "Partenaires du consortium (séparés par ;)").split(";") if c.strip()]
    partenaires_consortium = [p for p in (_resoudre_partenaire(n, "MISE_EN_OEUVRE") for n in noms_consortium) if p]

    identifiants_affectes = [
        i.strip()
        for i in _texte(champs, "Utilisateurs affectés — identifiants séparés par ; (accès plateforme)").split(";")
        if i.strip()
    ]
    utilisateurs_affectes = []
    for identifiant in identifiants_affectes:
        utilisateur = User.objects.filter(username__iexact=identifiant).first()
        if utilisateur:
            utilisateurs_affectes.append(utilisateur)
        else:
            avertissements.append(
                {"ligne": 0, "message": f"Utilisateur « {identifiant} » introuvable — non affecté au projet."}
            )

    projet = Projet.objects.create(
        nom=nom,
        code=code,
        pays=pays,
        cadre_strategique=cadre,
        budget_total=_nombre(champs, "Budget total (FCFA)"),
        fonds_propres=_nombre(champs, "Fonds propres (FCFA)"),
        date_debut=date_debut,
        date_fin=date_fin,
        statut=statut,
        type_mise_en_oeuvre=type_mise_en_oeuvre,
        partenaire_bailleur=bailleur,
        partenaire_mise_en_oeuvre=partenaire_mise_en_oeuvre,
        chef_de_projet_nom=_texte(champs, "Chef de projet"),
        cible_totale=_entier_ou_none(champs, "Cible totale"),
        cible_hommes=_entier_ou_none(champs, "Cible hommes"),
        cible_femmes=_entier_ou_none(champs, "Cible femmes"),
        cible_jeunes=_entier_ou_none(champs, "Cible jeunes"),
        cible_pdi=_entier_ou_none(champs, "Cible PDI"),
    )
    if partenaires_consortium:
        projet.partenaires_consortium.set(partenaires_consortium)
    if utilisateurs_affectes:
        projet.utilisateurs_affectes.set(utilisateurs_affectes)

    resultat_plan = {
        "objectifs_generaux": 0,
        "objectifs_specifiques_crees": 0,
        "activites_creees": 0,
        "sous_activites_creees": 0,
        "erreurs": [],
    }
    if "Planification" in wb.sheetnames:
        resultat_plan = importer_planification(wb["Planification"], projet)

    return {
        "projet_id": projet.id,
        "projet_code": projet.code,
        **resultat_plan,
        "erreurs": erreurs + resultat_plan["erreurs"],
        "avertissements": avertissements,
    }
