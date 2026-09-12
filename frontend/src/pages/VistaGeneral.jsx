import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import KpiCard from "../components/KpiCard.jsx";
import Card from "../components/Card.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import DifferentiatorChart from "../components/DifferentiatorChart.jsx";
import BarChartCard from "../components/BarChartCard.jsx";
import DonutChartCard from "../components/DonutChartCard.jsx";
import { MapaRiesgoCard } from "../components/MapaRiesgo.jsx";
import { escuelasPorNivel, escuelasEnRiesgo, kpis, kpisMockParaComparacion2Ciclos, parDiferenciador, driverNombres } from "../data/mock.js";
import { getEscuela, getPrediccion, getKpis } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";

// "El diferenciador" conectado al API real 11-sep (revisión de Edgar, PR
// #302). El par que se muestra es el elegido por Marina García el 6-sep
// sobre el Gold rematerializado tras DEC-019 (Guion_Demo_US006, bloque "El
// diferenciador"): dos CCTs reales con el mismo índice de riesgo pero
// distinto driver dominante y distinta recomendación -- la tesis del
// bloque es aislar esa única variable, así que el par queda fijo aquí en
// vez de elegirse dinámicamente.
//
// "ubicacion" (municipio/entidad) NO está en el contrato del API
// (EscuelaOut/EscuelaDetalleOut solo traen cve_mun, sin nombre -- mismo
// gap documentado en lib/api.js), así que queda como texto fijo conocido
// de este par específico, no como un dato que el API resuelva.
//
// El resto de la página (KPIs, mapa, matrícula por ciclo, distribución por
// nivel) sigue en mock -- mismos gaps de contrato ya documentados en
// Arquitectura_Frontend_React.md §9 (sin variación de matrícula por ciclo,
// sin lat/lon ni nombre de municipio/entidad). Rotulado con DemoBadge
// 11-sep (revisión de Edgar, PR #321): el dato seguía siendo mock, pero en
// pantalla no se notaba -- mismo patrón ya aplicado a "El diferenciador".
const PAR_DIFERENCIADOR = [
  { cct: "15DPR0920D", ubicacion: "Ecatepec de Morelos, Estado de México" },
  { cct: "15DPR2254O", ubicacion: "Ecatepec de Morelos, Estado de México" },
];

async function fetchEscuelaDelPar({ cct, ubicacion }) {
  const [escuelaRes, prediccionRes] = await Promise.all([getEscuela(cct), getPrediccion(cct)]);
  if (escuelaRes.error) return { error: escuelaRes.error };
  if (prediccionRes.error) return { error: prediccionRes.error };
  const escuela = escuelaRes.data;
  const prediccion = prediccionRes.data;
  return {
    data: {
      nombre: escuela.nombre,
      cct: escuela.cct,
      ubicacion,
      indiceRiesgo: prediccion.indice_riesgo,
      driver: prediccion.driver_dominante,
      driverNombre: driverNombres[prediccion.driver_dominante] ?? prediccion.driver_dominante,
      recomendacion: prediccion.recomendacion,
    },
  };
}

async function getParDiferenciadorReal() {
  const [a, b] = await Promise.all(PAR_DIFERENCIADOR.map(fetchEscuelaDelPar));
  if (a.error || b.error) return { data: null, error: a.error ?? b.error };
  return { data: { a: a.data, b: b.data }, error: null };
}

// Comparación de 2 ciclos (Christian, 12-sep, respuesta a la pregunta de
// Diana sobre la serie histórica): /series no existe y nunca existió --
// US-411 lo descartó fuera de alcance, y fact_escuela_ciclo solo
// materializa 2 ciclos, así que no hay una tendencia real de 3+ puntos que
// graficar. Se deriva del contrato ya publicado en KpisOut, sin pedir un
// endpoint nuevo ni inventar el valor del ciclo anterior:
// variacion_matricula = (actual - anterior) / anterior, así que
// anterior = actual / (1 + variacion_matricula) -- ambos números ya son la
// fuente de verdad del backend (KpisOut), solo se despejan.
function matriculaComparacion2Ciclos(k) {
  const actual = k.matricula_total;
  const anterior = Math.round(actual / (1 + k.variacion_matricula));
  if (!Number.isFinite(anterior)) return null;
  return [
    { ciclo: "Ciclo anterior", matricula: anterior },
    { ciclo: "Ciclo actual", matricula: actual },
  ];
}

export default function VistaGeneral() {
  const {
    status: parStatus,
    data: par,
    error: parError,
  } = useApiResource(() => getParDiferenciadorReal(), { mock: parDiferenciador, deps: [] });

  const {
    status: kpisStatus,
    data: kpisData,
    error: kpisError,
  } = useApiResource(() => getKpis(), { mock: kpisMockParaComparacion2Ciclos, deps: [] });
  const matriculaComparacion = kpisData ? matriculaComparacion2Ciclos(kpisData) : null;

  return (
    <PageContainer>
      <PageHeader title="Panorama general" subtitle="Una visión rápida de la situación de las escuelas en riesgo." />

      <div>
        <div className="mb-2">
          <DemoBadge />
        </div>
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {kpis.map((k) => (
            <KpiCard key={k.label} {...k} tone={k.label.includes("riesgo alto") ? "alert" : "default"} />
          ))}
        </section>
      </div>

      {parStatus === "loading" ? (
        <Card title="El diferenciador">
          <p className="text-sm py-6" style={{ color: "var(--color-ink-faint)" }}>Cargando el par de demostración…</p>
        </Card>
      ) : parStatus === "error" ? (
        <Card title="El diferenciador">
          <p className="text-sm py-6" style={{ color: "var(--color-risk-high)" }}>
            No se pudo cargar el par de demostración ({parError}).
          </p>
        </Card>
      ) : (
        <div>
          {parStatus === "demo" && (
            <div className="mb-2">
              <DemoBadge />
            </div>
          )}
          <DifferentiatorChart data={par} />
        </div>
      )}

      <div>
        <div className="mb-2">
          <DemoBadge />
        </div>
        <MapaRiesgoCard subtitle="Ubicación de las escuelas en riesgo" data={escuelasEnRiesgo} />
      </div>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          {kpisStatus === "demo" && (
            <div className="mb-2">
              <DemoBadge />
            </div>
          )}
          {kpisStatus === "loading" ? (
            <p className="text-sm py-6" style={{ color: "var(--color-ink-faint)" }}>Cargando matrícula…</p>
          ) : kpisStatus === "error" || !matriculaComparacion ? (
            <p className="text-sm py-6" style={{ color: "var(--color-risk-high)" }}>
              No se pudo cargar la comparación de matrícula ({kpisError ?? "dato no disponible"}).
            </p>
          ) : (
            <BarChartCard
              title="Matrícula, 2 ciclos"
              subtitle="Ciclo anterior vs. ciclo actual -- no hay serie histórica en el contrato (US-411)"
              data={matriculaComparacion}
              xKey="ciclo"
              yKey="matricula"
            />
          )}
        </div>
        <div>
          <div className="mb-2">
            <DemoBadge />
          </div>
          <DonutChartCard
            title="Distribución por nivel educativo"
            subtitle="Universo cubierto"
            data={escuelasPorNivel}
            nameKey="nombre"
            valueKey="valor"
          />
        </div>
      </section>
    </PageContainer>
  );
}
