// Modo demo explícito para datos de ejemplo (revisión de Edgar en PR #302,
// 10-sep): los mocks de src/data/mock.js solo deben aparecer en pantalla
// cuando esta bandera está prendida A PROPÓSITO, nunca como fallback
// silencioso de un error de red o de un endpoint que aún no existe.
//
// Activarlo en desarrollo: agrega VITE_USE_MOCK=true a frontend/.env
// (NUNCA a .env.production -- ver sección Seguridad de la plantilla del PR).
export const isDemoMode = () => import.meta.env.VITE_USE_MOCK === "true";
