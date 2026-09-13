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

// Referencia Técnica (US-601): documenta cómo funciona el sistema -- componentes, modelo de
// datos, capas, cubos, decisiones y modelos. No lleva número de fase a propósito: no forma parte
// del relato de los 7 casos, se consulta aparte.
//
// **Nombres alineados con la reestructura de Diana Alvarez** (comentario en el PR #350, 13-sep):
// ella ya dejó en su rama un placeholder deshabilitado llamado "Cómo funciona FARO" bajo una
// sección "Referencia Técnica", anticipando que esto llegaría. Se adoptan sus dos nombres tal
// cual para que al reconciliar no queden dos entradas compitiendo: su placeholder y esta entrada
// son el mismo item, así que el merge es habilitarlo, no fusionar dos definiciones.
export const REFERENCIA = [
  { label: "Cómo funciona FARO", to: "/como-funciona" },
];

// Las 6 vistas "heredadas" de Fase 1 (vista-general, mapa, drivers,
// comparacion-territorial, comparativa, hallazgos) se retiraron el 12-sep
// (decisión de arquitectura de Marina García del Buey): la arquitectura
// final del producto son estas 7 pantallas, sin una sección secundaria de
// vistas duplicadas.
//
// Ruta -> etiqueta de pantalla, para el breadcrumb del Header. La entrada
// dinamica "/escuela/:cct" se resuelve aparte (Header.jsx) porque lleva un
// parametro.
const TODAS = [...FASES, ...EXPLORACION, ...REFERENCIA];

export function tituloDeRuta(pathname) {
  if (pathname.startsWith("/escuela/")) return "Expediente";
  const exacta = TODAS.find((f) => f.to === pathname);
  if (exacta) return exacta.label;
  return null;
}
