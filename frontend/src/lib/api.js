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

// Origen absoluto del API -- SOLO para el link de "Iniciar sesion" (US-405,
// ADR-012). El boton no puede pasar por el proxy /api/* de este frontend: la
// cookie anti-CSRF `faro_oauth_state` se tiene que fijar en el origen del API,
// no en el del frontend, o Google regresa a un origen que nunca la fijo y el
// callback responde 401. Variable separada de VITE_API_BASE_URL a proposito --
// esa se queda vacia (rutas relativas via proxy) y esta va con URL absoluta;
// compartir una sola variable para las dos rompe alguna de las dos.
//   - local:  VITE_API_ORIGIN=http://localhost:8000
//   - prod:   VITE_API_ORIGIN=https://<host real de faro-api> (coordinar con Christian/Luis --
//             ese mismo valor, sin / final, es el que Christian valida contra FRONTEND_REDIRECT_URIS)
const API_ORIGIN = import.meta.env.VITE_API_ORIGIN ?? "";

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
// Fix 11-sep (segunda revisión de Edgar, PR #302): la versión anterior
// desenvolvía el sobre de paginación pero devolvía data.items completo sin
// aplicar la línea de alerta ni el recorte que este mismo comentario ya
// prometía -- "Los 7 casos" podía mostrar escuelas fuera del umbral, más de
// siete registros, y tronaba en LosSieteCasos.jsx (`e.indice_riesgo.toFixed(2)`)
// si entraba un registro con indice_riesgo: null. Ahora:
//   1. descarta indice_riesgo no numérico (nunca truena .toFixed() en quien
//      consume esto);
//   2. aplica la línea de alerta real, indice_riesgo >= 0.50 (DEC-019, misma
//      que src/api/repositorio_gold.py);
//   3. recorta al conteo oficial de KpisOut.escuelas_en_riesgo -- ese número
//      es la fuente de verdad del backend, no "los que alcancen el umbral
//      en esta página".
//
// OJO -- gap de contrato encontrado al implementar esto: EscuelaOut (la
// forma real de cada fila) trae cct/nombre/nivel/indice_riesgo/
// driver_dominante/matricula_total/tiene_prediccion, pero NO latitud/
// longitud, NO nombre de municipio/entidad (solo cve_mun) y NO variación de
// matrícula por escuela. El mapa (MapaRiesgo/MapaCasos) y esos 2 campos NO
// se pueden conectar al API real todavía -- falta que alguien (DS/API) los
// agregue al contrato. Documentado también en PLAN_TRABAJO_E5.md.
const LINEA_ALERTA_RIESGO = 0.5;

export const getEscuelasEnRiesgo = async (size = 50) => {
  // El endpoint de lista devuelve un sobre de paginación (Page[EscuelaOut]:
  // { items, total, page, size }), no un arreglo -- bug encontrado 11-sep en
  // pruebas de "Los 7 casos" (la página se quedaba en blanco sin error
  // porque escuelas.length de un objeto es undefined). Se desenvuelve aquí
  // para que el resto del código siga tratando el resultado como arreglo.
  const [escuelasRes, kpisRes] = await Promise.all([
    request(
      `/api/v1/escuelas?${new URLSearchParams({ order_by: "indice_riesgo", order: "desc", size: String(size) })}`
    ),
    request("/api/v1/kpis"),
  ]);
  if (escuelasRes.error) return { data: null, error: escuelasRes.error };
  if (kpisRes.error) return { data: null, error: kpisRes.error };

  const enRiesgo = escuelasRes.data.items.filter(
    (e) => typeof e.indice_riesgo === "number" && e.indice_riesgo >= LINEA_ALERTA_RIESGO
  );
  return { data: enRiesgo.slice(0, kpisRes.data.escuelas_en_riesgo), error: null };
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
// `historial`: turnos previos del chat (pregunta del usuario + respuesta del agente),
// del mas antiguo al mas reciente, max. MAX_TURNOS_HISTORIAL turnos (10, ver
// src/api/schemas.py). Opcional y retrocompatible -- un arreglo vacio (default) se
// comporta igual que antes de este cambio. Contrato exacto y ejemplos:
// tests/test_agente_historial.py.
//
// OJO -- pendiente de acuerdo con backend (Andres/Karla, 11-sep): si una `respuesta`
// de un turno pasa de 500 caracteres, el contrato la rechaza con 422 al reenviarla.
// La decision es que trunque el API (en redactar_respuesta_con_llm, src/agente/llm.py),
// no este cliente -- no se agrega recorte aqui hasta que ese cambio este en main.
//
// Quien construya el estado del chat (turnos) debe pasar `historial` ya armado como
// lista de { pregunta, respuesta }; esta funcion solo lo reenvia tal cual.
export const postAgenteConsulta = (pregunta, historial = []) =>
  request("/api/v1/agente/consulta", {
    method: "POST",
    body: JSON.stringify({ pregunta, historial }),
  });

// --- Auth (US-402, US-405, C4, ADR-012) ---
export const getAuthMe = () => request("/api/v1/auth/me");

// Arranca el flujo de login (US-405). URL absoluta a proposito -- ver
// comentario de API_ORIGIN arriba: se lee en el momento del click, no al
// cargar el modulo, para que siempre use el origen real del tab (relevante
// si algun dia el front vive en mas de un origen valido).
export const getAuthLoginUrl = () =>
  `${API_ORIGIN}/api/v1/auth/login?redirect=${encodeURIComponent(window.location.origin)}`;

// Canje del codigo de un solo uso por la sesion, modo cookie (US-405,
// ADR-010, ADR-012). Ruta RELATIVA a proposito -- a diferencia del login de
// arriba, esta llamada SI va por el proxy same-origin de este frontend
// (via request(), que ya manda credentials: "same-origin"), porque la
// cookie httpOnly de sesion se tiene que fijar en el origen del frontend,
// no en el del API. Nunca toca JWT: la respuesta es SesionOut (solo
// expira_en), nunca TokenPair -- ver src/api/schemas.py.
export const postAuthExchange = (code) =>
  request("/api/v1/auth/exchange?sesion=cookie", {
    method: "POST",
    body: JSON.stringify({ code }),
  });

// Cierre de sesion: el frontend no guarda ni refresca tokens -- solo pide
// logout y la cookie httpOnly la borra el API.
export const postAuthLogout = () => request("/api/v1/auth/logout", { method: "POST" });

export const API_BASE_URL = BASE_URL;
