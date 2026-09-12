import * as d3 from "d3";
import { useEffect, useRef, useState } from "react";
import { getAuthLoginUrl } from "../lib/api.js";
import mexicoStates from "../data/geo/mexico-states.json";

// Pantalla 0 -- Login (mockup 00_Login.html, 01_UX_Architecture.md "Mockup 0
// -- Login"). Nueva 12-sep (auditoría mockups vs código, a pedido de Diana):
// hasta hoy esta SPA no tenía una pantalla de login propia -- App.jsx
// montaba el shell completo (Sidebar/Header) sin importar la sesión, y cada
// pantalla fallaba por su cuenta con "sin sesión iniciada". Ver App.jsx:
// ahora el layout raíz muestra esta pantalla completa mientras
// session.status === "anonimo" (o directo en /login, ver main.jsx, para
// verla sin apagar el modo demo).
//
// CORRECCIÓN 12-sep (segunda vuelta, a pedido explícito de Diana): panel
// dividido con un mapa de México real (mismo geojson y d3-geo que
// MapaRiesgo.jsx) resaltando las 4 entidades del alcance -- para acercar
// el LAYOUT al mockup sin adoptar su copy institucional ("Sistema Nacional
// de Observación Socioescolar", "La Escuela como Sensor Social"): Diana
// confirmó mantener el tono llano ya usado en el resto de la app (mismo
// criterio que P1, P2 y P6, donde esa narrativa ya se dejó fuera por no
// estar en el spec aprobado). El mapa es de verdad (geojson real de los 32
// estados), no un gráfico decorativo inventado.
//
// Contenido contra el spec: "un único botón de acceso con Google, sin
// campos de usuario o contraseña... el diseño debe aprovechar ese espacio
// para identidad y narrativa, no para un formulario que no existe."
//
// Estados: "en reposo" (por defecto) y "redirigiendo a Google" (tras el
// clic). NO hay estado de "credenciales inválidas" -- nota explícita del
// spec (hallazgo de Marina, `src/api/v1/auth.py`): un fallo de OAuth no
// vuelve por esta pantalla, el backend lo resuelve en el callback.
// `lib/session.jsx` ya trata un canje fallido igual que "nunca se
// intentó" -- no se inventa un estado de error que el backend no expone.
const ENTIDADES_ALCANCE = ["MX-CMX", "MX-MEX", "MX-NLE", "MX-JAL"];
const ENTIDADES_LABEL = [
  { id: "MX-CMX", nombre: "CDMX" },
  { id: "MX-MEX", nombre: "Edomex" },
  { id: "MX-NLE", nombre: "Nuevo León" },
  { id: "MX-JAL", nombre: "Jalisco" },
];

// Mapa decorativo con geografía real (mismo geojson/d3-geo que
// components/MapaRiesgo.jsx) -- a diferencia de ese componente, aquí no hay
// escuelas que ubicar ni interacción: solo resalta las 4 entidades del
// alcance de FARO sobre el resto del país, para dar identidad visual sin
// inventar un dato que no existe.
function MapaEntidadesLogin() {
  const svgRef = useRef(null);
  const size = 420;

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("viewBox", `0 0 ${size} ${size}`);

    const projection = d3.geoMercator().fitSize([size, size], mexicoStates);
    const path = d3.geoPath(projection);

    svg
      .append("g")
      .selectAll("path")
      .data(mexicoStates.features)
      .join("path")
      .attr("d", path)
      .attr("fill", (d) =>
        ENTIDADES_ALCANCE.includes(d.properties.id) ? "var(--faro-signal-soft)" : "rgba(255,255,255,0.05)"
      )
      .attr("stroke", "rgba(255,255,255,0.18)")
      .attr("stroke-width", 0.6);
  }, []);

  return (
    <svg
      ref={svgRef}
      role="img"
      aria-label="Mapa de México con Ciudad de México, Estado de México, Nuevo León y Jalisco resaltados"
      style={{ width: "100%", height: "auto", maxWidth: "22rem" }}
    />
  );
}

export default function Login() {
  const [redirigiendo, setRedirigiendo] = useState(false);

  function iniciarSesion(e) {
    e.preventDefault();
    setRedirigiendo(true);
    window.location.assign(getAuthLoginUrl());
  }

  return (
    <div
      className="min-h-screen flex flex-col md:flex-row"
      style={{ background: "linear-gradient(135deg, #0b1524 0%, #16283f 100%)" }}
    >
      <div className="flex-1 flex items-center justify-center p-6 md:p-12">
        <div className="w-full flex flex-col gap-6 text-center md:text-left items-center md:items-start" style={{ maxWidth: "26rem" }}>
          <div>
            <span
              className="font-mono-dato text-[11px] uppercase font-semibold tracking-wider"
              style={{ color: "var(--faro-signal-soft)" }}
            >
              FARO
            </span>
            <h1 className="text-3xl leading-tight mt-3" style={{ color: "#ffffff", fontWeight: 700 }}>
              Investigar el riesgo de abandono escolar
            </h1>
            <p className="text-sm mt-4 leading-relaxed" style={{ color: "#b7c0d1" }}>
              FARO analiza 6 líneas de evidencia por escuela en 4 entidades del país para señalar
              dónde intervenir antes de que la matrícula se pierda.
            </p>
          </div>

          <div
            className="w-full rounded-2xl p-5 flex flex-col gap-4"
            style={{ border: "1px solid rgba(255,255,255,0.14)", background: "rgba(255,255,255,0.03)" }}
          >
            <span
              className="font-mono-dato text-[10px] uppercase font-semibold tracking-wider"
              style={{ color: "var(--faro-signal-soft)" }}
            >
              Acceso del equipo FARO
            </span>
            <button
              type="button"
              onClick={iniciarSesion}
              disabled={redirigiendo}
              className="inline-flex items-center justify-center gap-2.5 text-sm font-semibold px-6 py-3.5 rounded-full w-full"
              style={{ background: "#ffffff", color: "#0b1524", opacity: redirigiendo ? 0.7 : 1 }}
            >
              {redirigiendo ? (
                "Conectando con Google…"
              ) : (
                <>
                  <GoogleIcon />
                  Iniciar sesión con Google
                </>
              )}
            </button>
            <p className="text-xs" style={{ color: "#6b7a94" }}>
              Al continuar, Google comparte tu nombre y correo con FARO para verificar tu acceso.
            </p>
          </div>

          <p className="text-xs" style={{ color: "#5b677e" }}>
            Plataforma de uso interno para el equipo FARO.
          </p>
        </div>
      </div>

      <div
        className="hidden md:flex flex-1 items-center justify-center p-12"
        style={{ borderLeft: "1px solid rgba(255,255,255,0.08)" }}
      >
        <div className="flex flex-col items-center gap-6">
          <MapaEntidadesLogin />
          <div className="flex flex-wrap items-center justify-center gap-2">
            {ENTIDADES_LABEL.map((e) => (
              <span
                key={e.id}
                className="text-xs font-semibold px-3 py-1.5 rounded-full"
                style={{ background: "rgba(255,255,255,0.08)", color: "#ffffff" }}
              >
                {e.nombre}
              </span>
            ))}
          </div>
          <p className="text-xs text-center" style={{ color: "#6b7a94", maxWidth: "18rem" }}>
            FARO cubre escuelas de estas 4 entidades del país.
          </p>
        </div>
      </div>
    </div>
  );
}

// Icono oficial "G" de Google (guía de marca de Google para botones de
// inicio de sesión) -- no un logo inventado ni el de otra plataforma.
function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" focusable="false">
      <path
        fill="#4285F4"
        d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.71v2.26h2.92c1.71-1.57 2.68-3.88 2.68-6.61z"
      />
      <path
        fill="#34A853"
        d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.81.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 0 0 9 18z"
      />
      <path
        fill="#FBBC05"
        d="M3.97 10.72A5.4 5.4 0 0 1 3.68 9c0-.6.1-1.18.28-1.72V4.95H.96A9 9 0 0 0 0 9c0 1.45.35 2.83.96 4.05l3.01-2.33z"
      />
      <path
        fill="#EA4335"
        d="M9 3.58c1.32 0 2.51.45 3.44 1.35l2.59-2.59C13.46.89 11.43 0 9 0A9 9 0 0 0 .96 4.95l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z"
      />
    </svg>
  );
}
