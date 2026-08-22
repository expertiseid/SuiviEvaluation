import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { Intervenant, Paginated } from "../types";

export function useIntervenants(projetId?: number) {
  return useQuery({
    queryKey: ["intervenants", projetId],
    queryFn: async () =>
      (
        await apiClient.get<Paginated<Intervenant>>("/intervenants/", {
          params: projetId ? { projets_associes: projetId } : undefined,
        })
      ).data.results,
  });
}

export function useCreateIntervenant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Intervenant>) =>
      (await apiClient.post<Intervenant>("/intervenants/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["intervenants"] }),
  });
}

export function useUpdateIntervenant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: Partial<Intervenant> }) =>
      (await apiClient.patch<Intervenant>(`/intervenants/${id}/`, payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["intervenants"] }),
  });
}

export function useDeleteIntervenant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => apiClient.delete(`/intervenants/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["intervenants"] }),
  });
}
