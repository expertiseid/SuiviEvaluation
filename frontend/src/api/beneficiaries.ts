import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { Beneficiaire, ImportBeneficiairesResultat, Paginated, SignalementDoublon } from "../types";

export function useBeneficiaires(search?: string) {
  return useQuery({
    queryKey: ["beneficiaires", search],
    queryFn: async () =>
      (await apiClient.get<Paginated<Beneficiaire>>("/beneficiaires/", { params: { search } })).data
        .results,
  });
}

export function useBeneficiaire(id: number | undefined) {
  return useQuery({
    queryKey: ["beneficiaires", id],
    queryFn: async () => (await apiClient.get<Beneficiaire>(`/beneficiaires/${id}/`)).data,
    enabled: !!id,
  });
}

export function useCreateBeneficiaire() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Beneficiaire>) =>
      (await apiClient.post<Beneficiaire>("/beneficiaires/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["beneficiaires"] }),
  });
}

export async function telechargerModeleImportBeneficiaires() {
  const response = await apiClient.get("/beneficiaires/modele-import/", { responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "modele_import_beneficiaires.xlsx");
  document.body.appendChild(link);
  link.click();
  link.remove();
}

export function useImporterBeneficiaires() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (formData: FormData) =>
      (
        await apiClient.post<ImportBeneficiairesResultat>("/beneficiaires/importer/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      ).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["beneficiaires"] }),
  });
}

export function useVerifierDoublons() {
  return useMutation({
    mutationFn: async (beneficiaireId: number) =>
      (await apiClient.post<SignalementDoublon[]>(`/beneficiaires/${beneficiaireId}/verifier-doublons/`))
        .data,
  });
}

export function useSignalementsDoublons(statut?: string) {
  return useQuery({
    queryKey: ["signalements-doublons", statut],
    queryFn: async () =>
      (
        await apiClient.get<Paginated<SignalementDoublon>>("/signalements-doublons/", {
          params: statut ? { statut } : undefined,
        })
      ).data.results,
  });
}

export function useTraiterSignalement() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, statut }: { id: number; statut: "ECARTE" | "FUSIONNE" }) =>
      (await apiClient.patch<SignalementDoublon>(`/signalements-doublons/${id}/`, { statut })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["signalements-doublons"] }),
  });
}
