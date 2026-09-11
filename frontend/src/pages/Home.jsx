import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import { getKpis } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { kpis as kpisMock } from "../data/mock.js";

const FEATURES = [
  { icon: "🛡️", label: "Datos confiables" },
  { icon: "📍", label: "Análisis territorial" },
  { icon: "🔎", label: "6 líneas de investigación" },
  { icon: "✅", label: "Recomendaciones para la acción" },
];

// Traduce KpisOut (API real) a las mismas 4 tarjetas del mockup de UX/UI.
// "Índice de riesgo promedio" no existe en el contrato real (KpisOut no trae
// un promedio) -- se sustituye por variacion_matricula, que sí es real.
// Ver revisión de Edgar en PR #302 (10-sep): antes esta pantalla usaba
// mock.js directo y sin rótulo, aun fuera de modo desarrollo.
function kpisDesdeApi(k) {
  const pct = (v) => `${v >= 0 ? "+" : ""}${(v * 100).toFixed(1)}%`;
  return [
    { label: "Matrícula total", value: k.matricula_total.toLocaleString("es-MX"), hint: "Alumnado inscrito, ciclo vigente" },
    { label: "Completitud de drivers", value: `${Math.round(k.indice_completitud_drivers * 100)}%`, hint: "Promedio de drivers observados" },
    { label: "Variación de matrícula", value: pct(k.variacion_matricula), hint: "Respecto al ciclo anterior" },
    { label: "Escuelas en riesgo alto", value: String(k.escuelas_en_riesgo), hint: "Índice ≥ 0.50 (línea de alerta, DEC-019)" },
  ];
}

// Título del hero -- ya no un "7" fijo en el texto (revisión de Edgar en
// PR #302, 10-sep): usa el conteo real de KpisOut.escuelas_en_riesgo en
// cuanto llega; mientras carga, un texto neutro que no inventa un número.
function tituloHero(status, data) {
  if (status === "ok") return `${data.escuelas_en_riesgo} escuelas están en riesgo.`;
  if (status === "demo") return `${data.find((k) => k.label.includes("riesgo alto"))?.value ?? "—"} escuelas están en riesgo.`;
  return "Escuelas en riesgo.";
}

export default function Home() {
  const { status, data, error } = useApiResource(getKpis, { mock: kpisMock });
  const tarjetas = status === "ok" ? kpisDesdeApi(data) : status === "demo" ? data : null;

  return (
    <>
      {/* Hero a todo lo ancho, fondo oscuro (como en el mockup de UX/UI) */}
      <div style={{ background: "linear-gradient(135deg, #0b1524 0%, #16283f 100%)" }}>
        <div className="max-w-6xl mx-auto px-8 pt-16 pb-12">
          <h1 className="text-5xl leading-tight" style={{ color: "#ffffff", fontWeight: 800, maxWidth: "16ch" }}>
            {tituloHero(status, data)}
          </h1>
          <p className="text-base mt-5 leading-relaxed" style={{ color: "#b7c0d1", maxWidth: "48ch" }}>
            La matrícula nos dio la primera pista. Ahora es momento de investigar qué está pasando con cada una.
          </p>
          <Link
            to="/casos"
            className="inline-block text-sm font-semibold px-5 py-3 rounded-full mt-6"
            style={{ background: "var(--color-primary)", color: "#ffffff" }}
          >
            Comenzar la investigación →
          </Link>

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

      {/* Franja de cifras, fondo claro */}
      <PageContainer>
        {status === "demo" && (
          <div className="mb-3">
            <DemoBadge />
          </div>
        )}
        {status === "loading" && (
          <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando cifras…</p>
        )}
        {status === "error" && (
          <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
            No se pudieron cargar las cifras del API ({error}).
          </p>
        )}
        {tarjetas && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {tarjetas.map((k) => (
              <div key={k.label} className="p-5 rounded-2xl" style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", boxShadow: "var(--shadow-card)" }}>
                <span className="text-2xl font-extrabold tabular block" style={{ color: "var(--color-ink)" }}>{k.value}</span>
                <span className="text-xs" style={{ color: "var(--color-ink-faint)" }}>{k.label}</span>
              </div>
            ))}
          </div>
        )}
      </PageContainer>
    </>
  );
}
