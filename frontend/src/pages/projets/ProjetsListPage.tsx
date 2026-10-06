import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { FileSpreadsheet, FolderKanban, Pencil, Search, Trash2 } from "lucide-react";
import { ActionIcon, Button, Card, Group, Modal, Stack, Table, Text, TextInput, Title, Tooltip } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useDeleteProjet, useProjets } from "../../api/projects";
import { ProjetForm } from "./ProjetForm";
import { ImportProjetModal } from "./ImportProjetModal";
import { StatusBadge } from "../../components/common/StatusBadge";
import { EmptyState } from "../../components/common/EmptyState";
import { confirmerSuppression } from "../../components/common/confirmerSuppression";
import { PROJET_STATUT_LABEL, PROJET_STATUT_TONE } from "../../utils/statusTones";
import { correspond } from "../../utils/recherche";
import { BoutonModeEdition } from "../../components/common/BoutonModeEdition";
import type { Projet } from "../../types";

export function ProjetsListPage() {
  const { data: projets, isLoading } = useProjets();
  const deleteProjet = useDeleteProjet();
  const [modalOpen, setModalOpen] = useState(false);
  const [modalImportOuvert, setModalImportOuvert] = useState(false);
  const [projetEnEdition, setProjetEnEdition] = useState<Projet | null>(null);
  const [recherche, setRecherche] = useState("");
  const [editionActive, setEditionActive] = useState(false);

  const projetsFiltres = useMemo(
    () => (projets ?? []).filter((p) => correspond(p.nom, recherche) || correspond(p.code, recherche)),
    [projets, recherche],
  );

  function handleSupprimer(id: number, nom: string) {
    confirmerSuppression({
      message: `Supprimer le projet "${nom}" ainsi que toute sa planification et ses indicateurs ? Cette action est irréversible.`,
      onConfirm: async () => {
        try {
          await deleteProjet.mutateAsync(id);
          notifications.show({ message: "Projet supprimé", color: "green" });
        } catch {
          notifications.show({ message: "Erreur lors de la suppression du projet", color: "red" });
        }
      },
    });
  }

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Title order={2}>Projets</Title>
        <Group gap="xs">
          <BoutonModeEdition actif={editionActive} onToggle={() => setEditionActive((v) => !v)} />
          <Button variant="light" leftSection={<FileSpreadsheet size={16} />} onClick={() => setModalImportOuvert(true)}>
            Importer depuis Excel
          </Button>
          <Button onClick={() => setModalOpen(true)}>Nouveau projet</Button>
        </Group>
      </Group>

      <TextInput
        placeholder="Rechercher un projet (nom ou code)…"
        leftSection={<Search size={15} />}
        value={recherche}
        onChange={(e) => setRecherche(e.currentTarget.value)}
        maw={400}
      />

      <Card withBorder padding="md" radius="md">
        {isLoading ? (
          <Text c="dimmed">Chargement…</Text>
        ) : !projets || projets.length === 0 ? (
          <EmptyState icon={<FolderKanban size={32} strokeWidth={1.5} />} message="Aucun projet pour le moment." />
        ) : projetsFiltres.length === 0 ? (
          <EmptyState icon={<FolderKanban size={32} strokeWidth={1.5} />} message="Aucun projet ne correspond à la recherche." />
        ) : (
          <Table.ScrollContainer minWidth={640}>
            <Table striped highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Code</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Nom</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Statut</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Période</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Chef de projet</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {projetsFiltres.map((p) => (
                  <Table.Tr key={p.id}>
                    <Table.Td>
                      <Text size="sm" c="dimmed" fw={500}>{p.code}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Text component={Link} to={`/projets/${p.id}`} size="sm" fw={500} c="teal.8">
                        {p.nom}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <StatusBadge tone={PROJET_STATUT_TONE[p.statut]}>{PROJET_STATUT_LABEL[p.statut]}</StatusBadge>
                    </Table.Td>
                    <Table.Td>
                      <Text size="sm" c="dimmed">{p.date_debut} → {p.date_fin}</Text>
                    </Table.Td>
                    <Table.Td>{p.chef_de_projet_nom || "—"}</Table.Td>
                    <Table.Td>
                      {editionActive && (
                      <Group gap={4} wrap="nowrap">
                        <Tooltip label="Modifier le projet">
                          <ActionIcon variant="subtle" onClick={() => setProjetEnEdition(p)}>
                            <Pencil size={15} />
                          </ActionIcon>
                        </Tooltip>
                        <Tooltip label="Supprimer le projet">
                          <ActionIcon
                            variant="subtle"
                            color="red"
                            loading={deleteProjet.isPending}
                            onClick={() => handleSupprimer(p.id, p.nom)}
                          >
                            <Trash2 size={15} />
                          </ActionIcon>
                        </Tooltip>
                      </Group>
                      )}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Card>

      <Modal opened={modalOpen} onClose={() => setModalOpen(false)} title="Nouveau projet" size="lg">
        <ProjetForm onDone={() => setModalOpen(false)} />
      </Modal>

      <Modal opened={!!projetEnEdition} onClose={() => setProjetEnEdition(null)} title="Modifier le projet" size="lg">
        {projetEnEdition && (
          <ProjetForm projet={projetEnEdition} onDone={() => setProjetEnEdition(null)} />
        )}
      </Modal>

      <ImportProjetModal opened={modalImportOuvert} onClose={() => setModalImportOuvert(false)} />
    </Stack>
  );
}
