import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Pencil, Trash2, Upload } from "lucide-react";
import { ActionIcon, Button, Group, Modal, Pagination, Stack, Table, Text, TextInput, Title, Tooltip } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useBeneficiaires, useDeleteBeneficiaire } from "../../api/beneficiaries";
import { confirmerSuppression } from "../../components/common/confirmerSuppression";
import { messageErreurApi } from "../../utils/erreurs";
import { BeneficiaireForm } from "./BeneficiaireForm";
import { ImportBeneficiairesModal } from "./ImportBeneficiairesModal";
import type { Beneficiaire } from "../../types";

const TAILLE_PAGE = 25;

export function BeneficiairesListPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const { data, isLoading } = useBeneficiaires(search || undefined, page);
  const beneficiaires = data?.results;
  const nombrePages = data ? Math.ceil(data.count / TAILLE_PAGE) : 1;
  const deleteBeneficiaire = useDeleteBeneficiaire();
  const [modalOpen, setModalOpen] = useState(false);
  const [modalImportOpen, setModalImportOpen] = useState(false);
  const [beneficiaireEnEdition, setBeneficiaireEnEdition] = useState<Beneficiaire | null>(null);

  // Toute recherche repart de la première page — sinon on peut se retrouver
  // sur une page qui n'existe plus pour les nouveaux résultats filtrés.
  useEffect(() => {
    setPage(1);
  }, [search]);

  function handleSupprimer(b: Beneficiaire) {
    confirmerSuppression({
      message: `Supprimer "${b.nom} ${b.prenom}" ? Ses participations aux projets et signalements de doublon associés seront aussi supprimés. Cette action est irréversible.`,
      onConfirm: async () => {
        try {
          await deleteBeneficiaire.mutateAsync(b.id);
          notifications.show({ message: "Bénéficiaire supprimé", color: "green" });
        } catch (error) {
          notifications.show({
            message: messageErreurApi(error, "Erreur lors de la suppression du bénéficiaire"),
            color: "red",
          });
        }
      },
    });
  }

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

      <Group justify="space-between" align="flex-end">
        <TextInput
          placeholder="Rechercher par nom, téléphone, pièce d'identité…"
          value={search}
          onChange={(e) => setSearch(e.currentTarget.value)}
          w={400}
        />
        {data && <Text size="sm" c="dimmed">{data.count} bénéficiaire{data.count > 1 ? "s" : ""} au total</Text>}
      </Group>

      {isLoading ? (
        <div>Chargement…</div>
      ) : (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Nom</Table.Th>
              <Table.Th>Sexe</Table.Th>
              <Table.Th>Tranche d'âge</Table.Th>
              <Table.Th>Téléphone</Table.Th>
              <Table.Th>Zone</Table.Th>
              <Table.Th>Projets</Table.Th>
              <Table.Th w={40} />
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
                <Table.Td>{b.tranche_age ?? "—"}</Table.Td>
                <Table.Td>{b.telephone}</Table.Td>
                <Table.Td>{b.zone_nom ?? "—"}</Table.Td>
                <Table.Td>{b.participations.map((p) => p.projet_nom).join(", ") || "—"}</Table.Td>
                <Table.Td>
                  <Group gap={4} wrap="nowrap">
                    <Tooltip label="Modifier">
                      <ActionIcon size="sm" variant="subtle" onClick={() => setBeneficiaireEnEdition(b)}>
                        <Pencil size={13} />
                      </ActionIcon>
                    </Tooltip>
                    <Tooltip label="Supprimer">
                      <ActionIcon
                        size="sm"
                        variant="subtle"
                        color="red"
                        loading={deleteBeneficiaire.isPending && deleteBeneficiaire.variables === b.id}
                        onClick={() => handleSupprimer(b)}
                      >
                        <Trash2 size={13} />
                      </ActionIcon>
                    </Tooltip>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}

      {nombrePages > 1 && (
        <Group justify="center">
          <Pagination value={page} onChange={setPage} total={nombrePages} />
        </Group>
      )}

      <Modal opened={modalOpen} onClose={() => setModalOpen(false)} title="Nouveau bénéficiaire" size="lg">
        <BeneficiaireForm onDone={() => setModalOpen(false)} />
      </Modal>

      <Modal
        opened={!!beneficiaireEnEdition}
        onClose={() => setBeneficiaireEnEdition(null)}
        title={`Modifier — ${beneficiaireEnEdition?.nom ?? ""} ${beneficiaireEnEdition?.prenom ?? ""}`}
        size="lg"
      >
        {beneficiaireEnEdition && (
          <BeneficiaireForm
            key={beneficiaireEnEdition.id}
            beneficiaire={beneficiaireEnEdition}
            onDone={() => setBeneficiaireEnEdition(null)}
          />
        )}
      </Modal>

      <ImportBeneficiairesModal opened={modalImportOpen} onClose={() => setModalImportOpen(false)} />
    </Stack>
  );
}
