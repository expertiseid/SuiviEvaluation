import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { Paginated, RapportSuivi } from "../types";

export function useRapports(projetId?: number) {
  return useQuery({
    queryKey: ["rapports", projetId],
    queryFn: async () =>
      (
        await apiClient.get<Paginated<RapportSuivi>>("/rapports/", {
          params: projetId ? { projet: projetId } : undefined,
        })
      ).data.results,
  });
}

export function useCreateRapport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<RapportSuivi>) =>
      (await apiClient.post<RapportSuivi>("/rapports/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rapports"] }),
  });
}

export function useSoumettreRapport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => (await apiClient.post(`/rapports/${id}/soumettre/`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rapports"] }),
  });
}

export function useValiderRapport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => (await apiClient.post(`/rapports/${id}/valider/`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rapports"] }),
  });
}

export async function telechargerExportRapport(id: number, format: "pdf" | "excel") {
  const response = await apiClient.get(`/rapports/${id}/export/${format}/`, { responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `rapport_${id}.${format === "pdf" ? "pdf" : "xlsx"}`);
  document.body.appendChild(link);
  link.click();
  link.remove();
}
