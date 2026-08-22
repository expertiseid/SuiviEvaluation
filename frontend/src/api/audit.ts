import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { HistoriqueEntree } from "../types";

export function useHistorique(appLabel: string, modelName: string, objectId: number | undefined) {
  return useQuery({
    queryKey: ["audit", appLabel, modelName, objectId],
    queryFn: async () =>
      (await apiClient.get<HistoriqueEntree[]>(`/audit/${appLabel}/${modelName}/${objectId}/historique/`))
        .data,
    enabled: !!objectId,
  });
}
