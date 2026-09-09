---
project: "FARO"
date: "2026-09-06"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude (Cowork)"
model: "claude-sonnet-5"
session_duration: "verificación corta, un solo archivo"
touches: ["BUG-048", "US-113", "REQ-001"]
tags: [devlog, bug-048, validacion, gold-dump, ml-01]
---

# DevLog — 2026-09-06 — Diana Aracely Alvarez Varela — BUG-048: "7 de 45,276" confirmado contra un Gold real

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|BUG-048]]

## Qué se pidió

Marina García reportó desde producción que, tras el ajuste de umbral de riesgo en `dbt/` (0.6→0.5),
el conteo de escuelas en riesgo es **7 de 45,276**, con `indice_riesgo` promedio ~0.36 y máximo real
0.5717. El cambio de dbt ya estaba probado por los tests de paridad; lo que faltaba era confirmar ese
número contra un Gold que trajera predicciones reales, no un mock ni una corrida rota.

## Candidatos descartados antes de llegar al bueno

- Un dump mock con `mlflow_run_id` tipo `MOCK-US203` — descartado de inmediato, no es dato real.
- Un run local con `mlflow_run_id = 'local-sin-mlflow'`: mismo orden de filas que producción (45,329)
  pero distribución rota (`avg ≈ 0.99`, `max = 1.0`) — casi todas las escuelas pegadas a 1.0, no es
  un patrón sano de un modelo de riesgo. Probablemente una corrida de ML-01 sin trackear en MLflow y
  con algo mal en la escala del índice.

## El dump correcto

`gold_bug048_final2_2026-09-05.sql` (66.6 MB), recibido en `~/Downloads` de mi Mac — no llegó al
chat por el límite de tamaño (>30 MB), así que se leyó directo del equipo enlazado sin necesidad de
subirlo. `mlflow_run_id = 'bug048-20260905-temporal-robusto'`, un run trackeado real, distinto tanto
del mock como del run local roto.

Verificado parseando directo el bloque `COPY gold.predicciones` del dump (45,276 filas, grano
escuela, ciclo único 2024-2025, modelo ML-01):

| Métrica | Este dump | Lo que reportó Marina (prod) |
|---|---|---|
| filas | 45,276 | 45,276 |
| `indice_riesgo` promedio | 0.351030 | ~0.36 |
| `indice_riesgo` máximo | 0.571702 | 0.5717 |
| escuelas con `indice_riesgo >= 0.5` | **7** | **7** |
| escuelas con `indice_riesgo >= 0.6` | 0 | — |

Coincide al dígito. El "7 de 45,276" es un número real, no un artefacto de mock ni de una corrida sin
trackear.

## Conclusión

El cambio de umbral en `dbt/` (0.6→0.5) queda validado de punta a punta: código correcto, tests de
paridad en verde, y ahora también el número final coincide con lo reportado desde producción. No
queda pendiente de verificación de mi lado en BUG-048.

## Verificado

Parseo directo del bloque `COPY gold.predicciones` de `gold_bug048_final2_2026-09-05.sql` (awk sobre
la columna `indice_riesgo`, sin pasar por Postgres) · comparación del `mlflow_run_id` contra los dos
candidatos descartados (mock y run local) · cruce de las cinco cifras contra lo reportado por Marina.

## IDs tocados

`BUG-048`, `US-113`, `REQ-001`

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] No se modificó ningún archivo del repo ni el dump — solo lectura
- [x] DevLog enlaza a los IDs afectados

## Bloqueantes

Ninguno de mi lado. Pendiente operativo, no mío: `gold_bug048_final2_2026-09-05.sql` vive solo en mi
`~/Downloads`, fuera del repo y fuera de la carpeta del proyecto (`MTIIA/escuela-concausa-bi/`) donde
están los demás dumps de BUG-048 — vale la pena moverlo ahí o compartirlo por el mismo canal que los
anteriores para que el resto del equipo no lo pierda de vista.

## Próximos pasos

- Mover o compartir `gold_bug048_final2_2026-09-05.sql` por el canal habitual (mismo criterio que los
  dumps anteriores de BUG-048, fuera de Git).
- Si Luis Téllez (C5) todavía no confirma el import a Cloud SQL, este dump y sus cifras sirven como
  evidencia independiente de que el Gold que hay que servir en producción es correcto.
