import Card from "./Card.jsx";

export default function RankingList({ title, subtitle, data, labelKey, sublabelKey, valueKey }) {
  const max = Math.max(...data.map((d) => d[valueKey]));

  return (
    <Card title={title} subtitle={subtitle}>
      <ul className="flex flex-col gap-3">
        {data.map((d, i) => (
          <li key={i} className="flex items-center gap-3">
            <span
              className="text-xs font-semibold w-5 text-right"
              style={{ color: "var(--color-ink-faint)" }}
            >
              {i + 1}
            </span>
            <div className="flex-1">
              <div className="flex justify-between items-baseline mb-1">
                <span className="text-sm font-medium" style={{ color: "var(--color-ink)" }}>
                  {d[labelKey]}
                  {sublabelKey && (
                    <span className="ml-1.5 text-xs font-normal" style={{ color: "var(--color-ink-faint)" }}>
                      {d[sublabelKey]}
                    </span>
                  )}
                </span>
                <span className="text-xs tabular-nums" style={{ color: "var(--color-ink-soft)" }}>
                  {d[valueKey].toLocaleString("es-MX")}
                </span>
              </div>
              <div className="h-1.5 rounded-full" style={{ background: "var(--color-primary-soft)" }}>
                <div
                  className="h-1.5 rounded-full"
                  style={{
                    width: `${(d[valueKey] / max) * 100}%`,
                    background: "var(--color-primary)",
                  }}
                />
              </div>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
