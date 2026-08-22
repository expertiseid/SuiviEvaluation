import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { ImportPlanificationCompleteResultat } from "../types";

export async function telechargerModeleImportComplet() {
  const response = await apiClient.get("/planification/modele-import/", { responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "modele_planification_complete.xlsx");
  document.body.appendChild(link);
  link.click();
  link.remove();
}

export function useImporterComplet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (formData: FormData) =>
      (
        await apiClient.post<ImportPlanificationCompleteResultat>("/planification/importer/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      ).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cadres-strategiques"] });
      queryClient.invalidateQueries({ queryKey: ["types-niveaux"] });
      queryClient.invalidateQueries({ queryKey: ["elements-strategiques"] });
      queryClient.invalidateQueries({ queryKey: ["projets"] });
      queryClient.invalidateQueries({ queryKey: ["indicateurs"] });
      queryClient.invalidateQueries({ queryKey: ["beneficiaires"] });
    },
  });
}
