import { useState } from "react";
import { FileText } from "lucide-react";
import { Button, Card, Group, Modal, Select, Stack, Table, Text, Textarea, Title } from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { notifications } from "@mantine/notifications";
import { useProjets } from "../../api/projects";
import { useCreateRapport, useRapports, useSoumettreRapport, useValiderRapport, telechargerExportRapport } from "../../api/reports";
import { useAuth } from "../../auth/useAuth";
import { StatusBadge } from "../../components/common/StatusBadge";
import { EmptyState } from "../../components/common/EmptyState";
import { RAPPORT_STATUT_LABEL, RAPPORT_STATUT_TONE } from "../../utils/statusTones";

function RapportForm({ onDone }: { onDone: () => void }) {
  const { data: projets } = useProjets();
  const createRapport = useCreateRapport();

  const [projet, setProjet] = useState<string | null>(null);
  const [type, setType] = useState<string | null>("MENSUEL");
  const [debut, setDebut] = useState<string | null>(null);
  const [fin, setFin] = useState<string | null>(null);
  const [contenu, setContenu] = useState("");

  async function handleSubmit() {
    if (!projet || !type || !debut || !fin) {
      notifications.show({ message: "Merci de compléter tous les champs.", color: "orange" });
      return;
    }
    try {
      await createRapport.mutateAsync({
        projet: Number(projet),
        type_rapport: type as never,
        periode_debut: debut,
        periode_fin: fin,
        contenu,
      });
      notifications.show({ message: "Rapport créé en brouillon", color: "green" });
      onDone();
    } catch {
      notifications.show({ message: "Erreur lors de la création", color: "red" });
    }
  }

  return (
    <Stack gap="sm">
      <Select label="Projet" data={projets?.map((p) => ({ value: String(p.id), label: p.nom })) ?? []} value={projet} onChange={setProjet} searchable required />
      <Select label="Type" data={[{ value: "MENSUEL", label: "Mensuel" }, { value: "TRIMESTRIEL", label: "Trimestriel" }, { value: "AUTRE", label: "Autre" }]} value={type} onChange={setType} />
      <Group grow>
        <DateInput label="Début de période" value={debut} onChange={setDebut} required />
        <DateInput label="Fin de période" value={fin} onChange={setFin} required />
      </Group>
      <Textarea label="Contenu" minRows={4} value={contenu} onChange={(e) => setContenu(e.currentTarget.value)} />
      <Group justify="flex-end">
        <Button onClick={handleSubmit} loading={createRapport.isPending}>Créer en brouillon</Button>
      </Group>
    </Stack>
  );
}

export function RapportsListPage() {
  const { user } = useAuth();
  const { data: rapports, isLoading } = useRapports();
  const soumettre = useSoumettreRapport();
  const valider = useValiderRapport();
  const [modalOpen, setModalOpen] = useState(false);

  const peutValider = user && ["ADMIN", "COORDO_GENERAL", "CHARGE_SE"].includes(user.role);

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Title order={2}>Rapports de suivi</Title>
        <Button onClick={() => setModalOpen(true)}>Nouveau rapport</Button>
      </Group>

      <Card withBorder padding="md" radius="md">
        {isLoading ? (
          <Text c="dimmed">Chargement…</Text>
        ) : !rapports || rapports.length === 0 ? (
          <EmptyState icon={<FileText size={32} strokeWidth={1.5} />} message="Aucun rapport pour le moment." />
        ) : (
          <Table.ScrollContainer minWidth={700}>
            <Table striped highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Projet</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Type</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Période</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Statut</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {rapports.map((r) => (
                  <Table.Tr key={r.id}>
                    <Table.Td>{r.projet_nom}</Table.Td>
                    <Table.Td>
                      <Text size="sm" c="dimmed">{r.type_rapport}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Text size="sm" c="dimmed">{r.periode_debut} → {r.periode_fin}</Text>
                    </Table.Td>
                    <Table.Td>
                      <StatusBadge tone={RAPPORT_STATUT_TONE[r.statut]}>{RAPPORT_STATUT_LABEL[r.statut]}</StatusBadge>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs" wrap="nowrap">
                        {r.statut === "BROUILLON" && (
                          <Button size="xs" variant="light" onClick={() => soumettre.mutate(r.id)}>Soumettre</Button>
                        )}
                        {r.statut === "SOUMIS" && peutValider && (
                          <Button size="xs" variant="light" color="teal" onClick={() => valider.mutate(r.id)}>Valider</Button>
                        )}
                        <Button size="xs" variant="subtle" onClick={() => telechargerExportRapport(r.id, "pdf")}>PDF</Button>
                        <Button size="xs" variant="subtle" onClick={() => telechargerExportRapport(r.id, "excel")}>Excel</Button>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Card>

      <Modal opened={modalOpen} onClose={() => setModalOpen(false)} title="Nouveau rapport" size="lg">
        <RapportForm onDone={() => setModalOpen(false)} />
      </Modal>
    </Stack>
  );
}
