import type { ReactNode } from "react";
import { Stack, Text } from "@mantine/core";

export function EmptyState({ icon, message }: { icon?: ReactNode; message: string }) {
  return (
    <Stack align="center" gap={6} py="xl">
      {icon}
      <Text c="dimmed" size="sm">
        {message}
      </Text>
    </Stack>
  );
}
