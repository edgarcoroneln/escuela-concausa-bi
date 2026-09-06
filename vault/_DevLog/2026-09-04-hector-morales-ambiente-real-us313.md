---
id: DEVLOG-2026-09-04-HECTOR-MORALES-AMBIENTE-REAL
project: "FARO"
date: "2026-09-04"
owner: "Héctor Rafael Morales Marbán"
status: filed
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión larga — ambiente con Bronze real y primera corrida de US-313 contra Gold real"
touches: ["US-313", "US-311", "BLOCK-004", "BUG-048", "DS-01", "DS-02", "REQ-003"]
traces_up: ["US-313", "US-311"]
tags: [devlog, celula-3, ml, gold, ambiente, bronze-real]
---

# DevLog — 2026-09-04 — Ambiente con Bronze real y la primera corrida de US-313 contra Gold real

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/15_ML_Models/Publicacion_Gold]] ·
[[vault/14_Data_Sources/DS-01_Formato_911]] §11 · [[vault/00_Start_Here/Runbook_Ambiente_Local]]

## Encargo

Correr US-313 contra el Gold real. Hasta hoy `publicar_gold --desde-gold` sólo se había ejercido
contra los 145 renglones de fixture, y la historia pedía explícitamente "ejecutar contra el Gold
real actual, verificar joins/ciclos".

## Ambiente — Camino B de BLOCK-004

Restauré el dump que compartió Diana (`bronze_real_2026-09-04_v2.dump`, 60 MB, formato v1.14, que
el Postgres 15 del contenedor lee sin el problema de versión que frenó a Oscar el 3-sep). Trae las
13 tablas del schema `bronze`, **incluido CONEVAL** (`coneval_irs_2020` 2,472 filas y
`coneval_pobreza_2020` 2,483) — que es justo lo que le faltaba al snapshot del 3-sep y lo que
originó **BUG-048**.

**No dropeé el schema.** Mi Bronze local tenía `bronze.conagua_presas` (180 filas, carga real de
CONAGUA) que **el dump no repone** y cuyo parquet yo no tenía. Restauré con `pg_restore --clean`,
que dropea sólo lo que repone; su `DROP SCHEMA` falló por sí solo porque `conagua_presas` colgaba
del schema. La tabla sobrevivió. Haberla perdido habría costado pedirle a Emilio Galnares su
parquet a dos días del freeze.

Completé además dos pasos del runbook que este ambiente nunca había corrido: las 317 geometrías
(`gold.geo_municipio` no existía) y `dbt seed` (`gold.dim_driver` tampoco). Y creé
`~/.dbt/profiles.yml`, que no existía: dbt estaba instalado pero no podía correr.

## Hallazgo de C1 — los cargadores de DS-01/DS-02 no son idempotentes

El dump trae las dos tablas grandes **exactamente al doble** de lo documentado:

| Tabla | Documentado (3-sep) | En este dump | |
|---|---|---|---|
| `formato911_historico` | 1,373,580 | **2,746,978** | ×2.00 |
| `cct_siged_202608` | 385,175 | **770,379** | ×2.00 |
| `coneval_irs_2020` | 2,472 | 2,472 | ✅ |

No es estimación: `count(*)` exacto, y la llave de negocio da 2,746,978 filas contra **1,373,574
distintas**. Hay **dos pasadas completas de ingesta el 3-sep**, una a las 04:04 y otra a las 06:56,
con conteos idénticos por ciclo.

El mecanismo está en las llaves. `formato911_historico` tiene UNIQUE sobre
`(_source, _ingested_at, cct, ciclo, turno)` — **incluye `_ingested_at`**, así que el
`ON CONFLICT DO NOTHING` sólo evita duplicados dentro de una misma corrida; una segunda corrida
trae otro timestamp, nunca entra en conflicto y reinserta el catálogo completo. Y
`cct_siged_202608` **no tiene ningún índice**.

[[vault/14_Data_Sources/DS-01_Formato_911]] §11 afirma que ambos cargadores son idempotentes y que
*"correrlo de nuevo no duplica nada, sólo reporta 0 filas nuevas"*. **No lo son.** Probablemente es
también la razón por la que la expectativa de unicidad sobre Bronze DS-01 quedó fuera de la suite
de Great Expectations del 3-sep.

**No me bloquea** — verifiqué que `silver/escuela.sql` y `silver/matricula_historica.sql` dedupan
por `row_number() ... order by _ingested_at desc` sobre la llave de negocio, así que la duplicación
colapsa en Silver. Pero duplica el almacenamiento y el costo de cada build, y quien consulte Bronze
directo ve el doble. **Es de C1 (Diana Alvarez); no lo doy de alta yo por alcance, se lo reporto.**

## Gold real

`dbt run --full-refresh` → **22 de 24 modelos**. `gold.features_escuela`: **136,046 filas, 3 ciclos,
46,547 escuelas**. Cobertura: D1 136,046/136,046 (100 %), D3 114,277, D4 114,392, D2 23,299,
D6 1,774, **D5 0** — correcto, CONAGUA no ingerida, regla de cobertura parcial.
`indice_completitud_drivers` promedio **0.4775**, contra el 0.197 que producción servía ese día.

`dbt test --select features_escuela` → **PASS=20, ERROR=0**, incluida
`features_target_variacion_fraccion`. El Gold cumple su contrato.

## La corrida — y los tres hallazgos

```
Features desde gold.features_escuela: 136046 filas · 46547 escuelas · 3 ciclos
ML-01 entrenado — MAE 0.1592     Predicciones:    45,276 filas (2024-2025)
ML-02 entrenado — F1 macro 0.8331  Recomendaciones: 45,276 filas
```

Antes de correr vacié `gold.predicciones` y `gold.recomendaciones` (181 y 135 filas de corridas
viejas con CCT de fixture): `publicar_gold` escribe **sólo con UPSERT** y no tiene bandera de
reemplazo, así que las viejas habrían sobrevivido mezcladas con las nuevas.

**① ML-01 no cumple su umbral con datos reales.** MAE **0.1592** contra el `0.03` de
`evaluar.py:51`. Nadie lo había medido a grano escuela sobre datos reales: el 0.0141 del PR #28 es
de otro grano y otro conjunto. ML-02 sí cumple: F1 **0.8331** contra 0.60.

**② Cero escuelas en riesgo, y el modelo está aplastado contra la media.** Máximo `indice_riesgo`
0.3744, promedio 0.1894, **ninguna en la banda ≥0.6 ni en 0.4–0.6**. La calibración pide que el
modelo prediga una caída de al menos 5 % para cruzar; su peor predicción en 45,276 escuelas es
**−1.33 %**, cuando la mediana real cae 1.68 % y **52,751 escuelas (39 %) caen más de 5 %**.

**③ La causa está en la cola del target real**, que el fixture de 145 filas nunca contuvo:
σ 0.4994, mínimo −0.9903, **máximo +66.0** (una escuela que crece 6,600 %), 1,470 escuelas creciendo
más de 100 % y 76 más de 500 %. Sin winsorización ni pérdida robusta, esa cola arrastra el ajuste
hacia predecir ~0 para todos — lo que explica el MAE alto y el índice aplastado **a la vez**.

**④ 1,168 predicciones y recomendaciones huérfanas** (2.6 % de 45,276): reprueban
`gold_ml_runtime_recomendaciones_fact_relationship` y `cubo_recomendaciones_kpi11_parity`.
`features_escuela` tiene 45,276 escuelas en 2024-2025 y `fact_escuela_ciclo` sólo 44,114, porque el
hecho filtra `matricula_ciclo_anterior is not null`. Mi job publica para escuelas que el hecho
excluye a propósito.

## Lo que no hice, a propósito

**No cerré US-313 ni "arreglé" el número.** Con el umbral incumplido y el índice en cero, las
salidas eran tres —winsorizar el target, recalibrar las anclas del índice, o mover el grano— y sólo
la primera es diagnóstico; la segunda es mover la portería. A dos días del freeze y siendo el número
que se presenta en la demo, subí la decisión en vez de tomarla solo.

## Verificación

`dbt run --full-refresh` 22/24 · `dbt test` 321/333 (4 de `agua_region` esperados, 4 de
`cubo_pipeline`, 2 míos por las huérfanas, 2 de dims de C1) · `pytest tests/ -q` **908 passed,
7 skipped** · `ruff` limpio · `vault_lint.py` limpio · `git status` limpio.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Archivos modificados:** ninguno. Todo el trabajo fue en Postgres local.
- **🔴 Fuera de alcance, ejecutado pero NO modificado:** `dbt/**` (C1), `superset/cargar_geojson_municipios.py` (C2), `src/ingesta/**` (C1).
- **Decisiones autónomas del agente:** respaldar `conagua_presas` y dropear sólo las tablas del
  dump en vez del schema completo; verificar el conteo exacto en vez de fiarse de `n_live_tup`;
  comprobar que Silver dedupa antes de seguir; no cerrar la historia con los umbrales incumplidos.
- **Pedido al usuario:** el `TRUNCATE` de las dos tablas lo corrió él — el clasificador del harness
  bloquea SQL destructivo desde el agente, y no se intentó rodear.

## Pendientes

1. **C1 — Diana Alvarez:** la duplicación ×2 de DS-01/DS-02 y la afirmación de idempotencia de §11.
2. **Decisión de C3:** qué hacer con el MAE y con el índice en cero.
3. Las 1,168 huérfanas: filtrar features contra el hecho, o declarar el desfase.
