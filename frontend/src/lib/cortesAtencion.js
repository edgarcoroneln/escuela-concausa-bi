import { getVersion } from "./api.js";
import { useApiResource } from "./useApiResource.js";

// Umbrales de nivel de atención, leídos de GET /api/v1/version (público, sin
// login -- DEC-023/DEC-026, US-621, hallazgo de Diana 12-sep). NUNCA se
// escriben 0.50/0.30 a mano en el frontend: es el mismo patrón que causó
// BUG-058 (el diccionario de entidades hardcodeado). Ver nivelRiesgo() en
// data/mock.js, que ahora recibe estos cortes como parámetro en vez de
// tenerlos fijos.
//
// El mock de modo demo SÍ usa los valores ratificados por DEC-024
// (alta=0.50, media=0.30) -- eso es dato de ejemplo explícito bajo
// VITE_USE_MOCK, no el mismo error: la fuente de verdad en modo real sigue
// siendo /version, nunca un literal en este archivo.
const cortesAtencionMock = { alta: 0.5, media: 0.3, ancla_calibracion: 0.6 };

// Hook: { status: "loading" | "ok" | "demo" | "error", data: { alta, media, ancla_calibracion } | null }
export function useCortesAtencion() {
  const { status, data, error } = useApiResource(() => getVersion(), { mock: cortesAtencionMock });
  const cortes = status === "ok" ? data?.cortes_atencion : status === "demo" ? data : null;
  return { status, cortes: cortes ?? null, error };
}
