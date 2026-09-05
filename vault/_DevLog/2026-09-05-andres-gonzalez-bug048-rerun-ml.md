---
id: DEVLOG-2026-09-05-ANDRES-GONZALEZ-BUG048-ML
project: "FARO"
date: "2026-09-05"
owner: "Andrés González Habib"
status: filed
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "GitHub Copilot"
session_duration: "sesión crítica BUG-048"
touches: ["BUG-048", "US-302", "US-311", "US-313", "REQ-003"]
traces_up: ["BUG-048", "US-302", "US-311", "US-313"]
traces_down: ["src/modelos/entrenar_ml01.py", "tests/test_entrenar_ml01.py"]
tags: [devlog, celula-3, bug048, ml-01, ml-02, gold, demo]
---

# DevLog — 2026-09-05 — Rerun ML para BUG-048

→ [[vault/_DevLog/_index|Volver al índice]]

## Objetivo

Regenerar sobre el Gold post-BUG-045 las predicciones ML-01 y recomendaciones ML-02 del ciclo
2024-2025 sin perder los drivers ni los cubos que C1 preparó para producción.

## Insumo

- Dump definitivo recibido de Diana Alvarez: `gold_bug048_final1_2026-09-05.sql`, transferido fuera
	de Git; reemplaza los dumps anteriores al incorporar CONAPO real y nueve cubos.
- Importación local: 136,046 filas de `gold.features_escuela`, 46,547 escuelas y tres ciclos.
- Cobertura: D1/D2 100 %, D3/D4 ~83 %, D6 parcial y D5 `SIN_DATO` en features; `cubo_pipeline`
	llega materializado con CONAGUA real.

## Diagnóstico ML-01

Con la pérdida cuadrática vigente, el holdout temporal 2024-2025 dio MAE 0.159148 contra baseline
0.159223: mejora prácticamente nula. Las predicciones fueron todas positivas y produjeron 0 escuelas
sobre el umbral 0.6. El 98.9 % en riesgo del dump provenía de outputs ML anteriores y desincronizados,
no del rerun actual.

Se evaluó `loss="absolute_error"` sobre la misma ventana temporal, sin cambiar las anclas de riesgo ni
buscar un porcentaje objetivo:

- MAE 0.141652; RMSE 0.436390; baseline MAE 0.159223; mejora 11.04 %.
- Riesgo mínimo 0.0106, mediana 0.3595, máximo 0.8744.
- 214 de 45,276 escuelas (0.47 %) quedan en riesgo `>= 0.6`.

La pérdida absoluta se adopta porque mejora el holdout frente al baseline y reduce la influencia de
una cola minoritaria de outliers del target; no es un ajuste cosmético del porcentaje de riesgo.

Con CONAPO real, el rerun definitivo mantiene MAE 0.141458 pero cambia la señal: riesgo mínimo
0.0292, mediana 0.3533 y máximo 0.5717. Ninguna escuela cruza 0.6 porque la caída máxima predicha es
4.53 %, por debajo del umbral ratificado de 5 %. No se movió el umbral para fabricar casos.

## Resultado ML-02 y publicación local

`publicar_gold --desde-gold --ventanas 1` produjo por upsert:

- 45,276 predicciones ML-01 para 2024-2025.
- 45,276 recomendaciones ML-02 para 2024-2025, sin huérfanas respecto a predicciones/features.
- F1 macro ML-02: 0.8333.
- Drivers: D1 2,843; D2 27,075; D3 2,104; D4 12,835; D6 419.
- D5 excluido explícitamente por ausencia total, nunca convertido en cero.

## Seguridad y calidad

- [x] No se tocó producción.
- [x] El dump de 292 MB se excluyó localmente de Git y se entregará por canal privado.
- [x] Partición temporal, nunca aleatoria.
- [x] `tests/test_entrenar_ml01.py`: 34 passed.
- [x] `tests/test_publicar_gold.py`: 39 passed.
- [x] `tests/test_evaluar.py`: 26 passed; reporte canónico regenerado.
- [x] Ruff limpio en código y prueba modificados.
- [x] Ocho cubos reconstruidos con dbt; 158/159 pruebas pasaron.

La única prueba dbt en rojo fue `cubo_recomendaciones_kpi11_parity`: existen 1,168 recomendaciones
de escuelas presentes en `features_escuela` pero fuera de `fact_escuela_ciclo`. Se conserva el dato
porque Luis pidió las 45,276 recomendaciones y el desfase queda visible; no se borraron filas para
forzar el gate. El cubo observado contiene 44,108 recomendaciones y 213 escuelas en riesgo.

## Entregable para C5

- El primer dump C3 quedó superseded por `gold_bug048_final1_2026-09-05.sql` de C1 al llegar CONAPO
	real. El entregable definitivo es `gold_bug048_final2_2026-09-05.sql`, 69,873,466 bytes.
- SHA-256: `b8a3fc50a636a2943eb0bc25cbe495ed49914429a76838346e7ebcf6aaa5b32a`.
- Restauración desde cero: 45,276 predicciones, 45,276 recomendaciones, cinco drivers, ocho
	materialized views y `cubo_pipeline` real con 11 filas.
- El dump contiene únicamente las 45,276 predicciones/recomendaciones vigentes, antes de los ocho
	`REFRESH MATERIALIZED VIEW`; las 80 filas sintéticas 2023-2024 no se exportaron.
- Restauración desde cero verificada en una base aislada: 45,276 predicciones, 45,276
	recomendaciones, cinco drivers y ocho cubos; riesgo 0.0106–0.8744.

## Pendiente operativo

- C5 importa con backup previo, valida read-only y levanta Superset.
