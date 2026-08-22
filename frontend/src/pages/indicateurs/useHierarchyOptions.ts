import { useMemo } from "react";
import { useProjets } from "../../api/projects";

export function useHierarchyOptions() {
  const { data: projets } = useProjets();

  return useMemo(() => {
    const listeProjets: { value: string; label: string }[] = [];
    const objectifsGeneraux: { value: string; label: string }[] = [];
    const objectifsSpecifiques: { value: string; label: string }[] = [];
    const activites: { value: string; label: string }[] = [];

    // Pour retrouver, à partir de n'importe quel niveau de rattachement
    // choisi, le cadre stratégique du projet concerné — pour ne proposer que
    // les éléments stratégiques pertinents à ce projet.
    const cadreParProjetId = new Map<number, number | null>();
    const projetIdParOG = new Map<number, number>();
    const projetIdParOS = new Map<number, number>();
    const projetIdParActivite = new Map<number, number>();

    for (const projet of projets ?? []) {
      listeProjets.push({ value: String(projet.id), label: `${projet.code} · ${projet.nom}` });
      cadreParProjetId.set(projet.id, projet.cadre_strategique);

      const og = projet.objectif_general;
      if (!og) continue;
      objectifsGeneraux.push({
        value: String(og.id),
        label: `${projet.code} · ${og.libelle}`,
      });
      projetIdParOG.set(og.id, projet.id);
      for (const os of og.objectifs_specifiques) {
        objectifsSpecifiques.push({
          value: String(os.id),
          label: `${projet.code} · ${og.libelle} > ${os.libelle}`,
        });
        projetIdParOS.set(os.id, projet.id);
        for (const act of os.activites) {
          activites.push({
            value: String(act.id),
            label: `${projet.code} · ${os.libelle} > ${act.libelle}`,
          });
          projetIdParActivite.set(act.id, projet.id);
        }
      }
    }
    return {
      projets: listeProjets,
      objectifsGeneraux,
      objectifsSpecifiques,
      activites,
      cadreParProjetId,
      projetIdParOG,
      projetIdParOS,
      projetIdParActivite,
    };
  }, [projets]);
}
