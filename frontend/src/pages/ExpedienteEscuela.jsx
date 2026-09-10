import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import RiskGauge from "../components/RiskGauge.jsx";
import { driverColors, driverNombres, escuelasEnRiesgo, nivelRiesgo } from "../data/mock.js";

const TABS = ["Resumen", "Drivers", "Comparación", "Predicción", "Recomendación"];

// Expediente individual — una escuela, con tabs (calca los paneles 07-11 del
// mockup de UX/UI: son las 5 vistas de un mismo expediente, no pantallas
// sueltas). Todavía usa mock data; en la siguiente fase cada tab se conecta
// a su endpoint real:
//   Resumen/Drivers -> getEscuela(cct)          (EscuelaDetalleOut: d1..d6)
//   Predicción      -> getPrediccion(cct)
//   Recomendación   -> getPrediccionExplicacion(cct)
export default function ExpedienteEscuela() {
  const { cct } = useParams();
  const [tab, setTab] = useState(TABS[0]);
  const i = escuelasEnRiesgo.findIndex((e) => e.cct === cct);
  const escuela = escuelasEnRiesgo[i];

  if (!escuela) {
    return (
      <PageContainer>
        <Card title="No encontrado">
          <p className="text-sm mb-3">No hay datos mock para el CCT {cct}.</p>
          <Link to="/casos" className="text-sm font-semibold" style={{ color: "var(--color-primary)" }}>
            ← Volver a los 7 casos
          </Link>
        </Card>
      </PageContainer>
    );
  }

  const color = driverColors[escuela.driver_dominante] ?? "var(--color-primary)";
  const riesgo = nivelRiesgo(escuela.indice_riesgo);

  return (
    <PageContainer>
      <Link to="/casos" className="text-sm" style={{ color: "var(--color-ink-faint)" }}>
        ← Volver a casos
      </Link>

      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <p className="kicker mb-1">Expediente {String(i + 1).padStart(2, "0")} de {escuelasEnRiesgo.length}</p>
          <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>{escuela.nombre}</h1>
          <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>{escuela.cct} · {escuela.municipio}, {escuela.entidad}</p>
        </div>
        <div
          className="px-4 py-2.5 rounded-xl text-right"
          style={{ background: `${riesgo.color}1a` }}
        >
          <span className="text-xl font-extrabold tabular block" style={{ color: riesgo.color }}>{escuela.indice_riesgo.toFixed(2)}</span>
          <span className="text-[11px] font-semibold" style={{ color: riesgo.color }}>{riesgo.label} · Índice de riesgo</span>
        </div>
      </div>

      <Card>
        <div className="flex gap-1 mb-4 border-b overflow-x-auto" style={{ borderColor: "var(--color-border)" }}>
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className="text-sm px-3 py-2 -mb-px whitespace-nowrap"
              style={
                tab === t
                  ? { borderBottom: "2px solid var(--color-primary)", color: "var(--color-primary)", fontWeight: 600 }
                  : { color: "var(--color-ink-faint)" }
              }
            >
              {t}
            </button>
          ))}
        </div>

        {tab === "Resumen" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 py-2">
            <table className="text-sm">
              <tbody>
                {[
                  ["Nivel educativo", escuela.nivel],
                  ["Municipio", escuela.municipio],
                  ["Entidad", escuela.entidad],
                  ["Variación último ciclo", `${escuela.variacion}%`],
                ].map(([k, v]) => (
                  <tr key={k} style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <td className="py-2 pr-4" style={{ color: "var(--color-ink-faint)" }}>{k}</td>
                    <td className="py-2 font-medium" style={{ color: "var(--color-ink)" }}>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="flex flex-col items-center gap-3">
              <RiskGauge value={escuela.indice_riesgo} color={color} />
              <span className="text-xs font-semibold px-3 py-1 rounded-full" style={{ background: `${color}1a`, color }}>
                Driver dominante: {driverNombres[escuela.driver_dominante]}
              </span>
            </div>
          </div>
        )}
        {tab !== "Resumen" && (
          <p className="text-sm py-6" style={{ color: "var(--color-ink-faint)" }}>
            Tab "{tab}" pendiente de conectar a /api/v1/predicciones/{"{cct}"} y /explicacion.
          </p>
        )}
      </Card>
    </PageContainer>
  );
}
