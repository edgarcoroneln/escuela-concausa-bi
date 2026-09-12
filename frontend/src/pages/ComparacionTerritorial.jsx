import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import { escuelasEnRiesgo as escuelasMock, nivelRiesgo } from "../data/mock.js";
import { riskRampColor } from "../lib/riskRamp.js";
import { getComparacionTerritorial } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { useCortesAtencion } from "../lib/cortesAtencion.js";

// Conectado al API real 12-sep: el gap de contrato que dejaba esta pantalla
// en "en construcción" (revisión de Edgar, PR #302, 11-sep) quedó stale el
// mismo día en que se abrió -- EscuelaOut ya trae cve_mun y GET
// /municipios/{cve_mun} ya expone nombre_municipio/nombre_entidad (US-621,
// MunicipioOut en schemas.py), solo que nadie lo había probado desde
// ninguna pantalla. getComparacionTerritorial() (lib/api.js) hace UNA
// llamada por municipio único de las 7 escuelas en riesgo, no una por
// escuela.
//
// Alcance de esta conexión: la comparación que el dato real permite
// responder de forma honesta es "¿comparten municipio o nivel dos o más de
// las escuelas en riesgo?" -- no existe (todavía) un cálculo de "escuelas
// similares" en ningún endpoint, así que no se inventa uno aquí.
export default function ComparacionTerritorial() {
  const { status, data, error } = useApiResource(getComparacionTerritorial, { mock: escuelasMock });
  // Mismo patrón de 3 estados que ExpedienteEscuela.jsx/LosSieteCasos.jsx
  // (revisión de Edgar, PR #325, 12-sep): loading / error-o-ausente visible / ok.
  const { status: cortesStatus, cortes, error: cortesError } = useCortesAtencion();
  const esReal = status === "ok";
  const escuelas = status === "ok" ? data : status === "demo" ? data : [];

  const normalizadas = escuelas.map((e) => ({
    ...e,
    municipioLabel: esReal ? e.nombre_municipio : e.municipio,
    entidadLabel: esReal ? e.nombre_entidad : e.entidad,
  }));

  const porMunicipio = agruparPorMunicipio(normalizadas);
  const municipiosCompartidos = porMunicipio.filter((m) => m.escuelas.length > 1);

  return (
    <PageContainer>
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>¿Es un caso aislado?</h1>
          <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>
            Compara cada escuela con su municipio y su nivel educativo.
          </p>
          {status === "demo" && <div className="mt-2"><DemoBadge /></div>}
        </div>
        <Link
          to="/casos"
          className="text-sm font-semibold px-4 py-2.5 rounded-full whitespace-nowrap"
          style={{ background: "var(--color-surface-alt, #f4f4f5)", color: "var(--color-ink)" }}
        >
          ← Volver a los 7 casos
        </Link>
      </div>

      {status === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando escuelas y municipios…</p>
      )}
      {status === "error" && (
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No se pudieron cargar las escuelas o sus municipios ({error}).
        </p>
      )}

      {(status === "ok" || status === "demo") && cortesStatus === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando niveles de atención…</p>
      )}
      {(status === "ok" || status === "demo") && cortesStatus !== "loading" && !cortes && (
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No fue posible cargar los cortes de atención desde /version{cortesStatus === "error" && cortesError ? ` (${cortesError})` : ""}. Intenta de nuevo más tarde.
        </p>
      )}

      {normalizadas.length > 0 && cortes && (
        <>
          <Card
            title="Municipios con más de un caso"
            subtitle={
              municipiosCompartidos.length > 0
                ? "Estos municipios concentran más de una de las 7 escuelas en riesgo -- no es un patrón aislado."
                : "Ninguno de los 7 casos comparte municipio con otro -- cada escuela está en un municipio distinto."
            }
          >
            {municipiosCompartidos.length > 0 && (
              <div className="flex flex-col gap-2">
                {municipiosCompartidos.map((m) => (
                  <div
                    key={m.clave}
                    className="flex items-center justify-between text-sm px-3 py-2 rounded-lg"
                    style={{ background: "var(--color-surface-alt, #f4f4f5)" }}
                  >
                    <span style={{ color: "var(--color-ink)" }}>{m.municipioLabel}, {m.entidadLabel}</span>
                    <span className="font-semibold" style={{ color: "var(--color-ink)" }}>
                      {m.escuelas.length} escuelas
                    </span>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card title="Las 7 escuelas por municipio y nivel">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ color: "var(--color-ink-faint)" }}>
                    <th className="text-left font-semibold pb-2">Escuela</th>
                    <th className="text-left font-semibold pb-2">Nivel</th>
                    <th className="text-left font-semibold pb-2">Municipio</th>
                    <th className="text-left font-semibold pb-2">Entidad</th>
                    <th className="text-left font-semibold pb-2">Riesgo</th>
                  </tr>
                </thead>
                <tbody>
                  {normalizadas.map((e) => {
                    const riesgo = nivelRiesgo(e.indice_riesgo, cortes);
                    return (
                      <tr key={e.cct} style={{ borderTop: "1px solid var(--color-border)" }}>
                        <td className="py-2">
                          <Link to={`/escuela/${e.cct}`} className="font-semibold" style={{ color: "var(--color-primary)" }}>
                            {e.nombre ?? e.cct}
                          </Link>
                        </td>
                        <td className="py-2" style={{ color: "var(--color-ink-faint)" }}>{e.nivel}</td>
                        <td className="py-2" style={{ color: "var(--color-ink-faint)" }}>{e.municipioLabel ?? "Sin dato"}</td>
                        <td className="py-2" style={{ color: "var(--color-ink-faint)" }}>{e.entidadLabel ?? "Sin dato"}</td>
                        <td className="py-2">
                          <span className="inline-flex items-center gap-1.5" style={{ color: riskRampColor(e.indice_riesgo) }}>
                            {riesgo.icon} {riesgo.label}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </PageContainer>
  );
}

function agruparPorMunicipio(escuelas) {
  const grupos = new Map();
  for (const e of escuelas) {
    const clave = `${e.municipioLabel ?? "sin-dato"}|${e.entidadLabel ?? "sin-dato"}`;
    if (!grupos.has(clave)) {
      grupos.set(clave, { clave, municipioLabel: e.municipioLabel, entidadLabel: e.entidadLabel, escuelas: [] });
    }
    grupos.get(clave).escuelas.push(e);
  }
  return [...grupos.values()];
}
