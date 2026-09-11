export default function PageHeader({ kicker, title, subtitle }) {
  return (
    <header className="mb-1">
      {kicker && <p className="kicker mb-2">{kicker}</p>}
      <h1 className="text-3xl" style={{ color: "var(--color-ink)", fontWeight: 600 }}>
        {title}
      </h1>
      {subtitle && (
        <p className="text-sm mt-1.5" style={{ color: "var(--color-ink-faint)" }}>
          {subtitle}
        </p>
      )}
    </header>
  );
}
