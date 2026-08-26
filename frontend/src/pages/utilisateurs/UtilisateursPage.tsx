import { useEffect, useState } from "react";
import { Pencil } from "lucide-react";
import {
  ActionIcon,
  Badge,
  Button,
  Group,
  Modal,
  PasswordInput,
  Select,
  Stack,
  Switch,
  Table,
  Text,
  TextInput,
  Title,
  Tooltip,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useCreateUtilisateur, useUpdateUtilisateur, useUtilisateurs } from "../../api/accounts";
import type { User } from "../../types";

const ROLES = [
  { value: "ADMIN", label: "Administrateur" },
  { value: "COORDO_GENERAL", label: "Coordonnateur général" },
  { value: "CHARGE_SE", label: "Chargé de Suivi-Évaluation" },
  { value: "CHEF_PROJET", label: "Chef de projet" },
  { value: "CHEF_SERVICE", label: "Chef de service" },
  { value: "ANIMATEUR_TERRAIN", label: "Animateur de terrain" },
];

const NIVEAUX_ACCES = [
  { value: "LECTURE_SEULE", label: "Voir seulement" },
  { value: "LECTURE_ECRITURE", label: "Créer et modifier" },
];

const LIBELLES_NIVEAU_ACCES: Record<string, string> = {
  LECTURE_SEULE: "Voir seulement",
  LECTURE_ECRITURE: "Créer et modifier",
};

function ModifierUtilisateurModal({ utilisateur, onClose }: { utilisateur: User | null; onClose: () => void }) {
  const updateUtilisateur = useUpdateUtilisateur();

  const [prenom, setPrenom] = useState("");
  const [nom, setNom] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<string | null>("ANIMATEUR_TERRAIN");
  const [niveauAcces, setNiveauAcces] = useState<string | null>("LECTURE_ECRITURE");
  const [actif, setActif] = useState(true);
  const [password, setPassword] = useState("");

  // Le modal reste monté en permanence (seul `utilisateur` change à chaque
  // clic sur "Modifier") — un useEffect est donc nécessaire pour resynchroniser
  // les champs à chaque nouvel utilisateur, un useState initial ne suffit pas.
  useEffect(() => {
    if (!utilisateur) return;
    setPrenom(utilisateur.first_name);
    setNom(utilisateur.last_name);
    setEmail(utilisateur.email);
    setRole(utilisateur.role);
    setNiveauAcces(utilisateur.niveau_acces);
    setActif(utilisateur.is_active);
    setPassword("");
  }, [utilisateur]);

  const estAdmin = role === "ADMIN";

  async function handleEnregistrer() {
    if (!utilisateur) return;
    try {
      await updateUtilisateur.mutateAsync({
        id: utilisateur.id,
        payload: {
          first_name: prenom,
          last_name: nom,
          email,
          role: role as never,
          niveau_acces: (estAdmin ? "LECTURE_ECRITURE" : niveauAcces) as never,
          is_active: actif,
          ...(password ? { password } : {}),
        },
      });
      notifications.show({ message: "Utilisateur modifié", color: "green" });
      onClose();
    } catch {
      notifications.show({ message: "Erreur lors de la modification", color: "red" });
    }
  }

  return (
    <Modal opened={!!utilisateur} onClose={onClose} title={`Modifier — ${utilisateur?.username ?? ""}`}>
      <Stack gap="sm">
        <Group grow>
          <TextInput label="Prénom" value={prenom} onChange={(e) => setPrenom(e.currentTarget.value)} />
          <TextInput label="Nom" value={nom} onChange={(e) => setNom(e.currentTarget.value)} />
        </Group>
        <TextInput label="Email" value={email} onChange={(e) => setEmail(e.currentTarget.value)} />
        <Select label="Rôle" data={ROLES} value={role} onChange={setRole} />
        <Select
          label="Niveau d'accès"
          data={NIVEAUX_ACCES}
          value={estAdmin ? "LECTURE_ECRITURE" : niveauAcces}
          onChange={setNiveauAcces}
          disabled={estAdmin}
          description={estAdmin ? "Toujours complet pour un Administrateur" : undefined}
        />
        <Switch label="Compte actif" checked={actif} onChange={(e) => setActif(e.currentTarget.checked)} />
        <PasswordInput
          label="Nouveau mot de passe"
          description="Laisser vide pour ne pas le changer"
          value={password}
          onChange={(e) => setPassword(e.currentTarget.value)}
        />
        <Group justify="flex-end" mt="sm">
          <Button onClick={handleEnregistrer} loading={updateUtilisateur.isPending}>Enregistrer</Button>
        </Group>
      </Stack>
    </Modal>
  );
}

export function UtilisateursPage() {
  const { data: utilisateurs, isLoading } = useUtilisateurs();
  const createUtilisateur = useCreateUtilisateur();
  const [utilisateurEnEdition, setUtilisateurEnEdition] = useState<User | null>(null);

  const [username, setUsername] = useState("");
  const [prenom, setPrenom] = useState("");
  const [nom, setNom] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<string | null>("ANIMATEUR_TERRAIN");
  const [niveauAcces, setNiveauAcces] = useState<string | null>("LECTURE_ECRITURE");
  const [password, setPassword] = useState("");

  const estAdmin = role === "ADMIN";

  async function handleCreate() {
    if (!username || !password || !role) {
      notifications.show({ message: "Identifiant, mot de passe et rôle requis.", color: "orange" });
      return;
    }
    try {
      await createUtilisateur.mutateAsync({
        username,
        first_name: prenom,
        last_name: nom,
        email,
        role: role as never,
        niveau_acces: (estAdmin ? "LECTURE_ECRITURE" : niveauAcces) as never,
        password,
      });
      setUsername("");
      setPrenom("");
      setNom("");
      setEmail("");
      setPassword("");
      notifications.show({ message: "Utilisateur créé", color: "green" });
    } catch {
      notifications.show({ message: "Erreur lors de la création (identifiant déjà utilisé ?)", color: "red" });
    }
  }

  return (
    <Stack gap="md">
      <div>
        <Title order={2}>Utilisateurs</Title>
        <Text c="dimmed" size="sm">
          Un Administrateur a toujours accès à tout. Pour les autres, choisis le rôle (détermine les projets
          visibles) et le niveau d'accès (voir seulement, ou créer et modifier dans son périmètre).
        </Text>
      </div>

      <Stack gap="xs">
        <Group align="flex-end">
          <TextInput label="Identifiant" value={username} onChange={(e) => setUsername(e.currentTarget.value)} />
          <TextInput label="Prénom" value={prenom} onChange={(e) => setPrenom(e.currentTarget.value)} />
          <TextInput label="Nom" value={nom} onChange={(e) => setNom(e.currentTarget.value)} />
          <TextInput label="Email" value={email} onChange={(e) => setEmail(e.currentTarget.value)} />
        </Group>
        <Group align="flex-end">
          <Select label="Rôle" data={ROLES} value={role} onChange={setRole} />
          <Select
            label="Niveau d'accès"
            data={NIVEAUX_ACCES}
            value={estAdmin ? "LECTURE_ECRITURE" : niveauAcces}
            onChange={setNiveauAcces}
            disabled={estAdmin}
            description={estAdmin ? "Toujours complet pour un Administrateur" : undefined}
          />
          <PasswordInput label="Mot de passe" value={password} onChange={(e) => setPassword(e.currentTarget.value)} />
          <Button onClick={handleCreate} loading={createUtilisateur.isPending}>Créer</Button>
        </Group>
      </Stack>

      {isLoading ? (
        <div>Chargement…</div>
      ) : (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Identifiant</Table.Th>
              <Table.Th>Nom</Table.Th>
              <Table.Th>Email</Table.Th>
              <Table.Th>Rôle</Table.Th>
              <Table.Th>Accès</Table.Th>
              <Table.Th>Actif</Table.Th>
              <Table.Th w={40} />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {utilisateurs?.map((u) => (
              <Table.Tr key={u.id}>
                <Table.Td>{u.username}</Table.Td>
                <Table.Td>{u.first_name} {u.last_name}</Table.Td>
                <Table.Td>{u.email}</Table.Td>
                <Table.Td><Badge variant="light">{u.role}</Badge></Table.Td>
                <Table.Td>
                  <Badge variant="light" color={u.role === "ADMIN" || u.niveau_acces === "LECTURE_ECRITURE" ? "teal" : "gray"}>
                    {u.role === "ADMIN" ? "Complet" : LIBELLES_NIVEAU_ACCES[u.niveau_acces] ?? u.niveau_acces}
                  </Badge>
                </Table.Td>
                <Table.Td>{u.is_active ? "Oui" : "Non"}</Table.Td>
                <Table.Td>
                  <Tooltip label="Modifier">
                    <ActionIcon size="sm" variant="subtle" onClick={() => setUtilisateurEnEdition(u)}>
                      <Pencil size={13} />
                    </ActionIcon>
                  </Tooltip>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}

      <ModifierUtilisateurModal utilisateur={utilisateurEnEdition} onClose={() => setUtilisateurEnEdition(null)} />
    </Stack>
  );
}
