import { useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import GlosarioOverlay from "../components/GlosarioOverlay.jsx";
import { FASES } from "../lib/navFases.js";
import WalkthroughOverlay from "../components/WalkthroughOverlay.jsx";
import { ENTIDADES_LABEL } from "../components/MapaEntidades.jsx";
import {
  IconHelpCenter,
  IconArrowForward,
  IconMenuBook,
  IconHub,
  IconSecurityUpdateGood,
  IconSensors,
  IconMemory,
  IconAssignmentTurnedIn,
  IconLockClock,
} from "../components/Icons.jsx";

// Pantalla 1 -- Entrada (mockup 01_Entrada.png, 01_UX_Architecture.md §2
// "Pantalla 1").
//
// Historial: la primera version (Fase 2, US-641) se escribio contra la
// ficha de 01_UX_Architecture.md y a proposito NO contra la copy de las
// plantillas Stitch, que traen una narrativa de "sensores"/"telemetria"
// que en ese momento no estaba en el spec aprobado. Tenia ademas un hero
// con degradado oscuro hecho a mano (no los tokens de src/index.css) y una
// fila de "features" con emoji que no existe en el mockup.
//
// CORRECCION 13-sep (misma auditoria de Login.jsx, a peticion explicita de
// Diana -- fidelidad al 99% contra las plantillas, texto informativo
// incluido): se adopta la copy institucional del mockup (eyebrow,
// encabezado "La Escuela como Sensor Social", parrafo, tarjeta de
// "Proposito operativo", nota de revelacion escalonada) y el tema claro de
// los tokens (PR #310) en vez del degradado oscuro suelto. Se quita la fila
// de emoji (no esta en el mockup, duplicaba info del parrafo).
//
// CORRECCION 13-sep (segunda vuelta, auditoria "sin excepciones" de P1,
// mismo dia): 6 ajustes.
// (a) Tipografia EXACTA contra Design_Tokens_Stitch.md (mismas clases
// .text-headline-*/.text-body-*/.text-label-* agregadas a index.css para
// Login) -- toda esta pantalla las usa ahora.
// (b) Forma real de los botones: el mockup usa esquinas suaves
// (rounded-lg = 0.5rem) en los botones de accion, NO pildora
// (rounded-full) como tenia esta pantalla, y la insignia "Pantalla 01..."
// va con esquinas totalmente rectas (sin rounded). Corregido con los
// tokens --faro-radius-*.
// (c) Iconos: se agregan los de components/Icons.jsx (copias exactas de
// Material Symbols Outlined auto-hospedadas, ver ese archivo) en vez de
// texto plano o sin icono.
// (d) El infografico "Red de Telemetria Multicapa" se reconstruye 1:1
// contra el layout del mockup (3 capas concentricas + 3 nodos + 3
// marcadores de categoria, con el rotulo "GEO_LAYER_v2.4"), no el diagrama
// radial anterior. Con dos salvedades de integridad de datos: (1) el
// mockup etiqueta uno de los 3 nodos "NODO_JAL_04" -- 04 NO es la clave
// real de Jalisco (es 14, ver ENTIDADES_LABEL/MapaEntidades.jsx) --se
// corrige a JAL_14; (2) el marcador "VULNERABILIDAD" del mockup usa rojo
// de alerta -- se mantiene iguial (es --color-alert, "alerta/error
// generico de UI", NO el semaforo de riesgo rojo/ambar/verde que
// 03_Visual_Identity.md rechaza explicitamente para NIVELES DE RIESGO;
// aqui es una etiqueta de categoria en un diagrama conceptual, no un
// indicador de riesgo por escuela). Las etiquetas de los otros 2 nodos se
// acortan (sin el prefijo "NODO_") para que quepan sin encimarse con el
// nodo central, a peticion explicita de Diana.
// (e) Header.jsx y Sidebar.jsx (chrome de toda pantalla autenticada, no
// solo P1) reciben la misma pasada -- ver comentarios en esos archivos.
//
// Sigue sin revelar "escuelas_en_riesgo" -- el spec es explicito: P1 nunca
// revela el conteo de casos, eso es tarea de P2 (Panorama). Pantalla
// estatica, sin estado de carga ni de error (§2).
const ETAPAS = [
  {
    n: "01",
    fase: "Detección",
    titulo: "Sensórica multipolar",
    texto:
      "Observación integrada de las 6 líneas de evidencia por escuela -- lo que no se pudo observar se marca explícito como SIN_DATO, nunca como cero.",
    tag: "Indicador de flujo // Señal continua",
    Icono: IconSensors,
  },
  {
    n: "02",
    fase: "Síntesis",
    titulo: "Inferencia territorial",
    texto:
      "El modelo combina las 6 líneas de evidencia en un índice de riesgo y un nivel de atención (alta, media o baja) por escuela.",
    tag: "Matriz crítica // Correlación 6 ejes",
    Icono: IconMemory,
  },
  {
    n: "03",
    fase: "Acción",
    titulo: "Dictamen preventivo",
    texto:
      "Cada escuela con predicción trae una recomendación asociada a su driver dominante, para priorizar dónde intervenir primero.",
    tag: "Salida técnica // Dictamen operativo",
    Icono: IconAssignmentTurnedIn,
  },
];

const LLAVE_WALKTHROUGH_VISTO = "faro_walkthrough_visto_v1";

export default function Home() {
  const { onPreguntar } = useOutletContext() ?? {};
  const [walkthroughAbierto, setWalkthroughAbierto] = useState(false);
  const [glosarioAbierto, setGlosarioAbierto] = useState(false);

  useEffect(() => {
    let visto = false;
    try {
      visto = localStorage.getItem(LLAVE_WALKTHROUGH_VISTO) === "1";
    } catch {
      // Storage bloqueado (modo privado, política del navegador): se trata
      // como primera visita cada vez, en vez de romper la pantalla.
    }
    if (!visto) setWalkthroughAbierto(true);
  }, []);

  function cerrarWalkthrough() {
    setWalkthroughAbierto(false);
    try {
      localStorage.setItem(LLAVE_WALKTHROUGH_VISTO, "1");
    } catch {
      // Best-effort -- si no se puede guardar, el walkthrough simplemente
      // se repite en la próxima visita, no es un error que mostrar.
    }
  }

  return (
    <>
      <div style={{ background: "var(--faro-canvas-subtle)" }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-10">
          {/* Barra de estado de la pantalla (mockup 01_Entrada.png) */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-8">
            <div className="flex flex-wrap items-center gap-3">
              {/* FIX (2026-09-13, US-651, obs. 8, Marina García + su IA): "Pantalla
                  01" pasa a "FASE_01" -- misma nomenclatura que ya usa la barra lateral
                  ("Flujo de Investigación", fases 00-06) y que Panorama/LosSieteCasos.
                  Se toma de FASES (lib/navFases.js), única definición, para que esta
                  insignia nunca se desincronice de la barra lateral. */}
              <span
                className="text-label-micro-mono uppercase px-1.5 py-0.5"
                style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
              >
                FASE_{FASES.find((f) => f.n === "01").n} · {FASES.find((f) => f.n === "01").label.toUpperCase()}
              </span>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
              <span className="text-label-micro-mono uppercase" style={{ color: "var(--faro-signal)" }}>
                Fase inicial: arquitectura sensorial
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={() => setWalkthroughAbierto(true)}
                className="text-label-ui inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--faro-radius-DEFAULT)] shadow-sm transition-colors"
                style={{ background: "var(--faro-canvas-container)", color: "var(--faro-command-base)" }}
              >
                <IconHelpCenter size={16} style={{ color: "var(--faro-signal)" }} />
                Guía rápida de investigación
              </button>
              <span
                className="text-label-data-mono px-3 py-1.5 rounded-[var(--faro-radius-DEFAULT)]"
                style={{ background: "var(--faro-canvas-container)", color: "var(--color-ink-soft)" }}
              >
                Entidades:{" "}
                <span style={{ color: "var(--faro-signal)", fontWeight: 600 }}>
                  {ENTIDADES_LABEL.map((e) => e.cveEnt).join(" · ")}
                </span>
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-7 flex flex-col gap-6">
              <div>
                <span className="text-label-micro-mono uppercase tracking-widest" style={{ color: "var(--faro-signal)" }}>
                  Observatorio de inteligencia estructural
                </span>
                <h1 className="text-headline-xl mt-2" style={{ color: "var(--faro-command-base)", maxWidth: "20ch" }}>
                  La escuela como sensor social
                </h1>
              </div>
              <p className="text-body-md" style={{ color: "var(--color-ink)", maxWidth: "56ch" }}>
                FARO transforma el análisis del riesgo educativo en una investigación guiada por
                evidencia: cada escuela se revisa a través de 6 líneas de evidencia territorial en
                4 entidades del país, para señalar dónde intervenir antes de que la matrícula se
                pierda.
              </p>

              <div
                className="rounded-[var(--faro-radius-xl)] p-5 shadow-sm flex flex-col gap-3"
                style={{ background: "var(--faro-canvas)" }}
              >
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <span className="text-label-micro-mono uppercase" style={{ color: "var(--color-ink-faint)" }}>
                    Propósito operativo del usuario
                  </span>
                  <span className="text-label-data-mono" style={{ color: "var(--faro-signal)" }}>
                    Protocolo: auditoría_expedientes
                  </span>
                </div>
                <p className="text-body-sm" style={{ color: "var(--color-ink-soft)" }}>
                  Como analista de formulación de política pública, tu tarea en esta sesión es
                  revisar la evidencia detrás de cada escuela en riesgo -- qué driver destaca y qué
                  recomendación le corresponde -- y decidir en cuáles vale la pena profundizar. El
                  conteo de casos y el panorama completo se revelan en la siguiente pantalla.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-4 pt-1">
                <Link
                  to="/panorama"
                  className="text-title-md inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-[var(--faro-radius-lg)] shadow-md transition-all group"
                  style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
                >
                  Iniciar investigación de señales
                  <IconArrowForward size={20} style={{ color: "var(--faro-signal-soft)" }} className="transition-transform group-hover:translate-x-1" />
                </Link>
                <button
                  type="button"
                  onClick={() => setGlosarioAbierto(true)}
                  className="text-title-md inline-flex items-center gap-2 px-5 py-3.5 rounded-[var(--faro-radius-lg)] transition-colors"
                  style={{ background: "var(--faro-canvas)", color: "var(--faro-command-base)" }}
                >
                  <IconMenuBook size={20} style={{ color: "var(--color-ink-faint)" }} />
                  Glosario metodológico
                </button>
              </div>
            </div>

            <div className="lg:col-span-5">
              <InfograficoArquitecturaSensorial />
            </div>
          </div>
        </div>
      </div>

      <PageContainer>
        <div className="flex items-center justify-between flex-wrap gap-2">
          <p className="text-label-micro-mono uppercase" style={{ color: "var(--color-ink-faint)" }}>
            Marco metodológico de tres etapas
          </p>
          <p className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
            Ciclo analítico homologado
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {ETAPAS.map((e) => (
            <div
              key={e.n}
              className="p-5 rounded-[var(--faro-radius-xl)] flex flex-col justify-between gap-3 shadow-sm"
              style={{ background: "var(--color-surface)" }}
            >
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-label-data-mono" style={{ color: "var(--faro-signal)", fontWeight: 700 }}>
                    {e.n} / {e.fase.toUpperCase()}
                  </span>
                  <span
                    className="p-1.5 rounded-[var(--faro-radius-DEFAULT)]"
                    style={{ background: "var(--faro-canvas-container)", color: "var(--faro-signal)" }}
                  >
                    <e.Icono size={18} />
                  </span>
                </div>
                <p className="text-title-md" style={{ color: "var(--faro-command-base)" }}>{e.titulo}</p>
                <p className="text-body-sm" style={{ color: "var(--color-ink-soft)" }}>{e.texto}</p>
              </div>
              <p className="text-label-micro-mono uppercase pt-2" style={{ color: "var(--color-ink-faint)" }}>
                {e.tag}
              </p>
            </div>
          ))}
        </div>

        <div
          className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-[var(--faro-radius-xl)]"
          style={{ background: "var(--faro-canvas-container)" }}
        >
          <div className="flex items-start gap-3">
            <span
              className="p-2 rounded-[var(--faro-radius-lg)] shrink-0"
              style={{ background: "var(--faro-canvas)", color: "var(--faro-signal)" }}
            >
              <IconLockClock size={24} />
            </span>
            <div className="flex-1">
              <p className="text-title-md" style={{ color: "var(--color-ink)" }}>
                Criterio de revelación escalonada de datos
              </p>
              <p className="text-body-sm mt-1 max-w-2xl" style={{ color: "var(--color-ink-faint)" }}>
                Por protocolo de rigor metodológico, los agregados cuantitativos y el conteo de casos
                en riesgo se desbloquean en el siguiente nivel de la investigación (Panorama de
                riesgo).
              </p>
            </div>
          </div>
          <span
            className="text-label-data-mono px-3 py-1.5 rounded-[var(--faro-radius-DEFAULT)] self-start md:self-center"
            style={{ background: "var(--faro-canvas)", color: "var(--color-ink-soft)" }}
          >
            Estado: sensores listos
          </span>
        </div>

        {/* Acceso a "Cómo funciona" desde la entrada (criterio 27 de la §9 de UX): quien llega
            por primera vez y quiere saber qué es esto antes de empezar debe poder entrar sin ir a
            buscarlo al rail. Va DESPUÉS de los tres pasos y con peso visual bajo: no compite con
            el recorrido narrativo, lo acompaña. */}
        <Link
          to="/como-funciona"
          className="flex items-center justify-between gap-4 p-4 rounded-2xl transition-colors"
          style={{
            background: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            color: "var(--color-ink)",
          }}
        >
          <span className="text-sm">
            <span style={{ fontWeight: 600 }}>¿Cómo funciona por dentro?</span>
            <span style={{ color: "var(--color-ink-faint)" }}>
              {" "}— las 8 fuentes, las tres capas de datos, los cubos y los tres modelos.
            </span>
          </span>
          <span
            className="font-mono-dato text-[11px] shrink-0"
            style={{ color: "var(--faro-signal)" }}
            aria-hidden="true"
          >
            →
          </span>
        </Link>
      </PageContainer>

      <WalkthroughOverlay abierto={walkthroughAbierto} onCerrar={cerrarWalkthrough} />
      <GlosarioOverlay
        abierto={glosarioAbierto}
        onCerrar={() => setGlosarioAbierto(false)}
        onPreguntar={onPreguntar}
      />
    </>
  );
}

// Infografico "Red de telemetria multicapa" (mockup 01_Entrada.png):
// reconstruido 1:1 contra el layout del mockup -- 3 "capas" concentricas
// (territorio / rejilla de planteles / vectores de contexto), 3 nodos de
// ejemplo en la capa media y 3 marcadores de categoria en la capa
// superior, exactamente como en la plantilla, incluyendo el rotulo
// "GEO_LAYER_v2.4".
//
// Dos correcciones de integridad de datos frente al mockup (nunca se
// fabrica un dato, ni siquiera en un grafico puramente decorativo):
// (1) el mockup etiqueta un nodo "NODO_JAL_04" -- 04 no es la clave INEGI
// real de Jalisco (es 14, igual que en ENTIDADES_LABEL /
// components/MapaEntidades.jsx, ya usada en Login.jsx) -- aqui dice
// JAL_14. Los otros 2 nodos del mockup (CDMX_09, NL_19) ya traian su
// clave real correcta.
// (2) las etiquetas de los 2 nodos laterales se acortan (sin el prefijo
// "NODO_") y el rotulo de la Capa 03 se recorrio a la parte baja de su
// ovalo -- en las coordenadas originales del mockup el texto de esa capa
// se encimaba con los marcadores de categoria de arriba (verificado
// renderizando el SVG) -- a peticion explicita de Diana de que ningun
// texto de este grafico se amontone.
//
// El marcador "VULNERABILIDAD" mantiene el rojo del mockup a proposito:
// es --color-alert (alerta/error generico de interfaz, ver index.css),
// NO el semaforo rojo/ambar/verde de nivel de riesgo que
// 03_Visual_Identity.md rechaza explicitamente -- aqui es solo la
// etiqueta de una categoria en un diagrama conceptual, no un indicador de
// riesgo de ninguna escuela.
function InfograficoArquitecturaSensorial() {
  return (
    <div
      className="rounded-[var(--faro-radius-xl)] p-4 md:p-5 shadow-md flex flex-col gap-3"
      style={{ background: "var(--faro-canvas)" }}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
          <span className="text-label-micro-mono uppercase" style={{ color: "var(--faro-command-base)" }}>
            Infográfico de arquitectura sensorial
          </span>
        </div>
        <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
          GEO_LAYER_v2.4
        </span>
      </div>

      <p className="text-title-md" style={{ color: "var(--faro-command-base)" }}>
        Red de Telemetría Multicapa // 4 Entidades Federativas
      </p>
      <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>
        Topología de acoplamiento entre centros escolares y vectores de presión física, hídrica y
        socioeconómica.
      </p>

      <div className="rounded-[var(--faro-radius-lg)] p-2" style={{ background: "var(--faro-canvas-container)" }}>
        <svg
          viewBox="0 0 460 270"
          role="img"
          aria-label="Diagrama de arquitectura sensorial en 3 capas: territorio operativo, rejilla de planteles educativos y vectores de contexto"
          className="w-full h-auto"
        >
          <rect x="10" y="10" width="440" height="250" rx="4" fill="var(--faro-canvas-subtle)" opacity="0.6" />
          <path
            d="M 40,60 L 420,60 M 40,120 L 420,120 M 40,180 L 420,180 M 40,240 L 420,240 M 80,30 L 80,250 M 170,30 L 170,250 M 260,30 L 260,250 M 350,30 L 350,250"
            stroke="var(--faro-hairline-hover)"
            strokeDasharray="3 3"
            strokeOpacity="0.5"
            strokeWidth="0.75"
          />

          {/* Capa 01: territorio operativo */}
          <ellipse cx="230" cy="200" rx="180" ry="40" fill="var(--faro-canvas-container)" />
          <text x="230" y="235" textAnchor="middle" className="font-mono-dato" style={{ fontSize: "9px", fontWeight: 700, fill: "var(--faro-command-base)" }}>
            CAPA 01: TERRITORIO OPERATIVO (CDMX · EDOMEX · NL · JAL)
          </text>

          {/* Capa 02: rejilla sensorial de planteles */}
          <ellipse cx="230" cy="130" rx="150" ry="32" fill="var(--faro-canvas-subtle)" />
          <text x="230" y="152" textAnchor="middle" className="font-mono-dato" style={{ fontSize: "9px", fontWeight: 700, fill: "var(--faro-command-base)" }}>
            CAPA 02: REJILLA SENSORIAL DE PLANTELES EDUCATIVOS
          </text>

          {/* Capa 03: telemetría de vectores de contexto -- rotulo recorrido
              a la base del ovalo para no encimarse con los marcadores. */}
          <ellipse cx="230" cy="65" rx="120" ry="24" fill="var(--faro-canvas)" stroke="var(--faro-hairline)" strokeWidth="1" />
          <text x="230" y="86" textAnchor="middle" className="font-mono-dato" style={{ fontSize: "9px", fontWeight: 700, fill: "var(--faro-command-base)" }}>
            CAPA 03: TELEMETRÍA DE VECTORES DE CONTEXTO
          </text>

          {/* Conectores entre capas */}
          <path d="M 120,200 L 140,130 L 160,65" fill="none" stroke="var(--faro-signal)" strokeDasharray="2 2" strokeOpacity="0.6" strokeWidth="1.5" />
          <path d="M 230,200 L 230,130 L 230,65" fill="none" stroke="var(--faro-signal)" strokeOpacity="0.6" strokeWidth="1.5" />
          <path d="M 340,200 L 320,130 L 300,65" fill="none" stroke="var(--faro-signal)" strokeDasharray="2 2" strokeOpacity="0.6" strokeWidth="1.5" />

          {/* Nodos de ejemplo en la Capa 02 -- claves reales de INEGI */}
          <g>
            <circle cx="140" cy="130" r="8" fill="var(--faro-canvas)" stroke="var(--faro-signal)" strokeWidth="2" />
            <circle cx="140" cy="130" r="3" fill="var(--faro-signal)" />
            <text x="152" y="133" className="font-mono-dato" style={{ fontSize: "9px", fontWeight: 700, fill: "var(--faro-command-base)" }}>JAL_14</text>
          </g>
          <g>
            <circle cx="230" cy="130" r="10" fill="var(--faro-canvas)" stroke="var(--faro-signal-soft)" strokeWidth="2" />
            <circle cx="230" cy="130" r="4" fill="var(--faro-signal)" />
            <text x="244" y="134" className="font-mono-dato" style={{ fontSize: "9px", fontWeight: 700, fill: "var(--faro-command-base)" }}>CDMX_09</text>
          </g>
          <g>
            <circle cx="320" cy="130" r="8" fill="var(--faro-canvas)" stroke="var(--faro-signal)" strokeWidth="2" />
            <circle cx="320" cy="130" r="3" fill="var(--faro-signal)" />
            <text x="332" y="133" className="font-mono-dato" style={{ fontSize: "9px", fontWeight: 700, fill: "var(--faro-command-base)" }}>NL_19</text>
          </g>

          {/* Marcadores de categoria en la Capa 03 */}
          <g>
            <polygon points="160,59 166,69 154,69" fill="var(--faro-signal)" />
            <text x="100" y="53" className="font-mono-dato" style={{ fontSize: "8px", fontWeight: 500, fill: "var(--faro-signal)" }}>ESTRÉS_HÍDRICO</text>
          </g>
          <g>
            <polygon points="230,59 236,69 224,69" fill="var(--color-alert)" />
            <text x="205" y="51" className="font-mono-dato" style={{ fontSize: "8px", fontWeight: 700, fill: "var(--color-alert)" }}>VULNERABILIDAD</text>
          </g>
          <g>
            <polygon points="300,59 306,69 294,69" fill="var(--faro-signal)" />
            <text x="308" y="53" className="font-mono-dato" style={{ fontSize: "8px", fontWeight: 500, fill: "var(--faro-signal)" }}>CONECTIVIDAD_RED</text>
          </g>
        </svg>
      </div>

      <div className="grid grid-cols-2 gap-2 pt-1">
        <span className="text-label-micro-mono inline-flex items-center gap-1.5" style={{ color: "var(--color-ink-faint)" }}>
          <IconHub size={14} style={{ color: "var(--faro-signal)" }} />
          Muestreo Federado
        </span>
        <span className="text-label-micro-mono inline-flex items-center gap-1.5" style={{ color: "var(--color-ink-faint)" }}>
          <IconSecurityUpdateGood size={14} style={{ color: "var(--faro-signal)" }} />
          Integridad Sin_Dato
        </span>
      </div>
    </div>
  );
}
