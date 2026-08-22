import { useMemo, useState } from "react";
import { Button, Group, MultiSelect, NumberInput, Select, Stack, TextInput } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useCreateIndicateur, useUpdateIndicateur } from "../../api/indicators";
import { useElementsStrategiques } from "../../api/strategy";
import { useHierarchyOptions } from "./useHierarchyOptions";
import type { Indicateur } from "../../types";

const FREQUENCES = [
  { value: "MENSUELLE", label: "Mensuelle" },
  { value: "TRIMESTRIELLE", label: "Trimestrielle" },
  { value: "SEMESTRIELLE", label: "Semestrielle" },
  { value: "ANNUELLE", label: "Annuelle" },
];

type Rattachement = "AUCUN" | "PROJET" | "OG" | "OS" | "ACTIVITE";

// Chaque niveau forme un groupe dans le sélecteur unique — l'utilisateur
// cherche et choisit directement, sans devoir d'abord préciser le type
// (projet, objectif, activité...).
const GROUPES_RATTACHEMENT: { type: Exclude<Rattachement, "AUCUN">; label: string }[] = [
  { type: "PROJET", label: "Projet" },
  { type: "OG", label: "Objectif général" },
  { type: "OS", label: "Objectif spécifique" },
  { type: "ACTIVITE", label: "Activité" },
];

function rattachementInitial(indicateur?: Indicateur): { type: Rattachement; id: string | null } {
  if (!indicateur) return { type: "AUCUN", id: null };
  if (indicateur.projet) return { type: "PROJET", id: String(indicateur.projet) };
  if (indicateur.objectif_general) return { type: "OG", id: String(indicateur.objectif_general) };
  if (indicateur.objectif_specifique) return { type: "OS", id: String(indicateur.objectif_specifique) };
  if (indicateur.activite) return { type: "ACTIVITE", id: String(indicateur.activite) };
  return { type: "AUCUN", id: null };
}

export function IndicateurForm({ indicateur, onDone }: { indicateur?: Indicateur; onDone: () => void }) {
  const enEdition = !!indicateur;
  const {
    projets,
    objectifsGeneraux,
    objectifsSpecifiques,
    activites,
    cadreParProjetId,
    projetIdParOG,
    projetIdParOS,
    projetIdParActivite,
  } = useHierarchyOptions();
  const createIndicateur = useCreateIndicateur();
  const updateIndicateur = useUpdateIndicateur();

  const initial = rattachementInitial(indicateur);
  const [rattachementValue, setRattachementValue] = useState<string | null>(
    initial.type === "AUCUN" || !initial.id ? null : `${initial.type}:${initial.id}`,
  );
  const [rattachementType, rattachementId] = useMemo((): [Rattachement, string | null] => {
    if (!rattachementValue) return ["AUCUN", null];
    const [type, id] = rattachementValue.split(":");
    return [type as Rattachement, id];
  }, [rattachementValue]);
  const [libelle, setLibelle] = useState(indicateur?.libelle ?? "");
  const [unite, setUnite] = useState(indicateur?.unite ?? "");
  const [valeurReference, setValeurReference] = useState<number | string>(indicateur?.valeur_reference ?? "");
  const [valeurCible, setValeurCible] = useState<number | string>(indicateur?.valeur_cible ?? "");
  const [frequence, setFrequence] = useState<string | null>(indicateur?.frequence_collecte ?? "TRIMESTRIELLE");
  const [elementsSelectionnes, setElementsSelectionnes] = useState<string[]>(
    indicateur?.elements_strategiques.map(String) ?? [],
  );

  const listesParType: Record<Exclude<Rattachement, "AUCUN">, { value: string; label: string }[]> = {
    PROJET: projets,
    OG: objectifsGeneraux,
    OS: objectifsSpecifiques,
    ACTIVITE: activites,
  };

  // Un seul sélecteur, avec toutes les options mélangées et regroupées par
  // niveau — l'utilisateur tape et trouve, quel que soit le niveau, plutôt
  // que de devoir choisir un type avant de chercher.
  const optionsRattachement = GROUPES_RATTACHEMENT.filter((g) => listesParType[g.type].length > 0).map((g) => ({
    group: g.label,
    items: listesParType[g.type].map((o) => ({ value: `${g.type}:${o.value}`, label: o.label })),
  }));

  // Détermine le projet concerné par le rattachement choisi (quel que soit
  // le niveau), pour ne proposer que les éléments stratégiques de son cadre.
  const projetIdCourant = useMemo(() => {
    if (!rattachementId) return null;
    const id = Number(rattachementId);
    if (rattachementType === "PROJET") return id;
    if (rattachementType === "OG") return projetIdParOG.get(id) ?? null;
    if (rattachementType === "OS") return projetIdParOS.get(id) ?? null;
    if (rattachementType === "ACTIVITE") return projetIdParActivite.get(id) ?? null;
    return null;
  }, [rattachementType, rattachementId, projetIdParOG, projetIdParOS, projetIdParActivite]);

  const cadreStrategiqueCourant = projetIdCourant ? cadreParProjetId.get(projetIdCourant) ?? null : null;

  const { data: elementsStrategiques } = useElementsStrategiques(
    cadreStrategiqueCourant ? { cadre_strategique: cadreStrategiqueCourant } : undefined,
  );

  async function handleSubmit() {
    if (!libelle || !unite || !valeurCible || !frequence) {
      notifications.show({ message: "Merci de compléter tous les champs requis.", color: "orange" });
      return;
    }
    const payload = {
      libelle,
      unite,
      valeur_reference: valeurReference === "" ? null : String(valeurReference),
      valeur_cible: String(valeurCible),
      frequence_collecte: frequence as never,
      projet: rattachementType === "PROJET" ? Number(rattachementId) : null,
      objectif_general: rattachementType === "OG" ? Number(rattachementId) : null,
      objectif_specifique: rattachementType === "OS" ? Number(rattachementId) : null,
      activite: rattachementType === "ACTIVITE" ? Number(rattachementId) : null,
      elements_strategiques: elementsSelectionnes.map(Number),
    };
    try {
      if (enEdition) {
        await updateIndicateur.mutateAsync({ id: indicateur.id, payload });
        notifications.show({ message: "Indicateur modifié", color: "green" });
      } else {
        await createIndicateur.mutateAsync(payload);
        notifications.show({ message: "Indicateur créé", color: "green" });
      }
      onDone();
    } catch {
      notifications.show({
        message: enEdition ? "Erreur lors de la modification de l'indicateur" : "Erreur lors de la création de l'indicateur",
        color: "red",
      });
    }
  }

  return (
    <Stack gap="sm">
      <TextInput label="Libellé" value={libelle} onChange={(e) => setLibelle(e.currentTarget.value)} required />
      <Group grow>
        <TextInput label="Unité" value={unite} onChange={(e) => setUnite(e.currentTarget.value)} required />
        <NumberInput label="Valeur de base" value={valeurReference} onChange={setValeurReference} min={0} />
        <NumberInput label="Valeur cible" value={valeurCible} onChange={setValeurCible} min={0} required />
      </Group>
      <Select label="Fréquence de collecte" data={FREQUENCES} value={frequence} onChange={setFrequence} required />

      <Select
        label="Rattaché à"
        description="Facultatif — cherche et choisis directement un projet, un objectif ou une activité, quel que soit son niveau. L'indicateur suit la grille d'alerte (paliers/libellés/couleurs) du projet, configurable depuis Paramètres d'alerte."
        placeholder="Rechercher…"
        data={optionsRattachement}
        value={rattachementValue}
        onChange={setRattachementValue}
        searchable
        clearable
      />

      <MultiSelect
        label="Éléments stratégiques rattachés"
        description={
          cadreStrategiqueCourant
            ? "Limité au cadre stratégique du projet choisi ci-dessus."
            : "Choisis d'abord un rattachement ci-dessus pour limiter la liste à son cadre stratégique — sinon tous les éléments sont proposés."
        }
        data={elementsStrategiques?.map((el) => ({
          value: String(el.id),
          label: `${el.type_niveau_nom} · ${el.code ? el.code + " — " : ""}${el.nom}`,
        })) ?? []}
        value={elementsSelectionnes}
        onChange={setElementsSelectionnes}
        searchable
        clearable
      />

      <Group justify="flex-end">
        <Button onClick={handleSubmit} loading={createIndicateur.isPending || updateIndicateur.isPending}>
          {enEdition ? "Enregistrer" : "Créer"}
        </Button>
      </Group>
    </Stack>
  );
}
