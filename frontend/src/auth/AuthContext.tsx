import { createContext, useEffect, useState, type ReactNode } from "react";
import { apiClient, tokenStorage } from "../api/client";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function fetchMe() {
    const { data } = await apiClient.get<User>("/utilisateurs/me/");
    setUser(data);
  }

  useEffect(() => {
    if (tokenStorage.getAccess()) {
      fetchMe()
        .catch(() => tokenStorage.clear())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  async function login(username: string, password: string) {
    const { data } = await apiClient.post("/auth/token/", { username, password });
    tokenStorage.set(data.access, data.refresh);
    await fetchMe();
  }

  function logout() {
    tokenStorage.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>
  );
}
