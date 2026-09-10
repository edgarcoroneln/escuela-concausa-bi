import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import RiskGauge from "../components/RiskGauge.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import { driverColors, driverNombres, escuelasEnRiesgo as escuelasMock, nivelRiesgo } from "../data/mock.js";
import { getEscuela } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";

const TABS = ["Resumen", "Drivers", "Comparación", "Predicción", "Recomendación"];

// Conectado al API real 10-sep (revisión de Edgar, PR #302) vía getEscuela(cct)
// (EscuelaDetalleOut: sí trae latitud/longitud, a diferencia de la lista --
// ver getEscuelasEnRiesgo en lib/api.js -- pero sigue sin variación de
// matrícula ni nombre de municipio/entidad, solo cve_mun). Con
// VITE_USE_MOCK=true se usa el mock, siempre rotulado.
export default function ExpedienteEscuela() {
  const { cct } = useParams();
  const [tab, setTab] = useState(TABS[0]);
  const { status, data, error } = useApiResource(() => getEscuela(cct), {
    mock: escuelasMock.find((e) => e.cct === cct) ?? null,
    deps: [cct],
  });

  if (status === "loading") {
    return (
      <PageContainer>
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando expediente…</p>
      </PageContainer>
    );
  }

  if (status === "error" || !data) {
    return (
      <PageContainer>
        <Card title="No encontrado">
          <p className="text-sm mb-3">
            {status === "error" ? `No se pudo cargar el CCT ${cct} (${error}).` : `No hay datos para el CCT ${cct}.`}
          </p>
          <Link to="/casos" className="text-sm font-semibold" style={{ color: "var(--color-primary)" }}>
            ← Volver a los 7 casos
          </Link>
        </Card>
      </PageContainer>
    );
  }

  const escuela = data;
  const color = driverColors[escuela.driver_dominante] ?? "var(--color-primary)";
  const riesgo = nivelRiesgo(escuela.indice_riesgo);
  const esReal = status === "ok";

  return (
    <PageContainer>
      <Link to="/casos" className="text-sm" style={{ color: "var(--color-ink-faint)" }}>
        ← Volver a casos
      </Link>

      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          {status === "demo" && <div className="mb-2"><DemoBadge /></div>}
          <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>{escuela.nombre}</h1>
          <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>
            {escuela.cct}{esReal ? ` · matrícula ${escuela.matricula_total.toLocaleString("es-MX")}` : ` · ${escuela.municipio}, ${escuela.entidad}`}
          </p>
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
                  ...(esReal
                    ? [["Matrícula total", escuela.matricula_total.toLocaleString("es-MX")]]
                    : [
                        ["Municipio", escuela.municipio],
                        ["Entidad", escuela.entidad],
                        ["Variación último ciclo", `${escuela.variacion}%`],
                      ]),
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
