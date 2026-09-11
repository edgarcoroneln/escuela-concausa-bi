export default function KpiCard({ label, value, hint, tone = "default" }) {
  const toneStyles = {
    default: { color: "var(--color-primary)" },
    accent: { color: "var(--color-accent)" },
    alert: { color: "var(--color-alert)" },
  };

  return (
    <div
      className="flex flex-col gap-2 p-5 rounded-2xl"
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        boxShadow: "var(--shadow-card)",
      }}
    >
      <span
        className="text-xs font-medium uppercase tracking-wide"
        style={{ color: "var(--color-ink-faint)" }}
      >
        {label}
      </span>
      <span
        className="text-3xl font-semibold tabular-nums"
        style={toneStyles[tone] ?? toneStyles.default}
      >
        {value}
      </span>
      {hint && (
        <span className="text-xs" style={{ color: "var(--color-ink-soft)" }}>
          {hint}
        </span>
      )}
    </div>
  );
}
