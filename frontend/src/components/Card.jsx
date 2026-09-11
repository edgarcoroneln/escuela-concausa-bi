export default function Card({ title, subtitle, children, className = "", hover = false, style = {} }) {
  return (
    <div
      className={`p-5 rounded-2xl ${hover ? "lift" : ""} ${className}`}
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        boxShadow: "var(--shadow-card)",
        borderRadius: "var(--radius-card)",
        ...style,
      }}
    >
      {title && (
        <div className="mb-4">
          <h3 className="text-sm font-semibold" style={{ color: "var(--color-ink)", fontFamily: "var(--font-sans)" }}>
            {title}
          </h3>
          {subtitle && (
            <p className="text-xs mt-0.5" style={{ color: "var(--color-ink-faint)" }}>
              {subtitle}
            </p>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
