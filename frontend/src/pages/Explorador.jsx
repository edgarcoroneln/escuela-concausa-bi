import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import Card from "../components/Card.jsx";
import { driverIcons, driverNombres, escuelasEnRiesgo as escuelasMock, nivelRiesgo } from "../data/mock.js";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";
import { getEscuelas } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { useCortesAtencion } from "../lib/cortesAtencion.js";

// Los 5 ciclos materializados hoy en Gold (src/modelos/generar_fixture.py::CICLOS) -- se muestran
// como opciones del filtro de ciclo (§3: "obligatorio, ciclo escolar"). Vacío = el más reciente
// materializado, que es lo que /escuelas usa por defecto si no se manda `ciclo` (§8.2).
const CICLOS = ["2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"];

// Las 4 entidades del alcance (SCOPE_ENTIDADES, CLAUDE.md §4 / tests/test_catalogo_client.py) --
// mismo catálogo fijo que ya se muestra en el panel de sesión del Sidebar, nunca un catálogo nuevo
// inventado aquí.
const ENTIDADES = [
  { cve: "09", nombre: "Ciudad de México" },
  { cve: "15", nombre: "Estado de México" },
  { cve: "19", nombre: "Nuevo León" },
  { cve: "14", nombre: "Jalisco" },
];

// Códigos reales de nivel educativo (src/modelos/generar_fixture.py: DPR/DJN/DES/DCT) -- EscuelaOut
// los trae tal cual, no hay catálogo de nombres largos en el contrato.
const NIVELES = [
  { cve: "DPR", nombre: "Primaria" },
  { cve: "DJN", nombre: "Preescolar" },
  { cve: "DES", nombre: "Secundaria" },
  { cve: "DCT", nombre: "Telesecundaria" },
];

const LLAVE_POPUP_VISTO = "faro_explorador_popup_visto_v1";

async function fetchEscuelasFiltradas(filtros) {
  const params = {};
  if (filtros.ciclo) params.ciclo = filtros.ciclo;
  if (filtros.cve_ent) params.cve_ent = filtros.cve_ent;
  if (filtros.nivel) params.nivel = filtros.nivel;
  params.order_by = "indice_riesgo";
  params.order = "desc";
  params.size = "50";
  const { data, error } = await getEscuelas(params);
  if (error) return { data: null, error };
  // Page[EscuelaOut]: { items, total, page, size } -- mismo sobre de paginación que
  // getEscuelasEnRiesgo() ya desenvuelve en lib/api.js.
  return { data: data.items, error: null };
}

// Pantalla 6 -- Explorador de escuelas (rediseño Fase 2, US-641), nueva. Contra
// 01_UX_Architecture.md §2 "Pantalla 6" y §7 (nombre elegido por Marina). Consolida el DESTINO de
// las 4 páginas heredadas (Mapa, Matriz de drivers, Comparación territorial, Comparativa) con los 3
// filtros obligatorios del §3 (ciclo, entidad, nivel) -- las 4 páginas heredadas NO se borran todavía
// (siguen listadas en "Vistas heredadas" del Sidebar) para no dejar a nadie del equipo sin acceso
// mientras se confirma que este Explorador cubre lo que cada una resolvía; ver DevLog de esta fecha
// para el detalle de qué falta reconciliar.
//
// Selección de escuela -> misma pantalla de expediente que la P4 (spec §2: "misma lógica de
// expediente, reutilizando sus mismas gráficas"), no una vista nueva -- por eso el CTA de cada
// escuela navega a /escuela/:cct, la MISMA ruta que P3 usa.
export default function Explorador() {
  const [popupVisible, setPopupVisible] = useState(false);
  const [filtros, setFiltros] = useState({ ciclo: "", cve_ent: "", nivel: "" });
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

  // Demo explícito: el mock de "los 7 casos" no trae cve_ent/nivel reales por escuela, así que en
  // modo demo los filtros no recortan el set de ejemplo (limitación documentada, no se inventa un
  // catálogo de coincidencias falso). El modo real sí filtra de verdad contra /escuelas.
  const { status, data, error } = useApiResource(() => fetchEscuelasFiltradas(filtros), {
    mock: escuelasMock,
    deps: [filtros.ciclo, filtros.cve_ent, filtros.nivel],
  });
  const escuelas = status === "ok" || status === "demo" ? data : [];
  const sinResultados = (status === "ok") && escuelas.length === 0;

  return (
    <PageContainer>
      <div className="flex items-start justify-between flex-wrap gap-4">
        <PageHeader
          kicker="Pantalla 06 · Exploración libre"
          title="Explorador de escuelas"
          subtitle="Sigue investigando otros casos con libertad, fuera de la narrativa guiada."
        />
        {status === "demo" && <DemoBadge />}
      </div>

      <Card title="Filtros">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <label className="flex flex-col gap-1 text-xs font-semibold" style={{ color: "var(--color-ink-faint)" }}>
            Ciclo escolar
            <select
              className="text-sm px-3 py-2 rounded-lg"
              style={{ border: "1px solid var(--color-border)", color: "var(--color-ink)" }}
              value={filtros.ciclo}
              onChange={(e) => setFiltros((f) => ({ ...f, ciclo: e.target.value }))}
            >
              <option value="">Más reciente</option>
              {CICLOS.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-xs font-semibold" style={{ color: "var(--color-ink-faint)" }}>
            Entidad
            <select
              className="text-sm px-3 py-2 rounded-lg"
              style={{ border: "1px solid var(--color-border)", color: "var(--color-ink)" }}
              value={filtros.cve_ent}
              onChange={(e) => setFiltros((f) => ({ ...f, cve_ent: e.target.value }))}
            >
              <option value="">Las 4 entidades</option>
              {ENTIDADES.map((ent) => (
                <option key={ent.cve} value={ent.cve}>{ent.nombre}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-xs font-semibold" style={{ color: "var(--color-ink-faint)" }}>
            Nivel educativo
            <select
              className="text-sm px-3 py-2 rounded-lg"
              style={{ border: "1px solid var(--color-border)", color: "var(--color-ink)" }}
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
      </Card>

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

      {escuelas.length > 0 && cortes && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {escuelas.map((e) => {
            const tienePrediccion = typeof e.indice_riesgo === "number";
            const color = tienePrediccion ? riskRampColor(e.indice_riesgo) : "var(--color-sin-dato)";
            const riesgo = tienePrediccion ? nivelRiesgo(e.indice_riesgo, cortes) : null;
            return (
              <Card key={e.cct} hover className="flex flex-col justify-between">
                <div>
                  <p className="text-sm font-bold mb-1" style={{ color: "var(--color-ink)" }}>{e.nombre}</p>
                  <p className="text-xs mb-0.5" style={{ color: "var(--color-ink-faint)" }}>{e.nivel} · CCT {e.cct}</p>
                  <p className="text-xs mb-3" style={{ color: "var(--color-ink-faint)" }}>
                    Matrícula: {e.matricula_total?.toLocaleString("es-MX") ?? "SIN_DATO"}
                  </p>
                  {tienePrediccion ? (
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg font-extrabold tabular" style={{ color: "var(--color-ink)" }}>
                        {e.indice_riesgo.toFixed(2)}
                      </span>
                      <span className="text-[11px] font-semibold" style={{ color: "var(--color-ink)" }}>
                        {riesgo.icon} {riesgo.label}
                      </span>
                    </div>
                  ) : (
                    <p className="text-xs mb-2" style={{ color: "var(--color-ink-faint)" }}>
                      Sin predicción disponible (SIN_DATO)
                    </p>
                  )}
                  {e.driver_dominante && (
                    <span
                      className="text-xs font-semibold px-2.5 py-1 rounded-full inline-flex items-center gap-1.5"
                      style={{ background: "var(--color-surface)", border: `2px solid ${DOMINANT_OUTLINE}`, color: "var(--color-ink)" }}
                    >
                      <span>{driverIcons[e.driver_dominante]}</span>
                      {driverNombres[e.driver_dominante]}
                    </span>
                  )}
                </div>
                <Link
                  to={`/escuela/${e.cct}`}
                  className="text-sm font-semibold mt-4 inline-block"
                  style={{ color: "var(--color-primary)" }}
                >
                  Abrir expediente →
                </Link>
              </Card>
            );
          })}
        </div>
      )}

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
            <span className="font-mono-dato text-[10px] uppercase font-semibold tracking-wider" style={{ color: "var(--faro-signal)" }}>
              Explorador de escuelas
            </span>
            {/* Texto literal del pop-up, 01_UX_Architecture.md §5. */}
            <p className="text-sm leading-relaxed" style={{ color: "var(--color-ink)" }}>
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
