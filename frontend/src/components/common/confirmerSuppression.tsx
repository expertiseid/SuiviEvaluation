import { Text } from "@mantine/core";
import { modals } from "@mantine/modals";

/**
 * Remplace window.confirm() par une boîte de dialogue du thème de la
 * plateforme (au lieu de la popup native du navigateur) — même geste partout
 * pour toutes les suppressions.
 */
export function confirmerSuppression({
  message,
  onConfirm,
  labelConfirmer = "Supprimer",
}: {
  message: string;
  onConfirm: () => void;
  labelConfirmer?: string;
}) {
  modals.openConfirmModal({
    title: "Confirmer la suppression",
    centered: true,
    children: <Text size="sm">{message}</Text>,
    labels: { confirm: labelConfirmer, cancel: "Annuler" },
    confirmProps: { color: "red" },
    onConfirm,
  });
}
