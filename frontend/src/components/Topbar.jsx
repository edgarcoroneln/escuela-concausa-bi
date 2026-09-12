import { NavLink } from "react-router-dom";
import { getAuthLoginUrl } from "../lib/api.js";
import { useSession } from "../lib/session.jsx";

const items = [
  { to: "/", label: "Inicio", end: true },
  { to: "/casos", label: "Casos" },
  { to: "/vista-general", label: "Vista general" },
  { to: "/mapa", label: "Mapa" },
  { to: "/drivers", label: "Drivers" },
  { to: "/hallazgos", label: "Acerca de" },
];

// Iniciales para el avatar de sesión -- cae a las dos primeras letras del
// correo si `name` viene vacío (Google no siempre lo expone, ver UserOut
// en src/api/schemas.py, acordado con C2 en US-405).
function inicialesDe(nombre, email) {
  const base = (nombre || email || "").trim();
  if (!base) return "?";
  const partes = base.split(/\s+/).filter(Boolean);
  if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase();
  return (partes[0][0] + partes[1][0]).toUpperCase();
}

export default function Topbar() {
  const { status, user, logout } = useSession();

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

      {status === "loading" ? (
        <div className="w-8 h-8" aria-hidden="true" />
      ) : status === "autenticado" ? (
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={logout}
            className="text-sm"
            style={{ color: "var(--color-header-text-soft)", fontWeight: 500 }}
          >
            Cerrar sesión
          </button>
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold"
            style={{ background: "var(--color-primary)", color: "#fff" }}
            title={user?.name || user?.email}
          >
            {inicialesDe(user?.name, user?.email)}
          </div>
        </div>
      ) : (
        <a
          href={getAuthLoginUrl()}
          className="text-sm font-semibold px-3 py-1.5 rounded-md"
          style={{ background: "var(--color-primary)", color: "#ffffff" }}
        >
          Iniciar sesión
        </a>
      )}
    </header>
  );
}
