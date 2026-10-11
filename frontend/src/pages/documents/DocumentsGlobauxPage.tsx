import { Stack, Text, Title } from "@mantine/core";
import { DocumentsTab } from "../../components/documents/DocumentsTab";

/**
 * Bibliothèque de documents libres, sans rattachement à un projet, une
 * activité ou une sous-activité précise — pour tout ce qui n'a pas sa place
 * ailleurs (ex : modèles, documents administratifs généraux...).
 */
export function DocumentsGlobauxPage() {
  return (
    <Stack gap="lg">
      <div>
        <Title order={2}>Documents</Title>
        <Text c="dimmed">Documents libres, sans rattachement à un projet en particulier.</Text>
      </div>
      <DocumentsTab />
    </Stack>
  );
}
