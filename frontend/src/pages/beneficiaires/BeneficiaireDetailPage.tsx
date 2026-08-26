import { Link, useParams } from "react-router-dom";
import { FolderKanban } from "lucide-react";
import { Badge, Card, Group, Stack, Table, Text, Title } from "@mantine/core";
import { useBeneficiaire } from "../../api/beneficiaries";
import { useStatutsParticuliers } from "../../api/referentiels";
import { EmptyState } from "../../components/common/EmptyState";
import { PAYS_MONDE } from "../../utils/pays";

export function BeneficiaireDetailPage() {
  const { id } = useParams();
  const beneficiaireId = Number(id);
  const { data: beneficiaire, isLoading } = useBeneficiaire(beneficiaireId);
  const { data: statuts } = useStatutsParticuliers();

  if (isLoading || !beneficiaire) return <Text>Chargement…</Text>;

  const libellesStatuts = beneficiaire.statuts_particuliers
    .map((sid) => statuts?.find((s) => s.id === sid)?.libelle)
    .filter(Boolean);

  return (
    <Stack gap="lg">
      <div>
        <Title order={2}>{beneficiaire.nom} {beneficiaire.prenom}</Title>
        <Text c="dimmed">
          {beneficiaire.sexe === "F" ? "Féminin" : "Masculin"}
          {beneficiaire.date_naissance && ` · Né(e) le ${beneficiaire.date_naissance}`}
          {beneficiaire.telephone && ` · ${beneficiaire.telephone}`}
        </Text>
      </div>

      <Card withBorder padding="md" radius="md">
        <Text size="xs" c="dimmed" fw={600} tt="uppercase" mb="sm" style={{ letterSpacing: 0.4 }}>
          Informations
        </Text>
        <Stack gap={4}>
          <Text size="sm"><strong>N° pièce d'identité :</strong> {beneficiaire.numero_piece_identite || "—"} {beneficiaire.type_piece && `(${beneficiaire.type_piece})`}</Text>
          <Text size="sm">
            <strong>Localisation :</strong>{" "}
            {PAYS_MONDE.find((p) => p.code === beneficiaire.pays)?.nom ?? (beneficiaire.pays || "—")}
            {beneficiaire.zone_nom && ` · ${beneficiaire.zone_nom}`}
          </Text>
          {libellesStatuts.length > 0 && (
            <Group gap={6} mt={4}>
              {libellesStatuts.map((l) => (
                <Badge key={l} variant="light" color="grape">{l}</Badge>
              ))}
            </Group>
          )}
        </Stack>
      </Card>

      <Card withBorder padding="md" radius="md">
        <Group gap="xs" mb="sm">
          <FolderKanban size={16} />
          <Text fw={600}>Projets qui l'ont aidé(e)</Text>
        </Group>
        {beneficiaire.participations.length === 0 ? (
          <EmptyState icon={<FolderKanban size={32} strokeWidth={1.5} />} message="Aucun projet pour le moment." />
        ) : (
          <Table.ScrollContainer minWidth={500}>
            <Table striped highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Projet</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Date d'inscription</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Rôle</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {beneficiaire.participations.map((p) => (
                  <Table.Tr key={p.id}>
                    <Table.Td>
                      <Text component={Link} to={`/projets/${p.projet}`} size="sm" fw={500} c="teal.8">
                        {p.projet_nom}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Text size="sm" c="dimmed">{p.date_inscription}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Text size="sm" c="dimmed">{p.role_dans_projet || "—"}</Text>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Card>
    </Stack>
  );
}
