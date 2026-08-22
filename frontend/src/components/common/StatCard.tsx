import type { ReactNode } from "react";
import { Group, Paper, Text, ThemeIcon, type MantineColor } from "@mantine/core";

/**
 * Carte de statistique réutilisable : icône, valeur en gros caractères,
 * accent coloré, légère élévation au survol.
 */
export function StatCard({
  label,
  value,
  icon,
  color = "teal",
}: {
  label: string;
  value: ReactNode;
  icon: ReactNode;
  color?: MantineColor;
}) {
  return (
    <Paper
      withBorder
      p="md"
      radius="md"
      style={{
        borderLeft: `3px solid var(--mantine-color-${color}-6)`,
        transition: "box-shadow 150ms ease, transform 150ms ease",
      }}
      className="stat-card"
    >
      <Group justify="space-between" align="flex-start" wrap="nowrap">
        <div>
          <Text size="xs" c="dimmed" fw={600} tt="uppercase" style={{ letterSpacing: 0.4 }}>
            {label}
          </Text>
          <Text size="1.6rem" fw={700} mt={4} c="dark.7">
            {value}
          </Text>
        </div>
        <ThemeIcon size={40} radius="md" variant="light" color={color}>
          {icon}
        </ThemeIcon>
      </Group>
    </Paper>
  );
}
