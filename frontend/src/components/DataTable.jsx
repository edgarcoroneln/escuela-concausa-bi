import Card from "./Card.jsx";

// columns: [{ key, label, align? }]
export default function DataTable({ title, subtitle, columns, rows }) {
  return (
    <Card title={title} subtitle={subtitle}>
      <div className="overflow-x-auto -mx-1">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr>
              {columns.map((c) => (
                <th
                  key={c.key}
                  className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-left whitespace-nowrap"
                  style={{ color: "var(--color-ink-faint)", borderBottom: "1px solid var(--color-border)" }}
                >
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} style={{ borderBottom: "1px solid var(--color-border)" }}>
                {columns.map((c) => (
                  <td key={c.key} className="px-3 py-2 whitespace-nowrap" style={{ color: "var(--color-ink)" }}>
                    {row[c.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
