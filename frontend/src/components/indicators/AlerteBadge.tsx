import { Badge } from "@mantine/core";

export function AlerteBadge({
  palier,
  taux,
}: {
  palier: { libelle: string; couleur: string } | null;
  taux?: number;
}) {
  if (!palier) return null;
  return (
    <Badge
      color={palier.couleur}
      variant="light"
      radius="sm"
      size="md"
      styles={{
        root: { textTransform: "none", maxWidth: "none" },
        label: { overflow: "visible", textOverflow: "unset", whiteSpace: "nowrap" },
      }}
    >
      {taux !== undefined ? `${palier.libelle} · ${taux}%` : palier.libelle}
    </Badge>
  );
}
