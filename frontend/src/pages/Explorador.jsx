import { useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import GlosarioOverlay from "../components/GlosarioOverlay.jsx";
import DriverBars from "../components/DriverBars.jsx";
import { nivelRiesgo, panoramaMock, driverNombres, recomendacionGeneralPorDriver } from "../data/mock.js";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";
import { getEscuelas, getUniversoEscuelas, getMunicipiosPorClaves, getPrediccion } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { useCortesAtencion } from "../lib/cortesAtencion.js";
import { IconMenuBook, IconCalendarMonth, IconLocationOn, IconSchool, IconVerified } from "../components/Icons.jsx";

const DRIVERS = ["D1", "D2", "D3", "D4", "D5", "D6"];
// D3/D4 se publican como "servicios presentes" (mayor = mejor) -- se orientan
// (1 - valor) para que, igual que en ExpedienteEscuela.jsx (P4) y en el propio
// pipeline (features_escuela.sql, spec §4.1.1), "mayor barra = mayor presión"
// signifique lo mismo en toda la app, incluida esta vista condensada.
const ORIENTADOS = ["D3", "D4"];

// Pantalla 6 -- Explorador de escuelas (rediseño Fase 2, US-641). Contra
// 01_UX_Architecture.md §2 "Pantalla 6" y §7 (nombre elegido por Marina).
//
// PASE DE FIDELIDAD 13-sep (auditoría "sin excepciones" contra
// mockups/06_Explorador.png/.html, a petición explícita de Diana). La
// plantilla real trae el modal de inducción cubriendo casi toda la pantalla
// en la captura, así que el contenido detrás se verificó contra el HTML
// completo del mockup (no solo el PNG) y contra 01_UX_Architecture.md /
// PLAN_TRABAJO.md del Equipo 3, tal como Diana pidió.
//
// Se adopta del mockup: el layout de "vista maestra" con encabezado
// operativo, tarjeta de filtros con iconos, tabla de resultados (antes era
// una grilla de tarjetas) con paginación real, y un botón "Glosario" en el
// encabezado.
//
// Tres cosas del mockup NO se replican tal cual, cada una por un motivo
// documentado, no por descuido -- pero Diana confirmó explícitamente
// (13-sep, 2da vuelta) que quiere el MISMO layout dividido tabla+panel del
// mockup, con datos reales en vez de fabricados, así que las tres se
// resuelven reconstruyendo la forma visual con la fuente real detrás:
//
// 1) El panel derecho "Expediente" del mockup trae escala 0-10 (el resto de
//    la app usa 0-1), percentiles nacional/regional inventados, "18,492
//    planteles"/"1 de 823" fijos, y botones "Exportar Ficha CCT (PDF)" /
//    "Vincular a Mesa de Enlace" que no existen. 01_UX_Architecture.md §2 es
//    explícito: P6 "reutiliza... misma lógica de expediente que P4... no se
//    rediseña ni se duplica". Se honra reutilizando el MISMO componente real
//    de la P4 (components/DriverBars.jsx, misma orientación D3/D4, mismo
//    color monocromático, misma franja SIN_DATO rayada) y la MISMA
//    recomendación real (getPrediccion(cct) de la escuela seleccionada en la
//    tabla, igual que ExpedienteEscuela.jsx) -- panel condensado, no un
//    expediente nuevo. Los 2 botones inventados del mockup se reemplazan por
//    1 solo botón real: "Ver expediente completo", que navega a
//    /escuela/:cct (la MISMA ruta que ya usa P3/P4).
// 2) El "FARO // COPILOT" flotante del mockup (con su propia sugerencia de
//    consulta fija y sin backend) sigue sin reconstruirse: ya existe como
//    componente real montado una sola vez en App.jsx
//    (components/AsistenteFaro.jsx), igual que ya se documentó en
//    ExpedienteEscuela.jsx -- duplicarlo por pantalla lo desincronizaría del
//    chat real. Su nombre visible tampoco cambia a "FARO // COPILOT": el
//    spec (01_UX_Architecture.md §6) fija "Asistente FARO" como nombre en
//    toda superficie.
// 3) El "Glosario de Vectores" del mockup (D1-D6 con fuentes no verificadas
//    en este proyecto: SESNSP, INIFED, CONAGUA, SINICA, buffers de 500m/10km)
//    se reemplaza por el glosario metodológico real que ya existe
//    (components/GlosarioOverlay.jsx, usado en Home.jsx) -- mismo botón
//    visible que pide el mockup, contenido real en vez de uno nuevo sin
//    respaldo.
//
// Además, el modal de inducción del mockup trae su propio texto largo
// ("Esta herramienta permite consultar..."); el pop-up de bienvenida de P6
// tiene su propio texto MANDATADO, entre comillas, en
// 01_UX_Architecture.md §5 ("Esta es tu zona de exploración libre...") --
// ese texto es el que ya estaba en este archivo y se conserva literal
// (spec > mockup cuando el spec cita el texto exacto), solo con estilo
// visual más cercano al del mockup.
//
// Integridad de datos: el badge "N PLANTELES" del encabezado usa el total
// real de /escuelas (size=1, mismo patrón que getUniversoEscuelas() ya usa
// en Panorama.jsx) y solo se muestra en modo real -- en modo demo no hay un
// universo real que mostrar, así que se omite en vez de inventarlo. El pie
// de la tabla sí muestra el total ya real de cada consulta filtrada
// (Page.total), en demo y en real. La paginación (ANT/SIG) es real:
// /escuelas ya pagina con page/size (src/api/schemas.py:Page), así que se
// conecta en vez de dejar los botones del mockup sin función.

const CICLOS = ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"];

const ENTIDADES = [
  { cve: "09", nombre: "Ciudad de México" },
  { cve: "15", nombre: "Estado de México" },
  { cve: "19", nombre: "Nuevo León" },
  { cve: "14", nombre: "Jalisco" },
];

const NIVELES = [
  { cve: "DPR", nombre: "Primaria" },
  { cve: "DJN", nombre: "Preescolar" },
  { cve: "DES", nombre: "Secundaria" },
  { cve: "DCT", nombre: "Telesecundaria" },
];

const LLAVE_POPUP_VISTO = "faro_explorador_popup_visto_v1";
const TAMANO_PAGINA = 12;

async function fetchEscuelasFiltradas(filtros, pagina) {
  const params = {};
  if (filtros.ciclo) params.ciclo = filtros.ciclo;
  if (filtros.cve_ent) params.cve_ent = filtros.cve_ent;
  if (filtros.nivel) params.nivel = filtros.nivel;
  params.order_by = "indice_riesgo";
  params.order = "desc";
  params.size = String(TAMANO_PAGINA);
  params.page = String(pagina);
  const { data, error } = await getEscuelas(params);
  if (error) return { data: null, error };
  // Municipio/entidad reales del listado -- mismo patrón que
  // getConclusionEscuelas() en lib/api.js (una llamada por municipio único
  // de esta página, no por escuela).
  const municipios = await getMunicipiosPorClaves(data.items.map((e) => e.cve_mun));
  if (municipios.error) return { data: null, error: municipios.error };
  const items = data.items.map((e) => ({
    ...e,
    nombre_municipio: municipios.data[e.cve_mun]?.nombre_municipio ?? null,
    nombre_entidad: municipios.data[e.cve_mun]?.nombre_entidad ?? null,
  }));
  return { data: { items, total: data.total, page: data.page, size: data.size }, error: null };
}

// panoramaMock (no escuelasEnRiesgo) porque ya trae los 6 drivers planos
// (d1..d6) que el panel de "Expediente" condensado necesita -- mismo mock
// que Panorama.jsx, para no tener dos formas de datos de ejemplo distintas.
const MOCK_ENVUELTO = {
  items: panoramaMock.map((e) => ({ ...e, nombre_municipio: e.municipio, nombre_entidad: e.entidad })),
  total: panoramaMock.length,
  page: 1,
  size: panoramaMock.length,
};

export default function Explorador() {
  const outletCtx = useOutletContext();
  const onPreguntar = outletCtx?.onPreguntar;

  const [popupVisible, setPopupVisible] = useState(false);
  const [glosarioAbierto, setGlosarioAbierto] = useState(false);
  const [filtros, setFiltros] = useState({ ciclo: "", cve_ent: "", nivel: "" });
  const [pagina, setPagina] = useState(1);
  const { cortes } = useCortesAtencion();

  useEffect(() => {
    let visto = false;
    try {
      visto = localStorage.getItem(LLAVE_POPUP_VISTO) === "1";
    } catch {
      // Storage bloqueado: se trata como primera visita, no rompe la pantalla.
    }
    if (!visto) setPopupVisible(true);
  }, []);

  function cerrarPopup() {
    setPopupVisible(false);
    try {
      localStorage.setItem(LLAVE_POPUP_VISTO, "1");
    } catch {
      // Best-effort.
    }
  }

  // Cambiar cualquier filtro regresa a la página 1 -- si no, un cambio de
  // filtro podría dejar la vista en una página que ya no existe.
  useEffect(() => {
    setPagina(1);
  }, [filtros.ciclo, filtros.cve_ent, filtros.nivel]);

  // Demo explícito: el mock de "los 7 casos" no trae cve_ent/nivel reales por
  // escuela, así que en modo demo los filtros no recortan el set de ejemplo
  // (limitación documentada, no se inventa un catálogo de coincidencias
  // falso). El modo real sí filtra y pagina de verdad contra /escuelas.
  const { status, data, error } = useApiResource(() => fetchEscuelasFiltradas(filtros, pagina), {
    mock: MOCK_ENVUELTO,
    deps: [filtros.ciclo, filtros.cve_ent, filtros.nivel, pagina],
  });
  const escuelas = status === "ok" || status === "demo" ? data.items : [];
  const total = status === "ok" || status === "demo" ? data.total : null;
  const sinResultados = status === "ok" && escuelas.length === 0;
  const totalPaginas = total ? Math.max(1, Math.ceil(total / TAMANO_PAGINA)) : 1;

  // Universo total del alcance (mismo patrón que getUniversoEscuelas() en
  // Panorama.jsx) -- solo tiene sentido en modo real, un badge en modo demo
  // estaría mostrando el tamaño del mock, no un universo real.
  const { status: statusUniverso, data: universo } = useApiResource(() => getUniversoEscuelas(), {
    deps: [],
  });

  const filtrosActivos = [filtros.ciclo, filtros.cve_ent, filtros.nivel].filter(Boolean).length;

  // Escuela seleccionada en la tabla, para el panel de "Expediente"
  // condensado de la derecha (mismo layout dividido del mockup). Por
  // defecto, la primera fila de cada página/filtro -- si la selección
  // actual ya no está en la lista (cambió de página o de filtro), se
  // reasigna a la primera fila visible en vez de dejar el panel apuntando a
  // una escuela que ya no se ve en la tabla.
  const [cctSeleccionado, setCctSeleccionado] = useState(null);
  useEffect(() => {
    if (escuelas.length > 0 && !escuelas.some((e) => e.cct === cctSeleccionado)) {
      setCctSeleccionado(escuelas[0].cct);
    }
    if (escuelas.length === 0 && cctSeleccionado !== null) {
      setCctSeleccionado(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [escuelas]);
  const seleccionada = escuelas.find((e) => e.cct === cctSeleccionado) ?? null;

  // Recomendación real para el driver dominante de la escuela seleccionada
  // -- MISMA llamada que ExpedienteEscuela.jsx (getPrediccion(cct)), no un
  // catálogo inventado aquí. En demo, recomendacionGeneralPorDriver ya es el
  // catálogo prescriptivo real (Publicacion_Gold.md §4) usado como texto
  // GENERAL por driver, mismo criterio que Conclusion.jsx.
  const seleccionadaTienePrediccion = seleccionada?.tiene_prediccion ?? typeof seleccionada?.indice_riesgo === "number";
  const prediccionMock = seleccionada
    ? { recomendacion: recomendacionGeneralPorDriver[seleccionada.driver_dominante] ?? null }
    : null;
  const { data: prediccionSel } = useApiResource(
    () =>
      status === "ok" && seleccionadaTienePrediccion
        ? getPrediccion(cctSeleccionado)
        : Promise.resolve({ data: null, error: null }),
    { mock: prediccionMock, deps: [cctSeleccionado, seleccionadaTienePrediccion, status] }
  );

  return (
    <PageContainer>
      {/* Encabezado operativo */}
      <div
        className="rounded-2xl p-6 flex flex-col gap-3"
        style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", boxShadow: "var(--shadow-card)" }}
      >
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-label-micro-mono uppercase" style={{ color: "var(--faro-signal)" }}>
            Pantalla 06 · Vista maestra
          </span>
          <span style={{ color: "var(--color-ink-faint)" }}>·</span>
          <span className="text-label-micro-mono uppercase" style={{ color: "var(--color-ink-faint)" }}>
            Diagnóstico territorial estratificado
          </span>
        </div>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex flex-col gap-1.5" style={{ maxWidth: "42rem" }}>
            <h1 className="text-headline-xl" style={{ color: "var(--color-ink)" }}>
              Explorador de escuelas
            </h1>
            <p className="text-body-md" style={{ color: "var(--color-ink-faint)" }}>
              Sigue investigando otros casos con libertad, fuera de la narrativa guiada. Exploración
              acotada a las 4 entidades federativas del alcance del proyecto (Ciudad de México, Estado
              de México, Nuevo León y Jalisco).
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0 flex-wrap">
            <button
              type="button"
              onClick={() => setGlosarioAbierto(true)}
              className="text-label-ui inline-flex items-center gap-1.5 px-3 py-2 rounded-lg"
              style={{ background: "var(--color-surface-alt)", color: "var(--color-ink)" }}
            >
              <IconMenuBook size={16} style={{ color: "var(--faro-signal)" }} />
              Glosario
            </button>
            {statusUniverso === "ok" && typeof universo?.total === "number" && (
              <span
                className="text-label-data-mono inline-flex items-center gap-1.5 px-3 py-2 rounded-lg"
                style={{ background: "var(--color-surface-alt)", color: "var(--color-ink)" }}
              >
                <span className="w-2 h-2 rounded-full" style={{ background: "var(--faro-signal)" }} />
                {universo.total.toLocaleString("es-MX")} planteles en el alcance
              </span>
            )}
            {status === "demo" && <DemoBadge />}
          </div>
        </div>
      </div>

      {/* Filtros obligatorios */}
      <div
        className="rounded-2xl p-6 flex flex-col gap-4"
        style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", boxShadow: "var(--shadow-card)" }}
      >
        <div className="flex items-center justify-between flex-wrap gap-1">
          <span className="text-label-micro-mono uppercase" style={{ color: "var(--faro-signal)" }}>
            Parámetros de consulta
          </span>
          <span className="text-label-micro-mono uppercase" style={{ color: "var(--color-ink-faint)" }}>
            {filtrosActivos} de 3 filtros activos
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <label className="flex flex-col gap-1.5">
            <span className="text-label-ui inline-flex items-center gap-1.5" style={{ color: "var(--color-ink)" }}>
              <IconCalendarMonth size={15} style={{ color: "var(--faro-signal)" }} />
              1. Ciclo escolar
            </span>
            <select
              className="text-sm px-3 py-2 rounded-lg"
              style={{ border: "1px solid var(--color-border)", color: "var(--color-ink)", background: "var(--color-surface-alt)" }}
              value={filtros.ciclo}
              onChange={(e) => setFiltros((f) => ({ ...f, ciclo: e.target.value }))}
            >
              <option value="">Más reciente</option>
              {CICLOS.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-label-ui inline-flex items-center gap-1.5" style={{ color: "var(--color-ink)" }}>
              <IconLocationOn size={15} style={{ color: "var(--faro-signal)" }} />
              2. Entidad federativa
            </span>
            <select
              className="text-sm px-3 py-2 rounded-lg"
              style={{ border: "1px solid var(--color-border)", color: "var(--color-ink)", background: "var(--color-surface-alt)" }}
              value={filtros.cve_ent}
              onChange={(e) => setFiltros((f) => ({ ...f, cve_ent: e.target.value }))}
            >
              <option value="">Las 4 entidades</option>
              {ENTIDADES.map((ent) => (
                <option key={ent.cve} value={ent.cve}>{ent.nombre}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-label-ui inline-flex items-center gap-1.5" style={{ color: "var(--color-ink)" }}>
              <IconSchool size={15} style={{ color: "var(--faro-signal)" }} />
              3. Nivel educativo
            </span>
            <select
              className="text-sm px-3 py-2 rounded-lg"
              style={{ border: "1px solid var(--color-border)", color: "var(--color-ink)", background: "var(--color-surface-alt)" }}
              value={filtros.nivel}
              onChange={(e) => setFiltros((f) => ({ ...f, nivel: e.target.value }))}
            >
              <option value="">Todos los niveles</option>
              {NIVELES.map((niv) => (
                <option key={niv.cve} value={niv.cve}>{niv.nombre}</option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {status === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando escuelas…</p>
      )}
      {status === "error" && (
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No se pudieron cargar las escuelas ({error}).
        </p>
      )}
      {sinResultados && (
        // Literal del spec (§8, "Combinación de filtros sin resultados (P6)").
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>
          No hay escuelas que coincidan con estos filtros. Prueba con otra combinación.
        </p>
      )}

      {/* Layout dividido maestro (tabla) + detalle (expediente condensado de
          la escuela seleccionada) -- mismo grid de 12 columnas del mockup
          (7 + 5), con datos 100% reales en ambos lados. */}
      {escuelas.length > 0 && cortes && (
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-start">
          {/* Columna izquierda: tabla de resultados */}
          <div
            className="xl:col-span-7 rounded-2xl overflow-hidden flex flex-col"
            style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", boxShadow: "var(--shadow-card)" }}
          >
            {/* Encabezado de la tabla: mismo renglón "Muestra filtrada" +
                "Orden" del mockup, pero con los filtros y el orden REALES
                de esta consulta -- nunca "Estado de México (15) ·
                Secundaria" fijo si el usuario no eligió esos filtros. */}
            <div className="p-3 flex items-center justify-between flex-wrap gap-2" style={{ background: "var(--color-surface-alt)" }}>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-label-ui uppercase font-semibold" style={{ color: "var(--color-ink)" }}>
                  Muestra filtrada
                  {(filtros.cve_ent || filtros.nivel) && (
                    <>
                      {": "}
                      {[
                        filtros.cve_ent ? `${ENTIDADES.find((e) => e.cve === filtros.cve_ent)?.nombre} (${filtros.cve_ent})` : null,
                        filtros.nivel ? NIVELES.find((n) => n.cve === filtros.nivel)?.nombre : null,
                      ]
                        .filter(Boolean)
                        .join(" · ")}
                    </>
                  )}
                </span>
                <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
                  ({escuelas.length} de {typeof total === "number" ? total.toLocaleString("es-MX") : "…"} registros)
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-label-micro-mono font-medium" style={{ color: "var(--color-ink-faint)" }}>ORDEN:</span>
                <span className="text-label-micro-mono font-semibold" style={{ color: "var(--faro-signal)" }}>FARO_INDEX DESC</span>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="text-label-micro-mono uppercase" style={{ background: "var(--color-surface-alt)", color: "var(--color-ink-faint)" }}>
                    <th className="p-3 pl-4">CCT / Nombre del plantel</th>
                    <th className="p-3">Municipio / Estado</th>
                    <th className="p-3 text-center">Nivel</th>
                    <th className="p-3 text-center">FARO Score</th>
                    <th className="p-3 text-center">Atención</th>
                    <th className="p-3 text-right pr-4">Acción</th>
                  </tr>
                </thead>
                <tbody className="text-body-sm">
                  {escuelas.map((e) => {
                    const tienePrediccion = typeof e.indice_riesgo === "number";
                    const riesgo = tienePrediccion ? nivelRiesgo(e.indice_riesgo, cortes) : null;
                    const estaSeleccionada = e.cct === cctSeleccionado;
                    return (
                      <tr
                        key={e.cct}
                        onClick={() => setCctSeleccionado(e.cct)}
                        className="cursor-pointer transition-colors"
                        style={{
                          borderTop: "1px solid var(--color-border)",
                          background: estaSeleccionada ? "var(--color-surface-alt)" : "transparent",
                        }}
                      >
                        <td className="p-3 pl-4">
                          <div className="flex flex-col">
                            <span className="text-title-md" style={{ color: "var(--color-ink)" }}>{e.cct}</span>
                            <span className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>{e.nombre}</span>
                          </div>
                        </td>
                        <td className="p-3">
                          <span className="text-body-sm" style={{ color: "var(--color-ink)" }}>
                            {e.nombre_municipio ?? "SIN_DATO"}
                          </span>
                          {e.nombre_entidad && (
                            <span className="text-label-micro-mono block" style={{ color: "var(--color-ink-faint)" }}>
                              {e.nombre_entidad}
                            </span>
                          )}
                        </td>
                        <td className="p-3 text-center text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
                          {e.nivel}
                        </td>
                        <td className="p-3 text-center">
                          {tienePrediccion ? (
                            <span className="font-mono-dato text-sm font-semibold" style={{ color: riskRampColor(e.indice_riesgo) }}>
                              {e.indice_riesgo.toFixed(3)}
                            </span>
                          ) : (
                            <span className="text-label-micro-mono" style={{ color: "var(--color-sin-dato)" }}>SIN_DATO</span>
                          )}
                        </td>
                        <td className="p-3 text-center">
                          {riesgo ? (
                            <span className="text-label-micro-mono font-semibold" style={{ color: "var(--color-ink)" }}>
                              {riesgo.icon} {riesgo.label.toUpperCase()}
                            </span>
                          ) : (
                            <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>—</span>
                          )}
                        </td>
                        <td className="p-3 pr-4 text-right">
                          <button
                            type="button"
                            onClick={(ev) => {
                              ev.stopPropagation();
                              setCctSeleccionado(e.cct);
                            }}
                            className="text-label-ui px-3 py-1.5 rounded-md inline-block"
                            style={{
                              background: estaSeleccionada ? "var(--color-primary)" : "var(--color-surface-alt)",
                              color: estaSeleccionada ? "#ffffff" : "var(--color-ink)",
                              border: "1px solid var(--color-border)",
                            }}
                          >
                            {estaSeleccionada ? "EXPEDIENTE" : "VER"}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <div className="p-3 flex items-center justify-between flex-wrap gap-2" style={{ background: "var(--color-surface-alt)" }}>
              <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
                {typeof total === "number"
                  ? `Mostrando ${escuelas.length} de ${total.toLocaleString("es-MX")} planteles en coincidencia`
                  : `${escuelas.length} planteles en coincidencia`}
              </span>
              {status === "ok" && totalPaginas > 1 && (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    disabled={pagina <= 1}
                    onClick={() => setPagina((p) => Math.max(1, p - 1))}
                    className="text-label-micro-mono px-2 py-1 rounded"
                    style={{ background: "var(--color-surface)", color: "var(--color-ink)", opacity: pagina <= 1 ? 0.5 : 1 }}
                  >
                    ANT
                  </button>
                  <span className="text-label-micro-mono font-semibold" style={{ color: "var(--faro-signal)" }}>
                    {pagina} / {totalPaginas}
                  </span>
                  <button
                    type="button"
                    disabled={pagina >= totalPaginas}
                    onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
                    className="text-label-micro-mono px-2 py-1 rounded"
                    style={{ background: "var(--color-surface)", color: "var(--color-ink)", opacity: pagina >= totalPaginas ? 0.5 : 1 }}
                  >
                    SIG
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Columna derecha: expediente condensado de la escuela seleccionada
              -- misma gráfica de drivers real de la P4 (DriverBars.jsx), misma
              recomendación real (getPrediccion), sin duplicar ni inventar. */}
          {seleccionada && (() => {
            const riesgoSel = typeof seleccionada.indice_riesgo === "number" ? nivelRiesgo(seleccionada.indice_riesgo, cortes) : null;
            const driversParaGrafica = Object.fromEntries(
              DRIVERS.map((code) => {
                const raw = seleccionada[code.toLowerCase()];
                const sinDato = raw === null || raw === undefined;
                const valor = !sinDato && ORIENTADOS.includes(code) ? 1 - raw : raw;
                return [code, sinDato ? null : valor];
              })
            );
            const kDrivers = DRIVERS.filter((code) => driversParaGrafica[code] != null).length;
            const lugarSel = [seleccionada.nombre_municipio, seleccionada.nombre_entidad].filter(Boolean).join(", ");
            return (
              <div
                className="xl:col-span-5 rounded-2xl p-5 flex flex-col gap-4"
                style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", boxShadow: "var(--shadow-card)" }}
              >
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div className="flex flex-col gap-1 min-w-0">
                    <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--faro-signal)" }}>
                      Expediente diagnóstico en tiempo real
                    </span>
                    <h2 className="text-headline-sm" style={{ color: "var(--color-ink)" }}>{seleccionada.cct}</h2>
                    <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>{seleccionada.nombre}</p>
                    {lugarSel && (
                      <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>{lugarSel}</span>
                    )}
                  </div>
                  {riesgoSel && (
                    <span
                      className="text-label-ui font-bold px-2.5 py-1 rounded inline-flex items-center gap-1 shrink-0"
                      style={{ background: "var(--color-surface-alt)", color: "var(--color-ink)" }}
                    >
                      {riesgoSel.icon} ATENCIÓN {riesgoSel.label.toUpperCase()}
                    </span>
                  )}
                </div>

                <div className="p-3 rounded-xl flex items-center justify-between gap-3 flex-wrap" style={{ background: "var(--color-surface-alt)" }}>
                  <div className="flex flex-col">
                    <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--color-ink-faint)" }}>
                      Índice algorítmico FARO (normalizado)
                    </span>
                    {typeof seleccionada.indice_riesgo === "number" ? (
                      <div className="flex items-baseline gap-1">
                        <span className="font-mono-dato font-bold" style={{ fontSize: 30, lineHeight: 1, color: "var(--color-ink)" }}>
                          {seleccionada.indice_riesgo.toFixed(3)}
                        </span>
                        <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>/ 1.000</span>
                      </div>
                    ) : (
                      <span className="text-label-micro-mono" style={{ color: "var(--color-sin-dato)" }}>SIN_DATO</span>
                    )}
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--color-ink-faint)" }}>
                      Medidor de evidencia
                    </span>
                    <span className="text-title-md font-semibold" style={{ color: "var(--color-ink)" }}>{kDrivers} de 6 pistas</span>
                    <div className="grid grid-cols-6 gap-1" style={{ width: "6.5rem", height: 6 }}>
                      {DRIVERS.map((code) => (
                        <div
                          key={code}
                          className="h-full rounded-sm"
                          style={{ background: driversParaGrafica[code] != null ? "var(--faro-signal)" : "var(--color-border)" }}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-label-ui font-semibold uppercase" style={{ color: "var(--color-ink)" }}>
                      Descomposición por drivers (0.0 – 1.0)
                    </span>
                    <span className="text-label-micro-mono uppercase" style={{ color: "var(--color-ink-faint)" }}>Escala real del modelo</span>
                  </div>
                  <DriverBars drivers={driversParaGrafica} driverDominante={seleccionada.driver_dominante} />
                </div>

                {seleccionada.driver_dominante && (
                  <div className="p-3 rounded-xl flex flex-col gap-2" style={{ background: "var(--color-surface-alt)" }}>
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <span className="text-label-ui font-bold inline-flex items-center gap-1.5" style={{ color: "var(--color-ink)" }}>
                        <IconVerified size={16} style={{ color: DOMINANT_OUTLINE }} />
                        Driver dominante
                      </span>
                      <span
                        className="text-label-micro-mono font-semibold uppercase px-2 py-0.5 rounded"
                        style={{ background: DOMINANT_OUTLINE, color: "#ffffff" }}
                      >
                        {seleccionada.driver_dominante}: {driverNombres[seleccionada.driver_dominante]}
                      </span>
                    </div>
                    {seleccionadaTienePrediccion && prediccionSel?.recomendacion ? (
                      <p className="text-body-sm" style={{ color: "var(--color-ink)" }}>“{prediccionSel.recomendacion}”</p>
                    ) : (
                      <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>
                        Sin recomendación disponible (SIN_DATO).
                      </p>
                    )}
                  </div>
                )}

                <Link
                  to={`/escuela/${seleccionada.cct}`}
                  className="text-label-ui font-semibold px-4 py-2 rounded-lg inline-flex items-center justify-center gap-1.5 self-end"
                  style={{ background: "var(--color-primary)", color: "#ffffff" }}
                >
                  Ver expediente completo →
                </Link>
              </div>
            );
          })()}
        </div>
      )}

      <GlosarioOverlay abierto={glosarioAbierto} onCerrar={() => setGlosarioAbierto(false)} onPreguntar={onPreguntar} />

      {popupVisible && (
        <div
          className="fixed inset-0 z-[60] flex items-center justify-center p-4"
          style={{ background: "rgba(15, 23, 42, 0.5)" }}
          onClick={cerrarPopup}
        >
          <div
            className="w-full rounded-xl p-6 flex flex-col gap-4"
            style={{ maxWidth: "28rem", background: "var(--color-surface)", boxShadow: "var(--faro-shadow-modal)" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full" style={{ background: "var(--faro-signal)" }} />
              <span className="text-label-micro-mono uppercase" style={{ color: "var(--faro-signal)" }}>
                Explorador de escuelas
              </span>
            </div>
            <p className="text-sm leading-relaxed" style={{ color: "var(--color-ink)" }}>
              {/* Texto literal del pop-up, 01_UX_Architecture.md §5 -- se conserva
                  igual aunque el modal del mockup trae otro texto: el spec cita
                  este texto entre comillas como el que corresponde a P6. */}
              Esta es tu zona de exploración libre. Aquí puedes revisar cualquier otra escuela con los
              filtros de ciclo, entidad y nivel. Ya no es parte de la conclusión que acabas de ver: cada
              caso se analiza por separado.
            </p>
            <div className="flex justify-end pt-1">
              <button
                type="button"
                onClick={cerrarPopup}
                className="text-sm font-semibold px-4 py-2 rounded-md"
                style={{ background: "var(--color-primary)", color: "#ffffff" }}
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
