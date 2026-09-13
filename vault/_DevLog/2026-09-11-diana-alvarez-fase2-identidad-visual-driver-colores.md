---
project: "FARO"
date: "2026-09-11"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — Fase 2 de identidad visual (rampa de riesgo + iconos de nivel, sustituyendo colores rechazados) sobre el PR #302 ya mergeado, y corrección de un desvío propio de la estrategia de ramas."
touches: ["US-621", "US-641", "REQ-002"]
tags: [devlog, equipo-5, frontend, react, identidad-visual, ownership]
---

# DevLog — 2026-09-11 — Fase 2 de identidad visual: rampa de riesgo + iconos, y corrección de rama

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity|03_Visual_Identity]] ·
[[vault/05_Engineering/Branching_Strategy|Branching Strategy]] · [[vault/08_CICD_DevOps/PLAN_TRABAJO_E5|Plan de trabajo E5]]

## Contexto

`PR #302` (Fase 1: tokens de identidad — colores, tipografía, radios, elevación) ya se había mergeado
a `main`. `03_Visual_Identity.md` (Juan Macías, `approved`) prohíbe explícitamente dos patrones que el
frontend seguía usando: un color fijo por driver (`driverColors`, `D1`…`D6`) y un semáforo
rojo/ámbar/verde para el nivel de atención (`nivelRiesgo()` devolvía `{label, color}`). Ambos quedan
etiquetados "RECHAZADO, NO USAR" en el documento — el reemplazo es una rampa secuencial de un solo tono
(`#EEF2F7→#0F172A`, 5 paradas) para cualquier magnitud 0→1, un acento ámbar `#B45309` **solo de
contorno** para el driver dominante, y nivel de atención por **icono + texto únicamente**
(▲ alta / ■ media / ● baja), nunca color.

## Qué se hizo

**`frontend/src/lib/riskRamp.js` (nuevo).** `riskRampColor(value)` sobre `d3.scaleLinear().domain([0,
0.25, 0.5, 0.75, 1]).range([...5 paradas]).clamp(true)`, con `SIN_DATO` explícito para `null`/`NaN`;
`DOMINANT_OUTLINE` (`#b45309`) y `NIVEL_ICONOS` (▲/■/●) como constantes compartidas.

**`frontend/src/data/mock.js`.** Se elimina `driverColors` por completo. `nivelRiesgo()` cambia de
`{label, color}` a `{label, icon}`.

**6 usos corregidos** en `ExpedienteEscuela.jsx`, `DifferentiatorChart.jsx`, `MapaRiesgo.jsx`,
`LosSieteCasos.jsx` y `Hallazgos.jsx`: todo color por driver pasa a `riskRampColor(...)`; el badge de
"Driver dominante" pasa de relleno de color a contorno ámbar (`DOMINANT_OUTLINE`); el nivel de riesgo
se pinta con icono + texto en vez de color. En `LosSieteCasos.jsx` se agregó además el icono/etiqueta
de nivel a la leyenda de "Índice de riesgo" de cada tarjeta — no pedido explícitamente, pero la tarjeta
codificaba el nivel **solo por color** sin texto en ningún lado, la misma violación que el documento
prohíbe.

Verificado en navegador por Diana (capturas): expediente, "Los 7 casos" y "Vista general" muestran el
patrón correcto — índice en texto oscuro + icono de nivel, badge de driver en contorno ámbar con su
propio icono, sin ningún color codificando riesgo o driver.

## Desvío de la estrategia de ramas — encontrado y corregido antes de pushear a `main`

Este trabajo se hizo primero en una rama nueva (`dev/diana-alvarez-identidad-visual`), abierta para
respetar la instrucción de no seguir tocando `dev/diana-alvarez` mientras Edgar revisaba el PR #302 en
curso. Al ir a pushearla, `vault/05_Engineering/Branching_Strategy.md` (v2.0, dueño Edgar) señala que
es exactamente el antipatrón que el documento nombra explícito: **una rama por persona, permanente,
nunca una rama por historia** — "es exactamente como una misma persona termina con dos ramas gemelas
para el mismo trabajo". La instrucción de no tocar el PR en revisión era válida; la solución correcta
era esperar en `dev/diana-alvarez` sin pushear, no abrir una segunda rama.

Con el PR #302 ya mergeado, se corrigió antes de tocar `main` otra vez: `git checkout
dev/diana-alvarez`, `git merge origin/main` (fast-forward limpio a `b0fdb54`), `git cherry-pick` del
commit de Fase 2 (`0aa01ee` → `f84859c` en `dev/diana-alvarez`, sin conflictos). La rama
`dev/diana-alvarez-identidad-visual` queda sin usar (no se borra — regla de bloqueo de borrado en
`dev/*` — y de cualquier forma el modelo no la necesita).

## Pruebas ejecutadas

```
Verificación manual en navegador (npm run dev, Diana), tras el cherry-pick sobre dev/diana-alvarez
sincronizada con main (b0fdb54):
  - Expediente de escuela: índice "▲ Alta · Índice de riesgo" (icono + texto, sin color) +
    "Driver dominante: Inseguridad" en contorno ámbar.
  - "Los 7 casos": mismo patrón en las 12 tarjetas visibles, badges de driver con icono propio,
    sin color fijo por driver.
  - "Vista general" · El diferenciador: comparativo Madero vs. Flores Magón con badges D4/D2 en
    contorno ámbar, sin colores distintos por driver.
```

No se corrió en este entorno (bash de edición, no el de Diana): `npm run dev` / `npm ci` — corridos y
confirmados por Diana vía capturas de navegador. `vault_lint.py` corrido en este entorno: limpio.

## Bloqueantes

Ninguno para este cambio en sí. Pendiente general del frente (documentado en la evidencia del
2026-09-11 anterior): botón de login sin construir (`ADR-012` define a dónde debe apuntar cuando se
implemente), y `MapaCasos`/`MatrizDrivers`/`ComparacionTerritorial`/`Comparativa` siguen bloqueadas por
gap de contrato del API.

## Próximos pasos

Abrir PR desde `dev/diana-alvarez` (ya sincronizada con `main`) para este commit; solicitar revisión
del PM.
