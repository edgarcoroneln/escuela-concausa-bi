import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Card from "../components/Card.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import LeyendaGrafica from "../components/LeyendaGrafica.jsx";
import { MapaRiesgoCard } from "../components/MapaRiesgo.jsx";
import { driverIcons, driverNombres, escuelasEnRiesgo as escuelasMock, nivelRiesgo } from "../data/mock.js";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";
import { getEscuelasEnRiesgo } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { useCortesAtencion } from "../lib/cortesAtencion.js";

// Conectada al API real 12-sep: MapaRiesgo.jsx (componente D3 real, con
// proyección Mercator sobre el geojson de estados) ya existía -- se
// construyó para VistaGeneral.jsx (pantalla de una fase anterior) pero
// solo con datos mock, nunca conectado aquí. EscuelaOut trae
// latitud/longitud reales desde el 11-sep (US-621); una escuela sin
// georreferencia (None) se OMITE del mapa -- dibujarla en (0,0) inventaría
// una ubicación, mismo criterio SIN_DATO del resto del proyecto -- pero
// sigue en la tabla de abajo con su riesgo.
//
// Decisión de alcance resuelta hoy, no solo una conexión de datos: esta
// pantalla es justo la que 02_Data_Visualization_Spec.md §8.1 (fila "Mapa
// de ubicación") y PLAN_TRABAJO.md §10.sexies dejaron pendiente "en el
// handoff con el Equipo 5" -- textualmente, con Diana Álvarez. La mitad
// técnica de la razón para no construirlo ("la API no expone geometría")
// cayó el 11-sep; la otra mitad seguía en pie: "dónde" no responde "qué
// situación", y unos puntos sobre el contorno de un par de estados no
// distinguen nada por sí solos. Por eso esta pantalla no es solo el mapa:
// ADR-011 §4 exige que el riesgo se pueda leer sin él, así que se agrega
// la tabla accesible de abajo con las 7 escuelas y su nivel de riesgo en
// texto plano -- el mapa aporta la lectura territorial, la tabla sigue
// siendo la fuente de verdad del riesgo, con o sin mapa.
export default function MapaCasos() {
  const { status, data, error } = useApiResource(getEscuelasEnRiesgo, { mock: escuelasMock });
  const { cortes } = useCortesAtencion();
  const [selectedCct, setSelectedCct] = useState(null);
  const escuelas = status === "ok" || status === "demo" ? data : [];

  useEffect(() => {
    if (!selectedCct && escuelas.length > 0) setSelectedCct(escuelas[0].cct);
  }, [escuelas, selectedCct]);

  const seleccionada = escuelas.find((e) => e.cct === selectedCct) ?? null;
  const sinGeorreferencia = escuelas.filter((e) => e.latitud == null || e.longitud == null);

  return (
    <PageContainer>
      <PageHeader
        title="¿Dónde están ocurriendo los casos?"
        subtitle="Explora la ubicación de las 7 escuelas y su contexto territorial."
      />
      {status === "demo" && <div className="mt-2"><DemoBadge /></div>}

      {status === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando escuelas…</p>
      )}
      {status === "error" && (
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No se pudieron cargar las escuelas del API ({error}).
        </p>
      )}

      {escuelas.length > 0 && cortes && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4">
            <div className="flex flex-col gap-2">
              <MapaRiesgoCard
                subtitle={
                  sinGeorreferencia.length > 0
                    ? `${escuelas.length - sinGeorreferencia.length} de ${escuelas.length} escuelas con coordenada real -- ${sinGeorreferencia.length} sin georreferencia, omitidas del mapa (siguen en la tabla).`
                    : `Coordenada real de las ${escuelas.length} escuelas en riesgo.`
                }
                data={escuelas}
                selectedCct={selectedCct}
                onSelect={setSelectedCct}
              />
              {/* Leyenda obligatoria, texto acordado con E5 (DEC-026, PLAN_TRABAJO.md §10.septies,
                  criterio 28 §7.bis) -- literal, no parafraseada: "aproximada" se queda porque la
                  base es estatal, no georreferencia una dirección. "ver lista" enlaza a "Los 7
                  casos" (LosSieteCasos.jsx), que es la superficie primaria de comparación por
                  índice -- el mapa acompaña, nunca la reemplaza (ADR-011 §4). */}
              <p className="text-xs px-1" style={{ color: "var(--color-ink-faint)" }}>
                Ubicación aproximada de las escuelas en riesgo -- no reemplaza la comparación por
                índice,{" "}
                <Link to="/casos" style={{ color: "var(--color-primary)", fontWeight: 600 }}>
                  ver lista
                </Link>
                .
              </p>
            </div>

            <Card title="Escuela seleccionada">
              {seleccionada ? (
                <div className="flex flex-col gap-2 text-sm">
                  <p className="font-bold" style={{ color: "var(--color-ink)" }}>
                    {seleccionada.nombre ?? seleccionada.cct}
                  </p>
                  <p style={{ color: "var(--color-ink-faint)" }}>{seleccionada.nivel}</p>
                  {status === "ok" && (
                    <p style={{ color: "var(--color-ink-faint)" }}>
                      Matrícula: {seleccionada.matricula_total?.toLocaleString("es-MX") ?? "Sin dato"}
                    </p>
                  )}
                  <p className="inline-flex items-center gap-1.5" style={{ color: riskRampColor(seleccionada.indice_riesgo) }}>
                    {nivelRiesgo(seleccionada.indice_riesgo, cortes).icon} {nivelRiesgo(seleccionada.indice_riesgo, cortes).label}
                    <span style={{ color: "var(--color-ink-faint)" }}>· {seleccionada.indice_riesgo?.toFixed(2)}</span>
                  </p>
                  <span
                    className="text-xs font-semibold px-2.5 py-1 rounded-full inline-flex items-center gap-1.5 w-fit"
                    style={{ background: "var(--color-surface)", border: `2px solid ${DOMINANT_OUTLINE}`, color: "var(--color-ink)" }}
                  >
                    <span>{driverIcons[seleccionada.driver_dominante]}</span>
                    {driverNombres[seleccionada.driver_dominante]}
                  </span>
                  {(seleccionada.latitud == null || seleccionada.longitud == null) && (
                    <p className="text-xs" style={{ color: "var(--color-ink-faint)" }}>
                      Sin georreferencia -- no aparece como punto en el mapa.
                    </p>
                  )}
                  <Link
                    to={`/escuela/${seleccionada.cct}`}
                    className="text-sm font-semibold mt-2"
                    style={{ color: "var(--color-primary)" }}
                  >
                    Ver expediente completo →
                  </Link>
                </div>
              ) : (
                <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>
                  Selecciona un caso en el mapa o en la tabla.
                </p>
              )}
            </Card>
          </div>

          <Card title="Las 7 escuelas y su nivel de riesgo, en texto">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ color: "var(--color-ink-faint)" }}>
                    <th className="text-left font-semibold pb-2">Escuela</th>
                    <th className="text-left font-semibold pb-2">Nivel</th>
                    <th className="text-left font-semibold pb-2">Riesgo</th>
                    <th className="text-left font-semibold pb-2">Driver dominante</th>
                    <th className="text-left font-semibold pb-2">En el mapa</th>
                  </tr>
                </thead>
                <tbody>
                  {escuelas.map((e) => {
                    const riesgo = nivelRiesgo(e.indice_riesgo, cortes);
                    const enMapa = e.latitud != null && e.longitud != null;
                    return (
                      <tr
                        key={e.cct}
                        style={{
                          borderTop: "1px solid var(--color-border)",
                          background: e.cct === selectedCct ? "var(--color-surface-alt, #f4f4f5)" : "transparent",
                          cursor: "pointer",
                        }}
                        onClick={() => setSelectedCct(e.cct)}
                      >
                        <td className="py-2">
                          <Link
                            to={`/escuela/${e.cct}`}
                            className="font-semibold"
                            style={{ color: "var(--color-primary)" }}
                            onClick={(ev) => ev.stopPropagation()}
                          >
                            {e.nombre ?? e.cct}
                          </Link>
                        </td>
                        <td className="py-2" style={{ color: "var(--color-ink-faint)" }}>{e.nivel}</td>
                        <td className="py-2">
                          <span className="inline-flex items-center gap-1.5" style={{ color: riskRampColor(e.indice_riesgo) }}>
                            {riesgo.icon} {riesgo.label}
                          </span>
                        </td>
                        <td className="py-2" style={{ color: "var(--color-ink-faint)" }}>
                          {driverIcons[e.driver_dominante]} {driverNombres[e.driver_dominante]}
                        </td>
                        <td className="py-2" style={{ color: "var(--color-ink-faint)" }}>{enMapa ? "Sí" : "Sin georreferencia"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          <Card>
            <LeyendaGrafica
              queSeVe="Cada punto del mapa es una escuela en riesgo, ubicada por su coordenada real; el color es su índice de riesgo. La tabla de abajo repite el mismo dato en texto para cada escuela, con o sin mapa."
              unidad="Índice de 0 a 1 que traduce la variación de matrícula que el modelo proyecta. No es probabilidad ni porcentaje."
              sinDato="Una escuela sin coordenada real no aparece como punto en el mapa -- se omite en vez de dibujarse en un lugar inventado -- pero sigue en la tabla con su riesgo."
              cicloYRecorte={`Ciclo más reciente materializado. Las ${escuelas.length} escuelas en riesgo, de mayor a menor índice.`}
            />
          </Card>
        </>
      )}
    </PageContainer>
  );
}
