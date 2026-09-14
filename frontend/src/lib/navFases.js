// Fuente unica del mapeo de fases -> rutas para Sidebar.jsx y Header.jsx
// (evita que ambos mantengan su propia copia y se desincronicen). Ver el
// comentario largo en Sidebar.jsx para el porque de cada mapeo interino.
//
// 13-sep -- pase de fidelidad "P1 Entrada" con Diana: pidio que el menu
// izquierdo respete el orden Y LOS NOMBRES exactos de mockups/01_Entrada.html.
// Cambios respecto a la version anterior:
//   - Los items 01-06 vivian en 2 arreglos separados (FASES + EXPLORACION,
//     bajo 2 etiquetas "Investigacion guiada" / "Exploracion libre"). En la
//     plantilla los 7 items (00-06) son UNA sola lista bajo una sola
//     etiqueta "Flujo de Investigacion" -- se fusionan aqui en un solo
//     arreglo FASES.
//   - Nombres corregidos 1:1 con el mockup: "Panorama de riesgo" ->
//     "Panorama de Riesgo", "Selección de caso" -> "Selección de Caso",
//     "Expediente" -> "Expediente de Escuela", "Conclusión Top 3" ->
//     "Conclusión Global" (asi le llama el mockup, aunque el resto del
//     proyecto -- PLAN_TRABAJO.md, US-xxx -- use "Top 3"; se prioriza la
//     plantilla porque Diana pidio fidelidad literal de nombres en este
//     punto), "Explorador de escuelas" -> "Explorador de Escuelas".
//   - El item "00 Iniciar Sesión" del mockup NO se agregó en esa ronda: en
//     el prototipo estatico las 7 pantallas comparten un solo <aside> que
//     enumera las 7 vistas como pasos de una demo, incluido el login: en
//     la app real Login vive fuera del shell autenticado (main.jsx: ruta
//     "/login" aparte, sin Sidebar), asi que mostrar "Iniciar Sesión" como
//     item de navegacion DENTRO de una sesion ya autenticada no tendria
//     sentido funcional -- se documentó la omision en vez de copiarla ciega.
//   - Se agrega REFERENCIA_TECNICA ("US" Cómo funciona FARO, "ID" Guía de
//     Identidad), la 2da seccion del menu del mockup. Ambos items quedan
//     con disabledHint porque ninguno tiene ruta real todavia: "Cómo
//     funciona FARO" es la superficie US-601 del Equipo 1, ya construida
//     pero sin mergear a main (confirmado por git diff origin/main...
//     origin/dev/manuel-serrania, ver mensaje que se le redacto a Diana
//     para el equipo el 13-sep); "Guía de Identidad" no tiene ningun
//     avance conocido en el repo.
//
// 13-sep, segunda ronda -- Diana pidió explícitamente agregar "Iniciar
// Sesión" arriba de "Entrada a FARO", revirtiendo la omisión de arriba: se
// agrega como "00", con ruta real a /login (no disabledHint -- la ruta
// existe y funciona, solo vive fuera del shell autenticado). Si alguien
// hace clic estando ya autenticado, simplemente vuelve a ver Login.jsx (esa
// ruta no depende de la sesión para renderizar, ver main.jsx).
//
// 13-sep, tercera ronda -- reconciliación contra el PR #350 de Héctor
// Morales (US-601, "Cómo funciona FARO"), ya mergeado a main. Su rama
// adoptó a propósito los mismos 2 nombres que Diana ya había dejado aquí
// como placeholder ("Cómo funciona FARO" bajo "Referencia Técnica",
// comentario del PR #350) para que reconciliar fuera solo habilitar el
// item, no fusionar 2 definiciones distintas. Se hace exactamente eso:
// "Cómo funciona FARO" deja de ser disabledHint y pasa a rutear a la
// página real que trajo su PR (/como-funciona, pages/ComoFunciona.jsx).
// "Guía de Identidad" se queda tal cual (disabledHint): no es parte del
// PR #350, sigue sin ningún avance conocido en el repo -- no se inventa
// una ruta ni se quita el item solo porque su vecino ya se resolvió.
// 13-sep, cuarta ronda -- 3 pedidos puntuales de Diana sobre este mismo menu,
// posteriores a las 3 rondas documentadas arriba:
//   1) Se quita "00 Iniciar Sesión" (revirtiendo la segunda ronda): el item vivía
//      SOLO en este rail, que a su vez solo se renderiza dentro del shell
//      autenticado (Sidebar.jsx recibe `session`, App.jsx lo monta junto al resto
//      de rutas protegidas) -- por eso alguien ya con sesión iniciada lo veía en su
//      propio menú, sin sentido funcional. El botón real de "Iniciar sesión" sigue
//      existiendo para quien SÍ está anónimo: vive en Header.jsx (esquina superior
//      derecha, getAuthLoginUrl()), fuera de esta lista -- no se toca aquí.
//   2) Se quita "04 Expediente de Escuela" de la lista: era un item disabledHint
//      (sin ruta propia, solo un aviso de "Elige un caso en Selección de Caso"),
//      no una pantalla a la que se navegue directo desde el menú -- se sigue
//      llegando al expediente real (`/escuela/:cct`) desde los links "Ver/Abrir
//      expediente completo" de Explorador.jsx y LosSieteCasos.jsx, que no dependen
//      de este arreglo. Los items siguientes se renumeran (05->04, 06->05) para
//      que la numeración visible en el rail angosto (<768px, ver Sidebar.jsx) siga
//      siendo consecutiva.
//   3) Se quita "Guía de Identidad" de REFERENCIA_TECNICA: seguía sin ningún avance
//      conocido en el repo (a diferencia de "Cómo funciona FARO", ya resuelto en la
//      tercera ronda) y sin fecha de entrega -- un item permanentemente
//      deshabilitado invita a preguntar "¿cuándo se habilita esto?" sin que haya
//      una respuesta real. Si el equipo la retoma más adelante, se vuelve a agregar
//      con ruta real en vez de reponer el placeholder.
export const FASES = [
  { n: "01", label: "Entrada a FARO", to: "/", end: true },
  { n: "02", label: "Panorama de Riesgo", to: "/panorama" },
  { n: "03", label: "Selección de Caso", to: "/casos" },
  { n: "04", label: "Conclusión Global", to: "/conclusion" },
  { n: "05", label: "Explorador de Escuelas", to: "/explorador" },
];

export const REFERENCIA_TECNICA = [
  { n: "US", label: "Cómo funciona FARO", to: "/como-funciona" },
];

// Las 6 vistas "heredadas" de Fase 1 (vista-general, mapa, drivers,
// comparacion-territorial, comparativa, hallazgos) se retiraron el 12-sep
// (decisión de arquitectura de Marina García del Buey): la arquitectura
// final del producto son estas 7 pantallas, sin una sección secundaria de
// vistas duplicadas.
//
// Ruta -> etiqueta de pantalla, para el breadcrumb del Header. La entrada
// dinamica "/escuela/:cct" se resuelve aparte (Header.jsx) porque lleva un
// parametro. NOTA: Header.jsx dejo de usar este helper para el breadcrumb
// (ahora muestra el texto estatico "SURVEILLANCE_NODE" de la plantilla);
// se conserva por si se retoma un breadcrumb dinamico mas adelante.
const TODAS = [...FASES, ...REFERENCIA_TECNICA];

export function tituloDeRuta(pathname) {
  if (pathname.startsWith("/escuela/")) return "Expediente de Escuela";
  const exacta = TODAS.find((f) => f.to === pathname);
  if (exacta) return exacta.label;
  return null;
}
