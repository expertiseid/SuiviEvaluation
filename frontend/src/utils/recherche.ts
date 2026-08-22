const REGEX_DIACRITIQUES = new RegExp("[̀-ͯ]", "g");

/** Comparaison insensible à la casse et aux accents, pour une recherche qui
 * trouve "ecole" dans "École" ou "eleve" dans "Élève". */
export function correspond(texte: string, requete: string): boolean {
  if (!requete.trim()) return true;
  const normaliser = (s: string) => s.toLowerCase().normalize("NFD").replace(REGEX_DIACRITIQUES, "");
  return normaliser(texte).includes(normaliser(requete));
}
