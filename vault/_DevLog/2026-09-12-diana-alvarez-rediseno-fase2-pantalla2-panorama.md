---
project: "FARO"
date: "2026-09-12"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — segunda de las 7 pantallas del rediseño Fase 2 (US-641): Pantalla 2 (Panorama de riesgo), primer uso real de DriverMatrix.jsx y corrección de su paleta de color."
touches: ["US-641", "US-621", "DEC-023", "DEC-024", "BUG-058"]
tags: [devlog, equipo-5, frontend, react, rediseño, ux-ui]
---

# DevLog — 2026-09-12 — Rediseño Fase 2 (US-641): Pantalla 2 (Panorama de riesgo)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/_DevLog/2026-09-12-diana-alvarez-rediseno-fase2-shell-y-pantalla1|DevLog de la Pantalla 1]]

## Contexto

Continuación pantalla por pantalla del rediseño Fase 2 (ver DevLog anterior, shell + Pantalla 1).
Diana confirmó avanzar tras resolver, en el camino, que su PR #325 (rename de ruta a
`/escuela/:cct`) traía sin querer 8 commits acumulados porque su branch personal
(`dev/diana-alvarez`) es también la rama de ese PR abierto en GitHub — cualquier commit nuevo se
sumaba automáticamente. Se separó el trabajo del rediseño a una rama local aparte,
`dev/diana-alvarez-rediseno` (sin subir, a petición de Diana), dejando `dev/diana-alvarez`/PR #325
exactamente como estaba. Esta Pantalla 2 se construyó ya sobre esa rama nueva.

## Qué se construyó

**`pages/Panorama.jsx`** (nueva, ruta `/panorama`), contra §2 "Pantalla 2" de
`01_UX_Architecture.md`:

- Frase central de revelación -- "N escuelas están en riesgo. Tenemos N casos por investigar." --
  con N siempre derivado de datos reales (`getPanoramaEscuelas()`, nunca escrito a mano). Es la
  única pantalla que revela este conteo (P1/`Home.jsx` explícitamente no lo hace).
- Matrícula agregada de los casos en riesgo ("dentro de la historia", como pide el spec) -- suma de
  `matricula_total` del conjunto, no la matrícula nacional de `KpisOut`.
- **Primer uso real de `components/DriverMatrix.jsx`**, que existía desde antes en el repo pero
  nunca se había conectado a ninguna pantalla -- `pages/MatrizDrivers.jsx` (ruta legada `/drivers`)
  se dejó "en construcción" en el PR #302 porque la matriz necesita el detalle (`d1`..`d6`) de cada
  escuela, uno a la vez (`GET /escuelas/{cct}`), y ese costo no se había asumido. El spec de UX/UI
  (§8) confirma que ese costo (~11 llamadas: conjunto + versión + N detalles) es exactamente el
  esperado para revelar el panorama, no un problema a resolver -- se conectó con `getPanoramaEscuelas()`
  nuevo en `api.js` (reutiliza `getEscuelasEnRiesgo()` + `Promise.all` de `getEscuela()` por caso).
- CTA "Elegir un caso →" hacia `/casos` (Pantalla 3).
- Estado de error literal del spec: "No pudimos cargar el panorama, intenta de nuevo." (sin
  detalle interno, a diferencia de otras pantallas que sí muestran el error crudo).

**Corrección encontrada de paso, no pedida:** `DriverMatrix.jsx` pintaba sus celdas con
`d3.interpolateRdYlGn` (semáforo rojo/amarillo/verde) -- exactamente el patrón que
`Design_Tokens_Stitch.md` rechaza ("Systematic Risk Drivers", igual que el semáforo de nivel de
atención que ya se corrigió en la entrega de ayer). Como el componente nunca se había usado en
pantalla, no había ninguna captura ni PR previo que reconciliar: se corrigió directo a la rampa
monocromática (`riskRampColor()`, el mismo helper que ya usa "Los 7 casos"), con su leyenda y el
color de texto de las celdas ajustados para seguir siendo legibles sobre el tono más oscuro de la
rampa.

`Home.jsx` (Pantalla 1): el CTA "Ver el panorama de riesgo →" que ayer apuntaba a `/vista-general`
(interino, porque Panorama no existía) ahora apunta a `/panorama`, la pantalla real.
`lib/navFases.js`: la fase 02 del sidebar apunta a `/panorama`; `/vista-general` pasa a la sección
"Vistas heredadas" (sigue existiendo y siendo alcanzable, ya no es el sustituto interino de la fase 2).

## Pendiente (sin tocar en esta sesión, explícito)

- **Filtros de §3** ("solo atenúan filas de la matriz, nunca recortan el conjunto, ninguna llamada
  nueva al API") -- no implementados en esta entrega. El spec no enumera explícitamente cuáles
  filtros tiene P2 (a diferencia de P6, que sí los nombra: ciclo/entidad/nivel), así que se prefirió
  no inventarlos sin confirmar con Diana en la revisión visual.
- **Carga fila por fila (§8)**: el spec pide que cada fila de la matriz muestre su propio estado de
  carga mientras llega su detalle, para no confundir "cargando" con `SIN_DATO`. Esta entrega usa un
  solo estado de carga para toda la matriz mientras resuelven las N llamadas en paralelo --
  simplificación deliberada; requiere extender `DriverMatrix.jsx` para aceptar un tercer estado por
  celda, no solo valor/`null`.
- Pantallas 3 a 6, siguiente turno tras revisión visual de Diana.

## Validación

- `python vault/_Meta/scripts/vault_lint.py .` → Vault limpio.
- Balance de llaves/paréntesis verificado por script en los 7 archivos tocados; mismo límite de
  siempre para `.jsx` en este entorno (sin `node --check` ni binarios nativos de lint disponibles) --
  verificación visual real queda en manos de Diana con `npm run dev`.
