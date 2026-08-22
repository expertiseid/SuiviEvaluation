import { Badge, Group, Paper, Stack, Text, Timeline } from "@mantine/core";
import { useHistorique } from "../../api/audit";

export function HistoriqueModification({
  appLabel,
  modelName,
  objectId,
}: {
  appLabel: string;
  modelName: string;
  objectId: number;
}) {
  const { data, isLoading } = useHistorique(appLabel, modelName, objectId);

  if (isLoading) return <Text size="sm" c="dimmed">Chargement de l'historique…</Text>;
  if (!data || data.length === 0) return <Text size="sm" c="dimmed">Aucune modification enregistrée.</Text>;

  return (
    <Timeline active={data.length}>
      {data.map((entree, index) => (
        <Timeline.Item key={index} title={entree.type}>
          <Group gap="xs" mb={4}>
            <Text size="xs" c="dimmed">{new Date(entree.date).toLocaleString("fr-FR")}</Text>
            {entree.utilisateur && <Badge size="xs" variant="outline">{entree.utilisateur}</Badge>}
          </Group>
          {entree.changements.length > 0 && (
            <Paper withBorder p="xs" radius="sm">
              <Stack gap={4}>
                {entree.changements.map((c, i) => (
                  <Text key={i} size="xs">
                    <strong>{c.champ}</strong> : {String(c.ancienne_valeur ?? "—")} → {String(c.nouvelle_valeur ?? "—")}
                  </Text>
                ))}
              </Stack>
            </Paper>
          )}
        </Timeline.Item>
      ))}
    </Timeline>
  );
}
