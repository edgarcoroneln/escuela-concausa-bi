import { NavLink } from "react-router-dom";
import { FASES, REFERENCIA_TECNICA } from "../lib/navFases.js";
import { IconPerson } from "./Icons.jsx";

// Barra lateral persistente (Fase 2 del rediseño, US-641) -- reemplaza el
// nav plano de Topbar.jsx por la navegacion de rail izquierdo que traen las
// 7 plantillas de UX/UI (vault/04_UX_Design/FARO_Storytelling_UX/mockups/
// 0[0-6]_*.html): la misma estructura de <aside> aparece identica en las 6
// pantallas autenticadas (01-06) y ausente en 00_Login.html, asi que es
// chrome persistente del producto, no navegacion libre entre pantallas de
// un prototipo -- confirmado comparando el HTML de las 6 plantillas.
//
// Colapso en movil (12-sep, pendiente documentado en el DevLog de la Fase 2 shell/Pantalla 1):
// bajo el breakpoint Mobile de Design_Tokens_Stitch.md (< 768px, coincide con el `md` de Tailwind),
// el rail se angosta a --faro-sidebar-collapsed (via --faro-sidebar-width en index.css, que
// Header.jsx y App.jsx tambien leen para quedar sincronizados) y las etiquetas de texto se ocultan
// -- se queda solo el numero/icono de cada item, como un rail de iconos convencional. Ningun
// mockup describe una navegacion movil distinta (los 7 HTML de Stitch son solo desktop), asi que
// esta es la interpretacion mas conservadora del token ya existente, no una pantalla nueva.
//
// 13-sep -- pase de fidelidad "P1 Entrada" con Diana (mockups/01_Entrada.html), 2 rondas:
//
// Ronda 1 -- "falta el texto que esta debajo de alerta temprana de abandono" / "falta el
// texto que esta a la izquierda debajo de el menu": se agrego el chip "SISTEMA SENSOR
// SOCIAL" debajo de la tagline, y se reconstruyo el pie del rail con la etiqueta
// "ROLES & ALCANCE" + el chip recuadrado "4 Entidades (09, 15, 19, 14)" (codigos INEGI
// reales de CDMX/Edomex/NL/Jalisco, ya usados en todo el proyecto -- no son datos
// inventados; "Analista de Políticas" / "Coordinación Federal" son, igual que en el
// mockup, descripciones fijas del alcance institucional -- ver ROL_LABEL/ALCANCE_LABEL).
//
// Ronda 2 -- 3 pedidos puntuales de Diana sobre este mismo menu:
//   1) "ordenas y nombre cada apartado de la manera que esta en la plantilla original y
//      los nombres" -> se fusionaron FASES + EXPLORACION (2 listas con 2 etiquetas
//      distintas) en una sola lista FASES bajo una sola etiqueta "Flujo de Investigación",
//      exactamente como en el mockup, y se corrigieron los 4 nombres que no coincidian
//      1:1 (ver el historial largo en lib/navFases.js). Se agrego ademas la seccion
//      "Referencia Técnica" (items "US" Cómo funciona FARO / "ID" Guía de Identidad) que
//      faltaba por completo -- quedan con disabledHint porque ninguna de las 2 tiene ruta
//      real todavia (Cómo funciona FARO es la superficie US-601 del Equipo 1, construida
//      pero no mergeada a main; Guía de Identidad no tiene avance conocido en el repo).
//      El item "00 Iniciar Sesión" del mockup se omite a proposito -- Login vive fuera del
//      shell autenticado en la app real, no tendria sentido como item de nav aqui dentro.
//   2) "el efecto de que cuando se seleccione el apartado se haga un poco mas grande" ->
//      NavItem ahora aplica un scale(1.04) con transition al item activo (ver itemStyle).
//   3) "pon en la misma tipografica de FARO como todas las demas" -> el wordmark "FARO"
//      del rail usaba un CSS var que no existe (--font-display, con guion simple; el token
//      real es --faro-font-display) y por eso nunca tomaba la tipografia de Login/Header.
//      Se corrige a la clase .text-headline-sm (misma familia -- Space Grotesk -- que usa
//      el resto del proyecto para titulos, definida en index.css). De paso se agrega el
//      texto "INTELLIGENCE // VIGILANCIA TERRITORIAL" que trae el mockup debajo del
//      wordmark, como una linea adicional (no reemplaza "Alerta temprana de abandono
//      escolar", que es copy propio del proyecto ya aprobado antes con Diana).
function itemStyle(isActive) {
  return {
    background: isActive ? "var(--faro-command-base)" : "transparent",
    color: isActive ? "#ffffff" : "var(--color-ink)",
    borderLeft: isActive ? "2px solid var(--faro-signal-soft)" : "2px solid transparent",
    transform: isActive ? "scale(1.04)" : "scale(1)",
    transformOrigin: "left center",
  };
}

function itemClasses(isActive) {
  return `flex items-center justify-center md:justify-start gap-2.5 px-3 py-2 rounded-lg text-sm transition-all duration-150 ${isActive ? "font-semibold" : "font-medium"}`;
}

// 13-sep -- Marina pidio quitar los numeros ("01", "02"...) del menu
// izquierdo y dejar solo el titulo de cada apartado. El numero se oculta
// en la vista normal (md y mas ancho, que es la que Marina esta viendo);
// se conserva SOLO por debajo del breakpoint md, donde el rail se angosta
// a --faro-sidebar-collapsed y el titulo se oculta (ver comentario de
// "Colapso en movil" arriba) -- sin el numero ahi, cada item quedaria en
// blanco en ese modo angosto, asi que no se elimina del todo, solo deja de
// mostrarse junto al titulo en la vista normal que se pidio limpiar.
function NavItem({ n, label, to, end, disabledHint }) {
  if (disabledHint) {
    return (
      <div
        className="flex items-center justify-center md:justify-start gap-2.5 px-3 py-2 rounded-lg text-sm font-medium cursor-not-allowed"
        style={{ color: "var(--faro-context-gray)" }}
        title={disabledHint}
      >
        {n && (
          <span className="font-mono-dato text-[11px] md:hidden" style={{ color: "var(--faro-context-gray)" }}>
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
      style={({ isActive }) => itemStyle(isActive)}
    >
      {n && (
        <span
          className="font-mono-dato text-[11px] md:hidden"
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

// Rol legible -- los 2 valores reales de RBAC (US-403, src/api/schemas.py::Rol).
// Nunca se inventa un tercer rol ni un "alcance" por usuario: SCOPE_ENTIDADES
// (PRD.md) es fijo para todo el sistema, no varía por analista. "Coordinación
// Federal" (footer) describe ese alcance fijo, igual para cualquier analista.
const ROL_LABEL = { analista: "Analista de Políticas", ciudadano: "Ciudadano" };
const ALCANCE_LABEL = { analista: "Coordinación Federal", ciudadano: "Consulta pública" };

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
            <span className="text-headline-sm hidden md:inline" style={{ color: "var(--color-ink)" }}>
              FARO
            </span>
          </div>
          <p
            className="font-mono-dato text-[10px] uppercase font-semibold tracking-wider mt-1 hidden md:block"
            style={{ color: "var(--faro-signal)" }}
          >
            Alerta temprana de abandono escolar
          </p>
          <p
            className="text-label-micro-mono uppercase mt-0.5 hidden md:block"
            style={{ color: "var(--faro-signal)" }}
          >
            Intelligence // Vigilancia Territorial
          </p>
          <div
            className="mt-1.5 hidden md:inline-flex items-center gap-1 px-1.5 py-0.5 rounded"
            style={{ background: "var(--faro-canvas-container)", border: "1px solid var(--faro-hairline)" }}
          >
            <span className="text-label-micro-mono" style={{ color: "var(--faro-context-gray)" }}>
              SISTEMA SENSOR SOCIAL
            </span>
          </div>
        </div>

        <SectionLabel>Flujo de Investigación</SectionLabel>
        <nav className="flex flex-col gap-0.5 px-2">
          {FASES.map((f) => (
            <NavItem key={f.n} {...f} />
          ))}
        </nav>

        <div className="my-3 mx-3 hidden md:block" style={{ borderTop: "1px solid var(--faro-hairline)" }} aria-hidden="true" />

        <SectionLabel>Referencia Técnica</SectionLabel>
        <nav className="flex flex-col gap-0.5 px-2 mb-2">
          {REFERENCIA_TECNICA.map((f) => (
            <NavItem key={f.n} {...f} />
          ))}
        </nav>
      </div>

      <div className="p-3" style={{ borderTop: "1px solid var(--faro-hairline)", background: "var(--color-surface-alt)" }}>
        {status === "loading" && (
          <div className="h-14" aria-hidden="true" />
        )}
        {status === "autenticado" && user && (
          <div className="flex flex-col gap-1.5">
            <div className="hidden md:flex items-center justify-between">
              <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--faro-context-gray)" }}>
                Roles &amp; alcance
              </span>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
            </div>

            <div className="flex items-center justify-center md:justify-start gap-2.5">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
                style={{ background: "var(--color-primary)", color: "#fff" }}
                title={user?.name || user?.email}
              >
                <IconPerson size={16} />
              </div>
              <div className="min-w-0 hidden md:block">
                <p className="text-label-ui font-semibold truncate" style={{ color: "var(--color-ink)" }}>
                  {ROL_LABEL[user?.role] || user?.role}
                </p>
                <p className="text-label-micro-mono truncate" style={{ color: "var(--faro-context-gray)" }}>
                  {ALCANCE_LABEL[user?.role] || user?.name || user?.email}
                </p>
              </div>
            </div>

            <div
              className="hidden md:flex items-center justify-between mt-0.5 px-1.5 py-0.5 rounded"
              style={{ background: "var(--faro-canvas)", border: "1px solid var(--faro-hairline)" }}
            >
              <span className="text-label-micro-mono font-medium" style={{ color: "var(--faro-signal)" }}>4 Entidades</span>
              <span className="text-label-micro-mono" style={{ color: "var(--faro-context-gray)" }}>(09, 15, 19, 14)</span>
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
