import type { StatusTone } from "../components/common/StatusBadge";
import type { StatutActivite, StatutProjet } from "../types";

export const PROJET_STATUT_TONE: Record<StatutProjet, StatusTone> = {
  EN_PREPARATION: "neutral",
  EN_COURS: "success",
  CLOTURE: "neutral",
};

export const PROJET_STATUT_LABEL: Record<StatutProjet, string> = {
  EN_PREPARATION: "En préparation",
  EN_COURS: "En cours",
  CLOTURE: "Clôturé",
};

export const ACTIVITE_STATUT_TONE: Record<StatutActivite, StatusTone> = {
  NON_REALISEE: "neutral",
  EN_COURS: "warning",
  REALISEE: "success",
};

export const ACTIVITE_STATUT_LABEL: Record<StatutActivite, string> = {
  NON_REALISEE: "Non réalisée",
  EN_COURS: "En cours",
  REALISEE: "Réalisée",
};

export const SOUS_ACTIVITE_STATUT_LABEL: Record<string, string> = {
  PLANIFIEE: "Planifiée",
  EN_COURS: "En cours",
  TERMINEE: "Terminée",
};

export const SUIVI_STATUT_GLOBAL_TONE: Record<string, StatusTone> = {
  ATTEINT: "success",
  EN_COURS: "warning",
  EN_RETARD: "danger",
};

export const SUIVI_STATUT_GLOBAL_LABEL: Record<string, string> = {
  ATTEINT: "Atteint",
  EN_COURS: "En cours",
  EN_RETARD: "En retard",
};
