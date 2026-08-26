import type { ReactNode } from "react";
import { Group, Paper, Text, ThemeIcon, type MantineColor } from "@mantine/core";

const ESPACE_INSECABLE = String.fromCharCode(160);

// Un nombre à groupes ("395 000 000 FCFA") ne doit jamais se couper au
// milieu d'un groupe de chiffres — seule la coupure avant l'unité est
// acceptable. On rend donc insécables les espaces entre deux chiffres,
// en laissant l'espace avant un mot (l'unité) normalement coupable.
function insecableEntreChiffres(valeur: string): string {
  return valeur.replace(/(\d) (?=\d)/g, `$1${ESPACE_INSECABLE}`);
}

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
  const texteLong = typeof value === "string" && value.length > 12;

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
        <div style={{ minWidth: 0 }}>
          <Text size="xs" c="dimmed" fw={600} tt="uppercase" style={{ letterSpacing: 0.4 }}>
            {label}
          </Text>
          <Text size={texteLong ? "1.15rem" : "1.6rem"} fw={700} mt={4} c="dark.7" style={{ lineHeight: 1.25 }}>
            {typeof value === "string" ? insecableEntreChiffres(value) : value}
          </Text>
        </div>
        <ThemeIcon size={40} radius="md" variant="light" color={color}>
          {icon}
        </ThemeIcon>
      </Group>
    </Paper>
  );
}
