import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import RiskGauge from "../components/RiskGauge.jsx";
import DriverBars from "../components/DriverBars.jsx";
import LeyendaGrafica from "../components/LeyendaGrafica.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import { driverNombres, escuelasEnRiesgo as escuelasMock, nivelRiesgo } from "../data/mock.js";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";
import { getEscuela, getPrediccion } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { useCortesAtencion } from "../lib/cortesAtencion.js";

const TABS = ["Resumen", "Drivers", "Comparación", "Predicción", "Recomendación"];

// Conectado al API real 10-sep (revisión de Edgar, PR #302) vía getEscuela(cct)
// (EscuelaDetalleOut: sí trae latitud/longitud, a diferencia de la lista --
// ver getEscuelasEnRiesgo en lib/api.js -- pero sigue sin variación de
// matrícula ni nombre de municipio/entidad, solo cve_mun). Con
// VITE_USE_MOCK=true se usa el mock, siempre rotulado.
//
// Actualizado 11-sep: tabs Drivers/Predicción/Recomendación conectados.
// Drivers usa d1..d6 + indice_completitud_drivers, ya incluidos en la
// respuesta de getEscuela(cct) (sin llamada extra). Predicción y
// Recomendación llaman a getPrediccion(cct) solo si tiene_prediccion es
// true; si es false se muestra SIN_DATO explícito -- nunca se inventa una
// predicción para una escuela sin cobertura suficiente. "Comparación" sigue
// pendiente: no hay endpoint de serie histórica/comparación en el contrato
// (ver Arquitectura_Frontend_React.md §9).
export default function ExpedienteEscuela() {
  const { cct } = useParams();
  const [tab, setTab] = useState(TABS[0]);
  const { status, data, error } = useApiResource(() => getEscuela(cct), {
    mock: escuelasMock.find((e) => e.cct === cct) ?? null,
    deps: [cct],
  });
  // Cortes del nivel de atención desde /version (DEC-026, hallazgo de Diana
  // 12-sep) -- nivelRiesgo() ya no trae 0.50/0.30 fijos, ver data/mock.js.
  // CORRECCIÓN 12-sep (revisión de Edgar, PR #325): antes solo se leía
  // `cortes` y se trataba igual que "cargando" si nunca llegaba -- si
  // /version fallaba, la pantalla se quedaba pegada en "Cargando
  // expediente..." para siempre en vez de avisar. Ahora se distingue
  // loading / error (o cortes ausentes) / ok-demo, como pide el checklist.
  const { status: cortesStatus, cortes, error: cortesError } = useCortesAtencion();

  const tienePrediccion = data?.tiene_prediccion ?? false;
  const escuelaMock = escuelasMock.find((e) => e.cct === cct) ?? null;
  const prediccionMock = escuelaMock
    ? {
        cct: escuelaMock.cct,
        id_ciclo: "demo",
        indice_riesgo: escuelaMock.indice_riesgo,
        driver_dominante: escuelaMock.driver_dominante,
        cluster: null,
        recomendacion: "Recomendación de ejemplo -- dato de muestra, no proviene del modelo real.",
        mlflow_run_id: "demo",
      }
    : null;

  const {
    status: prediccionStatus,
    data: prediccion,
    error: prediccionError,
  } = useApiResource(
    () => (tienePrediccion ? getPrediccion(cct) : Promise.resolve({ data: null, error: null })),
    { mock: prediccionMock, deps: [cct, tienePrediccion] }
  );

  if (status === "loading" || cortesStatus === "loading") {
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
            ← Volver a los casos
          </Link>
        </Card>
      </PageContainer>
    );
  }

  // Cortes ausentes: /version respondió pero sin cortes_atencion, o falló
  // directamente. Sin cortes no se puede calcular el nivel de atención
  // (nivelRiesgo() los necesita) -- se avisa explícito en vez de renderizar
  // con un valor inventado o quedarse en el estado de carga.
  if (!cortes) {
    return (
      <PageContainer>
        <Card title="No se pudo calcular el nivel de atención">
          <p className="text-sm mb-3">
            No fue posible cargar los cortes de atención desde /version{cortesStatus === "error" && cortesError ? ` (${cortesError})` : ""}. Intenta de nuevo más tarde.
          </p>
          <Link to="/casos" className="text-sm font-semibold" style={{ color: "var(--color-primary)" }}>
            ← Volver a los casos
          </Link>
        </Card>
      </PageContainer>
    );
  }

  const escuela = data;
  const color = riskRampColor(escuela.indice_riesgo);
  const riesgo = nivelRiesgo(escuela.indice_riesgo, cortes);
  const esReal = status === "ok";

  return (
    <PageContainer>
      <Link to="/casos" className="text-sm" style={{ color: "var(--color-ink-faint)" }}>
        ← Regresar a selección
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
          style={{ background: "var(--color-surface-alt)" }}
        >
          <span className="text-xl font-extrabold tabular block" style={{ color: "var(--color-ink)" }}>{escuela.indice_riesgo.toFixed(2)}</span>
          <span className="text-[11px] font-semibold" style={{ color: "var(--color-ink)" }}>{riesgo.icon} {riesgo.label} · Índice de riesgo</span>
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
              <RiskGauge
                value={escuela.indice_riesgo}
                color={color}
                alertLine={cortes.alta}
                max={cortes.ancla_calibracion ?? 0.6}
              />
              <span
                className="text-xs font-semibold px-3 py-1 rounded-full inline-flex items-center gap-1.5"
                style={{ background: "var(--color-surface)", border: `2px solid ${DOMINANT_OUTLINE}`, color: "var(--color-ink)" }}
              >
                ▲ Driver dominante: {driverNombres[escuela.driver_dominante]}
              </span>
            </div>
          </div>
        )}

        {tab === "Drivers" && (
          esReal ? (
            <div className="py-2">
              <p className="text-xs mb-4" style={{ color: "var(--color-ink-faint)" }}>
                Completitud de datos: {(escuela.indice_completitud_drivers * 100).toFixed(0)}%
                {escuela.es_estimado_por_grupo && " · valores estimados por grupo (no medición individual)"}
              </p>
              <DriverBars
                drivers={{ D1: escuela.d1, D2: escuela.d2, D3: escuela.d3, D4: escuela.d4, D5: escuela.d5, D6: escuela.d6 }}
                driverDominante={escuela.driver_dominante}
              />
              {/* Leyenda obligatoria (02_Data_Visualization_Spec.md §7.bis.2, fila "P4 · Comparativa
                  de los 6 drivers") -- texto literal, solo el ciclo se resuelve en vivo (nunca
                  tecleado, §8.2). */}
              <LeyendaGrafica
                queSeVe="Las seis pistas del entorno de esta escuela, siempre en el mismo orden. La barra mide cuánta presión ejerce cada una; la marcada con ▲ es la que más destaca según el modelo."
                unidad="Posición relativa de 0 a 1 entre las escuelas observadas. Infraestructura y conectividad se leen como falta: 1 es carencia total del servicio."
                sinDato="Pista rayada de punta a punta, con el motivo por el que falta. Un cero real se dibuja como una barra mínima con su «0.00»: no se parecen."
                cicloYRecorte={`Ciclo ${prediccion?.id_ciclo ?? "más reciente materializado"}, una sola escuela. Pobreza y rezago e inseguridad son valores de su municipio, compartidos con las demás escuelas de ahí.`}
              />
            </div>
          ) : (
            <p className="text-sm py-6" style={{ color: "var(--color-ink-faint)" }}>
              El desglose por driver no está en el set de ejemplo -- se conecta al API real.
            </p>
          )
        )}

        {tab === "Predicción" && (
          prediccionStatus === "loading" ? (
            <p className="text-sm py-6" style={{ color: "var(--color-ink-faint)" }}>Cargando predicción…</p>
          ) : prediccionStatus === "error" ? (
            <p className="text-sm py-6" style={{ color: "var(--color-risk-high)" }}>
              No se pudo cargar la predicción ({prediccionError}).
            </p>
          ) : !tienePrediccion || !prediccion ? (
            <p className="text-sm py-6" style={{ color: "var(--color-ink-faint)" }}>
              Esta escuela no tiene predicción disponible (SIN_DATO) -- cobertura insuficiente de
              drivers en el ciclo actual, no un valor de cero.
            </p>
          ) : (
            <div className="py-2">
              {prediccionStatus === "demo" && <div className="mb-3"><DemoBadge /></div>}
              <table className="text-sm">
                <tbody>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <td className="py-2 pr-4" style={{ color: "var(--color-ink-faint)" }}>Ciclo</td>
                    <td className="py-2 font-medium" style={{ color: "var(--color-ink)" }}>{prediccion.id_ciclo}</td>
                  </tr>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <td className="py-2 pr-4" style={{ color: "var(--color-ink-faint)" }}>Índice de riesgo (predicho)</td>
                    <td className="py-2 font-medium" style={{ color: "var(--color-ink)" }}>{prediccion.indice_riesgo.toFixed(2)}</td>
                  </tr>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <td className="py-2 pr-4" style={{ color: "var(--color-ink-faint)" }}>Driver dominante</td>
                    <td className="py-2 font-medium" style={{ color: "var(--color-ink)" }}>
                      {driverNombres[prediccion.driver_dominante] ?? prediccion.driver_dominante}
                    </td>
                  </tr>
                  {prediccion.cluster !== null && prediccion.cluster !== undefined && (
                    <tr>
                      <td className="py-2 pr-4" style={{ color: "var(--color-ink-faint)" }}>Cluster</td>
                      <td className="py-2 font-medium" style={{ color: "var(--color-ink)" }}>{prediccion.cluster}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )
        )}

        {tab === "Recomendación" && (
          prediccionStatus === "loading" ? (
            <p className="text-sm py-6" style={{ color: "var(--color-ink-faint)" }}>Cargando recomendación…</p>
          ) : prediccionStatus === "error" ? (
            <p className="text-sm py-6" style={{ color: "var(--color-risk-high)" }}>
              No se pudo cargar la recomendación ({prediccionError}).
            </p>
          ) : !tienePrediccion || !prediccion ? (
            <p className="text-sm py-6" style={{ color: "var(--color-ink-faint)" }}>
              No hay recomendación disponible para esta escuela (SIN_DATO).
            </p>
          ) : (
            <div className="py-2">
              {prediccionStatus === "demo" && <div className="mb-3"><DemoBadge /></div>}
              <p className="text-sm" style={{ color: "var(--color-ink)" }}>{prediccion.recomendacion}</p>
            </div>
          )
        )}

        {tab === "Comparación" && (
          <p className="text-sm py-6" style={{ color: "var(--color-ink-faint)" }}>
            Pendiente: no hay endpoint de comparación/serie histórica en el contrato actual del API
            (ver Arquitectura_Frontend_React.md §9).
          </p>
        )}
      </Card>

      <div className="flex justify-end">
        <Link
          to="/conclusion"
          className="inline-block text-sm font-semibold px-5 py-3 rounded-full"
          style={{ background: "var(--color-primary)", color: "#ffffff" }}
        >
          Ver la conclusión →
        </Link>
      </div>
    </PageContainer>
  );
}
