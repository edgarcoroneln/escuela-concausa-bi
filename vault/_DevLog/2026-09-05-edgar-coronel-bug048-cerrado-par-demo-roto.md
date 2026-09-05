---
project: "FARO"
date: "2026-09-05"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "cierre de la cola de PRs, verificación de BUG-048 en vivo y hallazgo del par de demostración"
tags: [devlog, pm, bug-048, dec-015, demo, produccion]
---

# DevLog — 2026-09-05 — BUG-048 cerrado, y el par de la demo que dejó de existir

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/10_Risk_Governance/Decision_Log]] ·
[[vault/06_Quality_Testing/Bug_Register]]

## 1. `BUG-048` cerrado, verificado en vivo y no en el registro

Luis Téllez importó el Gold regenerado a Cloud SQL. Antes de aprobarlo fui a la URL pública:

| | Antes | Ahora |
|---|---|---|
| `indice_completitud_drivers` | 0.197 | **0.6194** |
| `escuelas_en_riesgo` | 0 | 0 |

El número que peor contaba nuestra historia está arreglado. Y el que sigue en cero **ya no es un
síntoma**: con el rerun de CONAPO real, la caída máxima predicha es −4.53 %, por debajo del umbral
de −5 % de `DEC-006`. Nadie cruza porque nadie debe cruzar.

Vale registrar el procedimiento de C5, no sólo el resultado: **verificó el dump en read-only antes
de importarlo** y descartó dos dumps intermedios que no pasaron esa verificación.

## 2. El hallazgo: el par de demostración ya no existe en ningún ambiente

Marina me recordó que el par —dos escuelas con riesgo parecido y recomendación distinta— sólo se
sostenía en local mientras `BUG-048` siguiera abierto. **Fui a reconfirmarlo con el Gold ya
refrescado, y el problema no desapareció: cambió de causa.**

| CCT | Prod con Gold viejo | Local de Marina | **Prod ahora** |
|---|---|---|---|
| `15DJN0049A` | 0.129 · D3 | 0.7423 · D1 · becas | **0.3466 · D4 · conectividad** |
| `09DSN0042A` | — | 0.6692 · D2 · rutas | **0.1339 · D2 · rutas** |

El rerun con CONAPO real cambió el modelo a `absolute_error` y volteó la distribución de drivers
(D1 pasó de 24,180 a 2,843; D2 de 5,850 a 27,075). **0.35 contra 0.13 es 2.6× de diferencia: ya no
es "riesgo parecido".**

`DEC-015` decía que la salvedad vivía mientras `BUG-048` estuviera abierto. Cerró, y **la salvedad
sigue viva por otra razón** — que es peor, porque la primera se resolvía sola con el import y ésta
exige elegir un par nuevo. Actualizada la decisión con la medición.

**No se recicla el par viejo.** La narrativa del 9 tiene que salir de los datos de producción, y
elegirla es de C2 (Marina García).

## 3. La imagen de la API va por detrás de `main`

`/api/v1/version` devuelve `33fcbbb`, anterior a los merges de hoy. El refresco de `BUG-048` fue de
**datos**, no de código. Consecuencia concreta: producción todavía responde `0.0` donde no hay dato
en `/explicacion` — el `SIN_DATO` de `BUG-055` está mergeado pero no desplegado. Queda para C5,
después de que entre la cola de hoy.

## Verificado

`curl` a `/api/v1/kpis`, `/predicciones/15DJN0049A`, `/predicciones/09DSN0042A` y `/version` de
producción · `pytest tests/ -q` **991 passed, 4 skipped** · `ruff` limpio · `vault_lint` limpio ·
`TEST-002` verde.

## IDs tocados

`BUG-048`, `BUG-054`, `BUG-055`, `DEC-015`, `DEC-006`, `US-207`, `US-214a`, `US-412`, `US-505`,
`US-113`, `REQ-001`, `REQ-002`, `REQ-003`, `REQ-004`, `REQ-005`

## Pendiente ajeno, anotado y no corregido

`BUG-054`: los dos defectos de las métricas de DB-09 que encontró Marina revisando las capturas del
gate visual. Los verifiqué contra la base —`prioridad` en minúsculas contra `'ALTA'`, y la única
división entera de toda la capa semántica— y ambos arreglos son de una línea. Son de **Manuel
Serranía** y hay que verlos antes del 9: DB-09 es el tablero del diferenciador.

## Próximos pasos

- Marina elige el par nuevo con datos de producción.
- Manuel aplica los dos parches de `BUG-054`.
- C5 redespliega la API tras la cola de hoy.
- `US-006`, el ensayo, sigue sin arrancar y es mío.
