import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import Card from "../components/Card.jsx";
import LeyendaGrafica from "../components/LeyendaGrafica.jsx";
import DifferentiatorChart from "../components/DifferentiatorChart.jsx";
import { driverIcons, driverNombres, recomendacionGeneralPorDriver, parDiferenciador } from "../data/mock.js";
import { riskRampColor } from "../lib/riskRamp.js";
import { getConclusionEscuelas, getEscuela, getPrediccion } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { panoramaMock } from "../data/mock.js";

const DRIVERS = ["D1", "D2", "D3", "D4", "D5", "D6"];

// "El diferenciador", rescatado de VistaGeneral.jsx antes de retirar esa
// pantalla (12-sep, decisión de arquitectura de Marina García del Buey:
// "Vista general se retira, pero hay que rescatar esto primero" -- ver
// vault/_DevLog/2026-09-12-diana-alvarez-retiro-heredadas-diferenciador.md).
// Conectado al API real desde el 11-sep (revisión de Edgar, PR #302). El
// par lo eligió Marina el 6-sep sobre el Gold rematerializado tras
// DEC-019 (Guion_Demo_US006, bloque "El diferenciador"): dos CCTs reales
// con el mismo índice de riesgo pero distinto driver dominante y distinta
// recomendación -- la tesis del bloque es aislar esa única variable, así
// que el par queda fijo aquí en vez de elegirse dinámicamente. Es la
// prueba concreta de la tesis del proyecto (CLAUDE.md: "dos escuelas con
// el mismo riesgo reciben recomendaciones distintas según el driver
// dominante"), y va aquí -- no en Panorama -- porque es la evidencia de
// cierre de la conclusión, no el enunciado de apertura de la
// investigación.
//
// "ubicacion" (municipio/entidad) NO está en el contrato del API
// (EscuelaOut/EscuelaDetalleOut solo traen cve_mun, sin nombre -- mismo
// gap documentado arriba), así que queda como texto fijo conocido de este
// par específico, no como un dato que el API resuelva.
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

// Pantalla 5 -- Conclusión Top 3 (rediseño Fase 2, US-641), nueva por
// completo. Contra 01_UX_Architecture.md §2 "Pantalla 5" y
// 02_Data_Visualization_Spec.md §7.bis.2 fila "P5 · Gráfica de unidades
// del Top".
//
// Se reutiliza getPanoramaEscuelas() (ya construida para P2) en vez de
// escribir una llamada nueva: esa función YA trae, para el conjunto
// COMPLETO de escuelas en riesgo, tanto driver_dominante (de la lista)
// como d1..d6 (del detalle por escuela) -- exactamente lo que esta
// pantalla necesita para (a) contar el Top 3 de dominantes y (b) saber
// qué driver nunca tuvo dato en ninguna escuela (nota de cobertura, §7.bis.2).
//
// IMPORTANTE (§3 de la arquitectura, y la nota obligatoria de abajo): este
// conteo NUNCA debe filtrarse por lo que el usuario haya elegido en otra
// pantalla -- por eso llama a getPanoramaEscuelas() de cero, no recibe
// props ni lee un estado de filtros de otra pantalla.
export default function Conclusion() {
  const { status, data } = useApiResource(getConclusionEscuelas, { mock: panoramaMock });
  const {
    status: parStatus,
    data: par,
    error: parError,
  } = useApiResource(() => getParDiferenciadorReal(), { mock: parDiferenciador, deps: [] });
  const escuelas = status === "ok" || status === "demo" ? data : [];
  const n = escuelas.length;
  const esReal = status === "ok";

  // Top 3 (o menos -- Marina, PR #308/§8.3: "no rellenar hasta tres" si de
  // verdad solo dominan uno o dos) de driver_dominante sobre el conjunto
  // completo, nunca sobre un subconjunto filtrado.
  const conteoPorDriver = {};
  for (const e of escuelas) {
    if (!e.driver_dominante) continue;
    conteoPorDriver[e.driver_dominante] = (conteoPorDriver[e.driver_dominante] ?? 0) + 1;
  }
  const top = Object.entries(conteoPorDriver)
    .map(([code, count]) => ({ code, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);
  const maxCount = Math.max(1, ...top.map((t) => t.count));

  // Cobertura (§7.bis.2, "P5"): un driver que jamás tuvo dato en NINGUNA
  // escuela del conjunto no debe leerse como "no importa" -- se declara
  // aparte, no se confunde con que "nunca domina".
  const sinCoberturaEnElConjunto = DRIVERS.filter(
    (code) => escuelas.length > 0 && escuelas.every((e) => e[code.toLowerCase()] == null)
  );

  // Concentración por municipio (§2: "concentración por municipio"). Nombre
  // real del municipio desde el 12-sep (checklist "Municipio y entidad por
  // nombre real", US-621/BUG-077): antes se pintaba cve_mun crudo porque,
  // al escribirse esta pantalla, nadie había probado GET /municipios/{cve_mun}
  // desde ninguna parte. En modo demo (sin cve_mun, ver data/mock.js) se
  // agrupa por el nombre de municipio que ya trae el mock.
  const porMunicipio = {};
  for (const e of escuelas) {
    const clave = esReal ? e.cve_mun : e.municipio;
    const etiqueta = esReal ? e.nombre_municipio : e.municipio;
    if (!clave || !etiqueta) continue;
    if (!porMunicipio[clave]) porMunicipio[clave] = { etiqueta, count: 0 };
    porMunicipio[clave].count += 1;
  }
  const municipios = Object.entries(porMunicipio)
    .map(([clave, { etiqueta, count }]) => ({ clave, etiqueta, count }))
    .sort((a, b) => b.count - a.count);

  return (
    <PageContainer>
      <div className="flex items-start justify-between flex-wrap gap-4">
        <PageHeader
          kicker="Pantalla 05 · Conclusión"
          title="Lo que más se repite entre las escuelas en riesgo"
          subtitle="El hallazgo principal de esta investigación, visto sobre el conjunto completo."
        />
        {status === "demo" && <DemoBadge />}
      </div>

      {status === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando la conclusión…</p>
      )}
      {status === "error" && (
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No pudimos calcular la conclusión, intenta de nuevo.
        </p>
      )}

      {(status === "ok" || status === "demo") && (
        <>
          <Card
            title={`Top ${top.length} de drivers dominantes`}
            subtitle={`Sobre las ${n} escuelas en riesgo del conjunto completo, independientemente de cualquier filtro.`}
          >
            <div className="flex flex-col gap-4">
              {top.map(({ code, count }) => (
                <div key={code} className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 font-semibold" style={{ color: "var(--color-ink)" }}>
                      <span>{driverIcons[code]}</span>
                      {driverNombres[code]}
                    </span>
                    <span className="font-semibold tabular" style={{ color: "var(--color-ink)" }}>
                      {count} de {n} escuelas
                    </span>
                  </div>
                  <div className="rounded-full overflow-hidden" style={{ height: 14, background: "var(--color-surface-alt, #f4f4f5)" }}>
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${(count / maxCount) * 100}%`, background: riskRampColor(count / maxCount) }}
                    />
                  </div>
                  <p className="text-xs" style={{ color: "var(--color-ink-faint)" }}>
                    Recomendación general: {recomendacionGeneralPorDriver[code]}
                  </p>
                </div>
              ))}
            </div>

            <LeyendaGrafica
              queSeVe="Cada casilla es una escuela en riesgo, agrupada bajo la pista que más destaca en ella. Cuantas más casillas, más se repite esa pista."
              unidad="Conteo de escuelas, k de N. La proporción es secundaria: con N pequeño una escuela mueve muchos puntos."
              sinDato={
                sinCoberturaEnElConjunto.length > 0
                  ? `Las pistas que no pudieron verificarse en ninguna escuela no aparecen en el Top: ${sinCoberturaEnElConjunto.map((c) => driverNombres[c]).join(", ")}. Una pista con 0 no deja de existir.`
                  : "Las pistas que no pudieron verificarse en ninguna escuela no aparecen en el Top. Una pista con 0 no deja de existir."
              }
              cicloYRecorte={`Ciclo más reciente materializado. El conjunto completo de ${n} escuelas en riesgo, sin filtros, sin importar lo que se haya filtrado antes.`}
            />
          </Card>

          {municipios.length > 0 && (
            <Card title="Concentración por municipio" subtitle="Municipio real de cada escuela en riesgo del conjunto completo.">
              <div className="flex flex-wrap gap-2">
                {municipios.map((m) => (
                  <span
                    key={m.clave}
                    className="text-xs font-semibold px-3 py-1.5 rounded-full"
                    style={{ background: "var(--color-surface-alt, #f4f4f5)", color: "var(--color-ink)" }}
                  >
                    {m.etiqueta} · {m.count} {m.count === 1 ? "escuela" : "escuelas"}
                  </span>
                ))}
              </div>
            </Card>
          )}

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

          {/* Nota obligatoria literal (01_UX_Architecture.md §2, Pantalla 5). */}
          <p className="text-sm italic" style={{ color: "var(--color-ink-faint)" }}>
            Esta conclusión se calcula sobre el conjunto completo de escuelas en riesgo, independientemente
            de los filtros utilizados durante la exploración.
          </p>

          <div className="flex justify-end">
            <Link
              to="/explorador"
              className="inline-block text-sm font-semibold px-5 py-3 rounded-full"
              style={{ background: "var(--color-primary)", color: "#ffffff" }}
            >
              Ir al Explorador de escuelas →
            </Link>
          </div>
        </>
      )}
    </PageContainer>
  );
}
