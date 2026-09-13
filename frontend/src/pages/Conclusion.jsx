import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import { IconInfo, IconShield, IconRouter, IconEmptySquare } from "../components/Icons.jsx";
import { driverNombres, recomendacionGeneralPorDriver, panoramaMock } from "../data/mock.js";
import { DOMINANT_OUTLINE } from "../lib/riskRamp.js";
import { getConclusionEscuelas } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";

const DRIVERS = ["D1", "D2", "D3", "D4", "D5", "D6"];

// Pantalla 5 -- Conclusión Global / Top de drivers dominantes. REESCRITURA
// COMPLETA 13-sep contra mockups/05_Conclusion_Top3.png + .html, a pedido
// EXPLÍCITO de Diana de fidelidad 100% (mismo criterio ya aplicado en
// ExpedienteEscuela.jsx / Pantalla 4): "no hay manera que haya en esa
// pantalla otra cosa que no esté en la plantilla P5... desde la
// tipografía, colores, hasta recuadros, iconos, mapas y títulos."
//
// La versión anterior de este archivo tenía 3 bloques que este mockup NO
// tiene en absoluto: "Concentración por municipio" (chips por municipio),
// "El diferenciador" (comparación de 2 CCTs reales vía DifferentiatorChart)
// y un párrafo duplicado con la nota obligatoria (que aquí ya va como
// banner junto al H1). Los 3 se RETIRAN de esta pantalla por instrucción
// explícita de Diana -- igual que en la P4 se omitieron 2 frases exigidas
// por el spec pero ausentes del mockup. IMPORTANTE: 02_Data_Visualization_
// Spec.md §3 (fila "P5") sí pide "concentración por municipio" como
// requisito funcional de esta pantalla, y "El diferenciador" venía de una
// decisión de arquitectura de Marina García del Buey ("la prueba concreta
// de la tesis del proyecto") -- no se borra el código fuente de
// DifferentiatorChart.jsx ni el dato parDiferenciador de mock.js, solo se
// deja de importarlos aquí, por si Diana pide reincorporarlos en esta u
// otra pantalla.
//
// Verificado elemento por elemento contra src/api/schemas.py y
// 02_Data_Visualization_Spec.md §5 (la sección que describe ESTA
// mecánica, "Cómo se obtiene y comunica el Top 3"), con la misma
// clasificación de 3 tipos que en la P4:
//
//   A) Coincide con un campo/regla real -- se usa tal cual, en vivo:
//      - `driver_dominante` de cada escuela del conjunto COMPLETO (nunca
//        filtrado -- getConclusionEscuelas() llama getPanoramaEscuelas()
//        de cero, sin depender de ningún filtro de otra pantalla, §5.1
//        paso 2 y la nota obligatoria del banner).
//      - k_d (conteo por driver) y el ranking con RANGO COMPARTIDO en
//        empates (§5.1 paso 6: "1, 2, 2, 4"): entran al Top todos los
//        drivers con rango ≤ 3 y k_d > 0, así que un empate en tercer
//        lugar puede mostrar más de 3 tarjetas -- el mockup de hoy solo
//        muestra el caso real actual (2 dominantes reales + 1 vacante),
//        pero el cálculo de abajo es general.
//      - `recomendacion` general por driver: mismo catálogo de
//        recomendacionGeneralPorDriver de mock.js que ya usaba este
//        archivo, que espeja src/modelos/recomendaciones.py
//        (RECOMENDACION_POR_DRIVER) -- confirmado real en la reescritura
//        de ExpedienteEscuela.jsx (P4).
//      - "Alcance N Entidades" (footer de cada tarjeta dominante): NUEVO
//        cálculo 13-sep -- cuenta entidades (cve_ent) DISTINTAS entre las
//        escuelas de ese driver dominante. Requiere el municipio de cada
//        escuela (cve_mun -> cve_ent), así que getConclusionEscuelas() en
//        lib/api.js se extendió (sin llamada adicional: ya resolvía
//        municipios para el nombre) para incluir cve_ent/nombre_entidad
//        en el merge. En modo demo (sin cve_mun, ver data/mock.js) se usa
//        el campo `entidad` (nombre) que el mock ya trae directo.
//      - La leyenda obligatoria del banner (plan §5, literal, visible, sin
//        tooltip).
//      - "Sumatoria de frecuencias" y "Total casos de riesgo": sumados en
//        vivo de los porcentajes calculados, no tecleados -- ver nota B.
//
//   B) El mockup teclea números de su propio fixture -- se corrige a
//      cálculo en vivo (mismo hallazgo que el spec documenta en su propia
//      auditoría del mockup de referencia, §8 "05_Conclusion" -- "la copy
//      lleva conteos tecleados... en los mockups van como N y k"):
//      - "N=7 PLANTELES", "N=5", "N=2", "TOTAL CASOS DE RIESGO: 7" y el
//        "* 100" de la fórmula: todos son el N real (`escuelas.length`) y
//        los conteos reales, no el 7 fijo del mockup -- hoy da 7 porque
//        hoy hay 7 escuelas en riesgo, no porque esté escrito así.
//      - "FACTOR DOMINANTE (TOP 2)": el "2" se calcula (`top.length`), no
//        se fija -- si mañana hay 3 dominantes o un empate a 4, la
//        leyenda lo dice sola.
//      - "SUMATORIA FRECUENCIAS: 100%": se suma en vivo el % (redondeado)
//        de cada uno de los 6 drivers -- hoy da 100 porque ninguna escuela
//        tiene driver_dominante nulo, no porque el número esté fijo.
//      - "Factores basales como Pobreza (D1) o Infraestructura (D3)": los
//        2 ejemplos de la aclaración metodológica se toman en vivo de los
//        drivers realmente basales (k_d = 0) de hoy, no se dejan
//        tecleados -- si D1 alguna vez fuera dominante, el texto ya no lo
//        nombraría como ejemplo de "basal".
//
//   C) No existe ningún campo real ni equivalente -- se omite en vez de
//      inventarlo:
//      - Los íconos "shield" (D2) y "router" (D4) del mockup no tienen
//        equivalente real más allá de esos 2 drivers -- no hay un ícono
//        "oficial" documentado para D1/D3/D5/D6 en ningún lado. Si algún
//        día otro driver domina, la tarjeta usa un ícono neutro
//        (IconEmptySquare, el mismo de la ranura "vacante") en vez de
//        inventar un glifo nuevo sin precedente en el mockup.
//      - Las categorías "FACTOR PERIFÉRICO VECTORIAL" (D2) y "FACTOR
//        ESTRUCTURAL TECNOLÓGICO" (D4) son copy fijo del mockup para ESOS
//        2 drivers -- no existe un catálogo de "categorías" por driver en
//        ningún esquema. Mismo criterio: fallback neutro ("FACTOR EN
//        EVALUACIÓN") si otro driver llegara a dominar.
const NOMBRE_CORTO = {
  D1: "Pobreza",
  D2: "Inseguridad",
  D3: "Infraestructura",
  D4: "Conectividad",
  D5: "Estrés Hídrico",
  D6: "Calidad del Aire",
};

// Título largo + categoría + ícono de tarjeta dominante: copy LITERAL del
// mockup solo para D2 y D4 (los únicos 2 que el mockup dibuja como
// dominantes). D1/D3/D5/D6 llevan un fallback neutro documentado arriba
// (caso C) -- no aparecen en el mockup como tarjeta.
const TARJETA_POR_DRIVER = {
  D1: { titulo: driverNombres.D1, categoria: "FACTOR EN EVALUACIÓN", Icono: null },
  D2: { titulo: "Inseguridad del entorno", categoria: "FACTOR PERIFÉRICO VECTORIAL", Icono: IconShield },
  D3: { titulo: driverNombres.D3, categoria: "FACTOR EN EVALUACIÓN", Icono: null },
  D4: { titulo: "Conectividad digital", categoria: "FACTOR ESTRUCTURAL TECNOLÓGICO", Icono: IconRouter },
  D5: { titulo: driverNombres.D5, categoria: "FACTOR EN EVALUACIÓN", Icono: null },
  D6: { titulo: driverNombres.D6, categoria: "FACTOR EN EVALUACIÓN", Icono: null },
};

function ordinalLugar(rank) {
  if (rank === 1) return "1ER";
  return `${rank}º`;
}
function ordinalPosicion(pos) {
  const map = { 1: "1ª", 2: "2ª", 3: "3ª", 4: "4ª", 5: "5ª", 6: "6ª" };
  return map[pos] ?? `${pos}ª`;
}

export default function Conclusion() {
  const { status, data } = useApiResource(getConclusionEscuelas, { mock: panoramaMock });
  const escuelas = status === "ok" || status === "demo" ? data : [];
  const n = escuelas.length;
  const esReal = status === "ok";

  const cardStyle = { background: "var(--color-surface)", borderRadius: "var(--radius-card)", boxShadow: "var(--shadow-card-hover)" };

  if (status === "loading") {
    return (
      <PageContainer>
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Calculando la conclusión…</p>
      </PageContainer>
    );
  }

  if (status === "error") {
    return (
      <PageContainer>
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No pudimos calcular la conclusión, intenta de nuevo.
        </p>
      </PageContainer>
    );
  }

  // §5.1 paso 4-6: conteo por driver sobre el conjunto COMPLETO, rango
  // compartido en empates, Top = rango <= 3 y k_d > 0.
  const conteoPorDriver = {};
  const gruposPorDriver = {};
  for (const e of escuelas) {
    if (!e.driver_dominante) continue;
    conteoPorDriver[e.driver_dominante] = (conteoPorDriver[e.driver_dominante] ?? 0) + 1;
    (gruposPorDriver[e.driver_dominante] ??= []).push(e);
  }

  const counts = DRIVERS.map((code) => ({ code, count: conteoPorDriver[code] ?? 0 }))
    .filter((d) => d.count > 0)
    .sort((a, b) => b.count - a.count);

  const top = counts
    .map((d) => ({ ...d, rank: 1 + counts.filter((o) => o.count > d.count).length }))
    .filter((d) => d.rank <= 3);

  const rankConteo = {};
  for (const t of top) rankConteo[t.rank] = (rankConteo[t.rank] ?? 0) + 1;

  // "Alcance N Entidades": entidades DISTINTAS entre las escuelas de ese
  // driver dominante -- cve_ent en modo real (vía getConclusionEscuelas,
  // resuelto de cve_mun), nombre de entidad directo en modo demo (el mock
  // no trae cve_mun/cve_ent, ver data/mock.js).
  function alcanceEntidades(code) {
    const grupo = gruposPorDriver[code] ?? [];
    const claves = new Set();
    for (const e of grupo) {
      const clave = esReal ? e.cve_ent : e.entidad;
      if (clave != null) claves.add(clave);
    }
    return claves.size;
  }

  const pctPorDriver = {};
  DRIVERS.forEach((code) => {
    pctPorDriver[code] = n > 0 ? Math.round(((conteoPorDriver[code] ?? 0) / n) * 100) : 0;
  });
  const sumaPct = DRIVERS.reduce((acc, c) => acc + pctPorDriver[c], 0);

  const basales = DRIVERS.filter((code) => !top.some((t) => t.code === code));
  const [ejemploBasal1, ejemploBasal2] = basales;

  const vacantes = Math.max(0, 3 - top.length);
  const maxBarPx = 88;

  return (
    <>
      {/* ---- Barra de estado / telemetría (copy literal del mockup) ----
          Fuera de PageContainer a propósito: en el mockup esta franja
          ocupa todo el ancho del área de contenido (borde a borde bajo el
          header fijo), no el ancho centrado de max-w-7xl que usa el resto
          de la página -- <main> en App.jsx ya no tiene padding horizontal
          propio (solo el offset del sidebar), así que un div sin
          contenedor aquí sí llega borde a borde como en el mockup. */}
      <div
        className="w-full px-8 py-2.5 flex items-center justify-between flex-wrap gap-2"
        style={{ background: "var(--faro-canvas-container)" }}
      >
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--faro-signal)" }}>
            MÓDULO DE SÍNTESIS AGREGADA // SENSOR RED FEDERAL
          </span>
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
          <span className="text-label-data-mono" style={{ color: "var(--color-ink-faint)" }}>
            MUESTRA AUDITADA: N={n} PLANTELES
          </span>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>CORTE TEMPORAL: CICLO VIGENTE</span>
          <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>•</span>
          <span className="text-label-micro-mono font-semibold" style={{ color: "var(--color-ink)" }}>Auditoría activa</span>
          {status === "demo" && <DemoBadge />}
        </div>
      </div>

      <PageContainer>
      {/* ---- Encabezado con marco institucional ---- */}
      <div className="flex flex-col gap-1.5">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className="text-label-micro-mono uppercase px-2 py-0.5 rounded"
            style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
          >
            DIAGNÓSTICO TRANSCENSAL
          </span>
          <span className="text-label-data-mono" style={{ color: "var(--color-ink-faint)" }}>REF: FARO-PANORAMA-C5</span>
        </div>
        <h1 className="text-headline-xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>
          Factores de Riesgo Dominantes
        </h1>
        <p className="text-body-md max-w-4xl" style={{ color: "var(--color-ink-faint)" }}>
          Jerarquización sistemática calculada mediante agregación estadística sobre el universo censal verificado.
        </p>
        {/* Nota metodológica obligatoria (plan §5, 02_Data_Visualization_Spec.md): literal, visible, sin tooltip. */}
        <div className="mt-1 p-3 rounded-lg flex items-center gap-2 shadow-sm" style={{ background: "var(--faro-canvas-container)" }}>
          <IconInfo size={20} style={{ color: "var(--faro-signal)" }} />
          <p className="text-body-sm font-medium" style={{ color: "var(--color-ink)" }}>
            Esta conclusión se calcula sobre el conjunto completo de escuelas en riesgo, independientemente de los filtros utilizados durante la exploración.
          </p>
        </div>
      </div>

      {/* ---- Grilla principal: Top de drivers dominantes + ranura(s) vacante(s) ---- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 items-stretch">
        {top.map(({ code, count, rank }) => {
          const meta = TARJETA_POR_DRIVER[code];
          const Icono = meta.Icono ?? IconEmptySquare;
          const empatado = rankConteo[rank] > 1;
          const alcance = alcanceEntidades(code);
          return (
            <div key={code} className="rounded flex flex-col justify-between relative overflow-hidden" style={{ ...cardStyle, boxShadow: "var(--shadow-card-hover)" }}>
              <div className="absolute top-0 left-0 right-0" style={{ height: 6, background: DOMINANT_OUTLINE }} aria-hidden="true" />
              <div className="p-5 pt-6 flex flex-col gap-4">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="inline-flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ background: DOMINANT_OUTLINE }} aria-hidden="true" />
                    <span className="text-label-micro-mono font-bold uppercase" style={{ color: DOMINANT_OUTLINE, letterSpacing: "0.08em" }}>
                      {ordinalLugar(rank)} LUGAR DOMINANTE{empatado ? " (EMPATE)" : ""}
                    </span>
                  </div>
                  <span className="text-label-data-mono font-semibold px-2 py-0.5 rounded" style={{ background: "var(--faro-canvas-container)", color: "var(--color-ink-faint)" }}>
                    CÓDIGO: {code}
                  </span>
                </div>

                <div className="flex items-start gap-3">
                  <div className="p-2 rounded shrink-0" style={{ background: "var(--faro-canvas-container)", color: DOMINANT_OUTLINE }}>
                    <Icono size={28} />
                  </div>
                  <div>
                    <h2 className="text-headline-sm" style={{ color: "var(--color-ink)" }}>{meta.titulo}</h2>
                    <span className="text-label-micro-mono uppercase" style={{ color: "var(--color-ink-faint)", letterSpacing: "0.06em" }}>
                      {meta.categoria}
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded" style={{ background: "var(--faro-canvas-container)" }}>
                  <div className="flex items-baseline justify-between flex-wrap gap-x-2 gap-y-0.5 mb-1">
                    <span className="text-label-micro-mono uppercase" style={{ color: "var(--color-ink-faint)" }}>Presencia Diagnosticada</span>
                    <span className="text-label-data-mono font-medium" style={{ color: "var(--color-ink-faint)" }}>MUESTRA AUDITADA: N={n} PLANTELES</span>
                  </div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-headline-xl font-bold" style={{ color: "var(--color-ink)" }}>{pctPorDriver[code]}</span>
                    <span className="text-title-md font-bold" style={{ color: DOMINANT_OUTLINE }}>%</span>
                  </div>
                  <div className="w-full rounded overflow-hidden mt-2" style={{ height: 6, background: "var(--color-surface)" }}>
                    <div className="h-full" style={{ width: `${pctPorDriver[code]}%`, background: DOMINANT_OUTLINE }} />
                  </div>
                </div>

                <div className="flex flex-col gap-0.5">
                  <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--color-ink-faint)" }}>Recomendación Institucional Oficial</span>
                  <p className="text-body-md" style={{ color: "var(--color-ink)" }}>{recomendacionGeneralPorDriver[code]}</p>
                </div>
              </div>

              <div className="px-5 py-2.5 flex items-center justify-between flex-wrap gap-x-2 gap-y-0.5" style={{ background: "var(--faro-canvas-container)" }}>
                <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>MASA CRÍTICA TRANSVERSAL</span>
                <span className="text-label-data-mono font-semibold" style={{ color: "var(--color-ink)" }}>
                  N={count} // ALCANCE {alcance} ENTIDAD{alcance === 1 ? "" : "ES"}
                </span>
              </div>
            </div>
          );
        })}

        {Array.from({ length: vacantes }).map((_, i) => {
          const posicion = top.length + i + 1;
          return (
            <div key={`vacante-${posicion}`} className="rounded flex flex-col justify-between relative overflow-hidden" style={{ background: "var(--faro-canvas-container)", boxShadow: "var(--shadow-card)" }}>
              <div className="p-5 flex flex-col gap-4">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="inline-flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full" style={{ background: "var(--color-border)" }} aria-hidden="true" />
                    <span className="text-label-micro-mono font-semibold uppercase" style={{ color: "var(--color-ink-faint)", letterSpacing: "0.08em" }}>
                      {ordinalPosicion(posicion)} POSICIÓN // VACANTE
                    </span>
                  </div>
                  <span className="text-label-micro-mono uppercase px-2 py-0.5 rounded" style={{ background: "var(--color-surface)", color: "var(--color-ink-faint)" }}>
                    SIN CRITERIO
                  </span>
                </div>

                <div className="flex flex-col items-center text-center py-3">
                  <div className="w-14 h-14 rounded-full flex items-center justify-center mb-3" style={{ background: "var(--color-surface)", color: "var(--color-ink-faint)" }}>
                    <IconEmptySquare size={28} />
                  </div>
                  <h3 className="text-headline-sm mb-1" style={{ color: "var(--color-ink-faint)" }}>Sin factores concurrentes</h3>
                  <p className="text-body-md font-medium max-w-xs" style={{ color: "var(--color-ink-faint)" }}>
                    Solo {top.length} factor{top.length === 1 ? "" : "es"} aparece{top.length === 1 ? "" : "n"} como dominante{top.length === 1 ? "" : "s"} entre todas las escuelas en riesgo.
                  </p>
                </div>

                <div className="p-3 rounded" style={{ background: "var(--color-surface)" }}>
                  <span className="text-label-micro-mono uppercase font-semibold block mb-1" style={{ color: "var(--color-ink-faint)" }}>Aclaración Metodológica</span>
                  <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>
                    {ejemploBasal1 && ejemploBasal2
                      ? `Factores basales como ${NOMBRE_CORTO[ejemploBasal1]} (${ejemploBasal1}) o ${NOMBRE_CORTO[ejemploBasal2]} (${ejemploBasal2}) operan como condiciones de base sin alcanzar masa crítica transversal en este ciclo censal.`
                      : "Los factores restantes operan como condiciones de base sin alcanzar masa crítica transversal en este ciclo censal."}
                  </p>
                </div>
              </div>

              <div className="px-5 py-2.5 flex items-center justify-between flex-wrap gap-x-2 gap-y-0.5" style={{ background: "var(--faro-canvas-container)" }}>
                <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>ESTADO CENSAL</span>
                <span className="text-label-micro-mono uppercase font-medium" style={{ color: "var(--color-ink-faint)" }}>UMBRAL DISPERSIÓN NO ALCANZADO</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* ---- Distribución paramétrica total: las 6 barras ---- */}
      <div className="p-5 flex flex-col gap-5" style={cardStyle}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
          <div>
            <div className="flex items-center gap-1.5 mb-0.5">
              <span className="w-2 h-2" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
              <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--faro-signal)" }}>DISTRIBUCIÓN PARAMÉTRICA TOTAL</span>
            </div>
            <h2 className="text-headline-sm" style={{ color: "var(--color-ink)" }}>Frecuencia Absoluta de Incidencia por Factor Evaluado</h2>
          </div>
          <div className="flex items-center flex-wrap gap-x-4 gap-y-1.5 text-label-micro-mono">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 shrink-0" style={{ background: DOMINANT_OUTLINE }} aria-hidden="true" />
              <span style={{ color: "var(--color-ink-faint)" }}>FACTOR DOMINANTE (TOP {top.length})</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 shrink-0" style={{ background: "var(--color-surface-alt, #f4f4f5)" }} aria-hidden="true" />
              <span style={{ color: "var(--color-ink-faint)" }}>FACTOR BASAL / INCIDENCIA 0%</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-6 gap-3 pt-1">
          {DRIVERS.map((code) => {
            const pct = pctPorDriver[code];
            const enTop = top.find((t) => t.code === code);
            const barPx = pct === 0 ? 4 : Math.max(8, Math.round((pct / 100) * maxBarPx));
            return (
              <div
                key={code}
                className="p-3 rounded flex flex-col justify-between relative overflow-hidden"
                style={{ height: "12rem", background: enTop ? "var(--color-surface)" : "var(--faro-canvas-container)", boxShadow: enTop ? "var(--shadow-card)" : "none" }}
              >
                {enTop && <div className="absolute top-0 left-0 right-0" style={{ height: 4, background: DOMINANT_OUTLINE }} aria-hidden="true" />}
                <div className="flex justify-between items-start">
                  <span className="text-label-data-mono font-bold" style={{ color: enTop ? DOMINANT_OUTLINE : "var(--color-ink-faint)" }}>{code}</span>
                  <span className="text-label-data-mono font-bold" style={{ color: enTop ? DOMINANT_OUTLINE : "var(--color-ink-faint)" }}>
                    {conteoPorDriver[code] ?? 0} esc.
                  </span>
                </div>
                <div className="flex flex-col items-center justify-end gap-1" style={{ height: "7rem" }}>
                  <div className="w-full rounded-t" style={{ height: barPx, background: enTop ? DOMINANT_OUTLINE : "var(--color-surface)" }} />
                  <span className="text-label-data-mono font-bold" style={{ color: enTop ? DOMINANT_OUTLINE : "var(--color-ink-faint)" }}>{pct}%</span>
                </div>
                <div className="truncate">
                  <p className={`text-body-sm truncate ${enTop ? "font-semibold" : ""}`} style={{ color: enTop ? "var(--color-ink)" : "var(--color-ink-faint)" }} title={NOMBRE_CORTO[code]}>
                    {NOMBRE_CORTO[code]}
                  </p>
                  <span className="text-label-micro-mono uppercase" style={{ color: enTop ? DOMINANT_OUTLINE : "var(--color-ink-faint)", opacity: enTop ? 1 : 0.8 }}>
                    {enTop ? `${ordinalLugar(enTop.rank)} DOMINANTE` : "BASAL"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between flex-wrap gap-2 pt-2" style={{ borderTop: "1px solid var(--color-border)" }}>
          <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
            CÁLCULO: (ESCUELAS CON FACTOR / TOTAL ESCUELAS AUDITADAS N={n}) * 100
          </span>
          <span className="text-label-micro-mono font-medium" style={{ color: "var(--color-ink-faint)" }}>
            TOTAL CASOS DE RIESGO: {n} // SUMATORIA FRECUENCIAS: {sumaPct}%
          </span>
        </div>
      </div>

      {/* ---- CTA único ---- */}
      <div className="flex items-center justify-between flex-wrap gap-3 p-5 rounded" style={cardStyle}>
        <div className="flex flex-col">
          <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--color-ink-faint)" }}>SIGUIENTE ACCIÓN EN FLUJO CENSAL</span>
          <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>
            Concluido el análisis macro, continúe con la inspección individualizada de planteles territoriales.
          </p>
        </div>
        <Link
          to="/explorador"
          className="inline-flex items-center gap-2 px-5 py-3 rounded text-title-md font-semibold shadow"
          style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
        >
          Explorar otras escuelas
          <span className="text-label-data-mono">→</span>
        </Link>
      </div>
      </PageContainer>
    </>
  );
}
