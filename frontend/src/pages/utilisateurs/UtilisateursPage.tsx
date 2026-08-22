import { useState } from "react";
import { Badge, Button, Group, PasswordInput, Select, Stack, Table, TextInput, Title } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useCreateUtilisateur, useUtilisateurs } from "../../api/accounts";

const ROLES = [
  { value: "ADMIN", label: "Administrateur" },
  { value: "COORDO_GENERAL", label: "Coordonnateur général" },
  { value: "CHARGE_SE", label: "Chargé de Suivi-Évaluation" },
  { value: "CHEF_PROJET", label: "Chef de projet" },
  { value: "ANIMATEUR_TERRAIN", label: "Animateur de terrain" },
];

export function UtilisateursPage() {
  const { data: utilisateurs, isLoading } = useUtilisateurs();
  const createUtilisateur = useCreateUtilisateur();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<string | null>("ANIMATEUR_TERRAIN");
  const [password, setPassword] = useState("");

  async function handleCreate() {
    if (!username || !password || !role) {
      notifications.show({ message: "Identifiant, mot de passe et rôle requis.", color: "orange" });
      return;
    }
    try {
      await createUtilisateur.mutateAsync({ username, email, role: role as never, password });
      setUsername("");
      setEmail("");
      setPassword("");
      notifications.show({ message: "Utilisateur créé", color: "green" });
    } catch {
      notifications.show({ message: "Erreur lors de la création (identifiant déjà utilisé ?)", color: "red" });
    }
  }

  return (
    <Stack gap="md">
      <Title order={2}>Utilisateurs</Title>

      <Group align="flex-end">
        <TextInput label="Identifiant" value={username} onChange={(e) => setUsername(e.currentTarget.value)} />
        <TextInput label="Email" value={email} onChange={(e) => setEmail(e.currentTarget.value)} />
        <Select label="Rôle" data={ROLES} value={role} onChange={setRole} />
        <PasswordInput label="Mot de passe" value={password} onChange={(e) => setPassword(e.currentTarget.value)} />
        <Button onClick={handleCreate} loading={createUtilisateur.isPending}>Créer</Button>
      </Group>

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
              <Table.Th>Actif</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {utilisateurs?.map((u) => (
              <Table.Tr key={u.id}>
                <Table.Td>{u.username}</Table.Td>
                <Table.Td>{u.first_name} {u.last_name}</Table.Td>
                <Table.Td>{u.email}</Table.Td>
                <Table.Td><Badge variant="light">{u.role}</Badge></Table.Td>
                <Table.Td>{u.is_active ? "Oui" : "Non"}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}
    </Stack>
  );
}
