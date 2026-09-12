---
project: "FARO"
date: "2026-09-12"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude"
model: "claude-sonnet-5"
session_duration: "diagnostico y fix del frente de dato de BUG-077 (dbt), a partir del hallazgo de Edgar Coronel"
touches: ["BUG-077", "US-621", "REQ-002", "RISK-006"]
tags: [devlog, bug077, dbt, gold, dim_municipio, seed]
---

# BUG-077 (frente de dato) — `nombre_entidad` deja de depender de CONEVAL

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|Bug_Register]] · [[vault/_DevLog/2026-09-12-edgar-coronel-regresion-completa-bug077|DevLog de Edgar (hallazgo original)]]

## Qué estaba roto

Edgar Coronel encontró en su corrida de regresión del 12-sep que `GET /api/v1/municipios`
responde `500` para el 97% del universo (307 de 317 municipios), registrado como **BUG-077**
(`critical`). Diagnóstico verificado en el código, no solo en el síntoma:
`dim_municipio.sql` tomaba `nombre_entidad` de `silver.rezago_municipio` (CONEVAL) por
`LEFT JOIN`, bajo el supuesto documentado en el propio modelo de que "CONEVAL publica el índice
de rezago para TODOS los municipios del país". Ese supuesto es falso en el Postgres local
verificado, y `MunicipioOut.nombre_entidad` es `StrictStr` (no admite `None`) — el hueco de dato
revienta la serialización de Pydantic en vez de degradar. El `data_test`
`not_null_dim_municipio_nombre_entidad` ya existía para atrapar justo esto y sí falla
(confirmado por Edgar), pero ningún workflow de CI corre `dbt test` (solo `dbt parse`), así que
nunca se vio antes de producción.

## Arreglo aplicado (frente de dato, `dbt/**`)

El nombre de una entidad **no es un dato variable**: las 4 `SCOPE_ENTIDADES` del proyecto son
fijas y conocidas (`dbt/macros/scope_entidades.sql`), a diferencia de población/rezago/pobreza,
que sí pueden faltar por municipio de forma legítima (`SIN_DATO`). Por eso la fuente correcta no
es heredar la cobertura parcial de CONEVAL, sino un catálogo propio:

- **`dbt/seeds/dim_entidad.csv`** (nuevo): `cve_ent -> nombre_entidad` para las 4 entidades del
  alcance (mismo patrón que `dim_driver`, `BUG-022`).
- **`dbt/seeds/_gold__seeds.yml`**: documentado con `unique`/`not_null`/`accepted_values` en
  ambas columnas.
- **`dbt/models/gold/dim_municipio.sql`**: `rezago_ultimo` deja de exponer `nombre_entidad`
  (columna CONEVAL, ahora sin uso en este modelo); el `SELECT` final lo toma de un nuevo
  `LEFT JOIN` contra `{{ ref('dim_entidad') }}` por `cve_ent` (que a su vez ya se deriva por
  `substring(cve_mun, 1, 2)`, 100% poblado, sin depender de ningún `JOIN` externo). El
  `data_test not_null_dim_municipio_nombre_entidad` existente queda intacto y ahora sí debería
  pasar siempre, porque las 317 filas del universo tienen un `cve_ent` de las 4 entidades
  cubiertas por el seed.

## Verificación

Sin `dbt`/Postgres disponibles en este entorno de agente: YAML de `_gold__seeds.yml` validado
con `yaml.safe_load` (`dim_driver` + `dim_entidad`, ambos parseables); `dim_municipio.sql`
revisado con balance de paréntesis/llaves Jinja (46/46, 5/5) y lectura manual completa del
`diff` contra el original. **Pendiente de verificación real contra Postgres** (`dbt seed`,
`dbt run --select dim_municipio`, `dbt test --select dim_municipio` y `curl /api/v1/municipios`)
antes de abrir PR — no se afirma "corregido" hasta correrlo contra datos reales.

## Fuera de alcance de este fix (frente de código, `src/api/**`, Christian Ruiz)

El propio registro del bug pide, como segunda defensa independiente, declarar
`MunicipioOut.nombre_entidad: StrictStr | None` con el mismo criterio `SIN_DATO` que ya usan
`poblacion`/`pobreza_pct` en el mismo esquema — para que un hueco de dato *futuro* (en cualquier
columna, no solo esta) degrade en vez de tronar con 500. `src/api/schemas.py` es una ruta
propiedad de Christian Ruiz (C4); no se tocó aquí. Tampoco se confirmó si el Postgres
compartido/producción tiene el mismo hueco de cobertura CONEVAL que el local — ya no es
necesario para este síntoma puntual (el fix de arriba no depende de esa cobertura), pero sigue
siendo relevante para cualquier otro consumidor de `rezago_municipio` que si dependa de ella.

## Registro y trazabilidad

`Bug_Register.md`: fila de BUG-077, estado de `open` a `in progress`; nota agregada bajo
"Dueño propuesto" marcando el frente (1) de Diana Alvarez como hecho (pendiente de PR/merge) y
enlazando este DevLog. Trabajo hecho en la rama `fix/bug-077-nombre-entidad-municipios`
(sobre `main`), sin `git push` todavía.
