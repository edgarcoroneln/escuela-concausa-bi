import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import Card from "./Card.jsx";

const PALETTE = ["#0f3d5c", "#1b8a72", "#c99a2e", "#8a5cf6", "#b3401f", "#1b6fa8"];

export default function DonutChartCard({ title, subtitle, data, nameKey, valueKey }) {
  return (
    <Card title={title} subtitle={subtitle}>
      <div className="flex items-center gap-4">
        <div style={{ width: 140, height: 140, flexShrink: 0 }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={data}
                dataKey={valueKey}
                nameKey={nameKey}
                innerRadius={38}
                outerRadius={62}
                paddingAngle={2}
              >
                {data.map((_, i) => (
                  <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ borderRadius: 12, border: "1px solid var(--color-border)", fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <ul className="flex flex-col gap-2">
          {data.map((d, i) => (
            <li key={i} className="flex items-center gap-2 text-xs" style={{ color: "var(--color-ink-soft)" }}>
              <span
                className="inline-block rounded-full"
                style={{ width: 9, height: 9, background: PALETTE[i % PALETTE.length] }}
              />
              {d[nameKey]} · <span className="font-medium" style={{ color: "var(--color-ink)" }}>{d[valueKey]}%</span>
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
}
