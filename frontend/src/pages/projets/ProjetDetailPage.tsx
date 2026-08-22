import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Check, Download, Pencil, Plus, Search, Trash2, X } from "lucide-react";
import {
  ActionIcon,
  Badge,
  Button,
  Card,
  Group,
  List,
  Menu,
  Modal,
  Stack,
  Table,
  Tabs,
  Text,
  TextInput,
  Title,
  Tooltip,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
  useProjet,
  useCreateObjectifGeneral,
  useCreateObjectifSpecifique,
  useUpdateObjectifGeneral,
  useUpdateObjectifSpecifique,
  useDeleteObjectifGeneral,
  useDeleteObjectifSpecifique,
  useDeleteActivite,
  useDeleteSousActivite,
  useDeleteProjet,
  telechargerExportProjet,
} from "../../api/projects";
import { useDashboardProjet } from "../../api/dashboard";
import { AlerteBadge } from "../../components/indicators/AlerteBadge";
import { confirmerSuppression } from "../../components/common/confirmerSuppression";
import { HistoriqueModification } from "../../components/audit/HistoriqueModification";
import { DocumentsTab } from "../../components/documents/DocumentsTab";
import { BoutonModeEdition } from "../../components/common/BoutonModeEdition";
import { ActiviteForm } from "./ActiviteForm";
import { SousActiviteForm } from "./SousActiviteForm";
import { FinancementsTab } from "./FinancementsTab";
import { EquipeTab } from "./EquipeTab";
import { ProjetForm } from "./ProjetForm";
import { TauxParIndicateurChart } from "../../components/charts/TauxParIndicateurChart";
import { PAYS_MONDE } from "../../utils/pays";
import { correspond } from "../../utils/recherche";
import type { Activite } from "../../types";

function LibelleEditable({
  valeur,
  onSave,
  onDelete,
  size,
  fw,
  editable,
}: {
  valeur: string;
  onSave: (nouveauLibelle: string) => void;
  onDelete?: () => void;
  size?: string;
  fw?: number;
  editable: boolean;
}) {
  const [edition, setEdition] = useState(false);
  const [valeurEditee, setValeurEditee] = useState(valeur);

  if (edition) {
    return (
      <Group gap={6} wrap="nowrap">
        <TextInput
          size="xs"
          value={valeurEditee}
          onChange={(e) => setValeurEditee(e.currentTarget.value)}
          style={{ flex: 1 }}
          autoFocus
        />
        <ActionIcon
          size="sm"
          variant="subtle"
          color="green"
          onClick={() => {
            if (valeurEditee.trim()) {
              onSave(valeurEditee.trim());
              setEdition(false);
            }
          }}
        >
          <Check size={14} />
        </ActionIcon>
        <ActionIcon
          size="sm"
          variant="subtle"
          onClick={() => {
            setValeurEditee(valeur);
            setEdition(false);
          }}
        >
          <X size={14} />
        </ActionIcon>
      </Group>
    );
  }

  return (
    <Group gap={6} wrap="nowrap">
      <Text fw={fw ?? 500} size={size}>{valeur}</Text>
      {editable && (
      <Group gap={6} wrap="nowrap">
        <Tooltip label="Modifier le libellé">
          <ActionIcon size="sm" variant="subtle" onClick={() => setEdition(true)}>
            <Pencil size={12} />
          </ActionIcon>
        </Tooltip>
        {onDelete && (
          <Tooltip label="Supprimer">
            <ActionIcon size="sm" variant="subtle" color="red" onClick={onDelete}>
              <Trash2 size={12} />
            </ActionIcon>
          </Tooltip>
        )}
      </Group>
      )}
    </Group>
  );
}

function AjoutInline({ placeholder, onAdd }: { placeholder: string; onAdd: (libelle: string) => void }) {
  const [value, setValue] = useState("");
  return (
    <Group gap="xs" mt={4}>
      <TextInput size="xs" placeholder={placeholder} value={value} onChange={(e) => setValue(e.currentTarget.value)} />
      <Button
        size="xs"
        variant="light"
        onClick={() => {
          if (value.trim()) {
            onAdd(value.trim());
            setValue("");
          }
        }}
      >
        Ajouter
      </Button>
    </Group>
  );
}

export function ProjetDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const projetId = Number(id);
  const { data: projet, isLoading } = useProjet(projetId);
  const { data: dashboard } = useDashboardProjet(projetId);

  const createOG = useCreateObjectifGeneral();
  const createOS = useCreateObjectifSpecifique();
  const updateOG = useUpdateObjectifGeneral();
  const updateOS = useUpdateObjectifSpecifique();
  const deleteOG = useDeleteObjectifGeneral();
  const deleteOS = useDeleteObjectifSpecifique();
  const deleteActivite = useDeleteActivite();
  const deleteSousActivite = useDeleteSousActivite();
  const deleteProjet = useDeleteProjet();

  const [modalActiviteFor, setModalActiviteFor] = useState<number | null>(null);
  const [modalActiviteEdition, setModalActiviteEdition] = useState<Activite | null>(null);
  const [modalSousActiviteFor, setModalSousActiviteFor] = useState<number | null>(null);
  const [modalEditionOuvert, setModalEditionOuvert] = useState(false);
  const [recherchePlan, setRecherchePlan] = useState("");
  const [editionActive, setEditionActive] = useState(false);

  // Un objectif spécifique / activité est visible s'il correspond lui-même à
  // la recherche, ou si un de ses descendants y correspond — pour ne jamais
  // masquer le chemin vers un résultat trouvé en profondeur (ex: chercher
  // une sous-activité doit garder visibles son activité et son OS parents).
  const objectifsSpecifiquesFiltres = useMemo(() => {
    const liste = projet?.objectif_general?.objectifs_specifiques ?? [];
    if (!recherchePlan.trim()) return liste;
    return liste
      .map((os) => {
        const activitesFiltrees = os.activites
          .map((act) => {
            const sousActivitesFiltrees = act.sous_activites.filter((sa) => correspond(sa.libelle, recherchePlan));
            const activiteMatch = correspond(act.libelle, recherchePlan) || correspond(act.code_activite ?? "", recherchePlan);
            if (!activiteMatch && sousActivitesFiltrees.length === 0) return null;
            return { ...act, sous_activites: activiteMatch ? act.sous_activites : sousActivitesFiltrees };
          })
          .filter((act): act is Activite => act !== null);
        const osMatch = correspond(os.libelle, recherchePlan);
        if (!osMatch && activitesFiltrees.length === 0) return null;
        return { ...os, activites: osMatch ? os.activites : activitesFiltrees };
      })
      .filter((os): os is NonNullable<typeof os> => os !== null);
  }, [projet, recherchePlan]);

  if (isLoading || !projet) return <Text>Chargement…</Text>;

  const budgetDejaAlloue = (projet.objectif_general?.objectifs_specifiques ?? [])
    .flatMap((os) => os.activites)
    .reduce((somme, act) => somme + (act.budget_alloue ? Number(act.budget_alloue) : 0), 0);

  function handleSupprimer() {
    if (!projet) return;
    confirmerSuppression({
      message: `Supprimer le projet "${projet.nom}" ainsi que toute sa planification, ses indicateurs et ses rapports ? Cette action est irréversible.`,
      onConfirm: async () => {
        try {
          await deleteProjet.mutateAsync(projetId);
          notifications.show({ message: "Projet supprimé", color: "green" });
          navigate("/projets");
        } catch {
          notifications.show({ message: "Erreur lors de la suppression du projet", color: "red" });
        }
      },
    });
  }

  function supprimerAvecConfirmation(message: string, supprimer: () => Promise<unknown>, labelSucces: string) {
    confirmerSuppression({
      message,
      onConfirm: async () => {
        try {
          await supprimer();
          notifications.show({ message: labelSucces, color: "green" });
        } catch {
          notifications.show({ message: "Erreur lors de la suppression", color: "red" });
        }
      },
    });
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <div>
          <Title order={2}>{projet.nom}</Title>
          <Text c="dimmed">
            {projet.code} · {projet.statut}
            {projet.cadre_strategique_nom && ` · ${projet.cadre_strategique_nom}`}
            {projet.pays.length > 0 &&
              ` · ${projet.pays.map((code) => PAYS_MONDE.find((p) => p.code === code)?.nom ?? code).join(", ")}`}
          </Text>
        </div>
        <Group gap="lg">
          {dashboard && dashboard.indicateurs_par_statut.length > 0 && (
            <Group gap="xs">
              {dashboard.indicateurs_par_statut.map((p) => (
                <Group key={p.libelle} gap={4} wrap="nowrap">
                  <AlerteBadge palier={p} />
                  <Text size="sm">{p.count}</Text>
                </Group>
              ))}
            </Group>
          )}
          <Menu shadow="md" width={220}>
            <Menu.Target>
              <Button variant="light" leftSection={<Download size={16} />}>Exporter</Button>
            </Menu.Target>
            <Menu.Dropdown>
              <Menu.Label>Pour la collecte terrain</Menu.Label>
              <Menu.Item onClick={() => telechargerExportProjet(projetId, "xlsform")}>
                XLSForm (KoboToolbox/ODK)
              </Menu.Item>
              <Menu.Label>Pour l'analyse statistique</Menu.Label>
              <Menu.Item onClick={() => telechargerExportProjet(projetId, "spss")}>
                Données SPSS (.sav)
              </Menu.Item>
            </Menu.Dropdown>
          </Menu>
          <BoutonModeEdition actif={editionActive} onToggle={() => setEditionActive((v) => !v)} />
          {editionActive && (
          <Group gap="lg">
            <Tooltip label="Modifier le projet">
              <ActionIcon variant="subtle" size="lg" onClick={() => setModalEditionOuvert(true)}>
                <Pencil size={18} />
              </ActionIcon>
            </Tooltip>
            <Tooltip label="Supprimer le projet">
              <ActionIcon variant="subtle" color="red" size="lg" loading={deleteProjet.isPending} onClick={handleSupprimer}>
                <Trash2 size={18} />
              </ActionIcon>
            </Tooltip>
          </Group>
          )}
        </Group>
      </Group>

      <Tabs defaultValue="hierarchie">
        <Tabs.List>
          <Tabs.Tab value="hierarchie">Planification</Tabs.Tab>
          <Tabs.Tab value="equipe">Équipe de projet</Tabs.Tab>
          <Tabs.Tab value="indicateurs">Indicateurs</Tabs.Tab>
          <Tabs.Tab value="financement">Financement</Tabs.Tab>
          <Tabs.Tab value="documents">Documents</Tabs.Tab>
          <Tabs.Tab value="historique">Historique</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="hierarchie" pt="md">
          <Card withBorder padding="md">
            {!projet.objectif_general ? (
              <>
                <Text size="sm" c="dimmed" mb={4}>
                  Ce projet n'a pas encore d'objectif général — définis-le d'abord (un seul par projet).
                </Text>
                <AjoutInline
                  placeholder="Objectif général du projet…"
                  onAdd={(libelle) => createOG.mutate({ projet: projetId, libelle })}
                />
              </>
            ) : (
              <>
                <div style={{ marginBottom: 8 }}>
                  <Badge color="teal" variant="light" size="sm" mb={4}>Objectif général</Badge>
                  <LibelleEditable
                    valeur={projet.objectif_general.libelle}
                    onSave={(libelle) => updateOG.mutate({ id: projet.objectif_general!.id, payload: { libelle } })}
                    onDelete={() =>
                      supprimerAvecConfirmation(
                        `Supprimer l'objectif général "${projet.objectif_general!.libelle}" ainsi que tous ses objectifs spécifiques, activités, sous-activités et indicateurs liés ? Cette action est irréversible.`,
                        () => deleteOG.mutateAsync(projet.objectif_general!.id),
                        "Objectif général supprimé",
                      )
                    }
                    size="lg"
                    fw={700}
                    editable={editionActive}
                  />
                </div>
                <AjoutInline
                  placeholder="Nouvel objectif spécifique…"
                  onAdd={(libelle) => createOS.mutate({ objectif_general: projet.objectif_general!.id, libelle })}
                />
                {projet.objectif_general.objectifs_specifiques.length > 0 && (
                  <TextInput
                    placeholder="Rechercher un objectif, une activité ou une sous-activité…"
                    leftSection={<Search size={15} />}
                    value={recherchePlan}
                    onChange={(e) => setRecherchePlan(e.currentTarget.value)}
                    maw={400}
                    mt="sm"
                  />
                )}
                {recherchePlan.trim() && objectifsSpecifiquesFiltres.length === 0 && (
                  <Text c="dimmed" size="sm" mt="sm">Aucun résultat ne correspond à la recherche.</Text>
                )}
                <List mt="sm" spacing="xs">
                  {objectifsSpecifiquesFiltres.map((os) => (
                    <List.Item key={os.id}>
                      <Badge color="blue" variant="light" size="sm" mb={4}>Objectif spécifique</Badge>
                      <Group gap={6}>
                        <LibelleEditable
                          valeur={os.libelle}
                          onSave={(libelle) => updateOS.mutate({ id: os.id, payload: { libelle } })}
                          onDelete={() =>
                            supprimerAvecConfirmation(
                              `Supprimer l'objectif spécifique "${os.libelle}" ainsi que ses activités, sous-activités et indicateurs liés ? Cette action est irréversible.`,
                              () => deleteOS.mutateAsync(os.id),
                              "Objectif spécifique supprimé",
                            )
                          }
                          editable={editionActive}
                        />
                        <Tooltip label="Nouvelle activité">
                          <ActionIcon size="sm" variant="subtle" onClick={() => setModalActiviteFor(os.id)}>
                            <Plus size={14} />
                          </ActionIcon>
                        </Tooltip>
                      </Group>
                      <List mt={4} withPadding spacing={4}>
                        {os.activites.map((act) => (
                          <List.Item key={act.id}>
                            <Badge color="grape" variant="light" size="xs" mb={4}>Activité</Badge>
                            <Group gap={6} wrap="nowrap">
                              {act.code_activite && <Text size="xs" c="dimmed">{act.code_activite}</Text>}
                              <Text size="sm">{act.libelle}</Text>
                              {editionActive && (
                                <Tooltip label="Modifier l'activité">
                                  <ActionIcon size="sm" variant="subtle" onClick={() => setModalActiviteEdition(act)}>
                                    <Pencil size={12} />
                                  </ActionIcon>
                                </Tooltip>
                              )}
                              <Tooltip label="Nouvelle sous-activité">
                                <ActionIcon size="sm" variant="subtle" onClick={() => setModalSousActiviteFor(act.id)}>
                                  <Plus size={14} />
                                </ActionIcon>
                              </Tooltip>
                              {editionActive && (
                                <Tooltip label="Supprimer l'activité">
                                  <ActionIcon
                                    size="sm"
                                    variant="subtle"
                                    color="red"
                                    onClick={() =>
                                      supprimerAvecConfirmation(
                                        `Supprimer l'activité "${act.libelle}" ainsi que ses sous-activités et indicateurs liés ? Cette action est irréversible.`,
                                        () => deleteActivite.mutateAsync(act.id),
                                        "Activité supprimée",
                                      )
                                    }
                                  >
                                    <Trash2 size={12} />
                                  </ActionIcon>
                                </Tooltip>
                              )}
                            </Group>
                            <List mt={2} withPadding size="sm">
                              {act.sous_activites.map((sa) => (
                                <List.Item key={sa.id}>
                                  <Badge color="gray" variant="light" size="xs" mb={2}>Sous-activité</Badge>
                                  <Group gap={6} wrap="nowrap">
                                    <Text size="sm">{sa.libelle}</Text>
                                    {editionActive && (
                                      <Tooltip label="Supprimer la sous-activité">
                                        <ActionIcon
                                          size="sm"
                                          variant="subtle"
                                          color="red"
                                          onClick={() =>
                                            supprimerAvecConfirmation(
                                              `Supprimer la sous-activité "${sa.libelle}" ? Cette action est irréversible.`,
                                              () => deleteSousActivite.mutateAsync(sa.id),
                                              "Sous-activité supprimée",
                                            )
                                          }
                                        >
                                          <Trash2 size={12} />
                                        </ActionIcon>
                                      </Tooltip>
                                    )}
                                  </Group>
                                </List.Item>
                              ))}
                            </List>
                          </List.Item>
                        ))}
                      </List>
                    </List.Item>
                  ))}
                </List>
              </>
            )}
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="equipe" pt="md">
          <EquipeTab projetId={projetId} />
        </Tabs.Panel>

        <Tabs.Panel value="indicateurs" pt="md">
          {dashboard && dashboard.indicateurs.length > 0 && (
            <Card withBorder padding="md" radius="md" mb="md">
              <Text size="xs" c="dimmed" fw={600} tt="uppercase" mb="sm" style={{ letterSpacing: 0.4 }}>
                Taux de réalisation par indicateur
              </Text>
              <TauxParIndicateurChart indicateurs={dashboard.indicateurs} />
            </Card>
          )}
          <Table striped>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Indicateur</Table.Th>
                <Table.Th>Taux de réalisation</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {dashboard?.indicateurs.map((i) => (
                <Table.Tr key={i.id}>
                  <Table.Td>{i.libelle}</Table.Td>
                  <Table.Td>
                    <AlerteBadge palier={i.palier_actuel} taux={i.taux_realisation} />
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Tabs.Panel>

        <Tabs.Panel value="financement" pt="md">
          <FinancementsTab projetId={projetId} />
        </Tabs.Panel>

        <Tabs.Panel value="documents" pt="md">
          <DocumentsTab projetId={projetId} />
        </Tabs.Panel>

        <Tabs.Panel value="historique" pt="md">
          <HistoriqueModification appLabel="projects" modelName="projet" objectId={projetId} />
        </Tabs.Panel>
      </Tabs>

      <Modal opened={modalActiviteFor !== null} onClose={() => setModalActiviteFor(null)} title="Nouvelle activité" size="lg">
        {modalActiviteFor !== null && (
          <ActiviteForm
            objectifSpecifiqueId={modalActiviteFor}
            cadreStrategiqueId={projet.cadre_strategique}
            projetId={projetId}
            budgetProjetTotal={Number(projet.budget_total)}
            budgetDejaAlloue={budgetDejaAlloue}
            onDone={() => setModalActiviteFor(null)}
          />
        )}
      </Modal>

      <Modal opened={modalActiviteEdition !== null} onClose={() => setModalActiviteEdition(null)} title="Modifier l'activité" size="lg">
        {modalActiviteEdition !== null && (
          <ActiviteForm
            objectifSpecifiqueId={modalActiviteEdition.objectif_specifique}
            cadreStrategiqueId={projet.cadre_strategique}
            projetId={projetId}
            budgetProjetTotal={Number(projet.budget_total)}
            budgetDejaAlloue={budgetDejaAlloue - (modalActiviteEdition.budget_alloue ? Number(modalActiviteEdition.budget_alloue) : 0)}
            activite={modalActiviteEdition}
            onDone={() => setModalActiviteEdition(null)}
          />
        )}
      </Modal>

      <Modal opened={modalSousActiviteFor !== null} onClose={() => setModalSousActiviteFor(null)} title="Nouvelle sous-activité" size="lg">
        {modalSousActiviteFor !== null && (
          <SousActiviteForm
            activiteId={modalSousActiviteFor}
            cadreStrategiqueId={projet.cadre_strategique}
            onDone={() => setModalSousActiviteFor(null)}
          />
        )}
      </Modal>

      <Modal opened={modalEditionOuvert} onClose={() => setModalEditionOuvert(false)} title="Modifier le projet" size="lg">
        <ProjetForm projet={projet} onDone={() => setModalEditionOuvert(false)} />
      </Modal>
    </Stack>
  );
}
