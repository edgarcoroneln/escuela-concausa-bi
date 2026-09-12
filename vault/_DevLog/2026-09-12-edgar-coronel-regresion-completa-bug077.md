---
project: "FARO"
date: "2026-09-12"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "Corrida de regresion completa contra el ambiente local (backend, dbt, API, 9
  rutas del frontend); registro de BUG-077 y reporte para la junta de la tarde."
touches: ["US-621", "REQ-002", "REQ-004", "REQ-005", "RISK-006", "BUG-077"]
tags: [devlog, qa, regresion, bug, s7]
---

# DevLog — 2026-09-12 — Regresión completa de S7 y BUG-077

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Reporte_QA_Regresion_S7_2026-09-12|Reporte_QA_Regresion_S7_2026-09-12]]

## Qué se hizo

Siguiendo [[vault/06_Quality_Testing/QA_team_documentation/Plan_QA_Exhaustivo_S7]], se ejecutó una
corrida de regresión de 28 casos contra el ambiente local: `pytest` completo, `dbt parse`/`dbt test`,
18 casos de contrato/errores de la API vía `curl`, y las 9 rutas + 5 pestañas del frontend con
navegador real. Bitácora completa en
[[vault/06_Quality_Testing/QA_Logs/2026-09-12-edgar-coronel-qa-regresion-completa-s7]].

## Hallazgo principal: `BUG-077`

`dbt test --select gold` reveló que `gold.dim_municipio.nombre_entidad`/`poblacion` son `NULL` en
307 de 317 municipios locales — y que `MunicipioOut.nombre_entidad` es `StrictStr` (obligatorio),
así que `GET /api/v1/municipios` revienta con `500` para ese 97%, verificado tanto en el listado sin
filtro como en el detalle de municipios concretos. Lo más relevante no es el dato en sí: el equipo
ya había escrito un `data_test` de dbt (`not_null_dim_municipio_nombre_entidad`) diseñado para cazar
exactamente esto, y sí lo cazó — pero ningún workflow de `.github/**` ejecuta `dbt test` ni
`dbt run`, solo `dbt parse`. La guarda existe y nunca se disparó. Registrado como `BUG-077`
(`critical`, `open`), sin dueño único asignado: requiere que Diana Alvarez confirme si producción
tiene el mismo hueco de cobertura CONEVAL, y que Christian Ruiz haga que el campo degrade en vez de
tronar, independientemente de la respuesta anterior.

## Otros hallazgos, todos documentados sin registrar como bug nuevo hasta confirmarse en otro ambiente

- `cubo_riesgo_territorial_ml01_parity` (dbt): 5 combinaciones desalineadas — posible staleness de
  un `dbt run` parcial en el ambiente local, no necesariamente un defecto real.
- MLflow local vacío: confirma desde un segundo entorno independiente el hallazgo que ya había hecho
  Deni Garrido para `DEC-027`/`RISK-011`.
- `gold.recomendaciones` local sin `shap_d1..shap_d6`: probable volumen de Docker desactualizado del
  propio PO, produce `503` en `/predicciones/{cct}`.

## Qué NO se hizo

No se corrigió ningún código ni modelo dbt en esta sesión — es puramente de verificación y
documentación. No se probó Superset, Airflow ni el login real (OAuth), declarado explícitamente en
la bitácora como fuera de cobertura de esta corrida.

## Reporte para la junta

[[vault/06_Quality_Testing/Reporte_QA_Regresion_S7_2026-09-12]] — ordenado por impacto sobre el
*code freeze* de mañana, con plan de remediación y dueño propuesto por cada acción.
