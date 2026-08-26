import { useState } from "react";
import { Link } from "react-router-dom";
import { Upload } from "lucide-react";
import { Button, Group, Modal, Stack, Table, Text, TextInput, Title } from "@mantine/core";
import { useBeneficiaires } from "../../api/beneficiaries";
import { BeneficiaireForm } from "./BeneficiaireForm";
import { ImportBeneficiairesModal } from "./ImportBeneficiairesModal";

export function BeneficiairesListPage() {
  const [search, setSearch] = useState("");
  const { data: beneficiaires, isLoading } = useBeneficiaires(search || undefined);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalImportOpen, setModalImportOpen] = useState(false);

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Title order={2}>Bénéficiaires</Title>
        <Group gap="xs">
          <Button variant="light" leftSection={<Upload size={16} />} onClick={() => setModalImportOpen(true)}>
            Importer depuis Excel
          </Button>
          <Button onClick={() => setModalOpen(true)}>Nouveau bénéficiaire</Button>
        </Group>
      </Group>

      <TextInput
        placeholder="Rechercher par nom, téléphone, pièce d'identité…"
        value={search}
        onChange={(e) => setSearch(e.currentTarget.value)}
        w={400}
      />

      {isLoading ? (
        <div>Chargement…</div>
      ) : (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Nom</Table.Th>
              <Table.Th>Sexe</Table.Th>
              <Table.Th>Téléphone</Table.Th>
              <Table.Th>Zone</Table.Th>
              <Table.Th>Projets</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {beneficiaires?.map((b) => (
              <Table.Tr key={b.id}>
                <Table.Td>
                  <Text component={Link} to={`/beneficiaires/${b.id}`} size="sm" fw={500} c="teal.8">
                    {b.nom} {b.prenom}
                  </Text>
                </Table.Td>
                <Table.Td>{b.sexe}</Table.Td>
                <Table.Td>{b.telephone}</Table.Td>
                <Table.Td>{b.zone_nom ?? "—"}</Table.Td>
                <Table.Td>{b.participations.map((p) => p.projet_nom).join(", ") || "—"}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}

      <Modal opened={modalOpen} onClose={() => setModalOpen(false)} title="Nouveau bénéficiaire" size="lg">
        <BeneficiaireForm onDone={() => setModalOpen(false)} />
      </Modal>

      <ImportBeneficiairesModal opened={modalImportOpen} onClose={() => setModalImportOpen(false)} />
    </Stack>
  );
}
