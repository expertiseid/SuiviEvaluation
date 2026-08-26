import { Link } from "react-router-dom";
import { FolderKanban, Wallet, Users, Gauge, MapPin } from "lucide-react";
import { Card, Paper, SimpleGrid, Stack, Table, Text, Title } from "@mantine/core";
import { useDashboardConsolide } from "../api/dashboard";
import { StatCard } from "../components/common/StatCard";
import { IndicateursStatutChart } from "../components/charts/IndicateursStatutChart";

export function DashboardConsolidePage() {
  const { data, isLoading } = useDashboardConsolide();

  if (isLoading || !data) return <Text c="dimmed">Chargement…</Text>;

  const totalIndicateurs = data.indicateurs_par_statut.reduce((somme, p) => somme + p.count, 0);

  return (
    <Stack gap="lg">
      <Title order={2}>Tableau de bord consolidé</Title>

      <SimpleGrid cols={{ base: 1, xs: 2, md: 4 }} spacing="md">
        <StatCard label="Projets" value={data.nombre_projets} icon={<FolderKanban size={20} />} color="teal" />
        <StatCard
          label="Budget total"
          value={`${Number(data.budget_total).toLocaleString("fr-FR")} FCFA`}
          icon={<Wallet size={20} />}
          color="indigo"
        />
        <StatCard label="Bénéficiaires" value={data.nombre_beneficiaires} icon={<Users size={20} />} color="grape" />
        <StatCard label="Indicateurs suivis" value={totalIndicateurs} icon={<Gauge size={20} />} color="orange" />
      </SimpleGrid>

      {data.zones_couvertes.length > 0 && (
        <Paper withBorder p="md" radius="md">
          <Text size="xs" c="dimmed" fw={600} tt="uppercase" mb="sm" style={{ letterSpacing: 0.4 }}>
            Couverture géographique
          </Text>
          <SimpleGrid cols={{ base: 2, xs: 4 }} spacing="md">
            {data.zones_couvertes.map((z) => (
              <StatCard key={z.niveau} label={z.niveau} value={z.count} icon={<MapPin size={20} />} color="cyan" />
            ))}
          </SimpleGrid>
        </Paper>
      )}

      <Paper withBorder p="md" radius="md">
        <Text size="xs" c="dimmed" fw={600} tt="uppercase" mb="sm" style={{ letterSpacing: 0.4 }}>
          Répartition des indicateurs par statut
        </Text>
        <IndicateursStatutChart parStatut={data.indicateurs_par_statut} />
      </Paper>

      <Card withBorder padding="md" radius="md">
        <Title order={4} mb="sm">Projets</Title>
        {data.projets.length === 0 ? (
          <Text c="dimmed" ta="center" py="xl">
            Aucun projet pour le moment.
          </Text>
        ) : (
          <Table.ScrollContainer minWidth={520}>
            <Table striped highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Code</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Nom</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed">Statut</Table.Th>
                  <Table.Th tt="uppercase" fz="xs" c="dimmed" ta="right">Budget</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {data.projets.map((p) => (
                  <Table.Tr key={p.id}>
                    <Table.Td>
                      <Text size="sm" fw={500} c="dimmed">{p.code}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Text component={Link} to={`/projets/${p.id}`} size="sm" fw={500} c="teal.8">
                        {p.nom}
                      </Text>
                    </Table.Td>
                    <Table.Td>{p.statut}</Table.Td>
                    <Table.Td ta="right">{Number(p.budget_total).toLocaleString("fr-FR")} FCFA</Table.Td>
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
