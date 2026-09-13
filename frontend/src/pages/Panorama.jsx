import { useId } from "react";
import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import Card from "../components/Card.jsx";
import SiluetaEntidad from "../components/SiluetaEntidad.jsx";
import { ENTIDADES_LABEL } from "../components/MapaEntidades.jsx";
import { IconArrowForward, IconHub, IconSecurityUpdateGood } from "../components/Icons.jsx";
import { getConclusionEscuelas, getKpis, getUniversoEscuelas } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { panoramaMock, kpisMockParaComparacion2Ciclos, universoEscuelasMock, driverNombres } from "../data/mock.js";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";

const DRIVERS_ORDEN = ["D1", "D2", "D3", "D4", "D5", "D6"];

// Pantalla 2 -- Panorama de riesgo (rediseño Fase 2, US-641). Contra
// 01_UX_Architecture.md §2 "Pantalla 2": esta es la ÚNICA pantalla que
// revela el conteo de casos (P1 nunca lo hace, ver Home.jsx) y la ÚNICA
// donde se muestra la matrícula general de los casos "dentro de la
// historia" (VistaGeneral.jsx la muestra también, pero es la vista
// heredada, no la narrativa guiada).
//
// N siempre sale de datos reales (nunca escrito a mano): es el mismo
// arreglo que dibuja la tabla, ya recortado por getEscuelasEnRiesgo() al
// conteo oficial de KpisOut.escuelas_en_riesgo (DEC-024).
//
// 13-sep, segunda ronda -- 6 pedidos puntuales de Diana sobre esta pantalla,
// después del primer pase de fidelidad (ver el historial largo más abajo):
//   1) El kicker "Pantalla 02 · Panorama" (con su propio <h1> "El panorama
//      de riesgo") se quita del todo -- era el encabezado heredado de Fase 1
//      y quedaba duplicado con la barra de protocolo + "Diagnóstico
//      federativo // Las N escuelas frente a los 6 drivers" de arriba, que
//      es el encabezado real del mockup. El DemoBadge se reubica junto a
//      esa barra de protocolo para no perder el aviso de modo demo.
//   2) Se quita el "héroe oscuro" (recuadro de fondo --faro-command-base
//      con "N escuelas están en riesgo..."): con el encabezado de arriba
//      diciendo básicamente lo mismo, quedaba redundante -- esto es
//      justo lo que el comentario del primer pase ya dejaba como pregunta
//      abierta ("si prefieres que el héroe oscuro se quite... dímelo").
//      matriculaTotal se quita también: ya no lo usa nadie.
//   3) Las 3 tarjetas KPI (TarjetaKpiSeveridad) no cambiaron -- ya traían
//      toda la escala de severidad + "Driver dominante"/"Sin dato" +
//      etiqueta inferior que pidió Diana.
//   4) La "Comparativa de los 6 drivers" deja de ser el heatmap D3 de
//      DriverMatrix.jsx y se vuelve una TABLA real (nueva función
//      TablaDrivers, abajo) -- fila por escuela, columna por driver, con
//      el mismo criterio de color que ya usaba el heatmap (riskRampColor,
//      nunca color por driver) y el mismo contorno ámbar para el driver
//      dominante. Mismos datos, otra forma visual.
//   5) El panel "Enclave Georreferenciado" ahora dibuja la silueta REAL de
//      la entidad con más escuelas en riesgo (components/SiluetaEntidad.jsx,
//      mismo geojson real de 32 estados que ya usa MapaEntidades.jsx) con
//      las escuelas de esa entidad como puntos reales (lat/lon de
//      EscuelaOut) -- en vez del diagrama abstracto de nodos/curva del
//      mockup, que no tenía respaldo geográfico real.
//   6) Se quita la tarjeta "Entidades del alcance" (el mapa interactivo de
//      México con las 4 entidades, a la derecha de la comparativa): con la
//      tabla de drivers de punto 4 ya no hay heatmap que atenuar al pasar
//      el cursor, y el enclave ya tiene su propia silueta -- el mapa de
//      México quedaba redundante. Se consolidan además las 2 llamadas a
//      getPanoramaEscuelas/getConclusionEscuelas que corrían en paralelo
//      (pendiente que el primer pase ya había dejado anotado) en una sola
//      -- ya no hay heatmap que "no arriesgar" con el cambio.
//
// Comentarios del primer pase de fidelidad (13-sep, antes de estos 6 pedidos):
//
// Primer uso real de DriverMatrix.jsx (antes solo vivía en MatrizDrivers.jsx
// "en construcción", nunca conectada) -- el costo de "N+2 llamadas" que ese
// comentario dudaba en pagar es exactamente el que el propio spec de UX/UI
// documenta como esperado en §8 para revelar el panorama. [DriverMatrix ya
// no se usa en esta pantalla desde el punto 4 de arriba, pero el componente
// sigue viviendo en components/ por si se reutiliza en otra pantalla.]
//
// Filtros de §3 ("solo atenúan filas, nunca recortan el conjunto, sin
// llamada nueva al API") NO se implementaron en esta entrega -- deferido a
// propósito, ver DevLog de esta fecha.
//
// 13-sep -- pase de fidelidad contra mockups/02_Panorama_Escuelas_Riesgo.png
// (Diana lo pidió en el chat como "P3", pero el propio mockup resalta "02
// Panorama de Riesgo" en su menú y su encabezado dice "02 PROTOCOLO..." --
// se implementa aquí, la pantalla real a la que pertenece ese diseño, no en
// LosSieteCasos.jsx/P3 Selección de Caso, que es un mockup totalmente
// distinto -- avisado a Diana en la respuesta del chat).
//
// 3 números del mockup necesitaron una decisión de dato real (mismo
// criterio de "nunca inventar un dato" de todo el proyecto, CLAUDE.md §4):
//   - "44,114 escuelas verificadas" SÍ tiene respaldo real: es el
//     "Universo del alcance" documentado en 02_Data_Visualization_Spec.md
//     línea 107 ("Page.total de /escuelas"). Las 3 tarjetas KPI de arriba
//     (punto 3) NO se tocaron en esta ronda -- siguen pidiendo getKpis()
//     y getUniversoEscuelas() aparte, como en el primer pase; lo único que
//     se consolidó (punto 6) fue la llamada de escuelas en riesgo que
//     alimenta la tabla/hallazgos/enclave.
//   - "-2.9 % delta neto": el campo real es kpis.variacion_matricula, que
//     hoy vale +1.61% en el mock/API -- no -2.9% (ese número del mockup
//     parece de un corte de datos anterior al que documenta el propio
//     spec). Se muestra siempre el valor REAL vigente de ese campo, nunca
//     el -2.9% fijo del mockup.
//   - "Convergencia urbana: 100% Metropolitano" NO tiene campo real
//     (EscuelaOut/MunicipioOut no traen urbano/rural -- confirmado en
//     src/api/schemas.py) -- se omite en vez de inventarlo. En su lugar el
//     panel de Enclave muestra la brecha de telemetría (S/D), que sí se
//     puede calcular de los propios datos de la matriz de drivers.
// "Hallazgos Algorítmicos Dominantes" y "Enclave Georreferenciado" se
// calculan en vivo del conjunto real de escuelas en riesgo (conteo de
// driver_dominante, entidad/municipio más representados) -- nunca son las
// escuelas/números fijos que aparecen en el mockup (Colegio Montreal,
// Naucalpan, etc.), que son solo el ejemplo de diseño.
export default function Panorama() {
  // Fuente de datos única (13-sep, punto 6 de arriba): antes esta pantalla
  // pedía getPanoramaEscuelas() para la tabla/hallazgos Y getConclusionEscuelas()
  // aparte solo para el nombre real de municipio del Enclave -- mismo
  // catálogo de escuelas pedido 2 veces, ya anotado como pendiente de
  // consolidar en el primer pase. getConclusionEscuelas ya incluye todo lo
  // que traía getPanoramaEscuelas (d1..d6 vía EscuelaDetalleOut) más
  // nombre_municipio real (getMunicipiosPorClaves) -- una sola llamada.
  const { status, data, error } = useApiResource(getConclusionEscuelas, { mock: panoramaMock });
  const esReal = status === "ok";
  const escuelas = status === "ok" || status === "demo" ? data : [];
  const n = escuelas.length;

  // Agregados del alcance completo (4 entidades), no solo de las escuelas en
  // riesgo -- 02_Data_Visualization_Spec.md fila "P2 -- Panorama" pide
  // variacion_matricula e indice_completitud_drivers de KpisOut. Llamada
  // independiente de la de arriba -- si falla, la pantalla sigue mostrando
  // el resto (no bloquea el panorama por un agregado adicional). Sin
  // cambios en esta ronda (punto 3: las 3 tarjetas KPI se quedan igual).
  const { status: kpisStatus, data: kpisData } = useApiResource(getKpis, {
    mock: kpisMockParaComparacion2Ciclos,
  });
  const kpis = kpisStatus === "ok" || kpisStatus === "demo" ? kpisData : null;

  // "Universo del alcance": el total de escuelas del catálogo completo
  // (Page.total de /escuelas), no las N en riesgo. Llamada independiente y
  // liviana (size=1) -- si falla, la tarjeta 1 solo se queda sin ese dato.
  const { status: universoStatus, data: universoData } = useApiResource(getUniversoEscuelas, {
    mock: universoEscuelasMock,
  });
  const universoTotal = universoStatus === "ok" || universoStatus === "demo" ? universoData?.total : null;

  // cveEnt de cada escuela: en modo real, primeros 2 dígitos de cve_mun
  // (INEGI: entidad + municipio) -- mismo criterio que MunicipioOut.cve_ent.
  // En modo demo el mock no trae cve_mun (solo el nombre de la entidad como
  // texto): se resuelve el cveEnt buscando ese nombre en ENTIDADES_LABEL.
  const cveEntDeEscuela = (e) => {
    if (typeof e.cve_mun === "string") return e.cve_mun.slice(0, 2);
    const porNombre = ENTIDADES_LABEL.find(
      (ent) => ent.nombre.toLowerCase() === (e.entidad ?? "").toLowerCase()
    );
    return porNombre ? porNombre.cveEnt : null;
  };

  // Municipio + entidad real de una escuela, para la columna "Escuela y
  // contexto" de la tabla de drivers (punto 4) -- mismo patrón que ya usa
  // LosSieteCasos.jsx.
  const lugarDeEscuela = (e) => {
    const cveEnt = cveEntDeEscuela(e);
    const nombreEnt = cveEnt ? ENTIDADES_LABEL.find((ent) => ent.cveEnt === cveEnt)?.nombre ?? null : null;
    const municipio = esReal ? e.nombre_municipio ?? null : e.municipio ?? null;
    return [municipio, nombreEnt].filter(Boolean).join(", ");
  };

  const matrizData = escuelas.map((e) => ({
    cct: e.cct,
    nombre: e.nombre,
    nivel: e.nivel,
    lugar: lugarDeEscuela(e),
    cveEnt: cveEntDeEscuela(e),
    latitud: e.latitud,
    longitud: e.longitud,
    drivers: { D1: e.d1, D2: e.d2, D3: e.d3, D4: e.d4, D5: e.d5, D6: e.d6 },
    // Driver dominante ya resuelto por el backend/mock -- se usa para
    // dibujar el contorno ámbar (03_Visual_Identity.md S3) en la tabla.
    dominante: e.driver_dominante,
  }));

  // "Hallazgos Algorítmicos Dominantes" (13-sep): top 2 drivers por
  // frecuencia de driver_dominante en el conjunto real de escuelas en
  // riesgo -- mismo cálculo que ya usa Conclusion.jsx para su Top 3, aquí
  // recortado a 2 para calzar con el panel del mockup. El rango de valores
  // y los nombres de escuela salen del propio conjunto, nunca son los que
  // trae el mockup de ejemplo (Colegio Montreal, etc.).
  const conteoPorDriver = {};
  const valoresPorDriver = {};
  for (const e of escuelas) {
    if (!e.driver_dominante) continue;
    conteoPorDriver[e.driver_dominante] = (conteoPorDriver[e.driver_dominante] ?? 0) + 1;
    const valor = e[e.driver_dominante.toLowerCase()];
    if (typeof valor === "number") {
      (valoresPorDriver[e.driver_dominante] ??= []).push(valor);
    }
  }
  const hallazgosTop = Object.entries(conteoPorDriver)
    .map(([code, count]) => {
      const valores = valoresPorDriver[code] ?? [];
      const nombresEscuelas = escuelas.filter((e) => e.driver_dominante === code).map((e) => e.nombre);
      return {
        code,
        count,
        min: valores.length ? Math.min(...valores) : null,
        max: valores.length ? Math.max(...valores) : null,
        nombresEscuelas,
      };
    })
    .sort((a, b) => b.count - a.count)
    .slice(0, 2);

  // "Enclave Georreferenciado" (13-sep): entidad con más escuelas en riesgo
  // del conjunto real, y desglose por municipio dentro de esa entidad
  // (nombre real vía getConclusionEscuelas, mismo patrón que "Concentración
  // por municipio" de Conclusion.jsx). "Brecha de telemetría (S/D)":
  // cuántos de los 6 drivers tienen al menos un hueco SIN_DATO entre las
  // escuelas de esa entidad -- cálculo real sobre matrizData, no un
  // porcentaje inventado.
  const conteoPorEntidad = {};
  for (const d of matrizData) {
    if (!d.cveEnt) continue;
    conteoPorEntidad[d.cveEnt] = (conteoPorEntidad[d.cveEnt] ?? 0) + 1;
  }
  const cveEntTop = Object.entries(conteoPorEntidad).sort((a, b) => b[1] - a[1])[0]?.[0] ?? null;
  const entidadTop = cveEntTop ? ENTIDADES_LABEL.find((e) => e.cveEnt === cveEntTop) : null;

  const cctsEnEntidadTop = new Set(matrizData.filter((d) => d.cveEnt === cveEntTop).map((d) => d.cct));
  const porMunicipioEnEntidadTop = {};
  for (const e of escuelas) {
    if (!cctsEnEntidadTop.has(e.cct)) continue;
    const clave = esReal ? e.cve_mun : e.municipio;
    const etiqueta = esReal ? e.nombre_municipio : e.municipio;
    if (!clave || !etiqueta) continue;
    porMunicipioEnEntidadTop[clave] = (porMunicipioEnEntidadTop[clave] ?? { etiqueta, count: 0 });
    porMunicipioEnEntidadTop[clave].count += 1;
  }
  const municipiosTop = Object.values(porMunicipioEnEntidadTop)
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);

  const driversConHueco = DRIVERS_ORDEN.filter((code) =>
    matrizData.some((d) => d.cveEnt === cveEntTop && d.drivers[code] == null)
  );
  const celdasEntidadTop = matrizData.filter((d) => d.cveEnt === cveEntTop);
  const totalCeldas = celdasEntidadTop.length * DRIVERS_ORDEN.length;
  const celdasSinDato = celdasEntidadTop.reduce(
    (acc, d) => acc + DRIVERS_ORDEN.filter((code) => d.drivers[code] == null).length,
    0
  );
  const brechaPct = totalCeldas > 0 ? (celdasSinDato / totalCeldas) * 100 : null;

  // Puntos reales (lat/lon de EscuelaOut) de las escuelas de la entidad top,
  // para dibujar sobre su silueta real (punto 5) -- nunca coordenadas
  // inventadas.
  const puntosEntidadTop = matrizData
    .filter((d) => d.cveEnt === cveEntTop && typeof d.latitud === "number" && typeof d.longitud === "number")
    .map((d) => ({ lat: d.latitud, lon: d.longitud, etiqueta: d.nombre }));

  return (
    <PageContainer>
      {/* ---- Barra de protocolo + tarjetas KPI ---- */}
      {(status === "ok" || status === "demo") && (
        <div className="flex flex-col gap-4">
          <div
            className="rounded-xl px-4 py-3 flex items-center justify-between flex-wrap gap-3"
            style={{ background: "var(--faro-canvas-container)", border: "1px solid var(--faro-hairline)" }}
          >
            <div className="flex items-center gap-3 flex-wrap">
              <span
                className="text-label-micro-mono font-semibold px-2 py-1 rounded"
                style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
              >
                02
              </span>
              <span className="text-label-data-mono" style={{ color: "var(--color-ink)" }}>
                PROTOCOLO DE VIGILANCIA TERRITORIAL <span style={{ color: "var(--faro-context-gray)" }}>/</span>{" "}
                <span style={{ color: "var(--faro-signal)" }}>MATRIZ_RIESGO_OPERATIVA</span>
              </span>
            </div>
            <div className="flex items-center gap-3">
              {status === "demo" && <DemoBadge />}
              <span className="text-label-micro-mono inline-flex items-center gap-1.5" style={{ color: "var(--faro-signal)" }}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
                ESTADO: AUDITORÍA ACTIVA
              </span>
            </div>
          </div>

          <span
            className="text-label-micro-mono uppercase inline-flex items-center gap-1.5 self-start px-2 py-1 rounded"
            style={{ background: "var(--faro-canvas-container)", color: "var(--faro-context-gray)" }}
          >
            Diagnóstico federativo // Reporte de exclusión
          </span>

          <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-headline-xl" style={{ color: "var(--color-ink)" }}>
                Las {n} {n === 1 ? "escuela" : "escuelas"} frente a los 6 drivers
              </h2>
              <p className="text-body-md mt-1" style={{ color: "var(--color-ink-faint)" }}>
                Todas cruzan el umbral de riesgo, pero el factor que destaca es distinto en cada caso.
              </p>
            </div>
            <Link
              to="/casos"
              className="inline-flex items-center gap-1.5 text-body-sm font-semibold px-4 py-2.5 shrink-0"
              style={{ background: "var(--color-primary)", color: "#ffffff", borderRadius: "var(--faro-radius-lg)" }}
            >
              Proceder a selección de caso
              <IconArrowForward size={16} />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <TarjetaKpiSeveridad
              numero="1"
              titulo="Matrícula total del alcance (4 entidades)"
              valor={kpis ? kpis.matricula_total.toLocaleString("es-MX") : "—"}
              detalle={`alumnos en ${universoTotal != null ? universoTotal.toLocaleString("es-MX") : "…"} escuelas verificadas`}
              tag="Cobertura: CDMX, Edomex, NL, Jal"
            />
            <TarjetaKpiSeveridad
              numero="2"
              titulo="Variación interanual"
              valor={kpis && typeof kpis.variacion_matricula === "number" ? `${(kpis.variacion_matricula * 100).toFixed(1)} %` : "—"}
              valorSufijo="delta neto"
              detalle={
                kpis && typeof kpis.variacion_matricula === "number"
                  ? kpis.variacion_matricula < 0
                    ? "contracción de matrícula respecto al ciclo previo"
                    : "crecimiento de matrícula respecto al ciclo previo"
                  : "variación de matrícula respecto al ciclo previo"
              }
              tag="Deserción estructural persistente"
            />
            <TarjetaKpiSeveridad
              numero="3"
              titulo="Completitud promedio de drivers"
              valor={kpis && typeof kpis.indice_completitud_drivers === "number" ? (kpis.indice_completitud_drivers * 6).toFixed(1) : "—"}
              valorSufijo="/ 6 drivers auditables"
              detalle="densidad de telemetría por nodo escolar"
              tag={
                kpis && typeof kpis.indice_completitud_drivers === "number"
                  ? `Confianza del vector ${(kpis.indice_completitud_drivers * 100).toFixed(1)}% efectiva`
                  : undefined
              }
            />
          </div>
        </div>
      )}

      {status === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando el panorama…</p>
      )}
      {status === "error" && (
        // Literal del spec (§2, "Pantalla 2", Estados): sin detalle interno,
        // a diferencia de otras pantallas que sí muestran el error crudo.
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No pudimos cargar el panorama, intenta de nuevo.
        </p>
      )}

      {(status === "ok" || status === "demo") && (
        <>
          <Card
            title="Comparativa de los 6 drivers"
            subtitle="Cada fila es una escuela; cada columna, una de las 6 líneas de evidencia. Claro = menos presión, oscuro = más."
          >
            <TablaDrivers data={matrizData} />
            {/* 13-sep, tercera ronda -- pedido explícito de Diana: quita el bloque de 4
                declaraciones (Qué se ve/Unidad/Sin dato/Ciclo y recorte) que
                02_Data_Visualization_Spec.md §7.bis.2 pedía aquí ("P2 · Matriz de casos") y
                pone en su lugar la misma "Escala de severidad" que ya usan las 3 tarjetas KPI
                de arriba (EscalaSeveridad, definida más abajo) -- mismo criterio de color
                (riskRampColor) y mismas 2 declaraciones fijas (driver dominante / sin dato),
                nada inventado, solo se deja de repetir el formato largo de LeyendaGrafica en
                esta tabla en particular. */}
            <div className="mt-3 pt-3" style={{ borderTop: "1px solid var(--faro-hairline)" }}>
              <EscalaSeveridad />
            </div>
            <p
              className="text-label-micro-mono uppercase mt-3 pt-3 flex items-center gap-2 flex-wrap"
              style={{ borderTop: "1px solid var(--faro-hairline)", color: "var(--faro-context-gray)" }}
            >
              Cohorte auditada: {n} plantel{n === 1 ? "" : "es"} prioritario{n === 1 ? "" : "s"}
              <span aria-hidden="true">·</span>
              Sensores pendientes de levantamiento físico: {DRIVERS_ORDEN.filter((code) => escuelas.every((e) => e[code.toLowerCase()] == null)).join(", ") || "ninguno"}
              <span className="inline-flex items-center gap-1.5 ml-auto" style={{ color: "var(--faro-signal)" }}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
                Estado: auditoría activa
              </span>
            </p>
          </Card>

          {/* ---- Hallazgos algorítmicos + enclave georreferenciado ---- */}
          {(hallazgosTop.length > 0 || entidadTop) && (
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4 items-start">
              <Card>
                <div className="flex items-center justify-between gap-2 flex-wrap mb-3">
                  <p className="text-title-md inline-flex items-center gap-2" style={{ color: "var(--color-ink)" }}>
                    <span className="inline-block w-2 h-2" style={{ background: "var(--faro-command-base)" }} aria-hidden="true" />
                    Hallazgos algorítmicos dominantes
                  </p>
                  {hallazgosTop.length > 0 && (
                    <span className="text-label-micro-mono uppercase" style={{ color: "var(--faro-context-gray)" }}>
                      Criterio: {hallazgosTop.map((h) => h.code).join(" / ")} polarizado
                    </span>
                  )}
                </div>
                {hallazgosTop.length === 0 ? (
                  <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>
                    Aún no hay suficientes escuelas con driver dominante para calcular un hallazgo.
                  </p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {hallazgosTop.map((h) => (
                      <div
                        key={h.code}
                        className="rounded-lg p-3"
                        style={{ background: "var(--faro-canvas-container)", border: `1px solid var(--faro-hairline)` }}
                      >
                        <div className="flex items-center justify-between gap-2 flex-wrap mb-1">
                          <span className="text-label-micro-mono uppercase font-semibold" style={{ color: DOMINANT_OUTLINE }}>
                            Dominancia {h.code} // {driverNombres[h.code]?.toUpperCase()}
                          </span>
                          <span className="text-label-micro-mono uppercase" style={{ color: "var(--faro-context-gray)" }}>
                            {h.count} de {n} escuelas
                          </span>
                        </div>
                        <p className="text-body-sm" style={{ color: "var(--color-ink)" }}>
                          {h.nombresEscuelas.join(", ")} {h.nombresEscuelas.length === 1 ? "muestra" : "muestran"} los valores más altos de {driverNombres[h.code]?.toLowerCase()}
                          {h.min != null && h.max != null ? ` (${h.min.toFixed(2)} – ${h.max.toFixed(2)})` : ""} como principal vector de riesgo.
                        </p>
                      </div>
                    ))}
                  </div>
                )}
                <p
                  className="text-label-micro-mono uppercase mt-3 pt-3 flex items-center justify-between flex-wrap gap-2"
                  style={{ borderTop: "1px solid var(--faro-hairline)", color: "var(--faro-context-gray)" }}
                >
                  <span>Faro engine // pesos territoriales calibrados</span>
                  <span style={{ color: "var(--faro-signal)" }}>Auditoría activa</span>
                </p>
              </Card>

              {entidadTop && (
                <Card>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <p className="text-label-micro-mono uppercase" style={{ color: "var(--faro-context-gray)" }}>
                      Enclave georreferenciado
                    </p>
                    <span className="text-label-data-mono font-semibold" style={{ color: entidadTop.color }}>
                      {entidadTop.nombre} ({entidadTop.cveEnt})
                    </span>
                  </div>

                  <div className="rounded-lg mb-3" style={{ background: "var(--faro-canvas-container)", border: "1px solid var(--faro-hairline)" }}>
                    <SiluetaEntidad
                      entidadId={entidadTop.id}
                      color={entidadTop.color}
                      puntos={puntosEntidadTop}
                      ariaLabel={`Silueta de ${entidadTop.nombre} con la ubicación real de las escuelas en riesgo de esa entidad`}
                    />
                  </div>

                  {municipiosTop.length > 0 && (
                    <div className="flex flex-col gap-1.5 mb-3">
                      {municipiosTop.map((m) => (
                        <div key={m.etiqueta} className="flex items-center justify-between text-body-sm">
                          <span style={{ color: "var(--color-ink)" }}>{m.etiqueta}</span>
                          <span className="text-label-micro-mono" style={{ color: "var(--faro-context-gray)" }}>{m.count} escuela{m.count === 1 ? "" : "s"}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="flex flex-col gap-2 pt-2" style={{ borderTop: "1px solid var(--faro-hairline)" }}>
                    <span className="text-label-micro-mono inline-flex items-center gap-1.5" style={{ color: "var(--color-ink-faint)" }}>
                      <IconHub size={14} style={{ color: "var(--faro-signal)" }} />
                      Escuelas en el enclave: {cctsEnEntidadTop.size} de {n}
                    </span>
                    {brechaPct != null && (
                      <span className="text-label-micro-mono inline-flex items-center gap-1.5" style={{ color: "var(--color-ink-faint)" }}>
                        <IconSecurityUpdateGood size={14} style={{ color: "var(--faro-signal)" }} />
                        Brecha de telemetría (S/D): {brechaPct.toFixed(1)}% ({driversConHueco.length}/6 drivers)
                      </span>
                    )}
                  </div>
                </Card>
              )}
            </div>
          )}
        </>
      )}
    </PageContainer>
  );
}

// Mini leyenda de escala de severidad (13-sep, fidelidad mockup 02): barra
// degradada 0.0-1.0 (mismos --faro-ramp-1..5 de index.css que ya usa
// TablaDrivers/riskRamp.js) + las 2 declaraciones fijas de "Driver
// dominante" / "Sin dato", repetida dentro de cada tarjeta KPI, igual que
// el mockup. useId() evita que las 3 instancias compartan un mismo id de
// <pattern> SVG.
function EscalaSeveridad() {
  const id = useId();
  const stripesId = `panoramaKpiStripes-${id}`;
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between text-label-micro-mono uppercase" style={{ color: "var(--faro-context-gray)" }}>
        <span>Escala de severidad:</span>
      </div>
      <div
        className="h-1.5 rounded-full"
        style={{
          background:
            "linear-gradient(90deg, var(--faro-ramp-1), var(--faro-ramp-2), var(--faro-ramp-3), var(--faro-ramp-4), var(--faro-ramp-5))",
        }}
        aria-hidden="true"
      />
      <div className="flex justify-between text-label-micro-mono" style={{ color: "var(--faro-context-gray)" }}>
        <span>0.0</span>
        <span>0.2</span>
        <span>0.4</span>
        <span>0.6</span>
        <span>0.8</span>
        <span>1.0</span>
      </div>
      <div className="flex flex-col gap-1 mt-1">
        <span className="inline-flex items-center gap-1.5 text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
          <span
            className="inline-flex items-center justify-center px-1 rounded text-[9px] font-bold"
            style={{ background: "var(--faro-ramp-2)", border: `2px solid ${DOMINANT_OUTLINE}`, color: "var(--faro-command-base)" }}
          >
            0.45
          </span>
          Driver dominante (contorno ámbar #B45309)
        </span>
        <span className="inline-flex items-center gap-1.5 text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
          <svg width="18" height="14" aria-hidden="true">
            <defs>
              <pattern id={stripesId} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                <rect width="6" height="6" fill="var(--color-sin-dato-bg)" />
                <line x1="0" y1="0" x2="0" y2="6" stroke="var(--color-sin-dato)" strokeWidth="2" />
              </pattern>
            </defs>
            <rect width="18" height="14" rx="3" fill={`url(#${stripesId})`} stroke="var(--color-border)" />
          </svg>
          Sin dato: pista no verificada, no es cero
        </span>
      </div>
    </div>
  );
}

// Tarjeta KPI (13-sep, fidelidad mockup 02): número + título, valor grande
// con sufijo opcional, detalle, escala de severidad y una etiqueta inferior
// opcional -- misma estructura que las 3 tarjetas del mockup.
function TarjetaKpiSeveridad({ numero, titulo, valor, valorSufijo, detalle, tag }) {
  return (
    <div className="rounded-xl p-4 flex flex-col gap-3" style={{ background: "var(--faro-canvas)", border: "1px solid var(--faro-hairline)" }}>
      <p className="text-label-micro-mono uppercase" style={{ color: "var(--faro-context-gray)" }}>
        {numero}. {titulo}
      </p>
      <div>
        <p className="text-headline-lg" style={{ color: "var(--color-ink)" }}>
          {valor}
          {valorSufijo && (
            <span className="text-title-md" style={{ color: "var(--faro-context-gray)" }}> {valorSufijo}</span>
          )}
        </p>
        <p className="text-body-sm mt-0.5" style={{ color: "var(--color-ink-faint)" }}>{detalle}</p>
      </div>
      <EscalaSeveridad />
      {tag && (
        <span
          className="text-label-micro-mono uppercase self-start px-2 py-1 rounded"
          style={{ background: "var(--faro-canvas-container)", color: "var(--faro-signal)", border: "1px solid var(--faro-hairline)" }}
        >
          {tag}
        </span>
      )}
    </div>
  );
}

// Encabezados cortos de columna (solo para esta tabla -- driverNombres, en
// data/mock.js, se queda con los nombres completos que usan las insignias
// y leyendas del resto del proyecto).
const DRIVER_HEADERS_CORTOS = {
  D1: "D1 Pobreza",
  D2: "D2 Inseguridad",
  D3: "D3 Infraestr.",
  D4: "D4 Conectiv.",
  D5: "D5 Agua",
  D6: "D6 Aire",
};

// Tabla de comparativa de los 6 drivers (13-sep, pedido explícito de Diana:
// reemplaza el heatmap D3 de DriverMatrix.jsx por una tabla real, "mismo
// formato" que su mockup de referencia). Fila por escuela, columna por
// driver; el color de cada celda sigue siendo la misma rampa monocromática
// de siempre (riskRampColor -- claro = menos presión, oscuro = más), nunca
// un color por driver, y el driver dominante de cada escuela lleva el
// mismo contorno ámbar (DOMINANT_OUTLINE) que ya usan DriverBars.jsx y
// LosSieteCasos.jsx -- mismos datos y mismo criterio de color que el
// heatmap que reemplaza, solo cambia la forma visual.
function TablaDrivers({ data }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse" style={{ minWidth: 640 }}>
        <thead>
          <tr style={{ borderBottom: "1px solid var(--faro-hairline)" }}>
            <th
              className="text-left text-label-micro-mono uppercase font-semibold py-2 pr-3"
              style={{ color: "var(--faro-context-gray)" }}
            >
              Escuela &amp; contexto
            </th>
            {DRIVERS_ORDEN.map((code) => (
              <th
                key={code}
                className="text-center text-label-micro-mono uppercase font-semibold py-2 px-2"
                style={{ color: "var(--faro-context-gray)" }}
              >
                {DRIVER_HEADERS_CORTOS[code]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((d) => (
            <tr key={d.cct} style={{ borderBottom: "1px solid var(--faro-hairline)" }}>
              <td className="py-2.5 pr-3 align-top">
                <p className="text-title-md" style={{ color: "var(--color-ink)" }}>{d.nombre}</p>
                <p className="text-label-micro-mono" style={{ color: "var(--faro-context-gray)" }}>
                  {d.lugar ? `${d.lugar} · ` : ""}
                  {d.nivel} · CCT {d.cct}
                </p>
              </td>
              {DRIVERS_ORDEN.map((code) => {
                const valor = d.drivers[code];
                const esDominante = code === d.dominante;
                const sinDato = valor == null;
                return (
                  <td key={code} className="text-center py-2.5 px-2">
                    <span
                      className="inline-flex items-center justify-center text-label-data-mono font-bold rounded"
                      style={{
                        width: 46,
                        height: 28,
                        background: sinDato
                          ? "repeating-linear-gradient(45deg, var(--color-sin-dato-bg), var(--color-sin-dato-bg) 4px, var(--color-border) 4px, var(--color-border) 8px)"
                          : riskRampColor(valor),
                        color: sinDato ? "var(--color-ink-faint)" : valor > 0.6 ? "#ffffff" : "#0f172a",
                        border: esDominante ? `2px solid ${DOMINANT_OUTLINE}` : "1px solid var(--color-border)",
                      }}
                      title={
                        sinDato
                          ? `${driverNombres[code]} · SIN_DATO`
                          : `${driverNombres[code]}: ${valor.toFixed(2)}${esDominante ? " · Driver dominante" : ""}`
                      }
                    >
                      {sinDato ? "S/D" : valor.toFixed(2)}
                    </span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
