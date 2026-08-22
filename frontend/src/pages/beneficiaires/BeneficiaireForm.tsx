import { useState } from "react";
import { Alert, Button, Group, MultiSelect, Select, Stack, TextInput } from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { notifications } from "@mantine/notifications";
import { useCreateBeneficiaire, useVerifierDoublons } from "../../api/beneficiaries";
import { useStatutsParticuliers } from "../../api/referentiels";
import { useNiveauxAdministratifs } from "../../api/geo";
import {
  ZoneCascadeFields,
  ZONE_CASCADE_VIDE,
  zoneResolueDe,
  type ZoneCascadeValue,
} from "../../components/common/ZoneCascadeFields";
import { PAYS_MONDE } from "../../utils/pays";
import type { SignalementDoublon } from "../../types";

export function BeneficiaireForm({ onDone }: { onDone: () => void }) {
  const { data: statuts } = useStatutsParticuliers();
  const createBeneficiaire = useCreateBeneficiaire();
  const verifierDoublons = useVerifierDoublons();

  const [nom, setNom] = useState("");
  const [prenom, setPrenom] = useState("");
  const [sexe, setSexe] = useState<string | null>("F");
  const [dateNaissance, setDateNaissance] = useState<string | null>(null);
  const [telephone, setTelephone] = useState("");
  const [numeroPiece, setNumeroPiece] = useState("");
  const [pays, setPays] = useState<string | null>("BF");
  const [zoneCascade, setZoneCascade] = useState<ZoneCascadeValue>(ZONE_CASCADE_VIDE);
  const [statutsSelectionnes, setStatutsSelectionnes] = useState<string[]>([]);
  const [doublonsDetectes, setDoublonsDetectes] = useState<SignalementDoublon[] | null>(null);

  const { data: niveaux } = useNiveauxAdministratifs(pays);

  async function handleSubmit() {
    if (!nom || !prenom) {
      notifications.show({ message: "Nom et prénom requis.", color: "orange" });
      return;
    }
    try {
      const zone = zoneResolueDe(zoneCascade, niveaux ?? []);

      const created = await createBeneficiaire.mutateAsync({
        nom,
        prenom,
        sexe: sexe as "F" | "M",
        date_naissance: dateNaissance,
        telephone,
        numero_piece_identite: numeroPiece,
        pays: pays ?? "",
        zone,
        statuts_particuliers: statutsSelectionnes.map(Number),
      });

      const doublons = await verifierDoublons.mutateAsync(created.id);
      if (doublons.length > 0) {
        setDoublonsDetectes(doublons);
        notifications.show({
          message: `${doublons.length} doublon(s) potentiel(s) détecté(s) — à traiter dans l'écran "Doublons signalés".`,
          color: "orange",
        });
      } else {
        notifications.show({ message: "Bénéficiaire créé, aucun doublon détecté.", color: "green" });
        onDone();
      }
    } catch {
      notifications.show({ message: "Erreur lors de la création.", color: "red" });
    }
  }

  return (
    <Stack gap="sm">
      {doublonsDetectes && (
        <Alert color="orange" title="Doublons potentiels détectés">
          {doublonsDetectes.map((d) => (
            <div key={d.id}>{d.beneficiaire_1_nom} / {d.beneficiaire_2_nom} — score {d.score}</div>
          ))}
        </Alert>
      )}
      <Group grow>
        <TextInput label="Nom" value={nom} onChange={(e) => setNom(e.currentTarget.value)} required />
        <TextInput label="Prénom" value={prenom} onChange={(e) => setPrenom(e.currentTarget.value)} required />
      </Group>
      <Group grow>
        <Select label="Sexe" data={[{ value: "F", label: "Féminin" }, { value: "M", label: "Masculin" }]} value={sexe} onChange={setSexe} />
        <DateInput label="Date de naissance" value={dateNaissance} onChange={setDateNaissance} />
      </Group>
      <Group grow>
        <TextInput label="Téléphone" value={telephone} onChange={(e) => setTelephone(e.currentTarget.value)} />
        <TextInput label="N° pièce d'identité" value={numeroPiece} onChange={(e) => setNumeroPiece(e.currentTarget.value)} />
      </Group>
      <Select
        label="Pays"
        data={PAYS_MONDE.map((p) => ({ value: p.code, label: p.nom }))}
        value={pays}
        onChange={(v) => {
          setPays(v);
          setZoneCascade(ZONE_CASCADE_VIDE);
        }}
        searchable
        maw={300}
      />
      <ZoneCascadeFields pays={pays} value={zoneCascade} onChange={setZoneCascade} />
      <MultiSelect
        label="Statuts particuliers"
        data={statuts?.map((s) => ({ value: String(s.id), label: s.libelle })) ?? []}
        value={statutsSelectionnes}
        onChange={setStatutsSelectionnes}
      />
      <Group justify="flex-end">
        <Button onClick={handleSubmit} loading={createBeneficiaire.isPending || verifierDoublons.isPending}>
          Créer
        </Button>
      </Group>
    </Stack>
  );
}
