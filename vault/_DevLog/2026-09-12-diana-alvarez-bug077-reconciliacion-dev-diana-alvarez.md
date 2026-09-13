---
title: "Reconciliación de fix/bug-077-nombre-entidad-municipios con dev/diana-alvarez: el frente de dato de BUG-077 entra a la rama fija tras el merge de PR #325"
fecha: 2026-09-12
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [BUG-077, US-621, REQ-002, RISK-006]
---

## Contexto

El frente de dato de `BUG-077` (`nombre_entidad` de `dim_municipio.sql` dejando de depender de
la cobertura de CONEVAL) se diagnosticó, corrigió y **verificó de punta a punta contra Postgres
real** (17/17 tests de `dbt test --select dim_municipio`, 317/317 municipios sin `nombre_entidad`
vacío, caso puntual `14113` confirmado) el mismo 12-sep, pero por error se hizo en una rama nueva
(`fix/bug-077-nombre-entidad-municipios`, sobre `main`) en vez de `dev/diana-alvarez` -- este repo
exige una rama fija por persona (`check_ownership.py`) y rechaza abrir PR desde cualquier otra.
Diana documentó entonces la decisión de **esperar a que el PR #325 se mergeara** antes de traer
esos commits a `dev/diana-alvarez`, en vez de mezclarlos con la revisión ya en curso (ver
[[vault/_DevLog/2026-09-12-diana-alvarez-bug077-nombre-entidad|DevLog original del fix]]). PR #325
ya se mergeó y `dev/diana-alvarez` ya se reconcilió dos veces desde entonces (con
`dev/diana-alvarez-rediseno` y con `origin/main`) -- toca cerrar ese pendiente.

## Qué se hizo

`git merge fix/bug-077-nombre-entidad-municipios` sobre `dev/diana-alvarez` (local). Un solo
conflicto real, en `vault/06_Quality_Testing/Bug_Register.md`: ambas ramas habían editado la
fila de `BUG-077` -- la de `dev/diana-alvarez` (heredada del merge con `origin/main`) seguía con
el estado `open` original de Edgar; la del fix la actualizaba a `fixed (frente de dato)` con el
detalle de la verificación real. Se conservó la versión actualizada del fix, corrigiendo de paso
la nota "sin `git push` todavía" (ya estaba pusheada) y "pendiente de PR/merge" (ya se está
mergeando aquí mismo), y se conservaron sin tocar las 3 filas de `BUG-078`/`BUG-079`/`BUG-080` que
`dev/diana-alvarez` ya traía del PR de Luis Téllez. `vault/_DevLog/_index.md` fusionó limpio, sin
conflicto (ambas ramas agregaron filas distintas).

Contenido real que entra a `dev/diana-alvarez` (3 commits): `dbt/seeds/dim_entidad.csv` nuevo
(catálogo propio `cve_ent -> nombre_entidad` para las 4 entidades del alcance, mismo patrón que
`dim_driver`/BUG-022), `dbt/seeds/_gold__seeds.yml` documentado con `unique`/`not_null`/
`accepted_values`, y `dbt/models/gold/dim_municipio.sql` resolviendo `nombre_entidad` contra ese
catálogo por `cve_ent` en vez del `LEFT JOIN` a `silver.rezago_municipio` (CONEVAL) que solo
cubría 10/317 filas.

## Lo que NO se tocó, y por qué

El frente de código (`src/api/schemas.py`, `MunicipioOut.nombre_entidad` como `StrictStr | None`
con defensa `SIN_DATO`) sigue siendo alcance de Christian Ruiz (C4) -- ya lo resolvió por su
cuenta en `dev/christian-ruiz` (commit `27a9956`, fuera de esta rama). Tampoco se confirmó si el
Postgres compartido/producción tiene el mismo hueco de cobertura CONEVAL que el local -- ya no es
necesario para este síntoma puntual (el fix no depende de esa cobertura), documentado como tal en
el DevLog original.

## Verificación

`git diff --check` limpio. `dbt/seeds/_gold__seeds.yml` parseable con `yaml.safe_load`.
`dim_municipio.sql`: balance de paréntesis/llaves Jinja 46/46, 10/10. `vault_lint.py` limpio
(mismos 11 huérfanos preexistentes). La verificación real contra Postgres (17/17 dbt tests,
317/317 municipios) ya se hizo antes, en la máquina de Diana, documentada en el DevLog original --
no se repite aquí, solo se reconcilia el código ya verificado.
