import { NavLink } from "react-router-dom";

const items = [
  { to: "/", label: "Inicio", end: true },
  { to: "/casos", label: "Casos" },
  { to: "/vista-general", label: "Vista general" },
  { to: "/mapa", label: "Mapa" },
  { to: "/drivers", label: "Drivers" },
  { to: "/hallazgos", label: "Acerca de" },
];

export default function Topbar() {
  return (
    <header
      className="sticky top-0 z-10 flex items-center justify-between px-6"
      style={{ background: "var(--color-header)", height: 60 }}
    >
      <div className="flex items-center gap-8">
        <span className="text-lg font-extrabold tracking-tight" style={{ color: "#ffffff" }}>
          FARO
        </span>
        <nav className="flex items-center gap-5">
          {items.map((it) => (
            <NavLink
              key={it.to}
              to={it.to}
              end={it.end}
              className="text-sm"
              style={({ isActive }) => ({
                color: isActive ? "#ffffff" : "var(--color-header-text-soft)",
                fontWeight: isActive ? 600 : 500,
              })}
            >
              {it.label}
            </NavLink>
          ))}
        </nav>
      </div>
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold"
        style={{ background: "var(--color-primary)", color: "#fff" }}
      >
        DA
      </div>
    </header>
  );
}
