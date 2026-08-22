import type { StatusTone } from "./StatusBadge";

/**
 * Palette de statut fixe (jamais thémée) partagée entre les badges et les
 * graphiques, pour que "critique" ait toujours exactement la même couleur
 * partout dans l'application.
 */
export const STATUS_HEX: Record<StatusTone, string> = {
  success: "#0ca30c",
  warning: "#fab219",
  danger: "#d03b3b",
  neutral: "#898781",
};
