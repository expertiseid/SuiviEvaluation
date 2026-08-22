import type { ReactNode } from "react";
import { Badge } from "@mantine/core";
import { STATUS_HEX } from "./statusPalette";

export type StatusTone = "success" | "warning" | "danger" | "neutral";

/**
 * Badge de statut réutilisable : largeur qui suit son contenu, jamais tronqué
 * (pas d'ellipsis même dans un conteneur étroit) et couleurs sémantiques
 * cohérentes dans toute l'application (mêmes teintes que les graphiques).
 */
export function StatusBadge({ tone, children }: { tone: StatusTone; children: ReactNode }) {
  return (
    <Badge
      color={STATUS_HEX[tone]}
      variant="light"
      radius="sm"
      size="md"
      styles={{
        root: { textTransform: "none", maxWidth: "none" },
        label: { overflow: "visible", textOverflow: "unset", whiteSpace: "nowrap" },
      }}
    >
      {children}
    </Badge>
  );
}
