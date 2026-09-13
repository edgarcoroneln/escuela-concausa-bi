---
project: "FARO"
date: "2026-09-13"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "2h"
touches: ["US-121a", "US-122a", "DS-03", "DS-05", "DS-06"]
tags: [devlog, us-121a, us-122a, ds-03, ds-05, ds-06, d3, d5, d6, produccion]
---

# DevLog — 2026-09-13 — D6 fix de producción (default *_test), D5 agua v1 y verificación de D3 en DS-03 (US-121a, US-122a)

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

1. **D6 (aire), fix de un hallazgo real de producción**: `dbt/models/sources.yml` traía
   como default las tablas `*_test` de SINAICA en vez de las reales.
2. **D5 (agua), v1 PROPUESTO**: nuevo modelo `silver.agua_presa_entidad` (capacidad NAMO de
   presas por entidad, CONAGUA) integrado en `gold.fact_escuela_ciclo`. **Sin mergear —
   pendiente de aprobación de Edgar Coronel y Emilio.**
3. **DS-03 (CEMABE)**: verificación de producción del hueco de cobertura de D3, documentada
   en el propio archivo DS-03 (§11).
4. Traído a la rama el trabajo ya coordinado de Andrés González (fixture de Gold para su
   chat/agente Text-to-SQL local), con su fix real ya incluido.

## 1. D6: el default de SINAICA apuntaba a fixtures de prueba

En `https://faro-frontend-eanzfglvyq-uc.a.run.app/panorama`, la comparativa de drivers
mostraba D6 en `SIN_DATO` para las 7 escuelas de mayor riesgo. Diagnóstico: `sources.yml`
define cada fuente Bronze como `var('bronze_X_identifier', '<default>')` — en **todas** las
demás fuentes del archivo el default ya es la tabla real de producción (`cemabe_2013`,
`sesnsp`, `conapo`, etc.), pero `sinaica_observaciones`/`sinaica_estaciones` tenían como
default `sinaica_observaciones_test`/`sinaica_estaciones_test`. Sin pasar `--vars`
explícito, un `dbt run` en producción caía de vuelta a los fixtures.

Confirmado contra el loader real (`src/ingesta/cargar_bronze_sinaica_real.py`, diccionario
`TABLAS = {'estaciones': 'sinaica_estaciones', 'observaciones': 'sinaica_observaciones'}`),
no se supuso el nombre. Corregidos los dos defaults en `sources.yml`. Verificado en Cloud
SQL tras un `dbt run` limpio (PASS=10, ERROR=0) que reconstruyó `silver.cemabe` (203,638
filas) y `gold.fact_escuela_ciclo` (132,566 filas): D6 pasa de 1.3% a **49.1%** de cobertura
OK — consistente con la limitación ya documentada de SINAICA (~80 zonas urbanas, radio
15km), no una regresión de este cambio.

## 2. D5: v1 propuesto, explícitamente sin aprobar todavía

Nuevo modelo `silver.agua_presa_entidad` (capacidad NAMO de presas por entidad; CDMX
resuelta vía el Sistema Cutzamala con el seed nuevo `dim_presa_cutzamala`, porque CDMX no
tiene presas propias) e integración en `gold.fact_escuela_ciclo` (d5/d5_cobertura). Usa
`bronze.conagua_presas` (snapshot real de presas, ya ingerido), no el contrato
diario/georreferenciado original de DS-06 que sigue sin ingerirse.

**El propio código lo marca como no mergeable todavía**: tanto el comentario de cabecera de
`fact_escuela_ciclo.sql` como la descripción del modelo en `schema.yml` dicen "PENDIENTE DE
APROBACIÓN de Edgar (dueño de este modelo) y de Emilio (dueño DS-06)". Se deja en esta rama
para que sea visible y discutible en el PR, no como trabajo cerrado.

Dos seeds nuevos (`dim_estado_inegi.csv`, `dim_presa_cutzamala.csv`) necesitaron
`+column_types` forzado a texto en `dbt_project.yml` — mismo patrón que `BUG-077`
(`dim_entidad`): sin esto, dbt infiere `INTEGER` de claves como "01"..."32" y el
`UNION`/`JOIN` contra la otra tabla (ya `varchar`) truena.

## 3. DS-03: verificación de producción de D3, hipótesis descartadas con datos reales

Investigación del mismo bug de Panorama de Riesgo: D3 también salía `SIN_DATO` para las 7
escuelas de mayor riesgo. A diferencia de D5/D6, el código no documenta a D3 como cobertura
parcial esperada (CEMABE es censo nacional a nivel escuela). Verificado contra
`gold.fact_escuela_ciclo` real:

- Cobertura por fila de ciclo: **85.8%** OK. Por escuela (exigiendo OK en todos sus ciclos):
  **84.6%** — casi idéntico porque `d3_cobertura` se une por `cct` contra `silver.cemabe` ya
  deduplicada (una fila por escuela), así que no varía entre ciclos de una misma escuela.
  Producción: **85.1%**. Las tres cifras consistentes entre sí.
- Se investigaron y **descartaron** dos hipótesis previas que no se sostuvieron con datos
  reales: un "56% por escuela" (la cifra real dio 84.6%) y un "~5% comunitario/CONAFE"
  (`sostenimiento` en `gold.dim_escuela` solo admite `PÚBLICO`/`PRIVADO` por diseño de DS-02
  — confirmado tanto en la documentación como contra los datos reales, público 86.6% OK /
  privado 83.0% OK, sin ninguna tercera categoría).
- El hueco (~14-15%) coincide con el riesgo ya anotado en DS-03 §10: CCT ausentes del censo
  CEMABE 2013 (reasignación de clave o escuelas creadas después del levantamiento).
- **Conclusión, documentada en DS-03 §11: D3 no requiere fix de código ni recarga de
  producción.**

## 4. Fixture de Gold para Andrés (C2), traído a la rama

`git merge wip/fixture-gold-chat-andres` trae el trabajo ya coordinado con Luis Téllez:
script generador (`generate_gold_chat_fixture.py`), loader
(`tests/fixtures/gold/cargar_fixture_gold.sql`) y su fix real (`variacion_matricula` es
`DOUBLE PRECISION`, no `INTEGER` — confirmado contra `fact_escuela_ciclo.sql:54-55`, nunca
fue `INTEGER` en Gold real). Ya tenía su propio DevLog
(`2026-09-13-diana-alvarez-fixture-gold-chat-andres.md`); se referencia aquí solo porque
entra a `dev/diana-alvarez` en esta sesión.

## Verificación

- `dbt run` / `dbt test` contra Cloud SQL: PASS=10, ERROR=0 (corrido por Diana Alvarez,
  13-sep-2026).
- D6: 49.1% OK (antes 1.3%) — confirmado con 3 consultas cruzadas (cobertura, drivers
  completos por fila, resumen por driver).
- D3 (DS-03): cobertura verificada por tres vías independientes (fila/escuela/producción),
  ver arriba.
- `pytest tests/ -q`: **pendiente de re-correr** con el contenido nuevo de esta rama antes
  de abrir el PR (última corrida confirmada, 1307 passed/10 skipped, fue antes de este
  trabajo).
- `python3 vault/_Meta/scripts/check_ownership.py --autor DianaVarela96 --rama dev/diana-alvarez --base origin/main`:
  pendiente de correr desde tu Mac antes de abrir el PR (todos los archivos tocados —
  `dbt/**`, `vault/14_Data_Sources/**` — están en tu verde; `tests/fixtures/gold/**` es
  amarillo, no bloqueante).
