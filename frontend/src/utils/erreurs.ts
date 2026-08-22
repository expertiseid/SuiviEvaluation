import { isAxiosError } from "axios";

/**
 * Remonte le message de validation renvoyé par l'API (ex : "Un objet Équipe
 * avec ce champ nom existe déjà.") au lieu d'un message générique — pour que
 * l'utilisateur comprenne exactement ce qui bloque (ex : nom déjà pris).
 */
export function messageErreurApi(error: unknown, message: string): string {
  if (isAxiosError(error) && error.response?.data) {
    const data = error.response.data;
    if (typeof data.detail === "string") return data.detail;
    for (const valeur of Object.values(data)) {
      if (Array.isArray(valeur) && typeof valeur[0] === "string") return valeur[0];
      if (typeof valeur === "string") return valeur;
    }
  }
  return message;
}
