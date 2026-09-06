---
project: "FARO"
date: "2026-09-05"
author_human: "Manuel Alejandro Serranía Reinada"
agent: "opencode"
model: "opencode/big-pickle"
session_duration: "sesión: BUG-054 DB-09 (prioridad ALTA y % escuelas), RISK-009 y revisoría de PR de C2"
touches: ["US-204", "REQ-002", "BUG-054", "RISK-009", "BUG-052", "BUG-050", "BUG-037", "PR-228", "PR-232", "PR-252", "DEC-016", "DEC-013"]
tags: [devlog, superset, bi, celula-2, qa]
---

# DevLog — 2026-09-05 — BUG-054 corregido (DB-09) y barrido de los mensajes cruzados de C2

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|Bug_Register]]

## Contexto

Cierre de ciclo de C2 en el sprint: la sesión cubrió (1) la revisoría del PR #228 de Monserrat
(US-215b, tabs DB-05) que terminó **aprobado**, (2) la evaluación del mensaje de Marina sobre
el PR #232 —agrupado de filas de `_layout_grilla()` (BUG-049) y paleta de `UX_Guidelines.md`
(BUG-050)—, y (3) el encargo recibido por mensaje sobre **BUG-054**: dos métricas rotas de
DB-09, el tablero del diferenciador, un día antes del freeze de la demo del 9-sep.

## 1. BUG-054 — dos defectos de hecho consumando en DB-09

Mensaje vía equipo (hallazgo de Marina, verificado contra la base por el PM). Confirmé ambos
en `metrics_db06_db09.yaml` sin necesidad de diagnóstico propio:

- **`:217`** — `recomendaciones_prioridad_alta` comparaba `prioridad = 'ALTA'` y el cubo la
  guarda en minúsculas (`alta`). `CASE` sin empates → `SUM` sobre vacío → `NULL` → la tarjeta
  "Recomendaciones de prioridad ALTA" mostraba `No data` con 2 escuelas `alta` en la base.
- **`:222`** — `pct_escuelas_recomendadas` dividía `SUM(recomendacion_emitida)` entre
  `COUNT(DISTINCT cct)`. `recomendacion_emitida` es `smallint` en `gold.cubo_recomendaciones`
  (`cubo_recomendaciones.sql:42`), así que su `SUM` es `bigint` y `bigint/bigint` es
  **división entera** en Postgres: hoy 55/55 = 100 % por coincidencia; con 54/55 mostraría
  **0 %**, no 98.2 %. Es el modo de falla de BUG-017/BUG-031: un número creíble que significa
  otra cosa. El PM sondearon las 19 divisiones de la capa con `pg_typeof`: esta era la única
  rota.

**Corrección aplicada (una línea cada una, inversión aditiva):**

```yaml
# :217
expresion: "SUM(CASE WHEN upper(prioridad) = 'ALTA' THEN 1 END)"
# :222
expresion: "SUM(recomendacion_emitida)::numeric / NULLIF(COUNT(DISTINCT cct), 0)"
```

**Guardas de regresión** en `tests/test_semantic_db06_db09.py`: las dos expresiones quedan
fijas en los tests existentes (rechazan que reaparezca la comparación sin `upper` o la
división sin `::numeric`). BUG-054 pasa a `fixed` en el registro con la evidencia, dejando
explícito el **re-sync pendiente** de la capa semántica para que se refleje en los tableros.

## 2. RISK-009 — ya estaba en main (lo registró el PM)

El mensaje traía el hallazgo de la familia: las otras 32 divisiones están a salvo por
coincidencia de tipos (`matricula_total` es `integer`/`bigint`/`numeric` según el cubo;
`variacion_ponderada_pct` existe en 5 copias, 2 con `* 1.0` y 3 sin). Al sincronizar con el
PR #254 del PM, la fila **RISK-009 ya está dada de alta** en `Risk_Register.md` (dueño:
Manuel Serranía, `abierto`, post-freeze). No se duplicó.

## 3. Revisoría — PR #228 (aprobado) y evaluación del mensaje de Marina

- **PR #228** (US-215b / BUG-038): primer review con `request-changes` (renumerar BUG-049→
  BUG-051 por DEC-013; sync; assert duplicado); la autora corrigió todo —`behind_by=0`,
  checks verdes, 0 refs a BUG-049— y emití **`approve`** en el re-review.
- **PR #232** (Marina): verifiqué `_agrupar_en_filas` contra los anchos reales de los YAML
  —sus números de filas por tablero dan exactos— y `test_el_layout_genera_estructura_v2`
  (la aserción vieja codificaba el defecto; el cambio es correcto y transparente). Paleta de
  `UX_Guidelines.md`: es de C2 — BUG-050 asigna el llenado a Manuel; acordé **ratificar la
  propuesta base de Marina** cuando la traiga (con AA 4.5:1 en ambos temas).
- **BUG-052** (intermitente, `test_frontend_dashboards_streamlit.py`, Windows): dueño Manuel
  (`src/frontend/**`). **Post-freeze** — el fix es replicar el patrón de
  `test_frontend_panel_ml_streamlit.py` (purga `cache_resource`); verificación determinística
  en macOS + loop en runner Windows.
- **BUG-037** (refresh de columnas tras PUT del sync): lo tomó **Oscar Quiroz**, post-freeze.

## Seguridad / calidad

- [x] `pytest tests/test_semantic_db06_db09.py -q` → 48 passed
- [x] `ruff check superset/ tests/` → limpio
- [x] `python vault/_Meta/scripts/vault_lint.py .` → sin bloqueos nuevos (los 3 son los
      untracked conocidos de la raíz, nunca se commitean)
- [x] Sync con `origin/main` antes y después de trabajar (`3b6c6cf`)
- [x] Sin secretos: ningún `.env` ni token en el árbol; los parches son expresiones SQL

## Riesgos y pendientes

- **Re-sync de la capa semántica pendiente** para que BUG-054 se vea en los tableros:
  coordinar con quien ejecute el próximo sync/bootstrap (Luis/Edgar) y reconfirmar en
  navegador antes del 9-sep. La tarjeta prioridad pasa de `No data`→2; el % puede mostrar
  fracción.
- Post-freeze: BUG-052 (fix del fixture), BUG-037 (Oscar), ratificación de la paleta de
  Marina.