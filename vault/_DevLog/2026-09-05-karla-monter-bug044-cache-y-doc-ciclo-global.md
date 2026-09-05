---
project: "FARO"
date: "2026-09-05"
author_human: "Karla Alejandra Monter Benitez"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — sync post-merge + dos pendientes menores de revisión de BUG-044"
touches: ["US-411", "BUG-044", "REQ-004"]
tags: [devlog, celula-4, api, gold, backend]
---

# DevLog — 2026-09-05 — BUG-044: cache de `_ciclo_mas_reciente()` y doc del default global

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/API_Specification|API_Spec §3.3]] ·
[[vault/06_Quality_Testing/Bug_Register|Bug_Register (BUG-044)]]

## Contexto

El PR #210 (BUG-044) ya se mergeó y Luis Téllez lo redesplegó el 2026-09-04
([[vault/_DevLog/2026-09-04-luis-tellez-bug044-redeploy-matricula-ciclo-vigente]]) — la URL
pública ya sirve el ciclo vigente correcto. Christian Ruiz dejó dos pendientes menores en la
revisión del PR, ninguno bloqueante:

1. `_ciclo_mas_reciente()` hace un `SELECT MAX(id_ciclo)` extra en cada petición a
   `/escuelas`/`/kpis`/`/escuelas/{cct}`; el set de ciclos solo cambia cuando corre dbt, así que
   cachearlo (`lru_cache` o TTL corto) es gratis.
2. El default de ciclo es **global** (`MAX` de toda la tabla), no por filtro: si una entidad no
   tiene datos todavía del ciclo más reciente, la respuesta es lista vacía, no el último ciclo
   *de esa entidad*. Christian cree que es el comportamiento correcto; falta documentarlo para
   que nadie lo lea como bug nuevo en dos semanas.

Primero sincronicé `dev/karla-monter` con `main` (224 commits, fast-forward sin conflictos —
mucho pasó estos dos días: BUG-044 en prod, BUG-045 a BUG-050, US-411/US-412 ya `done` en
`Execution_Status.md`, US-005 formaliza el rol de Vault Steward).

## Qué se hizo

**1. Cache TTL de 5 minutos.** `RepositorioGoldPostgres._ciclo_cache` (atributo de **clase**, no
de instancia: `get_repositorio_gold()` crea una instancia nueva por petición vía `Depends`, así
que un cache de instancia no serviría de nada). `_ciclo_mas_reciente()` reusa el valor si
`time.monotonic() - marca < 300`, si no vuelve a consultar. 300s en vez de un `lru_cache`
permanente porque el proceso de Cloud Run puede vivir horas bajo carga sostenida (no se recicla
en cada request) y un cache sin vencimiento serviría un ciclo obsoleto por todo ese tiempo si
corre un dbt nuevo mientras la instancia sigue viva.

**2. Documentado el alcance global del default**, en tres lugares para que quien lea cualquiera
de los tres lo entienda sin tener que encontrar los otros dos: el docstring de
`_ciclo_mas_reciente()` (la explicación completa, con el paralelo a BUG-017/BUG-030 -- números
"creíbles y falsos" por mezclar periodos sin marcarlo), los docstrings del `Protocol` (referencia
corta a la explicación completa) y `API_Specification.md` §3.3 (para quien lee el contrato sin
tocar código). El punto central: **no es un bug** que una entidad rezagada salga vacía sin
`ciclo` explícito -- es el filtro haciendo su trabajo. Para leer el último dato disponible de una
entidad que va atrás, hay que pedirlo con `ciclo` explícito.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-sonnet-5.
- **Archivos modificados:** `src/api/repositorio_gold.py`,
  `vault/03_Architecture/API_Specification.md`, este DevLog.
- **Archivos nuevos:** `tests/test_repositorio_gold_cache.py`.
- **Decisiones autónomas del agente:** TTL de 300s en vez de `lru_cache` permanente (la
  alternativa que sugería el reviewer), por el riesgo de servir un ciclo obsoleto en una
  instancia de Cloud Run de vida larga; diseño de las pruebas con un motor falso que solo cuenta
  llamadas a `execute()`, para no necesitar Postgres real ni tocar el patrón ya acordado con
  Christian de `RepositorioGoldFake` (que no necesita este cache: es O(1) en memoria). La
  redacción exacta de la nota de "ciclo global" (el paralelo con BUG-017/BUG-030) se le presentó
  a Karla antes de escribirla en el contrato público, por ser la pieza que más fácilmente se
  lee como bug si queda mal explicada.
- **Correcciones manuales:** ninguna; Karla confirmó el enfoque de TTL vs. `lru_cache` antes de
  implementarlo.

## Seguridad / calidad
- [x] Sin secretos hardcodeados
- [x] Tests agregados: `tests/test_repositorio_gold_cache.py` (3 casos: no repite la consulta
  dentro del TTL, recalcula pasado el TTL, el cache se comparte entre instancias). Suite completa
  `pytest tests/ -q`: **978 passed, 4 skipped**, sin fallos nuevos.
- [x] `vault_lint.py` → Vault limpio.
- [x] DevLog enlaza a los IDs afectados (US-411, BUG-044, REQ-004)

## Próximos pasos
- Ninguno de mi lado -- estos eran los dos pendientes menores que quedaban del PR de BUG-044.
- Abrir PR contra `dev/karla-monter` con este commit; no bloquea nada, es limpieza post-revisión.
