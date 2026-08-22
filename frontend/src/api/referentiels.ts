import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { Bailleur, Financement, Paginated, Partenaire, StatutParticulier } from "../types";

export function usePartenaires() {
  return useQuery({
    queryKey: ["partenaires"],
    queryFn: async () => (await apiClient.get<Paginated<Partenaire>>("/partenaires/")).data.results,
  });
}

export function useStatutsParticuliers() {
  return useQuery({
    queryKey: ["statuts-particuliers"],
    queryFn: async () =>
      (await apiClient.get<Paginated<StatutParticulier>>("/statuts-particuliers/")).data.results,
  });
}

export function useCreatePartenaire() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Partenaire>) =>
      (await apiClient.post<Partenaire>("/partenaires/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["partenaires"] }),
  });
}

export function useBailleurs() {
  return useQuery({
    queryKey: ["bailleurs"],
    queryFn: async () => (await apiClient.get<Paginated<Bailleur>>("/bailleurs/")).data.results,
  });
}

export function useCreateBailleur() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Bailleur>) => (await apiClient.post<Bailleur>("/bailleurs/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["bailleurs"] }),
  });
}

export function useFinancements(projetId?: number) {
  return useQuery({
    queryKey: ["financements", projetId],
    queryFn: async () =>
      (
        await apiClient.get<Paginated<Financement>>("/financements/", {
          params: projetId ? { projet: projetId } : undefined,
        })
      ).data.results,
    enabled: !!projetId,
  });
}

export function useCreateFinancement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { projet: number; bailleur: number; montant_finance: number }) =>
      (await apiClient.post<Financement>("/financements/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["financements"] }),
  });
}
