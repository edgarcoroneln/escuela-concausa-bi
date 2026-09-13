import { NavLink } from "react-router-dom";
import { FASES, EXPLORACION } from "../lib/navFases.js";

// Barra lateral persistente (Fase 2 del rediseño, US-641) -- reemplaza el
// nav plano de Topbar.jsx por la navegacion de rail izquierdo que traen las
// 7 plantillas de UX/UI (vault/04_UX_Design/FARO_Storytelling_UX/mockups/
// 0[0-6]_*.html): la misma estructura de <aside> aparece identica en las 6
// pantallas autenticadas (01-06) y ausente en 00_Login.html, asi que es
// chrome persistente del producto, no navegacion libre entre pantallas de
// un prototipo -- confirmado comparando el HTML de las 6 plantillas.
//
// Mapeo de fases a rutas (US-641, "pantalla por pantalla" con Diana) --
// ver lib/navFases.js para la tabla completa y su justificacion. Las 6
// vistas heredadas de Fase 1 que vivian aqui aparte (vista general, mapa,
// drivers, comparacion territorial, comparativa, hallazgos) se retiraron
// el 12-sep -- decision de arquitectura de Marina Garcia del Buey: la
// version final del producto son estas 7 pantallas, sin una seccion
// secundaria de vistas duplicadas.
//
// Colapso en movil (12-sep, pendiente documentado en el DevLog de la Fase 2 shell/Pantalla 1):
// bajo el breakpoint Mobile de Design_Tokens_Stitch.md (< 768px, coincide con el `md` de Tailwind),
// el rail se angosta a --faro-sidebar-collapsed (via --faro-sidebar-width en index.css, que
// Header.jsx y App.jsx tambien leen para quedar sincronizados) y las etiquetas de texto se ocultan
// -- se queda solo el numero/icono de cada item, como un rail de iconos convencional. Ningun
// mockup describe una navegacion movil distinta (los 7 HTML de Stitch son solo desktop), asi que
// esta es la interpretacion mas conservadora del token ya existente, no una pantalla nueva.
function itemClasses(isActive) {
  return `flex items-center justify-center md:justify-start gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${isActive ? "font-semibold" : "font-medium"}`;
}

function NavItem({ n, label, to, end, disabledHint }) {
  if (disabledHint) {
    return (
      <div
        className="flex items-center justify-center md:justify-start gap-2.5 px-3 py-2 rounded-lg text-sm font-medium cursor-not-allowed"
        style={{ color: "var(--faro-context-gray)" }}
        title={disabledHint}
      >
        {n && (
          <span className="font-mono-dato text-[11px]" style={{ color: "var(--faro-context-gray)" }}>
            {n}
          </span>
        )}
        <span className="flex-1 hidden md:inline">{label}</span>
      </div>
    );
  }
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) => itemClasses(isActive)}
      style={({ isActive }) => ({
        background: isActive ? "var(--faro-command-base)" : "transparent",
        color: isActive ? "#ffffff" : "var(--color-ink)",
        borderLeft: isActive ? "2px solid var(--faro-signal-soft)" : "2px solid transparent",
      })}
    >
      {n && (
        <span
          className="font-mono-dato text-[11px]"
          style={{ color: "inherit", opacity: 0.75 }}
        >
          {n}
        </span>
      )}
      <span className="flex-1 hidden md:inline">{label}</span>
    </NavLink>
  );
}

function SectionLabel({ children }) {
  return (
    <div className="px-3 pt-4 pb-1 hidden md:block">
      <span
        className="font-mono-dato text-[10px] uppercase font-semibold tracking-wider"
        style={{ color: "var(--faro-context-gray)" }}
      >
        {children}
      </span>
    </div>
  );
}

function inicialesDe(nombre, email) {
  const base = (nombre || email || "").trim();
  if (!base) return "?";
  const partes = base.split(/\s+/).filter(Boolean);
  if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase();
  return (partes[0][0] + partes[1][0]).toUpperCase();
}

// Rol legible -- los 2 valores reales de RBAC (US-403, src/api/schemas.py::Rol).
// Nunca se inventa un tercer rol ni un "alcance" por usuario: SCOPE_ENTIDADES
// (PRD.md) es fijo para todo el sistema, no varía por analista.
const ROL_LABEL = { analista: "Analista", ciudadano: "Ciudadano" };

export default function Sidebar({ session }) {
  const { status, user } = session;

  return (
    <aside
      className="fixed left-0 top-0 h-screen z-40 flex flex-col justify-between overflow-y-auto"
      style={{
        width: "var(--faro-sidebar-width)",
        background: "var(--faro-canvas)",
        borderRight: "1px solid var(--faro-hairline)",
      }}
    >
      <div className="flex flex-col">
        <div className="px-4 py-4" style={{ borderBottom: "1px solid var(--faro-hairline)" }}>
          <div className="flex items-center justify-center md:justify-start gap-2">
            <span
              className="w-2 h-2 rounded-full shrink-0"
              style={{ background: "var(--faro-signal)" }}
              aria-hidden="true"
            />
            <span
              className="text-lg tracking-tight hidden md:inline"
              style={{ fontFamily: "var(--font-display)", color: "var(--color-ink)" }}
            >
              FARO
            </span>
          </div>
          <p
            className="font-mono-dato text-[10px] uppercase font-semibold tracking-wider mt-1 hidden md:block"
            style={{ color: "var(--faro-signal)" }}
          >
            Alerta temprana de abandono escolar
          </p>
        </div>

        <SectionLabel>Investigación guiada</SectionLabel>
        <nav className="flex flex-col gap-0.5 px-2">
          {FASES.map((f) => (
            <NavItem key={f.n} {...f} />
          ))}
        </nav>

        <SectionLabel>Exploración libre</SectionLabel>
        <nav className="flex flex-col gap-0.5 px-2 mb-2">
          {EXPLORACION.map((f) => (
            <NavItem key={f.n} {...f} />
          ))}
        </nav>
      </div>

      <div className="p-3" style={{ borderTop: "1px solid var(--faro-hairline)", background: "var(--color-surface-alt)" }}>
        {status === "loading" && (
          <div className="h-10" aria-hidden="true" />
        )}
        {status === "autenticado" && user && (
          <div className="flex items-center justify-center md:justify-start gap-2.5">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold shrink-0"
              style={{ background: "var(--color-primary)", color: "#fff" }}
              title={user?.name || user?.email}
            >
              {inicialesDe(user?.name, user?.email)}
            </div>
            <div className="min-w-0 hidden md:block">
              <p className="text-xs font-semibold truncate" style={{ color: "var(--color-ink)" }}>
                {user?.name || user?.email}
              </p>
              <p className="font-mono-dato text-[10px] truncate" style={{ color: "var(--faro-context-gray)" }}>
                {ROL_LABEL[user?.role] || user?.role} · 4 entidades (CDMX, Edomex, NL, Jalisco)
              </p>
            </div>
          </div>
        )}
        {status === "anonimo" && (
          <p
            className="text-xs text-center md:text-left"
            style={{ color: "var(--faro-context-gray)" }}
            title="Sin sesión iniciada"
          >
            <span className="md:hidden" aria-hidden="true">–</span>
            <span className="hidden md:inline">Sin sesión iniciada</span>
          </p>
        )}
      </div>
    </aside>
  );
}
