import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { Paginated, User } from "../types";

export function useUtilisateurs() {
  return useQuery({
    queryKey: ["utilisateurs"],
    queryFn: async () => (await apiClient.get<Paginated<User>>("/utilisateurs/")).data.results,
  });
}

export function useCreateUtilisateur() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<User> & { password: string }) =>
      (await apiClient.post<User>("/utilisateurs/", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["utilisateurs"] }),
  });
}
