---
project: "FARO"
date: "2026-08-30"
author_human: "Manuel Alejandro Serrania Reinada"
agent: "OpenCode"
model: "opencode/big-pickle"
session_duration: "Fix R-3 DEC-012 de KPI-02: numerador/denominador separados tras la revisión post-merge del PR #134"
touches: ["US-212", "KPI-02", "DEC-008", "DEC-009", "DEC-011", "DEC-012", "ADR-007", "DOC-SCREENSPECS", "DOC-CUBESPECS-DB06-DB09", "BUG-031"]
tags: [devlog, bi, superset, semantic, metrics, celula-2, fix]
---

# DevLog — 2026-08-30 — KPI-02 corregido a la forma R-3 (DEC-012)

→ [[_DevLog/_index|Volver al índice]] · [[04_UX_Design/Screen_Specs]] · [[10_Risk_Governance/Decision_Log]]

## Contexto

El PR #134 se mergeó y el PM lo aprobó **con un comentario técnico posterior**: el defecto
`variacion_ponderada_pct` vive desde US-212 — pintaba **−54.5%** donde el real es **−0.19%**
(factor 287) en seis tableros (DB-01/02/03/04/06/09; la tarjeta de DB-04 ya se había retirado).
El PM pidió de C2 hoy: (1) cambiar las dos aserciones (`test_semantic_db01_db02.py` y
`test_semantic_db06_db09.py`) para exigir **numerador y denominador separados**, y (2) corregir
las tres expresiones de los YAML. Localicé una **cuarta** expresión del mismo tipo en
`metrics_db06_db09.yaml` (datos de `db06_predicciones_escuela`, producto inline) y el usuario
aprobó incluirla.

Causa raíz confirmada en el dato: `gold/fact_escuela_ciclo` define `variacion_matricula` como
**delta absoluto en alumnos** (`matricula_total − matricula_ciclo_anterior`), y `gold.cubo_matricula`
lo pre-multiplica (`SUM(delta × matricula)`) → la métrica promediaba un delta absoluto como si
fuera fracción. Es el mismo hueco de **unidad** que ADR-007 deja abierto, ahora apareciendo en la
capa semántica. **DEC-012 (R-3)** declara la unidad del numerador: fracción
`matricula_total / matricula_ciclo_anterior − 1`.

## Qué se hizo

### Contrato semántico
- `superset/semantic/metrics_db01_db02.yaml` (líneas 74 y 177) y `metrics_db06_db09.yaml`
  (líneas 73 y 142): `variacion_ponderada_pct` ahora es
  `SUM(variacion_ponderada) / NULLIF(SUM(matricula_total), 0)` con la clave **`unidad`** declarada
  (fracción, R-3 DEC-012). Nunca `* 100` (el formato `porcentaje_1` lo aplica al mostrar).
- `superset/semantic/db01_cubo_matricula.sql`, `db02_cubo_riesgo_territorial.sql`,
  `db06_cubo_predicciones.sql`: la columna gold `variacion_x_matricula` se re-exporta como
  `variacion_ponderada` (alias en la frontera; el repunteo US-205 queda intacto).
- `superset/semantic/db06_predicciones_escuela.sql`: nuevo numerador por fila
  `variacion_matricula * matricula_total AS variacion_ponderada`.

### Tests (los 2 que pidió el PM)
- `test_variacion_es_ponderada_por_matricula` → **`test_variacion_exige_numerador_y_denominador_separados`**
  en `tests/test_semantic_db01_db02.py` y `tests/test_semantic_db06_db09.py`. Cada uno valida:
  datasets con `variacion_ponderada` y `matricula_total`; **ninguna** columna de salida
  `variacion_x_matricula` (permitido solo convia `AS`); y en el YAML la expresión exacta R-3 más
  la unidad en las métricas de los cuatro datasets que la usan.

### Documentación de la decisión
- `10_Risk_Governance/Decision_Log.md` → **DEC-012 (proposed)**: contrato R-3 de KPI-02,
  numerador/denominador separados + unidad declarada; dependencia explícita de C1/ADR-007 para
  que los seis tableros muestren el número correcto.
- `04_UX_Design/Screen_Specs.md` §4 (KPI-02): se declara la unidad (fracción) y el contrato R-3;
  se corrigió la SQL de referencia (antes: producto ponderado de un delta absoluto).
- `04_UX_Design/Cube_Specs_DB06_DB09.md`: `variacion_ponderada` como numerador canónico de
  KPI-02 en el cubo y en el detalle por escuela.

## Verificación

- `pytest tests/test_semantic_db01_db02.py tests/test_semantic_db06_db09.py
  tests/test_semantic_repunteo_cubos.py tests/test_semantic_db03_db04.py tests/test_kpis_us221.py`
  → **163 passed**.
- Suite completa (excluyendo 7 módulos de API sin deps en `.venv`: `limits`/`cachetools`, y
  validaciones con great_expectations) → **555 passed**. Los 8 fallos restantes son
  **preexistentes y ambientales** (great_expectations/FastAPI, ajenos a este cambio).
- `ruff check` → ok.
- `vault_lint.py` → pendiente de correr en el PR.

## Handoff / pendientes

- **Dependencia dura (declarar en el PR):** el número en DB-01/02/06/09 seguirá mal hasta que C1
  re-materialice `gold.cubo_*` con **fracción** (gatillo: ratificación de ADR-007 en mesa hoy).
  Este PR desbloquea esa corrección: el contrato ya no exige el producto ponderado.
- **DEC-012 (proposed):** ratificar en mesa; el PM citará R-3 como evidencia en el ADR.
- Fuera de alcance (no tocados): `metrics_db03_db04.yaml` (Marina, DB-03/04, ya cubre su caso
  con regresión BUG-031), `kpi_02_variacion_matricula.sql` (Daniel, US-221, ya en forma R-3),
  `gold/*` (C1/Oscar).