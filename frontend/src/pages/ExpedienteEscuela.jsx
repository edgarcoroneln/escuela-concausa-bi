import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import {
  IconArrowBack,
  IconArrowForward,
  IconInfo,
  IconVerified,
  IconPsychology,
  IconHourglassEmpty,
  IconLock,
} from "../components/Icons.jsx";
import { escuelasEnRiesgo as escuelasMock, nivelRiesgo } from "../data/mock.js";
import { DOMINANT_OUTLINE } from "../lib/riskRamp.js";
import { getEscuela, getMunicipio, getPrediccion, getPrediccionExplicacion } from "../lib/api.js";
import SiluetaEntidad from "../components/SiluetaEntidad.jsx";
import { ENTIDADES_LABEL } from "../components/MapaEntidades.jsx";
import { useApiResource } from "../lib/useApiResource.js";
import { useCortesAtencion } from "../lib/cortesAtencion.js";
import { ORIENTADOS } from "../lib/driverOrientacion.js";

const DRIVERS = ["D1", "D2", "D3", "D4", "D5", "D6"];

// Barra de la Matriz de Presión Territorial con animación de relleno --
// mismo patrón que `Barra` en DriverBars.jsx (arranca en 0% y transita en
// CSS hasta su ancho real al montarse), pedido por Diana también aquí en
// la P4. No se reutiliza el componente de DriverBars.jsx directamente
// porque esa fila tiene su propio layout (label de 11rem + código + %) que
// no calza con el de esta matriz (título largo, badge de dominante, texto
// de motivo/fuente debajo) -- se replica solo la animación, no la fila
// completa.
function BarraDriver({ valor, color }) {
  const [ancho, setAncho] = useState(0);
  const anchoFinal = Math.max(valor * 100, 1.5);

  useEffect(() => {
    const id = requestAnimationFrame(() => setAncho(anchoFinal));
    return () => cancelAnimationFrame(id);
  }, [anchoFinal]);

  return (
    <div
      className="h-full rounded"
      style={{
        width: `${ancho}%`,
        background: color,
        transition: "width 650ms cubic-bezier(0.4, 0, 0.2, 1)",
      }}
    />
  );
}

// Pantalla 4 -- Expediente de Escuela. REESCRITURA COMPLETA 13-sep contra
// mockups/04_Expediente_Escuela.png + .html, a pedido EXPLÍCITO de Diana de
// fidelidad 100%: "no hay manera que haya en esa pantalla otra cosa que no
// esté en la plantilla P4... todo, todo elemento que está en la plantilla
// de mockups debe estar en esa hoja... desde la tipografía, colores, hasta
// recuadros, iconos, mapas y títulos." A diferencia de las Pantallas 2 y 3
// (donde Diana pidió QUITAR iconos), aquí pidió explícitamente lo contrario
// -- iconos incluidos -- así que este archivo sí los lleva.
//
// El archivo anterior era un diseño de pestañas (Resumen/Drivers/
// Comparación/Predicción/Recomendación) que no tiene nada que ver con el
// mockup real: la Pantalla 4 es UNA sola vista, sin pestañas, con la matriz
// de los 6 drivers siempre visible + protocolo de intervención + panel de
// explicación algorítmica (SHAP) + ficha operativa (mapa) + registro de
// auditoría. Se reescribe entero para seguir esa estructura.
//
// Verificado elemento por elemento contra src/api/schemas.py y
// vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec.md
// (§4, la sección que describe ESTA pantalla), con 3 tipos de resultado:
//
//   A) Coincide con un campo/regla real -- se usa tal cual, en vivo:
//      - Sostenimiento (`EscuelaDetalleOut.sostenimiento`), matrícula
//        (`matricula_total`), lat/lon, índice de riesgo, driver_dominante,
//        d1..d6, `indice_completitud_drivers` ("medidor de evidencia").
//      - `recomendacion` de `GET /predicciones/{cct}` -- el spec (§5.1.7)
//        dice que es texto FIJO por driver
//        (`src/modelos/recomendaciones.py`); se verificó ahí que la frase
//        de D2 del mockup ("Coordinar con seguridad pública rutas
//        escolares seguras y entornos protegidos.") es LITERAL, no
//        inventada por Stitch.
//      - Los 6 "motivos" de SIN_DATO (D1/D2 "sin dato para su municipio",
//        D3/D4 "sin registro en el censo CEMABE", D5 "aún no hay fuente de
//        estrés hídrico integrada", D6 "no hay estación de calidad del
//        aire a 15 km o menos") son copy OFICIAL del spec §4.3, no relleno
//        de Stitch -- se usan literales.
//      - "Explicación Algorítmica" SIN_DATO: la frase "La explicación del
//        modelo para esta escuela aún no está disponible (SIN_DATO)" es
//        también copy oficial del spec §4.4.
//      - D3/D4 se "orientan" (`1 - valor`) para la gráfica, igual que hace
//        el propio pipeline para elegir el dominante (`features_escuela.
//        sql:385-410`, spec §4.1.1): el valor publicado se conserva como
//        "Servicios presentes: X.XX" (spec, no Stitch).
//      - D1/D2 llevan la nota "Valor municipal" en vez del texto de Stitch
//        ("Indicador en decil bajo...", "Mayor vector de exposición...")
//        porque el spec (§4.1.3) exige esa nota exacta: esos 2 drivers son
//        del municipio, compartidos por todas sus escuelas.
//      - Todas las barras NO dominantes usan el MISMO tono neutro (spec
//        §4.2: "el color no codifica identidad de driver... el único
//        acento es el dominante") -- el mockup pinta D4 con un acento azul
//        que contradice esa regla (barra de 2px, posiblemente un residuo
//        de Stitch); se corrige a neutro, la regla del spec gana.
//
//   B) El mockup afirma algo que el propio spec contradice -- se corrige,
//      documentado aquí:
//      - FUENTE de D2: el mockup dice "SESNSP / RADIOS URBANOS"; el spec
//        (§4.1) dice "SESNSP ÷ CONAPO" -- se usa la fuente real.
//      - FUENTE de D4: el mockup dice "CENSOS IFT / CFE TELECOM"; el spec
//        dice que D3 y D4 vienen de CEMABE 2013 -- se corrige a "CEMABE
//        2013".
//      - "0.30 es una escuela que conserva su matrícula": no está en el
//        contrato (`CortesAtencionOut` no define qué significa 0.30 en
//        matrícula) -- se omite esa frase puntual y se deja solo lo que sí
//        está documentado: el ancla de calibración (`ancla_calibracion`)
//        SÍ tiene semántica real ("en ese valor, pierde 5% de matrícula",
//        docstring del schema) y los 3 cortes de nivel de atención, todos
//        leídos en vivo de `/version` -- nunca 0.50/0.30/0.60 tecleados
//        (eso ya causó BUG-058 antes en este proyecto).
//      - "Estado de producción... Requiere umbral mínimo de 4 de 6 drivers
//        activos": no existe tal regla documentada en ningún lado -- la
//        razón REAL de que no haya explicación (spec §4.4) es que las
//        columnas `shap_d1..shap_d6` de Gold simplemente no están pobladas
//        todavía (Equipo 4, US-631), sin relación con cuántos drivers
//        tenga esta escuela en particular. Se usa la razón real.
//      - "Contribuciones computadas: 0 de 42": ese "42" es un agregado de
//        LAS 7 escuelas × 6 drivers (una foto del proyecto completo al
//        momento del spec), pero esta pantalla solo tiene los datos de
//        UNA escuela vía `getPrediccionExplicacion(cct)` -- mostrar "42"
//        aquí afirmaría que esta llamada trajo 42 valores cuando trae 6.
//        Se muestra "X de 6", calculado en vivo de la escuela activa.
//      - "HASH: 8F2A-Mixcoac" (el PNG, no el HTML -- manda el PNG en
//        contenido, regla del proyecto): no hay un hash de expediente en
//        el contrato, pero si hay predicción sí hay un identificador real
//        equivalente -- `PrediccionOut.mlflow_run_id` -- se usa ese.
//
//   C) No existe ningún campo real ni equivalente -- se omite en vez de
//      inventarlo (CLAUDE.md §4):
//      - "Turno: Matutino" y "Zona Escolar: 042 / Sector V": ningún modelo
//        del contrato trae turno ni zona/sector escolar.
//      - "Docentes Asignados: 5 Plantilla": no existe conteo de personal
//        docente en ningún endpoint -- se sustituye esa celda de la Ficha
//        Operativa por "Variación vs. ciclo anterior"
//        (`variacion_matricula_alumnos`, SÍ real) para no dejar la
//        cuadrícula 2x2 con un hueco.
//      - "COMPETENCIA: SEGURIDAD MUNICIPAL · VINCULACIÓN EDUCATIVA" y
//        "PLAZO DE ATENCIÓN: INMEDIATO (30 DÍAS)" bajo la recomendación:
//        ninguna asignación de jurisdicción ni plazo institucional existe
//        en `recomendaciones.py` ni en ningún otro lado -- afirmar un
//        plazo legal/administrativo inventado es justo el tipo de dato
//        que este proyecto nunca fabrica. Se omite la fila completa.
//      - "Radio de Vigilancia: 1,500m" y "GEO_LOCK"-style: a diferencia de
//        los 2 anteriores, esto SÍ se conserva -- es una etiqueta de
//        sistema fija y universal (mismo criterio ya aplicado en
//        LosSieteCasos.jsx con "PERÍMETRO 250M"), no una medición
//        específica de esta escuela.
//      - La frase fija del spec "El driver dominante es el factor que más
//        destaca... no es la causa" (§4.2) y el "contexto territorial"
//        bajo D1 (§4.2, pobreza_pct del municipio) SÍ son requisitos
//        reales del spec, pero NO aparecen en el mockup -- se omiten aquí
//        por instrucción explícita de Diana de no agregar nada que la
//        plantilla no tenga; queda anotado por si se retoma como mejora.
//
// El dock flotante "Asistente FARO" del mockup NO se reconstruye aquí: ya
// existe como componente real montado una sola vez en App.jsx
// (components/AsistenteFaro.jsx) -- duplicarlo por pantalla lo
// desincronizaría del chat real.
export default function ExpedienteEscuela() {
  const { cct } = useParams();
  const escuelaMockRef = escuelasMock.find((e) => e.cct === cct) ?? null;

  const { status, data, error } = useApiResource(() => getEscuela(cct), {
    mock: escuelaMockRef,
    deps: [cct],
  });
  const { status: cortesStatus, cortes, error: cortesError } = useCortesAtencion();
  const esReal = status === "ok";
  const escuela = status === "ok" || status === "demo" ? data : null;

  const tienePrediccion = escuela?.tiene_prediccion ?? false;
  const prediccionMock = escuelaMockRef
    ? {
        cct: escuelaMockRef.cct,
        id_ciclo: "demo",
        indice_riesgo: escuelaMockRef.indice_riesgo,
        driver_dominante: escuelaMockRef.driver_dominante,
        cluster: null,
        recomendacion: "Recomendación de ejemplo -- dato de muestra, no proviene del modelo real.",
        mlflow_run_id: "demo-run-0001",
      }
    : null;
  const { data: prediccion } = useApiResource(
    () => (tienePrediccion ? getPrediccion(cct) : Promise.resolve({ data: null, error: null })),
    { mock: prediccionMock, deps: [cct, tienePrediccion] }
  );

  const explicacionMock = escuelaMockRef
    ? {
        cct: escuelaMockRef.cct,
        driver_dominante: escuelaMockRef.driver_dominante,
        contribuciones: { D1: null, D2: null, D3: null, D4: null, D5: null, D6: null },
      }
    : null;
  const { data: explicacion } = useApiResource(
    () => (tienePrediccion ? getPrediccionExplicacion(cct) : Promise.resolve({ data: null, error: null })),
    { mock: explicacionMock, deps: [cct, tienePrediccion] }
  );

  const municipioMock = escuelaMockRef
    ? {
        cve_mun: "demo",
        nombre_municipio: escuelaMockRef.municipio,
        cve_ent: null,
        nombre_entidad: escuelaMockRef.entidad,
        poblacion: null,
        indice_rezago_social: null,
        pobreza_pct: null,
      }
    : null;
  const { data: municipioData } = useApiResource(
    () => (esReal && escuela?.cve_mun ? getMunicipio(escuela.cve_mun) : Promise.resolve({ data: null, error: null })),
    { mock: municipioMock, deps: [esReal, escuela?.cve_mun] }
  );

  const cardStyle = { background: "var(--color-surface)", borderRadius: "var(--radius-card)", boxShadow: "var(--shadow-card-hover)" };

  if (status === "loading" || cortesStatus === "loading") {
    return (
      <PageContainer>
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando expediente…</p>
      </PageContainer>
    );
  }

  if (status === "error" || !escuela) {
    return (
      <PageContainer>
        <div className="p-5" style={cardStyle}>
          <p className="text-sm mb-3" style={{ color: "var(--color-ink-faint)" }}>
            {status === "error" ? `No se pudo cargar el CCT ${cct} (${error}).` : `No hay datos para el CCT ${cct}.`}
          </p>
          <Link to="/casos" className="text-sm font-semibold" style={{ color: "var(--faro-signal)" }}>
            ← Volver a los casos
          </Link>
        </div>
      </PageContainer>
    );
  }

  if (!cortes) {
    return (
      <PageContainer>
        <div className="p-5" style={cardStyle}>
          <p className="text-sm mb-3" style={{ color: "var(--color-ink-faint)" }}>
            No fue posible cargar los cortes de atención desde /version{cortesStatus === "error" && cortesError ? ` (${cortesError})` : ""}. Intenta de nuevo más tarde.
          </p>
          <Link to="/casos" className="text-sm font-semibold" style={{ color: "var(--faro-signal)" }}>
            ← Volver a los casos
          </Link>
        </div>
      </PageContainer>
    );
  }

  const riesgo = nivelRiesgo(escuela.indice_riesgo, cortes);
  const municipio = municipioData?.nombre_municipio ?? null;
  const entidad = municipioData?.nombre_entidad ?? null;
  const cveEnt = municipioData?.cve_ent ?? null;
  const lugar = [municipio, entidad].filter(Boolean).join(", ");
  const entidadAbrev = entidad ? entidad.toUpperCase().replace(/\s+/g, "_") : null;
  // FIX (2026-09-13, pedido de Diana -- "arreglar el mapa sin quitarlo"): cveEnt
  // (codigo INEGI real, ya resuelto arriba desde MunicipioOut) contra el mismo
  // catalogo de las 4 entidades del alcance (ENTIDADES_LABEL, MapaEntidades.jsx)
  // que ya usan Panorama.jsx/Login.jsx -- da el id ("MX-MEX") y el color de marca
  // que pide SiluetaEntidad.jsx, sin inventar ningun catalogo nuevo.
  // Fallback por nombre cuando no hay cveEnt (modo demo: municipioMock fija
  // cve_ent: null a propósito, ver ExpedienteEscuela.jsx arriba) -- mismo
  // criterio que cveEntDeEscuela() en LosSieteCasos.jsx, para que el mapa
  // también aparezca en modo demo, no solo con la API real.
  const entidadInfo = cveEnt
    ? ENTIDADES_LABEL.find((e) => e.cveEnt === cveEnt) ?? null
    : entidad
    ? ENTIDADES_LABEL.find((e) => e.nombre.toLowerCase() === entidad.toLowerCase()) ?? null
    : null;

  // Metadatos reales por driver -- ver comentario largo de arriba (fuente,
  // motivo y "orientación" verificados contra el spec, no copiados del
  // mockup a ciegas).
  // FIX (2026-09-13, US-651): "orientado" ya no se tecléa por driver aquí --
  // se deriva de ORIENTADOS (lib/driverOrientacion.js), única definición
  // compartida con Panorama/Conclusion/LosSieteCasos/Explorador.
  const DRIVER_META = {
    D1: { titulo: "Pobreza y rezago social", fuente: "CONEVAL / INEGI", motivo: "sin dato para su municipio", grano: "municipio" },
    D2: { titulo: "Inseguridad en el entorno escolar", fuente: "SESNSP / CONAPO", motivo: "sin dato para su municipio", grano: "municipio" },
    // FIX (2026-09-13, US-651, obs. 11, Marina García + su IA): "CEMABE 2013" pasa a
    // "CEMABE -- censo 2013" para que la antigüedad se lea sin tener que buscarla --
    // D4 es uno de los drivers dominantes de toda la conclusión y viene de un censo de
    // hace más de una década, no de datos por ciclo escolar.
    D3: { titulo: "Infraestructura y servicios básicos", fuente: "CEMABE — censo 2013", motivo: "sin registro en el censo CEMABE", grano: "escuela" },
    D4: { titulo: "Conectividad digital y equipamiento", fuente: "CEMABE — censo 2013", motivo: "sin registro en el censo CEMABE", grano: "escuela" },
    D5: { titulo: "Estrés hídrico", fuente: null, motivo: "aún no hay fuente de estrés hídrico integrada", grano: "escuela" },
    D6: { titulo: "Calidad del aire", fuente: "SINAICA", motivo: "no hay estación de calidad del aire a 15 km o menos", grano: "escuela" },
  };

  const filasDrivers = DRIVERS.map((code) => {
    const meta = DRIVER_META[code];
    const orientado = ORIENTADOS.includes(code);
    const raw = escuela[code.toLowerCase()];
    const sinDato = raw === null || raw === undefined;
    const valorMostrado = !sinDato && orientado ? 1 - raw : raw;
    const esDominante = escuela.driver_dominante === code;
    return { code, meta: { ...meta, orientado }, raw, sinDato, valorMostrado, esDominante };
  });

  const completitud = escuela.indice_completitud_drivers;
  const k = completitud != null ? Math.round(completitud * 6) : filasDrivers.filter((f) => !f.sinDato).length;
  const pct = completitud != null ? Math.round(completitud * 100) : Math.round((k / 6) * 100);

  const contribuciones = explicacion?.contribuciones ?? null;
  const contribucionesConValor = contribuciones ? Object.values(contribuciones).filter((v) => v != null).length : 0;
  const hayContribuciones = contribucionesConValor > 0;

  return (
    <PageContainer>
      {/* ---- Barra de acciones ---- */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3 flex-wrap">
          <Link
            to="/casos"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded font-semibold text-label-data-mono"
            style={{ background: "var(--faro-canvas-container)", color: "var(--color-ink)" }}
          >
            <IconArrowBack size={16} />
            Volver a Selección de Caso
          </Link>
          <span className="text-label-micro-mono uppercase" style={{ color: "var(--color-ink-faint)" }}>
            EXPEDIENTE DIAGNÓSTICO // REF-{escuela.cct}
          </span>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <span
            className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-label-micro-mono font-medium"
            style={{ background: "var(--faro-canvas-container)", color: "var(--color-ink-faint)" }}
          >
            <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
            SESIÓN_ACTIVA: AUDITORÍA_TERRITORIAL
          </span>
          {status === "demo" && <DemoBadge />}
          <Link
            to="/conclusion"
            className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded font-semibold text-label-data-mono shadow-sm"
            style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
          >
            Continuar a Conclusión Global
            <IconArrowForward size={16} />
          </Link>
        </div>
      </div>

      {/* ---- Encabezado del expediente: identidad + índice + medidor de evidencia ---- */}
      <div className="p-5 flex flex-col gap-4" style={cardStyle}>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex flex-col gap-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
              <span
                className="px-2 py-0.5 rounded uppercase font-semibold"
                style={{ background: "var(--faro-canvas-container)", color: "var(--faro-signal)" }}
              >
                CCT {escuela.cct}
              </span>
              {lugar && (
                <>
                  <span>·</span>
                  <span className="text-label-data-mono">{lugar}</span>
                </>
              )}
              <span>·</span>
              <span>{escuela.nivel}</span>
            </div>
            <h1 className="text-headline-xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>
              Plantel {escuela.nombre}
            </h1>
            {escuela.sostenimiento && (
              <p className="text-body-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>
                Sostenimiento: <strong style={{ color: "var(--color-ink)" }}>{escuela.sostenimiento}</strong>
              </p>
            )}
          </div>

          <div className="flex items-stretch gap-4 p-4 rounded-lg flex-wrap" style={{ background: "var(--faro-canvas-container)" }}>
            <div className="flex flex-col justify-between pr-4 min-w-0">
              <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--color-ink-faint)" }}>
                Índice de riesgo oficial
              </span>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-label-data-mono font-bold" style={{ fontSize: 36, lineHeight: 1, color: "var(--color-ink)" }}>
                  {escuela.indice_riesgo.toFixed(3)}
                </span>
                <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>/ 1.000</span>
              </div>
              <span
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-label-micro-mono font-bold uppercase mt-1 self-start"
                style={{ background: "var(--color-surface)", color: "var(--color-ink)" }}
              >
                {riesgo.icon} {riesgo.label}
              </span>
            </div>
            {/* Divisor oculto en pantallas angostas: si los dos bloques se
                envuelven a renglones distintos (flex-wrap de arriba), una
                línea vertical entre ellos no tiene sentido visual. */}
            <div className="hidden sm:block" style={{ width: 1, background: "var(--color-border)" }} aria-hidden="true" />
            <div className="flex flex-col justify-between pl-1 flex-1" style={{ minWidth: "10rem" }}>
              <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--color-ink-faint)" }}>
                Medidor de evidencia
              </span>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-title-md font-semibold" style={{ color: "var(--color-ink)" }}>{k} de 6 pistas</span>
                <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>({pct}%)</span>
              </div>
              <div className="grid grid-cols-6 gap-1 mt-1" style={{ height: 8 }}>
                {filasDrivers.map((f) => (
                  <div
                    key={f.code}
                    title={`${f.code}: ${f.sinDato ? "sin dato" : "activo"}`}
                    className="h-full rounded-sm"
                    style={{
                      background: f.sinDato
                        ? "repeating-linear-gradient(45deg, var(--color-sin-dato-bg), var(--color-sin-dato-bg) 2px, var(--color-border) 2px, var(--color-border) 4px)"
                        : "var(--faro-signal)",
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="p-3 rounded-lg flex items-start gap-2" style={{ background: "var(--faro-canvas-container)" }}>
          <IconInfo size={18} style={{ color: "var(--faro-signal)" }} />
          <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>
            <strong style={{ color: "var(--color-ink)" }}>Nota metodológica del índice:</strong> en {cortes.ancla_calibracion.toFixed(2)}, el modelo
            proyecta que la escuela perdería 5% de su matrícula (ancla de calibración). Nivel de atención: alta desde{" "}
            {cortes.alta.toFixed(2)} (línea de alerta), media desde {cortes.media.toFixed(2)}, baja por debajo.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* ---- Columna izquierda: matriz de drivers + protocolo de intervención ---- */}
        <div className="lg:col-span-8 flex flex-col gap-5">
          <div className="p-5 flex flex-col gap-4" style={cardStyle}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h2 className="text-headline-sm" style={{ color: "var(--color-ink)" }}>Matriz de Presión Territorial (Drivers D1 – D6)</h2>
                <p className="text-label-micro-mono uppercase mt-0.5" style={{ color: "var(--color-ink-faint)" }}>
                  0 = menor observada · 1 = mayor observada
                </p>
              </div>
              <span
                className="text-label-micro-mono font-semibold px-2 py-0.5 rounded self-start"
                style={{ background: "var(--faro-canvas-container)", color: "var(--faro-signal)" }}
              >
                EVALUACIÓN MULTI-FUENTE
              </span>
            </div>

            <div className="flex flex-col gap-3">
              {filasDrivers.map((f) => (
                <div
                  key={f.code}
                  className="p-3 rounded-lg flex flex-col gap-2 relative overflow-hidden"
                  style={{
                    background: f.esDominante ? "var(--color-surface)" : "var(--faro-canvas-container)",
                    boxShadow: f.esDominante ? "var(--shadow-card-hover)" : "none",
                    border: f.esDominante ? `1px solid ${DOMINANT_OUTLINE}55` : "1px solid transparent",
                  }}
                >
                  {f.esDominante && (
                    <div className="absolute left-0 top-0 bottom-0" style={{ width: 5, background: DOMINANT_OUTLINE }} aria-hidden="true" />
                  )}
                  <div className="flex items-center justify-between flex-wrap gap-2" style={{ paddingLeft: f.esDominante ? 10 : 0 }}>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-label-data-mono font-bold" style={{ color: f.esDominante ? DOMINANT_OUTLINE : "var(--color-ink)" }}>
                        {f.code}
                      </span>
                      <span className="text-title-md" style={{ color: "var(--color-ink)", fontWeight: f.esDominante ? 700 : 600 }}>
                        {f.meta.titulo}
                      </span>
                      {f.esDominante && (
                        <span
                          className="text-label-micro-mono font-bold uppercase px-2 py-0.5 rounded"
                          style={{ background: "#fef3c7", color: DOMINANT_OUTLINE }}
                        >
                          ▲ DRIVER DOMINANTE
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
                      {f.sinDato ? (
                        <span className="uppercase">Pista no verificada</span>
                      ) : (
                        <>
                          <span className="uppercase font-semibold">Valor</span>
                          <span className="text-label-data-mono font-bold" style={{ color: f.esDominante ? DOMINANT_OUTLINE : "var(--color-ink)" }}>
                            {f.valorMostrado.toFixed(2)}
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="w-full rounded overflow-hidden" style={{ height: 12, background: "var(--color-surface-alt, #f4f4f5)" }}>
                    {f.sinDato ? (
                      <div
                        className="w-full h-full"
                        style={{
                          background:
                            "repeating-linear-gradient(45deg, var(--color-sin-dato-bg), var(--color-sin-dato-bg) 4px, var(--color-border) 4px, var(--color-border) 8px)",
                        }}
                      />
                    ) : (
                      <BarraDriver valor={f.valorMostrado} color={f.esDominante ? DOMINANT_OUTLINE : "var(--color-ink-faint)"} />
                    )}
                  </div>

                  <div
                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-label-micro-mono"
                    style={{ paddingLeft: f.esDominante ? 10 : 0 }}
                  >
                    {f.sinDato ? (
                      <>
                        <span style={{ color: "var(--color-risk-high)" }}>SIN DATO — pista que no pudimos verificar</span>
                        <span style={{ color: "var(--color-ink-faint)" }}>Motivo: {f.meta.motivo}</span>
                      </>
                    ) : (
                      <>
                        <span style={{ color: "var(--color-ink-faint)" }}>
                          {f.meta.grano === "municipio"
                            ? `Valor municipal${municipio ? ` — compartido por todas las escuelas de ${municipio}` : ""}`
                            : f.meta.orientado
                              ? `Servicios presentes: ${f.raw.toFixed(2)}`
                              : ""}
                        </span>
                        {f.meta.fuente && (
                          <span className="font-medium" style={{ color: f.esDominante ? DOMINANT_OUTLINE : "var(--faro-signal)" }}>
                            FUENTE: {f.meta.fuente}
                          </span>
                        )}
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-5 flex flex-col gap-2" style={cardStyle}>
            <div className="flex items-center gap-2">
              <IconVerified size={20} style={{ color: "var(--faro-signal)" }} />
              <span className="text-label-micro-mono uppercase font-bold" style={{ color: "var(--faro-signal)" }}>
                Protocolo de Intervención Institucional
              </span>
            </div>
            {tienePrediccion && prediccion ? (
              <>
                <h3 className="text-headline-sm" style={{ color: "var(--color-ink)" }}>
                  Recomendación Oficial para Driver Dominante ({escuela.driver_dominante})
                </h3>
                <div className="p-4 rounded-lg mt-1" style={{ background: "var(--faro-canvas-container)" }}>
                  <p className="text-title-md font-semibold" style={{ color: "var(--color-ink)" }}>“{prediccion.recomendacion}”</p>
                </div>
              </>
            ) : (
              <p className="text-body-sm py-2" style={{ color: "var(--color-ink-faint)" }}>
                No hay recomendación disponible para esta escuela (SIN_DATO) -- cobertura insuficiente de drivers en el ciclo actual.
              </p>
            )}
          </div>
        </div>

        {/* ---- Columna derecha: explicación algorítmica + ficha operativa + registro de auditoría ---- */}
        <div className="lg:col-span-4 flex flex-col gap-5">
          <div className="p-5 flex flex-col gap-3" style={cardStyle}>
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2 min-w-0">
                <IconPsychology size={18} style={{ color: "var(--color-ink-faint)" }} />
                <h3 className="text-title-md font-semibold" style={{ color: "var(--color-ink)" }}>Explicación Algorítmica</h3>
              </div>
              <span
                className="text-label-micro-mono uppercase font-semibold px-2 py-0.5 rounded"
                style={{ background: "var(--faro-canvas-container)", color: "var(--color-ink-faint)" }}
              >
                SHAP // VALUE
              </span>
            </div>

            {!tienePrediccion ? (
              <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>
                Esta escuela no tiene predicción disponible (SIN_DATO); sin predicción no hay explicación que calcular.
              </p>
            ) : !hayContribuciones ? (
              <div className="p-3 rounded-lg flex flex-col gap-2" style={{ background: "var(--faro-canvas-container)" }}>
                <div className="flex items-center gap-2" style={{ color: "var(--color-ink-faint)" }}>
                  <IconHourglassEmpty size={18} />
                  <span className="text-label-micro-mono font-bold uppercase">Estado de producción: SIN_DATO</span>
                </div>
                {/* FIX (2026-09-13, US-651, hallazgo de Marina García + su IA): el texto
                    anterior traía nombres de columna de base de datos (shap_d1...shap_d6) y una
                    historia de usuario + equipo interno (US-631, Equipo 4) visibles para el
                    evaluador -- "lenguaje de la cocina, no del comedor". Se conserva la idea
                    (el hueco no es culpa de esta escuela) sin exponer implementación interna. */}
                <p className="text-body-sm font-medium" style={{ color: "var(--color-ink)" }}>
                  La explicación del modelo todavía no está disponible para ninguna escuela: es un
                  pendiente de datos del proyecto, no una particularidad de este caso.
                </p>
                <div className="flex flex-col gap-1 pt-1">
                  <div className="flex justify-between text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
                    <span>Explicación calculada</span>
                    <span className="font-bold" style={{ color: "var(--color-ink)" }}>{contribucionesConValor} de 6</span>
                  </div>
                  <div className="w-full rounded overflow-hidden" style={{ height: 6, background: "var(--color-surface-alt, #f4f4f5)" }}>
                    <div className="h-full" style={{ width: `${(contribucionesConValor / 6) * 100}%`, background: "var(--color-ink-faint)" }} />
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-1.5">
                {DRIVERS.map((code) => {
                  const v = contribuciones[code];
                  return (
                    <div key={code} className="flex items-center justify-between text-label-data-mono">
                      <span style={{ color: "var(--color-ink-faint)" }}>{code}</span>
                      <span style={{ color: v == null ? "var(--color-ink-faint)" : "var(--color-ink)" }}>
                        {v == null ? "SIN_DATO" : v.toFixed(3)}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="p-5 flex flex-col gap-3" style={cardStyle}>
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h3 className="text-title-md font-semibold min-w-0" style={{ color: "var(--color-ink)" }}>
                Ficha Operativa{municipio ? ` de ${municipio}` : ""}
              </h3>
              {entidadAbrev && (
                <span className="text-label-micro-mono shrink-0" style={{ color: "var(--color-ink-faint)" }}>
                  {entidadAbrev}{cveEnt ? ` // ${cveEnt}` : ""}
                </span>
              )}
            </div>

            {/* FIX (2026-09-13, US-651, hallazgo de Marina García + su IA): el mapa
                embebido original (iframe a openstreetmap.org/export/embed.html) se
                habia quitado -- en produccion, cuando el iframe no cargaba (red
                bloqueada, politica de terceros, sin conexion) no quedaba en blanco
                sino que se veia el icono de imagen rota, en todos los expedientes a
                la vez. Vuelve a haber mapa (pedido explicito de Diana, mismo dia:
                "arreglarlo sin quitarlo"), con SiluetaEntidad.jsx (mismo componente
                que ya usa el panel "Enclave Georreferenciado" de Panorama.jsx):
                silueta real de la entidad (geojson de los 32 estados, sin llamar a
                ningun servicio externo) con un punto en las coordenadas reales de
                ESTA escuela. Nunca puede salir roto porque no depende de que cargue
                nada fuera del propio bundle -- distinto del iframe, que dependia de
                un tercero. (Se probó también MapaPin.jsx -- mapa de la república
                completa con pin -- pero Diana pidió dejar ese estilo solo en la
                previsualización de caso de LosSieteCasos.jsx; aquí se queda con la
                silueta de la entidad). El chip "GEO_COORD" en texto plano que iba
                encima se quitó (pedido de Diana, mismo dia): quedaba redundante con
                el punto del mapa, que ya señala esa misma coordenada (el dato real
                sigue disponible al pasar el cursor sobre el punto). "Radio de
                Vigilancia: 1,500m" queda igual por ahora -- es la observación #7
                (Marina), pendiente de decidir aparte. */}
            {typeof escuela.latitud === "number" && typeof escuela.longitud === "number" && (
              <div
                className="rounded-lg flex flex-col gap-2 p-3"
                style={{ background: "var(--faro-canvas-container)", border: "1px solid var(--color-border)" }}
              >
                {/* FIX (2026-09-13, pedido de Diana -- "quita esa línea negra que dice
                    latitud y lon"): se quita el chip GEO_COORD -- el punto del mapa de abajo
                    ya señala la ubicación real de la escuela, el texto quedaba redundante.
                    El dato real sigue disponible al pasar el cursor sobre el punto (title
                    del <circle>, ver SiluetaEntidad.jsx) para quien lo necesite. */}
                {entidadInfo && (
                  <SiluetaEntidad
                    entidadId={entidadInfo.id}
                    color={entidadInfo.color}
                    puntos={[{ lat: escuela.latitud, lon: escuela.longitud, etiqueta: escuela.nombre ?? "Esta escuela" }]}
                    width={320}
                    height={170}
                    ariaLabel={`Ubicación real de ${escuela.nombre ?? "la escuela"} dentro de ${entidadInfo.nombre}`}
                  />
                )}
                {/* FIX (2026-09-13, US-651, obs. 7, Marina García + su IA): se quita
                    "Radio de Vigilancia: 1,500m" -- etiqueta fija de encuadre, no una
                    medida real de esta escuela (mismo hallazgo que GEO_LOCK/PERÍMETRO en
                    LosSieteCasos.jsx). El CCT ya se muestra arriba, en el encabezado. */}
              </div>
            )}

            <div className="grid grid-cols-2 gap-2">
              <div className="p-2 rounded" style={{ background: "var(--faro-canvas-container)" }}>
                <span className="text-label-micro-mono uppercase block" style={{ color: "var(--color-ink-faint)" }}>Matrícula Verificada</span>
                <span className="text-label-data-mono font-bold" style={{ color: "var(--color-ink)" }}>
                  {escuela.matricula_total.toLocaleString("es-MX")} Alumnos
                </span>
              </div>
              <div className="p-2 rounded" style={{ background: "var(--faro-canvas-container)" }}>
                <span className="text-label-micro-mono uppercase block" style={{ color: "var(--color-ink-faint)" }}>Variación vs. ciclo anterior</span>
                <span className="text-label-data-mono font-bold" style={{ color: "var(--color-ink)" }}>
                  {esReal
                    ? escuela.variacion_matricula_alumnos != null
                      ? `${escuela.variacion_matricula_alumnos > 0 ? "+" : ""}${escuela.variacion_matricula_alumnos} alumnos`
                      : "SIN_DATO"
                    : escuela.variacion != null
                      ? `${escuela.variacion}%`
                      : "SIN_DATO"}
                </span>
              </div>
            </div>
          </div>

          {/* FIX (2026-09-13, US-651, hallazgo de Marina García + su IA): se quita la
              tarjeta "Registro de Auditoría" completa. Mostraba mlflow_run_id como si fuera un
              "HASH" de verificación -- en producción llegó a mostrar el id de una corrida de
              prueba con un número de bug en el nombre ("bug048-20260905-temporal-robusto").
              "CADENA DE CUSTODIA DIGITAL VERIFICADA" además quedaba fijo incluso cuando el hash
              era SIN_DATO, afirmando una verificación que no ocurrió. El mlflow_run_id es
              trazabilidad interna (para debugging/soporte, no para quien usa el producto); si
              se necesita conservarla, debe viajar en un atributo del HTML, no en pantalla. */}
        </div>
      </div>
    </PageContainer>
  );
}
