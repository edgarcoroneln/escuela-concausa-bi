---
id: DOC-CUBESPEC-DB07
title: "Cube Specs — DB-07 Calidad y cobertura de datos"
owner: "Oscar Antonio Quiroz Lázaro"
status: approved
version: "1.0"
traces_up: ["vault/04_UX_Design/Screen_Specs", "US-222"]
traces_down: []
last_reviewed: "2026-09-04"
tags: [ux, dashboards, kpis, celula-2, completitud]
---

# Cube Specs — DB-07 Calidad y cobertura de datos

> Contrato semántico de DB-07: completitud de drivers por municipio/nivel/driver
> y mapa de vacíos territoriales. Implementa **US-222** (REQ-002), consumiendo
> el catálogo canónico de KPI-05 y KPI-06 ya fijado en
> [[vault/04_UX_Design/Screen_Specs]] §4 (US-201, Manuel Serranía).

## 1. Fuente de datos

`gold.cubo_completitud` (US-113, Diana Álvarez / Célula 1), materializado como
`materialized_view` en dbt (`dbt/models/gold/cubo_completitud.sql`). Grano:
`cve_mun × nivel × id_driver × id_ciclo`.

Las fórmulas de KPI-05 y KPI-06 están fijadas explícitamente en el contrato
dbt del modelo (`dbt/models/gold/_cubo_completitud.yml`):


```
completitud_promedio = SUM(suma_completitud) / NULLIF(SUM(total_escuelas), 0)
pct_sin_dato          = SUM(escuelas_sin_dato) / NULLIF(SUM(total_escuelas), 0)
```

Este documento no reinterpreta esas fórmulas — las expone tal cual en la capa
semántica de Superset.

## 2. Datasets

### `db07_cubo_completitud` — grano detallado

Casi un `SELECT *` sobre el cubo materializado. Expone `nivel` e `id_driver`
para desglose por driver o por nivel educativo. Bandera de cobertura:
`cobertura_driver` (`'OK'` / `'SIN_DATO'`).

### `db07_mapa_vacios` — grano agregado municipal

Agrega `db07_cubo_completitud` sin `nivel` ni `id_driver` (suma los 6 drivers),
unido a `gold.geo_municipio` para exponer `geometria` (texto GeoJSON). **Sin
nivel ni driver en el grano, a propósito** — mismo patrón que
[[vault/04_UX_Design/Screen_Specs]] usa en `db02_coropletico`: con esas dimensiones,
un municipio produciría varias filas y el JOIN geométrico dibujaría polígonos
superpuestos.

## 3. Validación realizada

Ambos SQL se corrieron directamente contra Postgres real (no solo contra
fixtures):

- `db07_cubo_completitud.sql` → 72 filas, coincide exactamente con las 72
  filas que dbt reportó al materializar `gold.cubo_completitud`.
- `db07_mapa_vacios.sql` → 6 filas (3 municipios × 2 ciclos), aritmética
  interna consistente (`escuelas_con_dato + escuelas_sin_dato = total_escuelas`
  en cada fila) y geometría poblada correctamente vía el `JOIN`.

7 pruebas automatizadas (`tests/test_db07_calidad_cobertura.py`) validan
contra fixtures sintéticas: coherencia interna, fórmulas KPI-05/06 con la
regla SIN_DATO≠0, ausencia de duplicados en el grano del mapa, presencia de
geometría, y que el agregado del mapa coincide exactamente con la suma manual
del detalle.

## 4. Bloqueo conocido — registro en Superset

El registro real de estos 2 datasets en Superset (vía
`sync_semantic_layer.py`) está **bloqueado**, pero no por un error de este
YAML o SQL: el sincronizador recorre alfabéticamente todos los `.sql` de
`superset/semantic/` y se detiene en `db09_cubo_recomendaciones.sql` (US-204,
Manuel Serranía) con el error `relation "gold.recomendaciones" does not
exist`.

Se investigó la causa raíz: ningún modelo del esquema `bronze` está cargado
en este ambiente local (`dbt run` completo falla con 9 errores, todos del
tipo `relation "bronze.*" does not exist`), por lo que ningún cubo Gold que
dependa de Bronze puede materializarse — incluyendo `gold.recomendaciones`.
Esto es un bloqueo de infraestructura de ambiente local, ajeno al SQL de
Manuel y fuera del alcance de esta historia (US-222).

`gold.cubo_completitud` sí pudo materializarse porque su única dependencia,
`gold.fact_escuela_ciclo`, ya existía como tabla en este ambiente.

**Actualización 2026-09-03 — bloqueo resuelto.** BUG-029 corregido (el sync ya no aborta en
cascada) y Bronze real cargado (CCT, Formato 911, CONEVAL vía el extractor oficial de Deni
Garrido). `dbt run` completo materializa `gold.cubo_completitud` con 162 filas reales; DB-07 está
registrado y vivo en Superset local, con captura real en
[[vault/04_UX_Design/Manual_Usuario_Dashboards]]. Pendiente aparte, no bloqueante: los KPIs que
dependen de `gold.predicciones`/`recomendaciones` (mock ML-01/02) siguen en SIN_DATO porque ese
mock no cruza con el catálogo real de escuelas.

**Actualización 2026-09-04 — BUG-047: el filtro de ciclo triplicaba los conteos absolutos.**
Edgar reportó (mismo aviso a Manuel) que un tile "total" sin el filtro de ciclo vigente aplicado
podía heredar el patrón de BUG-044 (API). Verificado en vivo: el filtro "Ciclo escolar" de DB-07
nacía sin `defaultDataMask` — `enableEmptyFilter: False` + `multiSelect: True` hacía que Superset
preseleccionara los 3 ciclos materializados. `total_escuelas` mostraba **25,578** (suma de
2022-2023 + 2023-2024 + 2024-2025) en vez de **8,382** (el ciclo vigente); mismo factor ~3× en
`escuelas_con_dato`/`escuelas_sin_dato`. `completitud_promedio` y `pct_sin_dato` (KPI-05/06) no se
vieron afectados — al ser razones `SUM/SUM`, numerador y denominador se inflaban igual (78.3%
antes y después). Corregido en `_filtros_nativos()` (`superset/sync_semantic_layer.py`): el
`default: ultimo_ciclo` ya declarado en `metrics_db07.yaml` ahora se resuelve dinámicamente contra
`MAX(id_ciclo)` real (nunca hardcodeado) y se agregó al YAML del tablero
(`superset/dashboards/db07_calidad_cobertura.yaml`), que no lo traía. Verificado tras el fix:
`total_escuelas` = 8,382. Detalle completo y evidencia de los otros 7 tableros afectados en
`BUG-047` ([[vault/06_Quality_Testing/Bug_Register]]). La captura de DB-07 en el manual quedó
tomada con el defecto activo — pendiente retomarla.

## 5. Trazabilidad

- **Implementa:** US-222 (REQ-002)
- **Consume:** [[vault/04_UX_Design/Screen_Specs]] (catálogo canónico KPI-05/06,
  US-201) · `gold.cubo_completitud` (US-113, Diana Álvarez)
- **Bloqueo documentado:** registro en Superset pendiente de que se resuelva
  la carga de Bronze en el ambiente (fuera del alcance de US-222)