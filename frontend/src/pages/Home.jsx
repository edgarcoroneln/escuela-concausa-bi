import { useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import GlosarioOverlay from "../components/GlosarioOverlay.jsx";
import WalkthroughOverlay from "../components/WalkthroughOverlay.jsx";

// Pantalla 1 -- Entrada (rediseño Fase 2, US-641). Reescrita contra la ficha
// de 01_UX_Architecture.md §2 "Pantalla 1", no contra la copy de las
// plantillas Stitch (esas usan una narrativa de "sensores"/"telemetría" que
// no está en el spec aprobado ni en el PRD -- se dejó fuera a propósito).
//
// CORRECCIÓN respecto a la Fase 1 de esta pantalla: el Home anterior
// revelaba "escuelas_en_riesgo" en el hero (`tituloHero()`, PR #302). El
// spec es explícito: **P1 nunca revela el conteo de casos, esa es tarea de
// P2 (Panorama)** -- por eso esta versión ya no llama a getKpis() ni
// muestra ningún número agregado. Pantalla estática, sin estado de carga
// ni de error (§2).
const FEATURES = [
  { icon: "🛡️", label: "Datos verificados" },
  { icon: "📍", label: "4 entidades: CDMX, Edomex, NL, Jalisco" },
  { icon: "🔎", label: "6 líneas de investigación por escuela" },
  { icon: "✅", label: "Recomendaciones para la acción" },
];

const LLAVE_WALKTHROUGH_VISTO = "faro_walkthrough_visto_v1";

export default function Home() {
  const { onPreguntar } = useOutletContext() ?? {};
  const [walkthroughAbierto, setWalkthroughAbierto] = useState(false);
  const [glosarioAbierto, setGlosarioAbierto] = useState(false);
  // "Visita recurrente" (§2): cambia el tono de la frase de apoyo y evita
  // disparar el walkthrough automático. Con localStorage porque el spec lo
  // describe como algo que persiste más allá de una sola pestaña ("la
  // primera vez que el usuario entra tras autenticarse"); en un navegador
  // compartido por varias personas esto puede saltarse una vez de más, pero
  // es una ayuda de onboarding, no una decisión con consecuencia de datos.
  const [visitaRecurrente, setVisitaRecurrente] = useState(true);

  useEffect(() => {
    let visto = false;
    try {
      visto = localStorage.getItem(LLAVE_WALKTHROUGH_VISTO) === "1";
    } catch {
      // Storage bloqueado (modo privado, política del navegador): se trata
      // como primera visita cada vez, en vez de romper la pantalla.
    }
    setVisitaRecurrente(visto);
    if (!visto) setWalkthroughAbierto(true);
  }, []);

  function cerrarWalkthrough() {
    setWalkthroughAbierto(false);
    setVisitaRecurrente(true);
    try {
      localStorage.setItem(LLAVE_WALKTHROUGH_VISTO, "1");
    } catch {
      // Best-effort -- si no se puede guardar, el walkthrough simplemente
      // se repite en la próxima visita, no es un error que mostrar.
    }
  }

  return (
    <>
      <div style={{ background: "linear-gradient(135deg, #0b1524 0%, #16283f 100%)" }}>
        <div className="max-w-6xl mx-auto px-8 pt-16 pb-12">
          <span className="font-mono-dato text-[11px] uppercase font-semibold tracking-wider" style={{ color: "var(--faro-signal-soft)" }}>
            Pantalla 01 · Entrada
          </span>
          <h1 className="text-4xl leading-tight mt-3" style={{ color: "#ffffff", fontWeight: 700, maxWidth: "22ch" }}>
            ¿Qué es FARO?
          </h1>
          <p className="text-base mt-5 leading-relaxed" style={{ color: "#b7c0d1", maxWidth: "56ch" }}>
            FARO es la herramienta de FARO Team para investigar el riesgo de abandono escolar en las
            escuelas de 4 entidades del país. Analiza 6 líneas de evidencia por escuela para señalar
            dónde intervenir antes de que la matrícula se pierda.
          </p>
          <p className="text-base mt-4 leading-relaxed font-semibold" style={{ color: "#ffffff", maxWidth: "48ch" }}>
            {visitaRecurrente
              ? "Tu investigación sigue donde la dejaste: cada caso se revisa por separado."
              : "La matrícula nos dio la primera pista. Ahora descubramos qué está pasando."}
          </p>

          <div className="bg-white/5 rounded-xl p-5 mt-6 max-w-2xl">
            <span className="font-mono-dato text-[10px] uppercase font-semibold tracking-wider" style={{ color: "var(--faro-signal-soft)" }}>
              Tu rol en esta sesión
            </span>
            <p className="text-sm mt-2 leading-relaxed" style={{ color: "#b7c0d1" }}>
              Revisar la evidencia detrás de cada escuela en riesgo -- qué driver destaca y qué
              recomendación le corresponde -- y decidir en cuáles vale la pena profundizar. El
              conteo de casos y el panorama completo se revelan en la siguiente pantalla.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-4 mt-8">
            <Link
              to="/panorama"
              className="inline-block text-sm font-semibold px-5 py-3 rounded-full"
              style={{ background: "var(--color-primary)", color: "#ffffff" }}
            >
              Ver el panorama de riesgo →
            </Link>
            <button
              type="button"
              onClick={() => setGlosarioAbierto(true)}
              className="text-sm font-semibold px-4 py-3 rounded-full"
              style={{ background: "rgba(255,255,255,0.08)", color: "#ffffff" }}
            >
              📖 Glosario metodológico
            </button>
            {visitaRecurrente && (
              <button
                type="button"
                onClick={() => setWalkthroughAbierto(true)}
                className="text-sm px-2 py-2 rounded-full"
                style={{ color: "#b7c0d1" }}
                title="Volver a ver la guía rápida"
                aria-label="Volver a ver la guía rápida"
              >
                ¿ Guía rápida
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-14 pt-8" style={{ borderTop: "1px solid #2a3850" }}>
            {FEATURES.map((f) => (
              <div key={f.label} className="flex items-center gap-2.5">
                <span className="text-lg">{f.icon}</span>
                <span className="text-xs" style={{ color: "#b7c0d1" }}>{f.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <PageContainer>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl" style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)" }}>
            <span className="font-mono-dato text-[11px] font-semibold" style={{ color: "var(--faro-signal)" }}>01 · Detección</span>
            <p className="text-sm font-semibold mt-2" style={{ color: "var(--color-ink)" }}>6 drivers por escuela</p>
            <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>
              Cada escuela se observa en 6 líneas de evidencia; lo que no se pudo observar se marca
              explícito como SIN_DATO, nunca como cero.
            </p>
          </div>
          <div className="p-5 rounded-2xl" style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)" }}>
            <span className="font-mono-dato text-[11px] font-semibold" style={{ color: "var(--faro-signal)" }}>02 · Síntesis</span>
            <p className="text-sm font-semibold mt-2" style={{ color: "var(--color-ink)" }}>Índice de riesgo</p>
            <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>
              El modelo combina los 6 drivers en un índice de riesgo y un nivel de atención (alta,
              media o baja) por escuela.
            </p>
          </div>
          <div className="p-5 rounded-2xl" style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)" }}>
            <span className="font-mono-dato text-[11px] font-semibold" style={{ color: "var(--faro-signal)" }}>03 · Acción</span>
            <p className="text-sm font-semibold mt-2" style={{ color: "var(--color-ink)" }}>Recomendación</p>
            <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>
              Cada escuela con predicción trae una recomendación asociada a su driver dominante.
            </p>
          </div>
        </div>
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
