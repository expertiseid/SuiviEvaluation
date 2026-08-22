import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { AppNotification, Paginated } from "../types";

export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: async () =>
      (await apiClient.get<Paginated<AppNotification>>("/notifications/", { params: { page_size: 20 } }))
        .data.results,
    refetchInterval: 60_000,
  });
}

export function useNonLuesCount() {
  return useQuery({
    queryKey: ["notifications", "non-lues-count"],
    queryFn: async () => (await apiClient.get<{ count: number }>("/notifications/non-lues-count/")).data.count,
    refetchInterval: 60_000,
  });
}

export function useMarquerLu() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => (await apiClient.post(`/notifications/${id}/marquer-lu/`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });
}

export function useToutMarquerLu() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => (await apiClient.post("/notifications/tout-marquer-lu/")).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });
}
