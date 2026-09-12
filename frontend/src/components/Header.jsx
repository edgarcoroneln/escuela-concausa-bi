import { useLocation } from "react-router-dom";
import { getAuthLoginUrl } from "../lib/api.js";
import { tituloDeRuta } from "../lib/navFases.js";

// Cabecera fija junto a la barra lateral (Fase 2, US-641) -- antes era
// Topbar.jsx (nav plana a todo lo ancho); ahora la navegacion vive en
// Sidebar.jsx y esta cabecera solo da ubicacion (breadcrumb) y sesion,
// igual que el <header> de las plantillas de UX/UI.
function inicialesDe(nombre, email) {
  const base = (nombre || email || "").trim();
  if (!base) return "?";
  const partes = base.split(/\s+/).filter(Boolean);
  if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase();
  return (partes[0][0] + partes[1][0]).toUpperCase();
}

export default function Header({ session }) {
  const { status, user, logout } = session;
  const location = useLocation();
  const pantalla = tituloDeRuta(location.pathname);

  return (
    <header
      className="fixed top-0 right-0 h-16 z-30 flex items-center justify-between px-6"
      style={{
        left: "var(--faro-sidebar-width)",
        background: "var(--faro-canvas)",
        borderBottom: "1px solid var(--faro-hairline)",
      }}
    >
      <div className="flex items-center gap-2 font-mono-dato text-xs">
        <span className="font-semibold" style={{ color: "var(--color-ink)" }}>FARO</span>
        {pantalla && (
          <>
            <span style={{ color: "var(--faro-context-gray)" }}>/</span>
            <span style={{ color: "var(--faro-signal)" }}>{pantalla}</span>
          </>
        )}
      </div>

      {status === "loading" ? (
        <div className="w-8 h-8" aria-hidden="true" />
      ) : status === "autenticado" ? (
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={logout}
            className="text-sm"
            style={{ color: "var(--faro-context-gray)", fontWeight: 500 }}
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
