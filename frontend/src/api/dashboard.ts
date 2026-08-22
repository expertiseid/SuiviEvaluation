import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { DashboardConsolide, DashboardProjet, Echeance } from "../types";

export function useDashboardConsolide() {
  return useQuery({
    queryKey: ["dashboard", "consolide"],
    queryFn: async () => (await apiClient.get<DashboardConsolide>("/dashboard/consolide/")).data,
  });
}

export function useEcheances() {
  return useQuery({
    queryKey: ["dashboard", "echeances"],
    queryFn: async () => (await apiClient.get<Echeance[]>("/dashboard/echeances/")).data,
    refetchInterval: 5 * 60 * 1000,
  });
}

export function useDashboardProjet(projetId: number | undefined) {
  return useQuery({
    queryKey: ["dashboard", "projet", projetId],
    queryFn: async () => (await apiClient.get<DashboardProjet>(`/dashboard/projet/${projetId}/`)).data,
    enabled: !!projetId,
  });
}
