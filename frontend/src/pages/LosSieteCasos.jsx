import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import { driverColors, driverIcons, driverNombres, escuelasEnRiesgo as escuelasMock, nivelRiesgo } from "../data/mock.js";
import { getEscuelasEnRiesgo } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";

// Conectado al API real 10-sep (revisión de Edgar, PR #302): ya no son 7
// CCT con "PLACEHOLDER-*" fijos, sino el catálogo real ordenado desc por
// indice_riesgo (getEscuelasEnRiesgo en lib/api.js). Con VITE_USE_MOCK=true
// se sigue viendo el mock, pero siempre rotulado con DemoBadge.
//
// Gap de contrato pendiente (ver Arquitectura_Frontend_React.md §9):
// EscuelaOut no trae municipio/entidad por nombre ni variación de matrícula
// por escuela -- en modo real esas dos líneas no se muestran (no se
// inventan) hasta que el API las exponga.
export default function LosSieteCasos() {
  const { status, data, error } = useApiResource(getEscuelasEnRiesgo, { mock: escuelasMock });
  const esReal = status === "ok";
  const escuelas = status === "ok" ? data : status === "demo" ? data : [];

  return (
    <PageContainer>
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>Nuestros 7 casos</h1>
          <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>
            Siete escuelas presentan una señal de riesgo. Cada una cuenta una historia distinta.
          </p>
          {status === "demo" && <div className="mt-2"><DemoBadge /></div>}
        </div>
        <button
          className="text-sm font-semibold px-4 py-2.5 rounded-full whitespace-nowrap"
          style={{ background: "var(--color-header)", color: "#fff" }}
        >
          Comparar los 7 casos
        </button>
      </div>

      {status === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando escuelas…</p>
      )}
      {status === "error" && (
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No se pudieron cargar las escuelas del API ({error}).
        </p>
      )}

      {escuelas.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {escuelas.map((e, i) => {
            const color = driverColors[e.driver_dominante] ?? "var(--color-primary)";
            const riesgo = nivelRiesgo(e.indice_riesgo);
            return (
              <Card key={e.cct} hover className="flex flex-col justify-between">
                <div>
                  <p className="text-sm font-bold mb-1" style={{ color: "var(--color-ink)" }}>
                    Escuela {String(i + 1).padStart(2, "0")}
                  </p>
                  <p className="text-xs mb-0.5" style={{ color: "var(--color-ink-faint)" }}>{e.nivel}</p>
                  <p className="text-xs mb-0.5" style={{ color: "var(--color-ink-faint)" }}>CCT {e.cct}</p>
                  {esReal ? (
                    <p className="text-xs mb-4" style={{ color: "var(--color-ink-faint)" }}>
                      Matrícula: {e.matricula_total.toLocaleString("es-MX")}
                    </p>
                  ) : (
                    <p className="text-xs mb-4" style={{ color: "var(--color-ink-faint)" }}>{e.municipio}, {e.entidad}</p>
                  )}

                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="text-2xl font-extrabold tabular" style={{ color: riesgo.color }}>
                      {e.indice_riesgo.toFixed(2)}
                    </span>
                    {!esReal && (
                      <span className="text-xs font-semibold tabular" style={{ color: "var(--color-ink-faint)" }}>
                        {e.variacion}%
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] mb-4" style={{ color: "var(--color-ink-faint)" }}>
                    Índice de riesgo{!esReal && " · Variación matrícula"}
                  </p>

                  <span
                    className="text-xs font-semibold px-2.5 py-1 rounded-full inline-flex items-center gap-1.5"
                    style={{ background: `${color}1a`, color }}
                  >
                    <span>{driverIcons[e.driver_dominante]}</span>
                    {driverNombres[e.driver_dominante]}
                  </span>
                </div>

                <Link
                  to={`/casos/${e.cct}`}
                  className="text-sm font-semibold mt-5 inline-block"
                  style={{ color: "var(--color-primary)" }}
                >
                  Abrir expediente →
                </Link>
              </Card>
            );
          })}
        </div>
      )}
    </PageContainer>
  );
}
