---
project: "FARO"
date: "2026-09-06"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "cierre de estado previo a la demo: 23 historias a done, con la deuda de cada una escrita en vez de borrada"
tags: [devlog, pm, execution-status, cierre, dec-020, dec-012, demo]
---

# DevLog — 2026-09-06 — Cierre de estado: 23 historias, con su deuda escrita

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/12_Roadmap_Sprints/Execution_Status]] ·
[[vault/10_Risk_Governance/Decision_Log]]

## Qué se hizo

Cierre de estado antes de la demo del 9. Se pasaron **23 historias a `done`**: el tablero va de
**52/89 (78.1 %) a 75/89 (88.5 %)**.

Se hizo una triaje de las 37 abiertas con tres preguntas por historia: (1) ¿la evidencia ya está en
`main`?, (2) ¿su entregable es una superficie desplegada, y por tanto manda `DEC-012`?, (3) ¿se va a
ver su ausencia el miércoles?

### Grupo A — 6 historias donde el registro iba atrasado

`US-526`, `US-405`, `US-207`, `US-522b`, `US-524a`, `US-215b`.

Aquí cerrar **corrige** el récord, no lo infla. `US-526` decía `planned` mientras FARO Web llevaba
horas sirviendo en Cloud Run. `US-405` decía *"solo andamiaje"* con el PR #267 de Christian ya
dentro. Y tres filas —`US-522b`, `US-524a`, `US-215b`— citaban PRs *"abiertos, pendientes de merge"*
que **ya estaban mergeados**: se verificó contra GitHub uno por uno (#87, #102, #228).

### Grupo D — 17 historias cerradas por decisión del PO

`US-004`, `US-005`, `US-113`, `US-204`, `US-302`, `US-303`, `US-304a`, `US-304b`, `US-313`,
`US-322`, `US-324`, `US-325`, `US-403`, `US-504`, `US-521c`, `US-522a`, `US-522c`.

Son historias en `in_review` cuyo "falta" era **ratificación, no trabajo**: *"falta ratificar la
política"*, *"falta revisión de los dueños de cada modelo"*, *"falta correr métricas sobre el Gold
actual"*.

**Se cierran sin la confirmación de cada dueño, y eso está escrito en cada fila.** La recomendación
del análisis era pedir una línea a cada uno; el PO decidió cerrarlas para llegar al ensayo con el
tablero al día. Para que la decisión sea defendible y no una afirmación falsa, **el "falta" no se
borró: se convirtió en deuda declarada** dentro de la misma celda de evidencia. Cada fila dice qué
la cierra **y** qué queda pendiente.

Las deudas que conviene tener presentes porque son visibles o contradictorias:

- **`US-324`** — la ficha de modelo de ML-03 **afirma implementación** mientras `US-321` sigue
  `in_progress` y el Panel de ML imprime `SIN_DATO` en pantalla. Es una contradicción que un
  evaluador puede encontrar. Corregir la ficha es seguimiento inmediato post-demo; no se tocó aquí
  porque el archivo es de C3.
- **`US-521c` / `US-522c`** — el DevLog de Edward Ruiz sigue **sin extensión `.md`, sin ID y sin
  estado válido**, así que el linter no lo evalúa. Incumple `Definition_of_Filed` y se cierra la
  historia con el incumplimiento anotado.
- **`US-005`** — cierra el entregable, **no** el problema que documenta: la rotación del Vault
  Steward no operó en S1–S4 y el costo está medido en el propio documento.
- **`US-302`** — se abre `BUG-062` sobre la misma historia: el argmax compara drivers normalizados
  min-max sobre coberturas distintas, así que D6 sale inflado. No se corrige antes del 9.
- **`US-204`** — la validación de DB-06/DB-09 se hizo sobre mock identificado como tal; repetirla
  contra las 45 356 predicciones reales quedaba pendiente y **no se hizo**.

### Lo que NO se tocó

El **grupo C** —`US-321`, `US-114`, `US-524c`, `US-525b`, `US-525c`— se dejó intacto. Son historias
sin PR ni commit, y en el caso de `US-321` marcarla `done` se contradiría con lo que el evaluador ve
en pantalla. La vía honesta para ésas es `descoped` con motivo y fecha, no `done`; queda a decisión
del PO y fuera de este cambio.

## Lo que queda abierto — 14 historias

**Post-despliegue o post-ensayo (9), que es exactamente lo que debe quedar abierto:** `US-006`
(falta el ensayo, lo pide su propio objetivo), `US-305` (E2E del chat con sesión contra producción),
`US-505` (*despliegue final y verificación*, la última por diseño), `US-423` (smoke de seguridad
contra la URL), `US-215a` (7 de 20 casos), `US-404`, `US-422`, `US-521b`, `US-524b`.

**Grupo C (5), pendiente de decisión de alcance:** `US-114`, `US-321`, `US-524c`, `US-525b`,
`US-525c`.

## Decisiones

- El grupo D cierra por decisión del PO **con el residual escrito**, no borrado. Un `done` con deuda
  declarada es defendible; un `done` que borra el "falta" no lo es.
- El grupo C **no** se cierra: si su ausencia se ve en la demo, `descoped` es el estado honesto.
- A partir de aquí los ajustes van **directo a producción**, con PRs de sincronía para que `main` y
  el local no se queden atrás. Eso ensancha a propósito el hueco que ya describe `BUG-061` —`main`
  no reproduce lo que corre en producción— y conviene tenerlo presente al declarar la deuda.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog.
- **Modificados:** `vault/12_Roadmap_Sprints/Execution_Status.md` (23 filas: estado, evidencia y
  fecha), `vault/02_Requirements/Traceability_Matrix.md`, `vault/_DevLog/_index.md` y los dos
  archivos generados del tablero PM.
- **Verificado por el agente antes de escribir:** el estado real en GitHub de los PRs #87, #102,
  #228, #131 y #132 (los cinco **mergeados**, contra filas que los daban por abiertos); que
  `/api/v1/predicciones/{cct}` responde **401** sin token en producción, que es lo que sostiene el
  cierre de `US-403`; y que el Panel de ML imprime `SIN_DATO` citando `US-321`, que es lo que impide
  cerrarla.
- **Recomendación del agente que el PO decidió no seguir:** pedir confirmación de una línea a cada
  dueño del grupo D antes de cerrar. Queda registrado aquí y en cada fila.
- **Correcciones manuales:** pendientes de revisión humana.
