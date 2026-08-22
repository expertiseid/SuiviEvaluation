import { Bar, BarChart, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { RepartitionPalier } from "../../types";

export function IndicateursStatutChart({ parStatut }: { parStatut: RepartitionPalier[] }) {
  if (parStatut.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={Math.max(120, parStatut.length * 36)}>
      <BarChart data={parStatut} layout="vertical" margin={{ top: 4, right: 24, bottom: 4, left: 4 }}>
        <XAxis type="number" hide allowDecimals={false} />
        <YAxis
          type="category"
          dataKey="libelle"
          width={90}
          tickLine={false}
          axisLine={false}
          tick={{ fill: "var(--mantine-color-dimmed)", fontSize: 12 }}
        />
        <Tooltip
          cursor={{ fill: "var(--mantine-color-gray-1)" }}
          formatter={(value) => [`${value} indicateur(s)`, ""]}
          labelFormatter={() => ""}
        />
        <Bar dataKey="count" radius={[0, 4, 4, 0]} maxBarSize={28}>
          {parStatut.map((entry) => (
            <Cell key={entry.libelle} fill={entry.couleur} />
          ))}
          <LabelList dataKey="count" position="right" style={{ fill: "var(--mantine-color-dark-6)", fontSize: 12, fontWeight: 600 }} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
