# `superset/semantic/` — capa semántica de Superset (datasets virtuales y métricas)

Artefactos de **US-211a** (Marina García del Buey, **US-204** y **US-211b** (Manuel Serranía),
**US-221/222** (Oscar Quiroz), **US-213** (Monserrat Miranda) y el **repunteo US-205**.
Contratos canónicos:
[`vault/04_UX_Design/Cube_Specs_DB03_DB04.md`](../../vault/04_UX_Design/Cube_Specs_DB03_DB04.md)
(`DOC-CUBESPEC-DB0304`) · [`Cube_Specs_DB05_DB08.md`](../../vault/04_UX_Design/Cube_Specs_DB05_DB08.md)
(`${DOC-CUBESPEC-DB0508}`) · [`Cube_Specs_DB06_DB09.md`](../../vault/04_UX_Design/Cube_Specs_DB06_DB09.md)
· [`Cube_Specs_DB07.md`](../../vault/04_UX_Design/Cube_Specs_DB07.md).
Convención canónica: [`../README.md`](../README.md) (US-202).

| Archivo | Qué es |
|---|---|
| `db01_*.sql` … `db09_*.sql` (15) | Datasets virtuales de Superset: **passthrough/enrich de los cubos físicos C1** (`gold.cubo_*`, repunteo US-205/US-113). 13 del repunteo US-205 + 2 de DB-07 (US-222). Uno por dataset de los tableros DB-01…DB-09. |
| `metrics_db01_db02.yaml` … `metrics_db07.yaml` (5) | Métricas, jerarquías, filtros globales y rutas de drill-down de cada familia de tableros. |
| `kpi_0*.sql` (5) | Catálogo canónico de KPIs de US-201 (insumo de `metrics_kpis_base_us221.yaml`, US-221). |
| `metrics_kpis_base_us221.yaml` | Tarjetas de KPI reutilizables (US-221) → ver BUG-027 (sql_ref pendiente de re-mapeo). |

## Para qué sirve cada cosa

- **`db0*.sql` — datasets virtuales de Superset.** Desde **US-205** leen **solo** los cubos
  físicos de la Célula 1 (`gold.cubo_matricula`, `gold.cubo_riesgo_territorial`,
  `gold.cubo_escuela_360`, `gold.cubo_comparador_municipio`, `gold.cubo_driver`,
  `gold.cubo_pivot`, `gold.cubo_recomendaciones`, `gold.cubo_completitud`) más el enrich de
  `gold.geo_municipio` / `gold.dim_driver` y el `LEFT JOIN` de `gold.predicciones` (db09).
  **Ninguno lee `gold.fact_*`**: la agregación la resolvió C1 (DEC-009/010).
- **`metrics_*.yaml` — contrato de métricas** que se dan de alta en Superset al construir cada
  tablero. Nombre de métrica = fórmula del KPI canónico (`Screen_Specs`).
- **`kpi_0*.sql` — SQL de referencia del catálogo** (US-201/US-221); se corren contra fixtures
  en `tests/test_kpis_us221.py`. Su re-mapeo a los datasets canónicos es el follow-up de BUG-027.

## Reglas que estos archivos respetan

- **Las salidas de ML llegan ya resueltas por el cubo C1** (`indice_riesgo`, `driver_dominante`,
  `recomendacion`, `prioridad`). La capa semántica no vuelve a unir `gold.predicciones` /
  `gold.recomendaciones` (la excepción es `db09`, que une `gold.predicciones` para el ranking de
  urgencia AC-010.0).
- **`SIN_DATO` explícito: nunca cero, nunca nulo silencioso.** No hay un solo `COALESCE(<driver>, 0)`.
  Cada métrica viaja con su bandera de cobertura y el tablero muestra *"sin dato disponible"*.
- **Línea de alerta `>= 0.5`** (DEC-019); el ancla de calibración de la sigmoide
  se mantiene en `0.60` (≈ perder ~5% de matrícula, DEC-006).
- Las razones se guardan como **numerador y denominador por separado**, para que se puedan reagregar
  con cualquier combinación de los filtros globales (ciclo, entidad, nivel).

## Cómo se validan

```bash
pytest tests/test_semantic_db01_db02.py tests/test_semantic_db03_db04.py \
       tests/test_semantic_db05_db08.py tests/test_semantic_db06_db09.py \
       tests/test_semantic_repunteo_cubos.py -q
```

Validación **estática**: no necesita base de datos. Comprueba el grano, las llaves, la prohibición
de `COALESCE(...,0)`, el repunteo (ningún SQL lee `gold.fact_*`; fuentes en la allowlist US-205) y
que toda expresión de métrica referencie columnas que el dataset sí expone (guarda de passthrough,
regresión `db09.prioridad`). La validación **contra datos reales** corre con
`../sync_semantic_layer.py --validar-datos` (requiere C1 materializado, US-113).

## Pendientes de coordinación

- **BUG-027** (`metrics_kpis_base_us221.yaml`): `sql_ref` apuntan a `sql/`, directorio que ya no
  existe — re-mapeo a los datasets canónicos (follow-up US-221, dueño Oscar Quiroz).
- **DB-05/DB-08**: tableros del PR #114 ya en `main` (Monserrat, US-213) **alineados a los nombres
  reescalados de US-205 (KPI-07)** — pendiente solo de `gold.dim_driver` correcto (BUG-015/BUG-022,
  C1) para sincronizar en Superset con datos reales.
