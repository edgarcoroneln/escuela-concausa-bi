---
project: "FARO"
date: "2026-09-05"
author_human: "Deni Garrido Fragoso"
agent: "Codex"
model: "GPT-5"
session_duration: "ADR-011, alineación Gold y regeneración controlada de US-113"
touches: ["ADR-011", "US-104", "US-112", "US-113", "US-311", "US-313", "DS-01", "DS-02", "DS-08"]
tags: [devlog, us113, adr, gold, ml, datos-reales]
---

# ADR-011 — alineación de `features_escuela` y regeneración de US-113

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/ADRs/ADR-011-universo-features-escuela]]

## Objetivo

Corregir la divergencia entre el universo ML de `gold.features_escuela` y el hecho central
`gold.fact_escuela_ciclo`, regenerar las salidas ML sin modificar código de C3 y volver a
materializar los nueve cubos de US-113 con datos DS-08 reales.

## Decisión y cambio realizado

- Se registró **ADR-011** como `accepted`: `dim_escuela`/DS-02 es la autoridad para la
  pertenencia a Gold y para `cve_mun`; DS-01 conserva la matrícula y el target.
- `features_escuela.sql` usa ahora el mismo `INNER JOIN` contra `dim_escuela` que
  `fact_escuela_ciclo`. Se eliminó el filtro redundante de `cve_ent` de DS-01: la dimensión
  canónica ya acota el scope y evitaba excluir 20 llaves legítimas del hecho.
- Se añadieron dos pruebas dbt: paridad bidireccional de `(cct, id_ciclo)` y paridad de
  `cve_mun` contra `dim_escuela`.
- No se modificaron los scripts, tablas ni contrato de C3. Los CCT que existen sólo en DS-01
  quedan fuera de ambos productos Gold hasta que DS-02 los catalogue.

## Ejecución runtime local

Base confirmada antes de escribir: `escuela_concausa_db` con `POSTGRES_HOST=localhost`.

1. `superset/cargar_geojson_municipios.py`: `gold.geo_municipio` = **317** filas.
2. `dbt seed --full-refresh`: `gold.dim_driver` = **6** filas.
3. dbt reconstruyó dimensiones, hecho y features con las variables runtime de SINAICA real.
4. Pruebas nuevas de paridad: **2/2 PASS**. Universo final:
   `gold.features_escuela` = `gold.fact_escuela_ciclo` = **132,566** llaves CCT×ciclo;
   municipio no canónico = **0**.
5. Vaciado controlado y atómico autorizado:
   `gold.predicciones` **45,276 → 0** y `gold.recomendaciones` **45,276 → 0** mediante
   `TRUNCATE` conjunto. Se conservaron la PK de recomendaciones y los índices únicos parciales
   de predicciones; no se usó `DROP TABLE`.
6. `python -m src.modelos.publicar_gold --desde-gold`:
   - 132,566 features, 45,318 escuelas, tres ciclos;
   - ML-01: **MAE 0.1374 ± 0.0000**;
   - ML-02: **F1 macro 0.8331 ± 0.0000**;
   - 44,114 predicciones y 44,114 recomendaciones publicadas;
   - D5 permanece excluido del entrenamiento por `SIN_DATO` explícito.
7. Los nueve cubos se regeneraron con `dbt run --full-refresh --select 'gold.cubo_*'`.

| Cubo | Filas |
|---|---:|
| `cubo_comparador_municipio` | 2,853 |
| `cubo_completitud` | 17,118 |
| `cubo_driver` | 17,118 |
| `cubo_escuela_360` | 132,566 |
| `cubo_matricula` | 2,853 |
| `cubo_pipeline` | 10 |
| `cubo_pivot` | 795,396 |
| `cubo_recomendaciones` | 132,566 |
| `cubo_riesgo_territorial` | 2,853 |

## Validación

- `dbt test --select 'cubo_*'`: **33/33 PASS**, incluido
  `cubo_recomendaciones_kpi11_parity`.
- DS-08 en `cubo_pipeline`: `DS-08_CONAPO` · cobertura `OK` · **2,272,050** filas.
- Duplicados: 0 en ambas llaves de `gold.predicciones` y en `gold.recomendaciones`.
- Predicciones/recomendaciones fuera de `fact_escuela_ciclo`: **0**.
- KPI de recomendaciones del cubo = recomendaciones publicadas = **44,114**.

## Gobierno y siguiente paso

La implementación queda lista para revisión de arquitectura por Diana Alvarez, revisión del
consumidor C3 por Andrés González y aprobación de PR por Edgar Coronel. La actualización formal
de `Execution_Status`/trazabilidad no se realizó: corresponde al PM y no al alcance de Deni.
