import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { PointSuivi, SuiviDashboard } from "../types";

export function useSuiviDashboard(projetId: number | undefined) {
  return useQuery({
    queryKey: ["suivi-dashboard", projetId],
    queryFn: async () => (await apiClient.get<SuiviDashboard>(`/suivi/projets/${projetId}/dashboard/`)).data,
    enabled: !!projetId,
  });
}

async function telecharger(url: string, nomFichier: string) {
  const response = await apiClient.get(url, { responseType: "blob" });
  const objetUrl = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = objetUrl;
  link.setAttribute("download", nomFichier);
  document.body.appendChild(link);
  link.click();
  link.remove();
}

export async function telechargerExportSuiviExcel(projetId: number, codeProjet: string) {
  await telecharger(`/suivi/projets/${projetId}/exporter/excel/`, `suivi_${codeProjet}.xlsx`);
}

export async function telechargerExportSuiviPdf(projetId: number, codeProjet: string) {
  await telecharger(`/suivi/projets/${projetId}/exporter/pdf/`, `suivi_${codeProjet}.pdf`);
}

export function useCreatePointSuivi() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<PointSuivi>) =>
      (await apiClient.post<PointSuivi>("/points-suivi/", payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["suivi-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["projets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useUpdatePointSuivi() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: Partial<PointSuivi> }) =>
      (await apiClient.patch<PointSuivi>(`/points-suivi/${id}/`, payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["suivi-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["projets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDeletePointSuivi() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => apiClient.delete(`/points-suivi/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["suivi-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["projets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
