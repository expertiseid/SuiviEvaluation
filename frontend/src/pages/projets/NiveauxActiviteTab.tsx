import { useMemo, useState } from "react";
import { ListTree, Pencil, Trash2 } from "lucide-react";
import { ActionIcon, Button, Card, Group, Modal, Stack, Text, TextInput, Tooltip } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
  useCreateNiveauActivite,
  useDeleteNiveauActivite,
  useNiveauxActivite,
  useUpdateNiveauActivite,
} from "../../api/projects";
import { EmptyState } from "../../components/common/EmptyState";
import { confirmerSuppression } from "../../components/common/confirmerSuppression";
import { messageErreurApi } from "../../utils/erreurs";
import type { NiveauActivite } from "../../types";

function ModalRenommer({
  opened,
  onClose,
  niveau,
}: {
  opened: boolean;
  onClose: () => void;
  niveau: NiveauActivite | null;
}) {
  const updateNiveau = useUpdateNiveauActivite();
  const [nom, setNom] = useState(niveau?.nom_niveau ?? "");

  async function enregistrer() {
    if (!niveau || !nom.trim()) {
      notifications.show({ message: "Le nom du niveau est requis.", color: "orange" });
      return;
    }
    try {
      await updateNiveau.mutateAsync({ id: niveau.id, payload: { nom_niveau: nom.trim() } });
      notifications.show({ message: "Niveau renommé", color: "green" });
      onClose();
    } catch (error) {
      notifications.show({ message: messageErreurApi(error, "Erreur lors du renommage"), color: "red" });
    }
  }

  return (
    <Modal opened={opened} onClose={onClose} title="Renommer le niveau">
      <Stack gap="sm">
        <TextInput label="Nom affiché" value={nom} onChange={(e) => setNom(e.currentTarget.value)} required />
        <Group justify="flex-end">
          <Button onClick={enregistrer} loading={updateNiveau.isPending}>Enregistrer</Button>
        </Group>
      </Stack>
    </Modal>
  );
}

/**
 * Noms affichés pour chaque profondeur d'imbrication d'Activité dans ce
 * projet (ex : profondeur 0 = « Résultat », profondeur 1 = « Activité »...) —
 * créés automatiquement au premier import Excel (une colonne entre
 * « Objectif spécifique » et « Sous-activité » = un niveau), modifiables ici
 * sans devoir réimporter. Purement cosmétique : renommer ou supprimer un
 * niveau ne change rien aux activités déjà créées à cette profondeur.
 */
export function NiveauxActiviteTab({ projetId }: { projetId: number }) {
  const { data: niveaux, isLoading } = useNiveauxActivite(projetId);
  const createNiveau = useCreateNiveauActivite();
  const deleteNiveau = useDeleteNiveauActivite();
  const [nomNouveauNiveau, setNomNouveauNiveau] = useState("");
  const [niveauEnEdition, setNiveauEnEdition] = useState<NiveauActivite | null>(null);

  const tries = useMemo(() => [...(niveaux ?? [])].sort((a, b) => a.profondeur - b.profondeur), [niveaux]);

  async function ajouter() {
    if (!nomNouveauNiveau.trim()) {
      notifications.show({ message: "Le nom du niveau est requis.", color: "orange" });
      return;
    }
    const prochaineProfondeur = tries.length > 0 ? tries[tries.length - 1].profondeur + 1 : 0;
    try {
      await createNiveau.mutateAsync({
        projet: projetId,
        profondeur: prochaineProfondeur,
        nom_niveau: nomNouveauNiveau.trim(),
      });
      notifications.show({ message: "Niveau ajouté", color: "green" });
      setNomNouveauNiveau("");
    } catch (error) {
      notifications.show({ message: messageErreurApi(error, "Erreur lors de l'ajout du niveau"), color: "red" });
    }
  }

  function supprimer(niveau: NiveauActivite) {
    confirmerSuppression({
      message: `Supprimer le niveau « ${niveau.nom_niveau} » ? Les activités déjà créées à cette profondeur ne sont pas affectées — elles s'afficheront simplement avec le nom par défaut « Activité ».`,
      onConfirm: async () => {
        try {
          await deleteNiveau.mutateAsync(niveau.id);
          notifications.show({ message: "Niveau supprimé", color: "green" });
        } catch (error) {
          notifications.show({ message: messageErreurApi(error, "Erreur lors de la suppression"), color: "red" });
        }
      },
    });
  }

  return (
    <Card withBorder padding="lg" radius="md">
      <Text fw={600} mb="xs">Configuration des niveaux</Text>
      <Text size="sm" c="dimmed" mb="sm">
        Chaque profondeur d'imbrication d'Activité dans ce projet (créée automatiquement à l'import Excel — une
        colonne entre « Objectif spécifique » et « Sous-activité » = un niveau) peut être renommée ici, sans
        réimporter. Ex : « Résultat » → « Activité » → « OK ».
      </Text>

      {isLoading ? (
        <Text c="dimmed">Chargement…</Text>
      ) : tries.length === 0 ? (
        <EmptyState
          icon={<ListTree size={32} strokeWidth={1.5} />}
          message="Aucun niveau personnalisé pour l'instant — ce projet utilise la hiérarchie classique (Activité / Sous-activité)."
        />
      ) : (
        <Stack gap={6} mb="sm">
          {tries.map((niveau) => (
            <Group key={niveau.id} gap={6} wrap="nowrap" justify="space-between">
              <Group gap={6} wrap="nowrap">
                <Text size="sm" c="dimmed" w={20}>{niveau.profondeur}.</Text>
                <Text size="sm" fw={500}>{niveau.nom_niveau}</Text>
              </Group>
              <Group gap={2} wrap="nowrap">
                <Tooltip label="Renommer">
                  <ActionIcon size="sm" variant="subtle" onClick={() => setNiveauEnEdition(niveau)}>
                    <Pencil size={13} />
                  </ActionIcon>
                </Tooltip>
                <Tooltip label="Supprimer">
                  <ActionIcon size="sm" variant="subtle" color="red" loading={deleteNiveau.isPending} onClick={() => supprimer(niveau)}>
                    <Trash2 size={13} />
                  </ActionIcon>
                </Tooltip>
              </Group>
            </Group>
          ))}
        </Stack>
      )}

      <Group gap="xs" align="flex-end">
        <TextInput
          size="xs"
          label="Ajouter un niveau"
          placeholder="Ex : Résultat"
          value={nomNouveauNiveau}
          onChange={(e) => setNomNouveauNiveau(e.currentTarget.value)}
          style={{ flex: 1 }}
        />
        <Button size="xs" variant="light" onClick={ajouter} loading={createNiveau.isPending}>
          Ajouter
        </Button>
      </Group>

      <ModalRenommer
        key={niveauEnEdition?.id ?? "aucun"}
        opened={!!niveauEnEdition}
        onClose={() => setNiveauEnEdition(null)}
        niveau={niveauEnEdition}
      />
    </Card>
  );
}
