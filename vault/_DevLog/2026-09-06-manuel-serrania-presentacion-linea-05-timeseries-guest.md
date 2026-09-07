---
id: DEVLOG-20260906-c2-manuel-umbrallinea05-timeseries-guest
title: "Presentación en 0.50 y fix definitivo del guest timeseries"
owner: "Manuel Alejandro Serranía Reinada"
status: approved
source_of_truth: true
story: "US-203 / US-215a / US-526"
tags: [devlog, umbral, dec-019, guest, superset, sync]
---

## Handoff — 2026-09-06 — OpenCode (big-pickle)

- **Current objective:** ejecutar el último PR de C2 antes del CODE FREEZE con los
  tres frentes acordados en el cierre: portada navegable, presentación alineada a
  `LINEA_DE_ALERTA` (0.50, DEC-019) y el 403 de los guests en timeseries cerrado de
  forma definitiva en el sync.
- **Current branch:** `dev/manuel-serrania` (base `origin/main` = `1a88a84`).
- **Latest graph status:** `graphify-out/GRAPH_REPORT.md` existe; no se re-corrió
  `graphify update` en esta sesión.
- **Relevant Graphify queries:** ninguna; se trabajó sobre refs directas
  `file:line` ya consolidadas del cierre anterior.
- **Files changed:**
  - `src/frontend/app.py` — botones de portada `st.button` (sin acción) →
    `st.page_link` a `pages/1_Dashboards.py`, `2_Panel_ML.py`, `3_Chat.py`
    (P1; label del menú lateral sigue siendo `app`, no se migró a `st.navigation`).
  - `superset/semantic/metrics_db01_db02.yaml` — `umbral: 0.6` → `0.5` en las dos
    métricas `escuelas_en_riesgo` (`db02_cubo_riesgo_territorial` y `db02_coropletico`).
  - `superset/semantic/metrics_kpis_base_us221.yaml` — nota KPI-04 cita `DEC-019`,
    índice ≥ 0.5.
  - `superset/dashboards/db02_mapa_riesgo.yaml` y `db09_recomendaciones.yaml` —
    `subheader` del tile KPI-04 → "≥ 0.5 (DEC-019)". **DB-03 KPI-17 NO se tocó**
    (sigue siendo el ancla de calibración 0.60, DEC-006; decisión del usuario).
  - `superset/sync_semantic_layer.py` — `_query_context_timeseries(eje_x)` +
    `ensure_chart` persiste `query_context` con ej X como adhoc `BASE_AXIS`
    (dict exacto de Superset 6.1.0) en charts `echarts_timeseries_*`, POST y PUT.
  - `tests/test_umbral_alineado.py` (nuevo) — `umbral:` == `LINEA_DE_ALERTA`,
    nota de KPI-04 sin DEC-006/0.6, subheaders sin 0.6.
  - `tests/test_semantic_db01_db02.py` — `UMBRAL_RIESGO` a 0.5 + docstring; 3 casos
    nuevos: helper `BASE_AXIS`, POST y PUT de `ensure_chart` con `query_context`.
- **IDs touched:** BUG-058, BUG-060, DEC-019, US-203, US-215a, US-526, REQ-002, AC-002.1.
- **Decisions made:**
  - P1 se resuelve solo con `st.page_link` (más pequeño, sin reestructurar el menú);
    el problema de etiqueta del label raíz (`app`) queda como mejora futura.
  - El umbral de la presentación se mueve a 0.5 **ahora**, porque la condición que
    Marina y Christian impusieron ya se cumplió: los cubos Gold cuentan con
    `>= 0.5` desde el PR #273 (C1, Diana). Cambiar el cartel antes que el dato lo
    hacía mentira; cambiarlo después cierra la cadena.
  - `tests/test_linea_de_alerta.py` (PM/Christian) + `tests/test_umbral_alineado.py`
    (C2) quedan como las dos guardas gemelas del corte: Python/dbt y presentación.
- **Open questions:** nada bloqueante para el PR. El cierre visual (KPI-04 > 0 en
  DB-02/DB-09) exige el re-sync del ambiente + mantener la re-materialización que ya
  corre con los cubos en 0.5. Verificar en navegador antes del 9-sep.
- **Risks:**
  - Un `dbt run` de Gold en 0.5 sin el re-sync de los YAML dejaría el cartel viejo;
    el re-sync sin los cubos re-materializados dejaría el dato viejo. Ambos pasos ya
    están hechos en código; falta ejecutarlos juntos en el ambiente (coordinado con
    Luis/Edgar).
  - El POST/PUT de charts con `query_context_generation=True` + `query_context`
    explícito replica exactamente la receta que C5 verificó en prod; si el servidor
    regenerara, el dict sigue entrando por delante. Monótono: solo 403→200.
- **Tests executed:**
  - `pytest tests/test_umbral_alineado.py tests/test_semantic_db01_db02.py
    tests/test_linea_de_alerta.py tests/test_semantic_repunteo_cubos.py` →
    **99 passed**.
  - Suite completa ignorando 13 archivos con deps ausentes (`limits`, etc., fallan
    idéntico antes/después con `git stash`): **898 passed**, 21 fallos pre-existentes
    idénticos, 4 skipped, **0 fallos introducidos**.
  - `ruff check` en app.py, sync, tests → limpio. `vault_lint.py` → pendiente de
    correr en el push final (3 archivos untracked conocidos en la raíz que **nunca**
    se commitean: `PLAN_US206_EMBEBIDO.md`, `avisosequipo.md`,
    `plan7diasporpersona.md`, `gx/`).
- **Next recommended action:**
  1. `repo-security-audit` + commit/push + PR estándar (título con sufijo `(BUG-060, BUG-058)`),
     reviewer `edgarcoroneln`.
  2. Coordinar con Luis/Edgar el re-sync de la capa semántica tras el merge y
     reconfirmar DB-07 (8 382), DB-09 y KPI-04 ≥ 1 en el navegador.
  3. BUG-052 (replicar purga `cache_resource` en el test de frontend) y BUG-037
     (dueño Monserrat, Manuel reviewer) quedan **post-freeze**, ya registrados.
---

## Segunda ronda (PR #275) — barrido de umbrales residuales, respuesta al PM

El PM (Edgar) corrió la rama completa (1070 passed, 4 skipped, ruff y vault_lint
limpios, 4 checks verdes) y detectó **3 sitios residuales en 0.6** que la guarda
original (4 archivos) no alcanzaba a ver:

1. `superset/semantic/db09_cubo_recomendaciones.sql:62` — `WHEN p.indice_riesgo >= 0.6
   THEN TRUE` (corte ejecutable, DB-09 cuenta con 0.6). → `>= 0.5`,
   comentario `-- DEC-019: linea de alerta`.
2. `superset/semantic/metrics_db06_db09.yaml` — `umbral: 0.6` ×3 (escuelas_en_riesgo
   de db06_cubo_predicciones y db06_predicciones_escuela y db09_cubo_recomendaciones)
   y `metrics_db03_db04.yaml` ×2, todos → 0.5.
3. `superset/dashboards/db03_ficha_escuela.yaml:87` — subheader del KPI-17
   «en riesgo desde 0.60 (DEC-006)» → «desde 0.50 (DEC-019)». **Anula la decisión
   previa de no tocar DB-03 KPI-17**: la etiqueta visible describe la línea de
   alerta, no el ancla. El ancla `ANCLA_SIGMOIDE = 0.60` sigue viva solo en Python
   y en la documentación de calibración.

**Además (consistencia con el barrido):** comentarios de cabecera de
db02/db03/db04/db06 (SQL), READMEs (superset/ y superset/semantic/), y la banda
ALTA `riesgo_mock >= 0.6` del mock. El bucket de distribución `rango_riesgo` de
db06 (`indice_riesgo < 0.6`, rotulado "0.40 - 0.59") **no es la línea de alerta** y
se conserva; queda documentado en la guarda.

**Guarda ensanchada** (`tests/test_umbral_alineado.py`): ya no escanea 4 archivos;
hace **barrido total de `superset/semantic/**` y `superset/dashboards/**`** y falle
ante cualquier 0.6/0.60 asociado a riesgo salvo contexto de ancla. Se añadió además
un barrido de subheaders sobre todos los tableros (soporta `charts` y `tabs`).
Tests de contrato `test_semantic_db03_db04.py` / `test_semantic_db06_db09.py` y el
test del mock ALTA pasan de ratificar 0.6 a ratificar **0.5 (DEC-019)**.

- **Tests executed (2.ª ronda):** suite completa → **899 passed**, 21 fallos
  pre-existentes idénticos (validaciones great-expectations, docker superset,
  agente/rbac/oauth por deps ausentes), 4 skipped, 13 errores de colección
  pre-existentes, **0 introducidos**. `ruff check` limpio. `vault_lint` → 3
  bloqueantes conocidos (untracked de raíz, nunca se commitean).
- **Next recommended action:** `repo-security-audit` + commit "Sweep de umbrales
  residuales (PR #275)" + push a `dev/manuel-serrania` (el PR #275 recoge el
  segundo commit) + avisar al PM para merge inmediato.
