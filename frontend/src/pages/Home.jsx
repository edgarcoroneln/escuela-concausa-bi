import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import { kpis } from "../data/mock.js";

const FEATURES = [
  { icon: "🛡️", label: "Datos confiables" },
  { icon: "📍", label: "Análisis territorial" },
  { icon: "🔎", label: "6 líneas de investigación" },
  { icon: "✅", label: "Recomendaciones para la acción" },
];

export default function Home() {
  return (
    <>
      {/* Hero a todo lo ancho, fondo oscuro (como en el mockup de UX/UI) */}
      <div style={{ background: "linear-gradient(135deg, #0b1524 0%, #16283f 100%)" }}>
        <div className="max-w-6xl mx-auto px-8 pt-16 pb-12">
          <h1 className="text-5xl leading-tight" style={{ color: "#ffffff", fontWeight: 800, maxWidth: "16ch" }}>
            7 escuelas están en riesgo.
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
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {kpis.map((k) => (
            <div key={k.label} className="p-5 rounded-2xl" style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", boxShadow: "var(--shadow-card)" }}>
              <span className="text-2xl font-extrabold tabular block" style={{ color: "var(--color-ink)" }}>{k.value}</span>
              <span className="text-xs" style={{ color: "var(--color-ink-faint)" }}>{k.label}</span>
            </div>
          ))}
        </div>
      </PageContainer>
    </>
  );
}
