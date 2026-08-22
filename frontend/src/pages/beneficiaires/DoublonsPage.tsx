import { Badge, Button, Group, Stack, Table, Title } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useSignalementsDoublons, useTraiterSignalement } from "../../api/beneficiaries";

export function DoublonsPage() {
  const { data: signalements, isLoading } = useSignalementsDoublons("SIGNALE");
  const traiter = useTraiterSignalement();

  async function handleTraiter(id: number, statut: "ECARTE" | "FUSIONNE") {
    try {
      await traiter.mutateAsync({ id, statut });
      notifications.show({ message: "Signalement mis à jour", color: "green" });
    } catch {
      notifications.show({ message: "Erreur lors de la mise à jour", color: "red" });
    }
  }

  return (
    <Stack gap="md">
      <Title order={2}>Doublons signalés</Title>
      {isLoading ? (
        <div>Chargement…</div>
      ) : signalements && signalements.length > 0 ? (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Bénéficiaire 1</Table.Th>
              <Table.Th>Bénéficiaire 2</Table.Th>
              <Table.Th>Méthode</Table.Th>
              <Table.Th>Score</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {signalements.map((s) => (
              <Table.Tr key={s.id}>
                <Table.Td>{s.beneficiaire_1_nom}</Table.Td>
                <Table.Td>{s.beneficiaire_2_nom}</Table.Td>
                <Table.Td>
                  <Badge variant="light">{s.methode === "PIECE_IDENTITE" ? "Pièce d'identité" : "Similarité"}</Badge>
                </Table.Td>
                <Table.Td>{s.score ?? "—"}</Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    <Button size="xs" variant="light" color="green" onClick={() => handleTraiter(s.id, "FUSIONNE")}>
                      Confirmer doublon
                    </Button>
                    <Button size="xs" variant="light" onClick={() => handleTraiter(s.id, "ECARTE")}>
                      Écarter (faux positif)
                    </Button>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      ) : (
        <div>Aucun doublon en attente de traitement.</div>
      )}
    </Stack>
  );
}
