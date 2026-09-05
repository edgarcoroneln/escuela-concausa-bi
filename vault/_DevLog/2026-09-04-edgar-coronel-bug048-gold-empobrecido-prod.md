---
project: "FARO"
date: "2026-09-04"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "cierre de la cola de PRs y hallazgo de BUG-048"
tags: [devlog, pm, bug-048, produccion, gold, demo]
---

# DevLog — 2026-09-04 — BUG-048: producción sirve un Gold empobrecido

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|BUG-048]] ·
[[vault/00_Start_Here/Runbook_Ambiente_Local]]

## Cómo apareció

No lo buscaba. Al validar el PR #223 de Luis Téllez (redespliegue de BUG-046) corrí el smoke contra la
URL pública para comprobar sus claims, y el `/kpis` de producción me quedó al lado del `/kpis` de mi
ambiente local recién reconstruido con el runbook. Los dos números que no cuadraban no eran los suyos:

| | Producción | Local (pipeline completo) |
|---|---|---|
| `matricula_total` | 6,704,229 ✅ | 11,828 (fixtures, esperado) |
| `escuelas_en_riesgo` | **0** | **2** |
| `indice_completitud_drivers` | **0.197** | **0.648** |

## Qué es y qué no es

**No es** una regresión de código ni de despliegue. `/version` devuelve `33fcbbb`, que contiene los
fixes de BUG-044 y BUG-046 —lo verifiqué con `git merge-base --is-ancestor`— y la matrícula de prod es
la correcta del ciclo vigente. El despliegue de Luis Téllez está bien hecho.

**Es** que el snapshot `gold_real.sql` que se importó a Cloud SQL en L1 se generó el **3-sep, antes
del fix de BUG-045 de Diana**. Aquel día CONEVAL no tenía fixture compatible y **D1 iba vacío**; hoy,
en local, D1 tiene 145 de 145. Lo desplegado es código nuevo sobre datos viejos.

Completitud por driver medida en local: D1 145/145 · D2 145/145 · D3 133/145 · D4 133/145 · D6 5/145 ·
D5 0/145 (CONAGUA no ingerida — correcto, es la regla de cobertura parcial).

## Por qué importa ahora y no la semana que viene

La demo es el **9-sep** y corre contra la URL pública. Quien la abra hoy ve **cero escuelas en riesgo
y 20 % de completitud de drivers**: los dos números que peor cuentan la historia de un proyecto cuyo
diferenciador es precisamente identificar escuelas en riesgo y explicar su driver dominante. Y ninguno
de los dos refleja el estado real del pipeline, que sí encuentra escuelas en riesgo y sí tiene cuatro
de seis drivers razonablemente poblados.

Esto reordena la prioridad: pesa más que lo que quedaba de la cola de PRs.

## El hueco que lo dejó pasar

Nada compara la completitud de producción contra la del pipeline. El smoke de despliegue valida rutas
HTTP y la cifra de matrícula —por eso cazó BUG-044— pero **una degradación de datos es invisible
mientras el código siga en verde**. Queda propuesta, no implementada (es de C5), una guarda que haga
fallar el smoke si `indice_completitud_drivers` cae por debajo de un umbral acordado.

Es el mismo patrón de fondo que BUG-045 y BUG-012: el sistema verifica que las cosas *corran*, no que
los *números tengan sentido*.

## Verificado

`curl` a `/api/v1/kpis` de producción y de local · completitud por driver consultada directamente en
`gold.features_escuela` · `git merge-base --is-ancestor` para confirmar que la imagen desplegada sí
contiene los fixes · `vault_lint.py` limpio.

## IDs tocados

`BUG-048`, `BUG-045`, `BUG-044`, `BUG-046`, `US-113`, `US-505`, `REQ-001`, `REQ-005`, `DS-07`

## Próximos pasos

- **Diana (C1)**: regenerar Gold con el pipeline post-BUG-045.
- **Luis Téllez (C5)**: subirlo con el procedimiento de L1 y, si alcanza, incluir los 9 cubos que L1
  excluyó a propósito.
- Reconfirmar `/kpis` de producción después: la completitud debe subir y el conteo de escuelas en
  riesgo dejar de ser cero.
