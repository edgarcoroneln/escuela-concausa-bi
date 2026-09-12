import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import RiskGauge from "../components/RiskGauge.jsx";
import LeyendaGrafica from "../components/LeyendaGrafica.jsx";
import { driverIcons, driverNombres, escuelasEnRiesgo as escuelasMock, nivelRiesgo } from "../data/mock.js";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";
import { getEscuelasEnRiesgo } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { useCortesAtencion } from "../lib/cortesAtencion.js";

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
  // Cortes del nivel de atención desde /version (DEC-026, hallazgo de Diana
  // 12-sep) -- nivelRiesgo() ya no trae 0.50/0.30 fijos, ver data/mock.js.
  const { cortes } = useCortesAtencion();
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
        <div className="flex items-center gap-2">
          <Link
            to="/panorama"
            className="text-sm font-semibold px-4 py-2.5 rounded-full whitespace-nowrap"
            style={{ background: "var(--color-surface-alt, #f4f4f5)", color: "var(--color-ink)" }}
          >
            ← Volver al panorama
          </Link>
          <button
            className="text-sm font-semibold px-4 py-2.5 rounded-full whitespace-nowrap"
            style={{ background: "var(--color-header)", color: "#fff" }}
          >
            Comparar los 7 casos
          </button>
        </div>
      </div>

      {status === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando escuelas…</p>
      )}
      {status === "error" && (
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No se pudieron cargar las escuelas del API ({error}).
        </p>
      )}

      {escuelas.length > 0 && cortes && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {escuelas.map((e, i) => {
            const color = riskRampColor(e.indice_riesgo);
            const riesgo = nivelRiesgo(e.indice_riesgo, cortes);
            return (
              <Card
                key={e.cct}
                hover
                className="flex flex-col justify-between aparicion-escalonada"
                style={{ "--delay": `${i * 60}ms` }}
              >
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

                  <div className="flex justify-center mb-1">
                    <RiskGauge
                      value={e.indice_riesgo}
                      color={color}
                      alertLine={cortes.alta}
                      max={cortes.ancla_calibracion ?? 0.6}
                      size={104}
                    />
                  </div>
                  <p className="text-[11px] text-center mb-4" style={{ color: "var(--color-ink-faint)" }}>
                    {riesgo.icon} {riesgo.label}{!esReal && ` · Variación matrícula ${e.variacion}%`}
                  </p>

                  <span
                    className="text-xs font-semibold px-2.5 py-1 rounded-full inline-flex items-center gap-1.5"
                    style={{ background: "var(--color-surface)", border: `2px solid ${DOMINANT_OUTLINE}`, color: "var(--color-ink)" }}
                  >
                    <span>{driverIcons[e.driver_dominante]}</span>
                    {driverNombres[e.driver_dominante]}
                  </span>
                </div>

                <Link
                  to={`/escuela/${e.cct}`}
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

      {escuelas.length > 0 && cortes && (
        <Card>
          {/* Leyenda obligatoria (02_Data_Visualization_Spec.md §7.bis.2, fila "P3 · Pista del
              índice de riesgo") -- una sola vez para toda la cuadrícula, no repetida por tarjeta. */}
          <LeyendaGrafica
            queSeVe="Una tarjeta por escuela. El número es su índice de riesgo y la pista muestra dónde cae ese índice, con la línea de alerta marcada."
            unidad="Índice de 0 a 1 que traduce la variación de matrícula que el modelo proyecta. No es probabilidad ni porcentaje."
            sinDato="Una escuela sin predicción lo dice en su tarjeta y no recibe marca en la pista; no se coloca en 0."
            cicloYRecorte={`Ciclo más reciente materializado. Las ${escuelas.length} escuelas en riesgo, de mayor a menor índice.`}
          />
        </Card>
      )}
    </PageContainer>
  );
}
