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

# DevLog — 2026-09-13 — D6 fix (código, pendiente de producción), D5 agua v1 rechazado en revisión y verificación de D3 en DS-03 (US-121a, US-122a)

→ [[vault/_DevLog/_index|Volver al índice]]

> **Corrección de Edgar Coronel (revisión de PR #358, 2026-09-13, dos rondas):** este DevLog
> originalmente afirmaba que D6 ya estaba verificado "en producción" y proponía D5 v1 como
> mergeable (ronda 1, secciones 1 y 2). En una segunda ronda, Edgar notó que DS-03 §11 tenía el
> mismo problema con D3 (85.8%/84.6%/85.1% "en producción") -- corregido también (sección 3).

## Qué se hizo

1. **D6 (aire), fix de código de un bug real**: `dbt/models/sources.yml` traía como default las
   tablas `*_test` de SINAICA en vez de las reales. El fix es correcto, pero **no cambia nada en
   producción todavía** — ver corrección de Edgar en la sección 1.
2. **D5 (agua), v1 propuesto y RECHAZADO en revisión**: nuevo modelo `silver.agua_presa_entidad`
   (capacidad NAMO de presas por entidad, CONAGUA). Edgar (dueño de `fact_escuela_ciclo.sql`) lo
   rechazó en la revisión del PR #358 y se sacó de la rama — ver sección 2.
3. **DS-03 (CEMABE)**: verificación del hueco de cobertura de D3, documentada en el propio
   archivo DS-03 (§11). **Corregida en una segunda ronda de revisión de Edgar** -- mismo error
   que D6: las cifras no eran de producción real. Ver sección 3.
4. Traído a la rama el trabajo ya coordinado de Andrés González (fixture de Gold para su
   chat/agente Text-to-SQL local) — **aprobado por Edgar** en la misma revisión (alcance y datos:
   260 escuelas anonimizadas, sin coordenadas ni infraestructura). Ver también su propio DevLog.

## 1. D6: fix de código correcto, pero producción no cambia todavía

En `https://faro-frontend-eanzfglvyq-uc.a.run.app/panorama`, la comparativa de drivers mostraba
D6 en `SIN_DATO` para las 7 escuelas de mayor riesgo. Diagnóstico: `sources.yml` define cada
fuente Bronze como `var('bronze_X_identifier', '<default>')` — en **todas** las demás fuentes del
archivo el default ya es la tabla real de producción (`cemabe_2013`, `sesnsp`, `conapo`, etc.),
pero `sinaica_observaciones`/`sinaica_estaciones` tenían como default
`sinaica_observaciones_test`/`sinaica_estaciones_test`. Confirmado contra el loader real
(`src/ingesta/cargar_bronze_sinaica_real.py`, diccionario `TABLAS = {'estaciones':
'sinaica_estaciones', 'observaciones': 'sinaica_observaciones'}`), no se supuso el nombre.
Corregidos los dos defaults en `sources.yml` — **el fix de código es correcto y se queda en el
PR**.

**Corrección de Edgar (revisión PR #358):** el `dbt run`/`dbt test` que corrí y que dio D6 en
49.1% de cobertura OK (`silver.cemabe` con 203,638 filas, `gold.fact_escuela_ciclo` con 132,566
filas) **no se corrió contra la base de datos de producción real**. Edgar confirma que producción
hoy solo tiene los Bronze de prueba (`cemabe_2013` con 72 filas) — mi verificación se hizo con
Bronze real ya cargado en otro entorno, no en producción. Esto significa que **hoy, en
producción, Panorama va a seguir mostrando D6 en `SIN_DATO`** hasta que alguien cargue el Bronze
real de SINAICA/CEMABE en producción y regenere e importe Gold ahí — este fix de `sources.yml`
es condición necesaria pero no suficiente por sí solo.

## 2. D5: v1 propuesto, RECHAZADO en revisión y sacado del PR

Se había propuesto un nuevo modelo `silver.agua_presa_entidad` (capacidad NAMO de presas por
entidad; CDMX resuelta vía el Sistema Cutzamala con un seed nuevo, `dim_presa_cutzamala`, porque
CDMX no tiene presas propias) integrado en `gold.fact_escuela_ciclo` (d5/d5_cobertura). Usaba
`bronze.conagua_presas` (snapshot real de presas, ya ingerido), no el contrato
diario/georreferenciado original de DS-06 que sigue sin ingerirse.

**Edgar (dueño de `fact_escuela_ciclo.sql`) lo rechazó en la revisión del PR #358**: la capacidad
de presas por entidad da el mismo valor a todas las escuelas de un mismo estado — grano
insuficiente para esta entrega, no se adopta. Por su indicación, se sacó del PR por completo:

- `dbt/models/silver/agua_presa_entidad.sql` (modelo) — eliminado.
- `dbt/seeds/dim_estado_inegi.csv`, `dbt/seeds/dim_presa_cutzamala.csv` (los dos seeds de apoyo)
  y su entrada en `dbt/seeds/_silver__seeds.yml` — eliminados.
- Su configuración de `+column_types` en `dbt/dbt_project.yml` — revertida.
- Su doc block en `dbt/models/silver/schema.yml` — revertido.
- La CTE `d5` y su `left join` en `dbt/models/gold/fact_escuela_ciclo.sql` — revertidos. **D5
  vuelve a ser `SIN_DATO` explícito** (`cast(null as double precision) as d5, 'SIN_DATO' as
  d5_cobertura`), igual que antes de este trabajo.

D5 sigue pendiente de una versión con el contrato real de DS-06 (diario/georreferenciado), no de
este atajo por infraestructura instalada.

## 3. DS-03: verificación de la lógica de D3 — mismo error de "producción" que D6, corregido

Investigación del mismo bug de Panorama de Riesgo: D3 también salía `SIN_DATO` para las 7
escuelas de mayor riesgo. **Corrección (Edgar, revisión de PR #358):** igual que con D6 arriba,
las cifras de abajo (85.8%, 84.6%, y un "85.1% en producción" ya retirado) **no salieron de
producción real** — vinieron del mismo entorno con `bronze.cemabe_2013` real cargado que se usó
para D6, no de Cloud SQL de producción. Corregido en detalle en DS-03 §11; resumen:

- Con censo real cargado (no producción): cobertura por fila de ciclo **85.8%** OK, por escuela
  **84.6%** — esto confirma que el join/la lógica de D3 (unión por `cct` contra `silver.cemabe`
  ya deduplicada) funciona bien cuando hay censo real. No dice nada sobre el estado actual de
  producción.
- Se investigaron y **descartaron** dos hipótesis previas: un "56% por escuela" (la cifra del
  entorno con censo real dio 84.6%) y un "~5% comunitario/CONAFE" (`sostenimiento` en
  `gold.dim_escuela` solo admite `PÚBLICO`/`PRIVADO` por diseño de DS-02 — esto sí es un hecho de
  esquema, confirmado independientemente del entorno).
- El hueco (~14-15%, con censo real cargado) coincide con el riesgo ya anotado en DS-03 §10: CCT
  ausentes del censo CEMABE 2013.
- **Conclusión corregida, documentada en DS-03 §11:** el join/la lógica de D3 no requiere fix de
  código, pero **sí hace falta cargar el censo CEMABE 2013 real en el Bronze de producción**
  (hoy solo tiene el fixture de 72 filas, igual que SINAICA en D6) — no es un pendiente ya
  resuelto, es el mismo pendiente que D6.

## 4. Fixture de Gold para Andrés (C2), traído a la rama — aprobado por Edgar

`git merge wip/fixture-gold-chat-andres` trae el trabajo ya coordinado con Luis Téllez: script
generador (`generate_gold_chat_fixture.py`), loader (`tests/fixtures/gold/cargar_fixture_gold.sql`)
y su fix real (`variacion_matricula` es `DOUBLE PRECISION`, no `INTEGER` — confirmado contra
`fact_escuela_ciclo.sql:54-55`, nunca fue `INTEGER` en Gold real). Ya tenía su propio DevLog
(`2026-09-13-diana-alvarez-fixture-gold-chat-andres.md`); se referencia aquí solo porque entra a
`dev/diana-alvarez` en esta sesión. **Edgar aprobó el alcance y los datos en la revisión del PR
#358** (260 escuelas anonimizadas, sin coordenadas ni infraestructura) — anotado en su propio
DevLog.

## Verificación

- `dbt run` / `dbt test`: PASS=10, ERROR=0 (corrido por Diana Alvarez, 13-sep-2026) — **contra un
  entorno con Bronze real cargado, no contra producción** (ver corrección de Edgar en la sección
  1). Sirve para confirmar que el fix de código funciona, no que producción ya cambió.
- D6: 49.1% OK en ese entorno (antes 1.3%) — confirmado con 3 consultas cruzadas (cobertura,
  drivers completos por fila, resumen por driver). **En producción sigue en `SIN_DATO`** hasta
  cargar Bronze real ahí y regenerar/importar Gold.
- D3 (DS-03): **corregido** — la cobertura de arriba (85.8%/84.6%) se verificó contra el mismo
  entorno no productivo que D6, no contra producción real (ver sección 3 y DS-03 §11). No hay
  verificación confirmada contra producción real para D3.
- `pytest tests/ -q`: **1322 passed** (confirmado por Edgar en su revisión del PR #358; la
  corrida anterior de esta rama, antes de traer `main`, había dado 1307 passed/10 skipped).
- `python3 vault/_Meta/scripts/check_ownership.py --autor DianaVarela96 --rama dev/diana-alvarez --base origin/main`:
  verde para todos los archivos tocados (`dbt/**`, `vault/14_Data_Sources/**`); `check_ownership`
  y `dbt` en verde según la revisión de Edgar.
