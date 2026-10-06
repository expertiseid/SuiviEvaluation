import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { Dossier, DocumentVersion, GedDocument, Paginated, PieceJustificative } from "../types";

export function usePiecesJustificatives(params: { valeur_indicateur?: number }) {
  return useQuery({
    queryKey: ["pieces-justificatives", params],
    queryFn: async () =>
      (await apiClient.get<Paginated<PieceJustificative>>("/pieces-justificatives/", { params })).data
        .results,
    enabled: !!params.valeur_indicateur,
  });
}

export function useUploadPieceJustificative() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (formData: FormData) =>
      (
        await apiClient.post<PieceJustificative>("/pieces-justificatives/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      ).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pieces-justificatives"] }),
  });
}

export function useDossiers(projetId?: number) {
  return useQuery({
    queryKey: ["dossiers", projetId],
    queryFn: async () =>
      (
        await apiClient.get<Paginated<Dossier>>("/dossiers/", {
          params: projetId ? { projet: projetId } : undefined,
        })
      ).data.results,
  });
}

export function useCreateDossier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { nom: string; projet?: number | null; parent?: number | null }) =>
      (await apiClient.post<Dossier>("/dossiers/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["dossiers"] }),
  });
}

export function useDocuments(params: {
  dossier?: number;
  projet?: number;
  activite?: number;
  sous_activite?: number;
  search?: string;
}) {
  return useQuery({
    queryKey: ["ged-documents", params],
    queryFn: async () =>
      (await apiClient.get<Paginated<GedDocument>>("/documents/", { params })).data.results,
  });
}

export function useCreateDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (formData: FormData) =>
      (
        await apiClient.post<GedDocument>("/documents/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      ).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["ged-documents"] }),
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/documents/${id}/`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["ged-documents"] }),
  });
}

export function useNouvelleVersion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ documentId, formData }: { documentId: number; formData: FormData }) =>
      (
        await apiClient.post<DocumentVersion>(`/documents/${documentId}/nouvelle-version/`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      ).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["ged-documents"] }),
  });
}

export function useDocumentVersions(documentId: number | undefined) {
  return useQuery({
    queryKey: ["ged-document-versions", documentId],
    queryFn: async () => (await apiClient.get<DocumentVersion[]>(`/documents/${documentId}/versions/`)).data,
    enabled: !!documentId,
  });
}
