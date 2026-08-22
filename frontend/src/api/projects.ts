import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { Equipe, ImportProjetResultat, Paginated, Projet, ProjetInput } from "../types";

export async function telechargerModeleImportProjet() {
  const response = await apiClient.get("/projets/modele-import/", { responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "modele_import_projet.xlsx");
  document.body.appendChild(link);
  link.click();
  link.remove();
}

export function useImporterProjet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (formData: FormData) =>
      (
        await apiClient.post<ImportProjetResultat>("/projets/importer/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      ).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useProjets() {
  return useQuery({
    queryKey: ["projets"],
    queryFn: async () => (await apiClient.get<Paginated<Projet>>("/projets/")).data.results,
  });
}

export function useActivitesPourProjet(projetId: number | null) {
  return useQuery({
    queryKey: ["activites", "pour-projet", projetId],
    queryFn: async () =>
      (await apiClient.get<{ id: number; libelle: string }[]>("/activites/pour-projet/", { params: { projet: projetId } }))
        .data,
    enabled: !!projetId,
  });
}

export function useProjet(id: number | undefined) {
  return useQuery({
    queryKey: ["projets", id],
    queryFn: async () => (await apiClient.get<Projet>(`/projets/${id}/`)).data,
    enabled: !!id,
  });
}

export function useCreateProjet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<ProjetInput>) =>
      (await apiClient.post<Projet>("/projets/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useUpdateProjet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: Partial<ProjetInput> }) =>
      (await apiClient.patch<Projet>(`/projets/${id}/`, payload)).data,
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["projets"] });
      queryClient.invalidateQueries({ queryKey: ["projets", variables.id] });
    },
  });
}

export function useDeleteProjet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => apiClient.delete(`/projets/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useCreateObjectifGeneral() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { projet: number; libelle: string; description?: string }) =>
      (await apiClient.post("/objectifs-generaux/", payload)).data,
    onSuccess: (_d, variables) => queryClient.invalidateQueries({ queryKey: ["projets", variables.projet] }),
  });
}

export function useUpdateObjectifGeneral() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: { libelle?: string; description?: string } }) =>
      (await apiClient.patch(`/objectifs-generaux/${id}/`, payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useDeleteObjectifGeneral() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => apiClient.delete(`/objectifs-generaux/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useCreateObjectifSpecifique() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { objectif_general: number; libelle: string; description?: string }) =>
      (await apiClient.post("/objectifs-specifiques/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useUpdateObjectifSpecifique() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: { libelle?: string; description?: string } }) =>
      (await apiClient.patch(`/objectifs-specifiques/${id}/`, payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useDeleteObjectifSpecifique() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => apiClient.delete(`/objectifs-specifiques/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useEquipes() {
  return useQuery({
    queryKey: ["equipes"],
    queryFn: async () => (await apiClient.get<Paginated<Equipe>>("/equipes/", { params: { page_size: 200 } })).data.results,
  });
}

export function useCreateEquipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      nom: string;
      membres?: number[];
      date_debut_contrat?: string | null;
      date_fin_contrat?: string | null;
    }) => (await apiClient.post<Equipe>("/equipes/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["equipes"] }),
  });
}

export function useUpdateEquipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: number;
      payload: { nom?: string; membres?: number[]; date_debut_contrat?: string | null; date_fin_contrat?: string | null };
    }) => (await apiClient.patch<Equipe>(`/equipes/${id}/`, payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["equipes"] });
      queryClient.invalidateQueries({ queryKey: ["intervenants"] });
    },
  });
}

export function useDeleteEquipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => apiClient.delete(`/equipes/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["equipes"] });
      queryClient.invalidateQueries({ queryKey: ["projets"] });
    },
  });
}

export function useCreateActivite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      objectif_specifique: number;
      libelle: string;
      budget_alloue?: number;
      date_debut?: string;
      date_fin?: string;
      responsable?: number;
    }) => (await apiClient.post("/activites/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useUpdateActivite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: Record<string, unknown> }) =>
      (await apiClient.patch(`/activites/${id}/`, payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useDeleteActivite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => apiClient.delete(`/activites/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export async function telechargerExportProjet(id: number, format: "xlsform" | "spss") {
  const response = await apiClient.get(`/projets/${id}/export/${format}/`, { responseType: "blob" });
  const extension = format === "xlsform" ? "xlsx" : "sav";
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `${format}_projet_${id}.${extension}`);
  document.body.appendChild(link);
  link.click();
  link.remove();
}

export function useCreateSousActivite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      activite: number;
      libelle: string;
      date_debut?: string;
      date_fin?: string;
      statut?: string;
    }) => (await apiClient.post("/sous-activites/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}

export function useDeleteSousActivite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => apiClient.delete(`/sous-activites/${id}/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projets"] }),
  });
}
