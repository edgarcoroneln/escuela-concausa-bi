import { useState } from "react";
import { getAuthLoginUrl } from "../lib/api.js";
import { ENTIDADES_LABEL } from "../components/MapaEntidades.jsx";

// Pantalla 0 -- Login (mockup 00_Login.png, 01_UX_Architecture.md "Mockup 0
// -- Login").
//
// Historial:
// - 12-sep: se agrego esta pantalla completa para "anonimo" (antes App.jsx
//   montaba el shell sin importar la sesion). Primera version: mapa D3 real
//   de Mexico (geojson de los 32 estados, ver components/MapaEntidades.jsx)
//   en vez del "radar de vigilancia" decorativo del mockup, que trae
//   coordenadas y conteos INVENTADOS (GEO_COORD, "Radio de Vigilancia:
//   1,500m", "TOLUCA (5)") -- hallazgo de Diana ese dia, ver DevLog
//   "comparativa-diseno-y-checklist-100.md" S0. Fondo oscuro + copy
//   "llano" (sin la narrativa institucional del mockup).
//
// - 13-sep (auditoria visual contra el mockup, a peticion explicita de
//   Diana -- fidelidad al 99% contra las plantillas, sin mas excepciones
//   que las explicitamente aprobadas): se revierte el fondo oscuro y el
//   copy llano -- ahora fondo claro y copy institucional tal cual
//   00_Login.png (badge, eyebrow, encabezado, parrafo, tarjeta de acceso,
//   tarjetas de entidad, pie), usando los tokens de src/index.css (PR
//   #310) en vez de colores sueltos.
//
// - 13-sep (segunda vuelta, mismo dia): Diana pidio adoptar tambien el
//   LAYOUT del "vector cartografico" del mockup (panel con puntos
//   conectados + coordenadas), pero sin repetir el problema de datos
//   inventados que motivo el cambio del 12-sep. Solucion: los 4 puntos
//   son las coordenadas REALES de la capital de cada una de las 4
//   entidades de alcance (ver lat/lon en ENTIDADES_LABEL,
//   components/MapaEntidades.jsx) -- nunca escuelas ni CCTs de muestra
//   (el mockup usa "CCT-09"/"CCT-15"/etc., que ni siquiera son CCTs
//   reales -- son los cveEnt disfrazados de CCT). Con esto el panel ya
//   puede vivir sobre el mismo fondo claro que el resto de la pantalla
//   (ya no depende de los trazos blancos translucidos de MapaEntidades.jsx,
//   pensados para fondo oscuro) -- ver VectorCoberturaEntidades abajo.
//
// - 13-sep (tercera vuelta, mismo dia): la primera version del vector
//   (posicion por lat/lon real + color por entidad + polyline punto a
//   punto) se veia como una linea en zigzag sin sentido (Nuevo Leon queda
//   muy al norte de las otras 3), sin leyenda y con colores distintos por
//   punto -- feedback de Diana. Se probo un layout RADIAL desde un centro
//   (misma idea que InfograficoArquitecturaSensorial en Home.jsx).
//
// - 13-sep (cuarta vuelta, mismo dia): Diana pidio ir mas literal --
//   replicar la MISMA imagen del mockup (las ondas punteadas decorativas
//   de fondo + la linea solida conectando los 4 puntos en el mismo layout
//   visual del mockup), cambiando unicamente los datos que el mockup
//   muestra en los puntos y el encabezado. Las posiciones de los puntos y
//   las ondas de fondo son fijas/decorativas -- igual que en el mockup, no
//   pretenden ser un mapa proporcional -- pero cada punto ahora muestra el
//   codigo real de su entidad ("ENT-09", el cveEnt de INEGI, en vez del
//   "CCT-09" inventado del mockup) y el encabezado muestra la coordenada
//   real (lat/lon de la capital) de la entidad activa, nunca un valor fijo
//   de ejemplo. La grilla "Entidades federativas en observatorio" tambien
//   se dejo identica al estilo del mockup (mismo color de acento uniforme
//   en la etiqueta "Entidad XX", sin borde de color por entidad).
//
// - 13-sep (quinta vuelta, mismo dia -- auditoria de fidelidad "sin
//   excepciones" pedida por Diana): 4 ajustes.
//   (a) Faltaba el texto de version del pie ("Version institucional
//   2025.1") -- se agrega, junto con el resto del pie, como fila de ancho
//   completo debajo de las dos columnas (asi se ve en 00_Login.png).
//   (b) Tipografia EXACTA contra el spec: hasta ahora se usaban tamanos
//   Tailwind aproximados (text-sm, text-xl, etc.), que NO coinciden pixel
//   a pixel con la escala real del mockup (Design_Tokens_Stitch.md,
//   seccion "typography"). Se agregaron clases .text-headline-xl/-lg,
//   .text-title-md, .text-body-md/-sm, .text-label-ui,
//   .text-label-data-mono/-micro-mono en src/index.css con los valores
//   exactos (tamano/interlineado/tracking/peso) de ese doc, y esta
//   pantalla ya las usa en todos los textos. De paso corrige una mezcla
//   de fuentes que se habia colado: la etiqueta "Vector Cartografico..."
//   y "Entidades federativas..." van en Inter (label-ui), NO en
//   JetBrains Mono -- solo COORD, ENT-XX, ENTIDAD XX y los textos de
//   estado/pie van en mono, igual que en el mockup.
//   (c) Layout ajustable de verdad: se reemplaza el flex de dos columnas
//   de ancho completo (imitaba la proporcion a ojo) por la MISMA
//   estructura de grid del mockup -- contenedor centrado max-w-7xl,
//   grid-cols-1 lg:grid-cols-12 con columna izquierda de 7 y derecha de
//   5 (exactamente la proporcion del mockup, ya no ~50/50) -- para que
//   la pantalla se reacomode igual en cualquier ancho de ventana, no solo
//   en el punto de quiebre lg.
//   (d) La tarjeta de acceso y el panel del vector ya NO tienen un
//   max-width fijo en rem inventado -- ahora ocupan el 100% de su columna
//   del grid (igual que en el mockup), por eso se ven "mas grandes" en
//   pantallas anchas.
//   OJO -- el HTML fuente del mockup (00_Login.html) trae textos
//   ligeramente distintos a los de 00_Login.png en 2 lugares (pie de
//   pagina y la linea de "Estado del nodo") -- parece una iteracion de
//   copy posterior a la captura de pantalla. Se siguio SIEMPRE el PNG
//   (la imagen que Diana ha estado comparando a simple vista) para el
//   contenido/copy, y el HTML solo para los valores tecnicos de
//   tipografia y proporcion de columnas que no se pueden leer a ojo en
//   una captura.
//
// Contenido contra el spec: "un unico boton de acceso con Google, sin
// campos de usuario o contrasena". Estados: "en reposo" (por defecto) y
// "redirigiendo a Google" (tras el clic). NO hay estado de "credenciales
// invalidas" -- nota explicita del spec (hallazgo de Marina,
// `src/api/v1/auth.py`): un fallo de OAuth no vuelve por esta pantalla, el
// backend lo resuelve en el callback. `lib/session.jsx` ya trata un canje
// fallido igual que "nunca se intento" -- no se inventa un estado de error
// que el backend no expone (por eso tampoco se implementa el selector de
// "Simulador OAuth: Reposo / Redirigiendo / Error" del mockup -- es un
// control del prototipo de diseno para previsualizar estados, no un
// elemento real de la interfaz).
export default function Login() {
  const [redirigiendo, setRedirigiendo] = useState(false);
  const [entidadSeleccionada, setEntidadSeleccionada] = useState(null);

  function iniciarSesion(e) {
    e.preventDefault();
    setRedirigiendo(true);
    window.location.assign(getAuthLoginUrl());
  }

  function alternarEntidad(id) {
    setEntidadSeleccionada((actual) => (actual === id ? null : id));
  }

  return (
    <div
      className="min-h-screen w-full flex items-center justify-center p-4 sm:p-6 lg:p-8"
      style={{ background: "var(--faro-canvas-subtle)" }}
    >
      <div className="flex flex-col w-full max-w-7xl mx-auto py-6 sm:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-stretch">
          {/* Columna izquierda -- narrativa institucional + vector de cobertura (mockup 00_Login.png), 7/12 igual que la plantilla */}
          <div className="lg:col-span-7 flex flex-col justify-between gap-8">
            <div className="flex flex-col gap-6">
              <span
                className="text-label-micro-mono uppercase inline-flex items-center gap-2 self-start px-3 py-1.5 rounded-full"
                style={{ background: "var(--faro-canvas-container)", color: "var(--faro-signal)" }}
              >
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
                Sistema Nacional de Observación Socioescolar
              </span>

              <div className="flex flex-col gap-3">
                <span className="text-label-data-mono uppercase block" style={{ color: "var(--faro-signal)" }}>
                  La escuela como sensor social
                </span>
                <h1 className="text-headline-xl" style={{ color: "var(--faro-command-base)" }}>
                  Plataforma de análisis y correlación de riesgo escolar.
                </h1>
                <p className="text-body-md max-w-2xl" style={{ color: "var(--color-ink-soft)" }}>
                  Plataforma analítica para la detección temprana de anomalías en comunidades escolares a
                  partir de indicadores socioespaciales, climáticos e institucionales en cuatro entidades
                  federativas: Ciudad de México, Estado de México, Nuevo León y Jalisco.
                </p>
              </div>

              <VectorCoberturaEntidades seleccionada={entidadSeleccionada} onSeleccionar={alternarEntidad} />

              <div className="flex flex-col gap-3">
                <p className="text-label-ui uppercase" style={{ color: "var(--color-ink-faint)" }}>
                  Entidades federativas en observatorio
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {ENTIDADES_LABEL.map((e) => {
                    const activa = entidadSeleccionada === e.id;
                    return (
                      <button
                        key={e.id}
                        type="button"
                        onClick={() => alternarEntidad(e.id)}
                        aria-pressed={activa}
                        className="text-left rounded-lg px-3 py-2.5 transition flex flex-col gap-1"
                        style={{
                          background: "var(--faro-canvas)",
                          border: `1px solid ${activa ? "var(--faro-signal)" : "var(--faro-hairline)"}`,
                        }}
                      >
                        <span className="text-label-micro-mono uppercase" style={{ color: "var(--faro-signal)" }}>
                          Entidad {e.cveEnt}
                        </span>
                        <span className="text-title-md" style={{ color: "var(--faro-command-base)" }}>
                          {e.nombre}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Columna derecha -- tarjeta de acceso institucional (mockup 00_Login.png), 5/12 igual que la plantilla, ocupa toda la columna */}
          <div className="lg:col-span-5 flex flex-col justify-center">
            <div
              className="w-full flex flex-col gap-5 p-6 sm:p-8 rounded-2xl"
              style={{
                background: "var(--faro-canvas)",
                border: "1px solid var(--faro-hairline)",
                boxShadow: "var(--faro-shadow-hover)",
              }}
            >
              <span
                className="text-label-micro-mono uppercase inline-flex items-center gap-2"
                style={{ color: "var(--faro-signal)" }}
              >
                <ShieldIcon />
                Credencialización central
              </span>

              <div className="flex flex-col gap-2">
                <h2 className="text-headline-lg" style={{ color: "var(--faro-command-base)" }}>
                  Punto de acceso institucional
                </h2>
                <p className="text-body-sm" style={{ color: "var(--color-ink-soft)" }}>
                  Acceso reservado a analistas, supervisores y formuladores de política pública
                  acreditados.
                </p>
              </div>

              <button
                type="button"
                onClick={iniciarSesion}
                disabled={redirigiendo}
                className="text-title-md inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-full w-full transition"
                style={{
                  background: "var(--faro-canvas-container)",
                  border: "1px solid var(--faro-hairline)",
                  color: "var(--faro-command-base)",
                  opacity: redirigiendo ? 0.7 : 1,
                }}
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

              <p className="text-label-micro-mono uppercase inline-flex items-center gap-2" style={{ color: "var(--color-ink-faint)" }}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
                Servicio autorizado de federación de identidades
              </p>

              <p className="text-label-micro-mono pt-3" style={{ color: "var(--color-ink-faint)", borderTop: "1px solid var(--faro-hairline)" }}>
                Plataforma de uso institucional sujeta a registro y auditoría de accesos.
              </p>
            </div>
          </div>
        </div>

        {/* Pie de pagina -- ancho completo, debajo de las dos columnas (00_Login.png) */}
        <div
          className="hidden sm:flex items-center justify-between text-label-micro-mono uppercase mt-10 pt-6"
          style={{ color: "var(--color-ink-faint)", borderTop: "1px solid var(--faro-hairline)" }}
        >
          <span>FARO // Observatorio de vigilancia socioespacial</span>
          <span>Versión institucional 2025.1</span>
        </div>
      </div>
    </div>
  );
}

// Panel "vector cartografico": replica el mismo diseño visual del mockup
// 00_Login.png (ondas punteadas decorativas de fondo + una linea solida
// conectando los 4 puntos en el mismo layout de la plantilla, un solo
// color de acento). Las posiciones de los puntos y las ondas de fondo son
// fijas/decorativas -- igual que en el mockup, no pretenden ser un mapa
// proporcional (para eso esta el mapa D3 real, reutilizado en otras
// pantallas). Lo unico que cambia frente al mockup son los DATOS: cada
// punto muestra el codigo real de su entidad ("ENT-09", el cveEnt de
// INEGI -- ver ENTIDADES_LABEL en components/MapaEntidades.jsx) en vez del
// "CCT-09" inventado del mockup (que ni siquiera es un CCT real), y el
// encabezado muestra la coordenada real (lat/lon de la capital) de la
// entidad activa, nunca el valor fijo de ejemplo de la plantilla. El SVG
// escala con viewBox + w-full h-auto, asi que el panel se ajusta solo al
// ancho de su columna en cualquier tamano de pantalla.
const VECTOR_POSICIONES = {
  "MX-CMX": { x: 103, y: 76 },
  "MX-MEX": { x: 171, y: 60 },
  "MX-JAL": { x: 237, y: 78 },
  "MX-NLE": { x: 294, y: 66 },
};

function VectorCoberturaEntidades({ seleccionada, onSeleccionar }) {
  const [hovered, setHovered] = useState(null);
  const activa = hovered ?? seleccionada;

  const puntos = ENTIDADES_LABEL.map((e) => ({ ...e, ...VECTOR_POSICIONES[e.id] }));
  // Conecta los puntos de izquierda a derecha, igual que en el mockup.
  const linea = [...puntos].sort((a, b) => a.x - b.x).map((p) => `${p.x},${p.y}`).join(" ");

  const entidadActiva = puntos.find((p) => p.id === activa);

  return (
    <div
      className="rounded-2xl p-5 md:p-6 flex flex-col gap-4"
      style={{ background: "var(--faro-canvas-container)", border: "1px solid var(--faro-hairline)" }}
    >
      <div className="w-full flex items-center justify-between">
        <span className="text-label-ui uppercase" style={{ color: "var(--color-ink-faint)" }}>
          Vector cartográfico de cobertura activa
        </span>
        <span className="text-label-micro-mono" style={{ color: "var(--faro-signal)" }}>
          {entidadActiva
            ? `Coord: ${entidadActiva.lat.toFixed(4)}° N, ${Math.abs(entidadActiva.lon).toFixed(4)}° O`
            : "4 entidades"}
        </span>
      </div>

      <svg viewBox="0 0 340 140" role="img" aria-label="Vector de cobertura con las 4 entidades del alcance de FARO" className="w-full h-auto">
        {/* Ondas decorativas de fondo, igual que en el mockup -- sin dato alguno. */}
        <path
          d="M -10 100 C 40 60 80 60 120 92 C 160 122 190 40 230 42 C 270 44 288 96 312 128"
          fill="none"
          stroke="var(--faro-hairline-hover)"
          strokeWidth="1"
          strokeDasharray="1.5 4"
          opacity="0.6"
        />
        <path
          d="M -10 58 C 30 96 68 112 108 72 C 148 32 188 108 228 128 C 258 142 300 98 350 62"
          fill="none"
          stroke="var(--faro-hairline-hover)"
          strokeWidth="1"
          strokeDasharray="1.5 4"
          opacity="0.6"
        />

        <polyline points={linea} fill="none" stroke="var(--faro-signal)" strokeWidth="1.5" />

        {puntos.map((p) => {
          const esActiva = activa === p.id;
          return (
            <g
              key={p.id}
              style={{ cursor: "pointer" }}
              onMouseEnter={() => setHovered(p.id)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => onSeleccionar(p.id)}
            >
              <circle cx={p.x} cy={p.y} r={esActiva ? 7 : 5} fill="var(--faro-signal)" opacity={esActiva ? 1 : 0.85} />
              {esActiva && (
                <circle cx={p.x} cy={p.y} r={10} fill="none" stroke="var(--faro-signal)" strokeWidth="1.5" opacity={0.5} />
              )}
              <text
                x={p.x}
                y={p.y - 12}
                textAnchor="middle"
                className="font-mono-dato"
                style={{ fontSize: "9px", fill: "var(--faro-command-base)", fontWeight: esActiva ? 700 : 500 }}
              >
                ENT-{p.cveEnt}
              </text>
            </g>
          );
        })}
      </svg>

      <p className="text-label-micro-mono uppercase text-center" style={{ color: "var(--color-ink-faint)" }}>
        <span aria-hidden="true">◎</span> Estado del nodo: telemetría y observación territorial sincronizada
      </p>
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

// Icono de escudo -- credencialización/seguridad institucional (mockup
// 00_Login.png, tarjeta "Credencialización central"). Glifo generico, sin
// marca de terceros.
function ShieldIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
      <path
        d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}
