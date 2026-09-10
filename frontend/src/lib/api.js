// Cliente del API real de FARO (contrato: api/openapi.v1.json).
// Base URL configurable por env var de Vite: VITE_API_BASE_URL
//   - local:  .env            -> http://localhost:8000
//   - prod:   .env.production -> https://faro-api-eanzfglvyq-uc.a.run.app
//
// Todas las funciones devuelven { data, error }. Nunca lanzan (throw) para que
// las páginas puedan hacer fallback a mock data mientras el resto de los
// equipos (C3 agente, C4 auth) termina su parte, sin romper la demo.

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request(path, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
      credentials: "include", // el API usa cookies/JWT de sesión (US-402 OAuth Google)
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

export const API_BASE_URL = BASE_URL;
