// Cliente del API real de FARO (contrato: api/openapi.v1.json).
// Base URL configurable por env var de Vite: VITE_API_BASE_URL
//   - local:  NO se define -> "" (rutas relativas; server.proxy de Vite las
//             manda a localhost:8000, ver vite.config.js)
//   - prod:   se sirve en el MISMO origen vía proxy nginx (ADR-012, Luis) ->
//             VITE_API_BASE_URL vacío en .env.production
//
// Todas las funciones devuelven { data, error }. Nunca lanzan (throw) para que
// la página decida cómo mostrar el error.
//
// OJO -- corregido 10-sep (revisión de Edgar, PR #302): antes este comentario
// decía que las páginas podían caer a mock data en error para "no romper la
// demo". Eso es justo el patrón que se pidió eliminar: un error real de red
// NUNCA debe disfrazarse de dato de ejemplo en silencio. El único mock
// permitido es el modo demo explícito de ./demoMode.js (VITE_USE_MOCK=true).
// Ver useApiResource.js para el patrón de carga recomendado.

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

async function request(path, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
      credentials: "same-origin", // mismo origen vía proxy nginx (ADR-012); la cookie httpOnly viaja sola
      ...options,
    });
    if (!res.ok) {
      return { data: null, error: `${res.status} ${res.statusText}` };
    }
    return { data: await res.json(), error: null };
  } catch (err) {
    return { data: null, error: err.message ?? "network_error" };
  }
}

// --- KPIs y catálogos ---
export const getKpis = () => request("/api/v1/kpis");
export const getEscuelas = (params = {}) =>
  request(`/api/v1/escuelas?${new URLSearchParams(params)}`);
export const getEscuela = (cct) => request(`/api/v1/escuelas/${cct}`);

// "Los 7 casos" -- escuelas en riesgo. El endpoint NO admite un filtro
// indice_riesgo_min (revisión de Edgar en PR #302, 10-sep): el contrato
// disponible es ordenar. Se pide el catálogo ordenado desc por indice_riesgo
// y se valida/recorta contra el conteo real de KpisOut.escuelas_en_riesgo.
//
// OJO -- gap de contrato encontrado al implementar esto: EscuelaOut (la
// forma real de cada fila) trae cct/nombre/nivel/indice_riesgo/
// driver_dominante/matricula_total/tiene_prediccion, pero NO latitud/
// longitud, NO nombre de municipio/entidad (solo cve_mun) y NO variación de
// matrícula por escuela. El mapa (MapaRiesgo/MapaCasos) y esos 2 campos NO
// se pueden conectar al API real todavía -- falta que alguien (DS/API) los
// agregue al contrato. Documentado también en PLAN_TRABAJO_E5.md.
export const getEscuelasEnRiesgo = async (size = 50) => {
  // El endpoint de lista devuelve un sobre de paginación (Page[EscuelaOut]:
  // { items, total, page, size }), no un arreglo -- bug encontrado 11-sep en
  // pruebas de "Los 7 casos" (la página se quedaba en blanco sin error
  // porque escuelas.length de un objeto es undefined). Se desenvuelve aquí
  // para que el resto del código siga tratando el resultado como arreglo.
  const { data, error } = await request(
    `/api/v1/escuelas?${new URLSearchParams({ order_by: "indice_riesgo", order: "desc", size: String(size) })}`
  );
  if (error) return { data: null, error };
  return { data: data.items, error: null };
};
export const getMunicipios = (params = {}) =>
  request(`/api/v1/municipios?${new URLSearchParams(params)}`);
export const getMunicipio = (cveMun) => request(`/api/v1/municipios/${cveMun}`);

// --- Predicciones / ML ---
export const getPrediccion = (cct) => request(`/api/v1/predicciones/${cct}`);
export const getPrediccionExplicacion = (cct) =>
  request(`/api/v1/predicciones/${cct}/explicacion`);
export const postPrediccionesBatch = (ccts) =>
  request("/api/v1/predicciones/batch", { method: "POST", body: JSON.stringify({ ccts }) });

// --- Agente (chat) ---
export const postAgenteConsulta = (pregunta) =>
  request("/api/v1/agente/consulta", { method: "POST", body: JSON.stringify({ pregunta }) });

// --- Auth (US-402, C4) ---
export const getAuthMe = () => request("/api/v1/auth/me");
export const getAuthLoginUrl = () => `${BASE_URL}/api/v1/auth/login`;
// Cierre de sesión (agregado 11-sep, revisión de seguridad de Christian):
// el frontend no guarda ni refresca tokens -- solo pide logout y la cookie
// httpOnly la borra el API. Falta el botón/UI que lo dispare (Topbar.jsx
// hoy no tiene ningún estado de sesión todavía).
export const postAuthLogout = () => request("/api/v1/auth/logout", { method: "POST" });

export const API_BASE_URL = BASE_URL;
