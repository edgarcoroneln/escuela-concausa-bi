import { useLocation } from "react-router-dom";
import { getAuthLoginUrl } from "../lib/api.js";
import { IconPerson } from "./Icons.jsx";

// Cabecera fija junto a la barra lateral (Fase 2, US-641) -- antes era
// Topbar.jsx (nav plana a todo lo ancho); ahora la navegacion vive en
// Sidebar.jsx y esta cabecera solo da ubicacion (breadcrumb) y sesion,
// igual que el <header> de las plantillas de UX/UI.
//
// 13-sep -- pase de fidelidad "P1 Entrada" con Diana (revision plantilla por
// plantilla, mockups/01_Entrada.html). Los 4 puntos de su lista que tocan
// este archivo:
//   1) "Fata los textos que esta en la parte de arriba en la barra despues
//      de FARO/" -> el breadcrumb dinamico (tituloDeRuta) se reemplaza por
//      el texto estatico "SURVEILLANCE_NODE" + separador + chip de alcance
//      "Alcance: 4 Entidades - CDMX, Edomex, NL, Jalisco", identicos al
//      HTML del mockup (linea del <header>, clases font-label-data-mono /
//      text-label-micro-mono). El chip de alcance usa las 4 entidades
//      reales del proyecto (PRD.md, SCOPE_ENTIDADES) -- no es dato
//      inventado, es el alcance fijo del sistema completo.
//   2) "Falta el texto de telimetria" -> chip "TELEMETRIA // EN VIVO" con
//      punto pulsante (animate-ping), igual al mockup.
//   3) "Falta el texto del rol, en la esquina superior derecha" -> bloque de
//      2 lineas junto al avatar. IMPORTANTE: el mockup pone ahi textos
//      literales "ANALISTA_04" / "FEDERAL_NODE" que parecen un ID de
//      analista y un codigo de nodo -- ninguno de los dos existe en los
//      datos reales de sesion (session.user solo trae name/email/role), asi
//      que en vez de inventar un ID se usa el dato real: linea 1 = nombre o
//      correo de la sesion, linea 2 = rol real (mismo ROL_LABEL que ya usa
//      Sidebar.jsx). Se preserva el estilo visual (mono, mayusculas,
//      alineado a la derecha) pero no el texto fabricado.
//   4) "Los iconos al 100% iguales que la plantilla" -> el avatar generico
//      pasa de iniciales a el icono "person" de Material Symbols (via
//      Icons.jsx, mismo SVG que consume Home.jsx), igual que el mockup en
//      vez de iniciales.
// Ademas, todo el bloque de alcance/telemetria se oculta en pantallas
// angostas (hidden lg:flex / md:flex) para que la cabecera siga siendo
// legible al minimizar la ventana, sin romper el requisito de que el
// breadcrumb y el avatar sigan siempre visibles.
// Rol legible -- mismos 2 valores de RBAC que Sidebar.jsx (US-403,
// src/api/schemas.py::Rol). "Coordinacion Federal" es el alcance fijo del
// sistema para cualquier analista (PRD.md, SCOPE_ENTIDADES no varia por
// usuario), no un dato personal por sesion.
const ROL_LABEL = { analista: "Analista de Políticas", ciudadano: "Ciudadano" };

export default function Header({ session }) {
  const { status, user, logout } = session;
  useLocation(); // se conserva para futuros breadcrumbs por ruta si se retoman

  return (
    <header
      className="fixed top-0 right-0 h-16 z-30 flex items-center justify-between gap-3 px-4 md:px-6"
      style={{
        left: "var(--faro-sidebar-width)",
        background: "var(--faro-canvas)",
        borderBottom: "1px solid var(--faro-hairline)",
      }}
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className="flex items-center gap-1.5 text-label-data-mono shrink-0">
          <span className="font-semibold" style={{ color: "var(--color-ink)" }}>FARO</span>
          <span style={{ color: "var(--faro-context-gray)" }}>/</span>
          <span className="font-medium" style={{ color: "var(--faro-signal)" }}>SURVEILLANCE_NODE</span>
        </div>

        <div className="hidden md:block w-px h-4" style={{ background: "var(--faro-hairline)" }} aria-hidden="true" />

        <div
          className="hidden md:inline-flex items-center gap-1.5 px-2 py-1 rounded-full"
          style={{ background: "var(--faro-canvas-container)", border: "1px solid var(--faro-hairline)" }}
        >
          <span className="text-label-micro-mono font-medium truncate" style={{ color: "var(--color-ink)" }}>
            Alcance: 4 Entidades · CDMX, Edomex, NL, Jalisco
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3 md:gap-5 shrink-0">
        <div
          className="hidden lg:flex items-center gap-1.5 px-2 py-1 rounded"
          style={{ background: "var(--faro-canvas-container)", border: "1px solid var(--faro-hairline)" }}
        >
          <span className="relative flex w-2 h-2" aria-hidden="true">
            <span
              className="absolute inline-flex h-full w-full rounded-full opacity-60 animate-ping"
              style={{ background: "var(--faro-signal-soft)" }}
            />
            <span className="relative inline-flex rounded-full w-2 h-2" style={{ background: "var(--faro-signal)" }} />
          </span>
          <span className="text-label-micro-mono font-semibold" style={{ color: "var(--faro-signal)" }}>
            TELEMETRÍA // EN VIVO
          </span>
        </div>

        {status === "loading" ? (
          <div className="w-8 h-8" aria-hidden="true" />
        ) : status === "autenticado" ? (
          <div
            className="flex items-center gap-2.5 pl-3"
            style={{ borderLeft: "1px solid var(--faro-hairline)" }}
          >
            <div className="text-right hidden sm:block leading-tight">
              <p className="text-label-ui font-semibold truncate max-w-[10rem]" style={{ color: "var(--color-ink)" }}>
                {user?.name || user?.email}
              </p>
              <p className="text-label-micro-mono truncate max-w-[10rem]" style={{ color: "var(--faro-context-gray)" }}>
                {(ROL_LABEL[user?.role] || user?.role || "").toString().toUpperCase()}
              </p>
            </div>
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
              style={{ background: "var(--color-primary)", color: "var(--faro-canvas)" }}
              title={user?.name || user?.email}
            >
              <IconPerson size={18} />
            </div>
            <button
              type="button"
              onClick={logout}
              className="text-body-sm hidden sm:inline"
              style={{ color: "var(--faro-context-gray)", fontWeight: 500 }}
            >
              Cerrar sesión
            </button>
          </div>
        ) : (
          <a
            href={getAuthLoginUrl()}
            className="text-body-sm font-semibold px-3 py-1.5"
            style={{ background: "var(--color-primary)", color: "var(--faro-canvas)", borderRadius: "var(--faro-radius-DEFAULT)" }}
          >
            Iniciar sesión
          </a>
        )}
      </div>
    </header>
  );
}
