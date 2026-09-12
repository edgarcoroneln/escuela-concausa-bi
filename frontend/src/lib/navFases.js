// Fuente unica del mapeo de fases -> rutas para Sidebar.jsx y Header.jsx
// (evita que ambos mantengan su propia copia y se desincronicen). Ver el
// comentario largo en Sidebar.jsx para el porque de cada mapeo interino.
export const FASES = [
  { n: "01", label: "Entrada", to: "/", end: true },
  { n: "02", label: "Panorama de riesgo", to: "/panorama" },
  { n: "03", label: "Selección de caso", to: "/casos" },
  { n: "04", label: "Expediente", disabledHint: "Elige un caso en Selección de caso" },
  { n: "05", label: "Conclusión Top 3", to: "/conclusion" },
];

export const EXPLORACION = [
  { n: "06", label: "Explorador de escuelas", to: "/explorador" },
];

export const HEREDADAS = [
  { label: "Vista general", to: "/vista-general" },
  { label: "Mapa", to: "/mapa" },
  { label: "Matriz de drivers", to: "/drivers" },
  { label: "Comparación territorial", to: "/comparacion-territorial" },
  { label: "Comparativa", to: "/comparativa" },
  { label: "Hallazgos", to: "/hallazgos" },
];

// Ruta -> etiqueta de pantalla, para el breadcrumb del Header. La entrada
// dinamica "/escuela/:cct" se resuelve aparte (Header.jsx) porque lleva un
// parametro.
const TODAS = [...FASES, ...EXPLORACION, ...HEREDADAS];

export function tituloDeRuta(pathname) {
  if (pathname.startsWith("/escuela/")) return "Expediente";
  const exacta = TODAS.find((f) => f.to === pathname);
  if (exacta) return exacta.label;
  return null;
}
