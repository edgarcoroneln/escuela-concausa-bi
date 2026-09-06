---
project: "FARO"
date: "2026-09-06"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — 2º hueco del embebido: los charts *timeseries* del shell salían en blanco para el usuario logueado (guardia anti-manipulación de guest de Superset 6.1.0); fix de metadata en 20 charts, sin código ni redeploy"
touches: ["US-526", "REQ-002", "AC-002.1"]
tags: [devlog, celula-5, superset, cloud-run, dashboards, bi, fase-2, despliegue, guest-token]
---

# DevLog — 2026-09-06 — Charts *timeseries* del shell: 403 de guest corregido (dashboards embebidos)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/_DevLog/2026-09-05-luis-tellez-superset-carga-tableros-prod|Carga de tableros]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy a Cloud Run]]

## Contexto

En US-526 (FARO Web embebido) los tableros de Superset se muestran en el shell mediante **guest token**.
Superset corre en prod una guardia anti-manipulación (`query_context_modified`, `superset/security/manager.py`)
que **solo se dispara para invitados**: exige que lo que pide el `buildQuery` del front (metrics/columns/
orderby) sea **subconjunto** de lo que el chart tiene guardado en `params ∪ query_context`. El fix del
**2026-09-05** materializó un `query_context` superconjunto en 106 charts y cerró el bloqueo para la mayoría
de tipos de visualización (big_number, table, pie, pivot, deck…).

**Reporte de Luis (2026-09-06):** seguían **sin verse** varios tableros concretos — "Matrícula observada por
ciclo", "Variación proyectada (ML-01) por ciclo" y "Escuelas por driver dominante (KPI-07)". Todos son de la
familia **`echarts_timeseries_*`** (barra/línea con eje X).

## Causa raíz (confirmada por fuente + prueba de guest)

Prod corre **Superset 6.1.0** (`/static/version_info.json`). Su front, en `normalizeTimeColumn.ts`, cuando el
chart define un `x_axis`, **envuelve la columna del eje X en un objeto adhoc `BASE_AXIS`** — **incluso sin
*time grain*** (rama "no adhoc", `timeGrain = extras?.time_grain_sqla` queda `undefined` y se omite):

```json
{"columnType":"BASE_AXIS","expressionType":"SQL","isColumnReference":true,"label":"ciclo","sqlExpression":"ciclo"}
```

Ese **dict** es lo que el iframe manda en `query_context.queries[0].columns`. Pero el `query_context` que dejó
el fix anterior guardaba el eje X **solo como string** (`"ciclo"`, `"nombre_driver"`). La guardia congela cada
valor con `json.dumps(sort_keys=True)` y compara conjuntos ⇒ `dict ⊄ {string}` ⇒ **Check B falla** ⇒
**403 "Guest user cannot modify chart payload"** ⇒ el chart aparece vacío. Es exactamente el hueco que dejó el
fix anterior: cubrió la forma **string** del eje X, no la forma **dict** que genera `normalizeTimeColumn`.

**Comprobado como guest real** (X-GuestToken, único camino donde corre la guardia): enviar el dict **exacto** de
6.1.0 → **403 hoy**; enviar el string → pasa. Afecta a **20 charts** con `x_axis` string (los 3 reportados +
17 iguales: D1–D6 "% escuelas por driver por ciclo", "por municipio", "Matrícula por ciclo", "Driver dominante",
"% SIN_DATO por driver"…).

## Qué se hizo (operación de despliegue — sin código)

1. **Respaldo de Cloud SQL** (red de seguridad, no destructivo): `gcloud sql backups create --instance=faro-postgres`
   → backup **`1788676050737`**. Snapshot app-level del `query_context` previo de los 20 charts →
   `/tmp/faro_qc_restore_ts.json` (reversible a mano).
2. **Aumento del `query_context` guardado** de los 20 charts *timeseries*: se agregó el **dict `BASE_AXIS`
   exacto de 6.1.0** (además del string, que se conserva) a `columns`, `groupby` y ambas direcciones en
   `orderby`. Aplicado por **REST `PUT /api/v1/chart/{id}` `{query_context, query_context_generation:true}`**
   (login admin de servicio por `POST /api/v1/security/login` `provider:"db"`; secreto `superset-admin-password`).
   - **Monótono-seguro:** la guardia **nunca ejecuta** ese `query_context` — solo lo usa para comparar
     subconjuntos de strings congelados. Agregar entradas al conjunto guardado **solo puede convertir 403→200**,
     nunca romper un chart que ya pasaba, y **no cambia el render** (la consulta real la arma el front).
   - **Metadata-only:** no toca datos del `gold`, no redeploy, imagen intacta (`faro-superset:00d3c14`).

## Cómo se probó

- **Guest real (dict exacto de 6.1.0), 20/20:** todos pasan de 403 a **200 con datos** (rowcount 3/6/7/100),
  0 bloqueados. Antes del fix, el mismo dict daba 403 en los 20.
- **En vivo, por Luis (logueado, hard-refresh):** confirma que **ya se ven** los tableros reportados —
  "Matrícula observada por ciclo", "Variación proyectada (ML-01) por ciclo", "Escuelas por driver dominante
  (KPI-07)" — y los D1–D6 por ciclo/municipio. **AC-002.1** (10 tableros embebidos pintando) queda cumplida
  end-to-end para la familia *timeseries*.

## Diagnósticos / aprendizajes (para C2 y para el runbook)

- **El eje X de un `echarts_timeseries_*` viaja como adhoc `BASE_AXIS`, no como string** — aunque el `x_axis`
  del YAML sea una columna física y no haya *time grain*. Cualquier fix del `query_context` para guests debe
  incluir **esa forma dict** (con `isColumnReference:true`), no solo el nombre de la columna.
- La guardia es **específica de invitados**: como admin nunca se ve el 403, por eso el defecto solo aparece en
  el embebido del shell y no al abrir el chart en la UI de Superset.
- La serialización debe ser **byte-idéntica** tras `sort_keys`: `timeGrain` es `undefined` en el front y **se
  omite** del JSON, así que el dict guardado tampoco debe llevar esa clave.

## Seguridad / calidad

- [x] **No se tocó código de C2** (`src/frontend/**`, `superset/**`): es un ajuste de **metadata** en la
  Superset de prod, dentro del alcance de operación de despliegue de C5 (US-526).
- [x] **No se tocaron env-vars de seguridad** (SSO, whitelist, `AUTH_LECTURA_PUBLICA`, CORS): intactas. La
  lectura sigue tras **SSO obligatorio + lista blanca**.
- [x] **Cero secretos en repo/chat/DevLog:** el `superset-admin-password` se leyó de Secret Manager en la
  terminal y **nunca** se imprimió ni se escribió a archivo.
- [x] **Reversible:** backup Cloud SQL `1788676050737` + snapshot `/tmp/faro_qc_restore_ts.json` (re-PUT del
  `query_context` previo por id).
- [x] **Sin redeploy:** imagen `faro-superset:00d3c14` intacta; es metadata en Cloud SQL, persiste a través de
  reinicios (`superset-init.sh` no re-sincroniza charts en cold-start).

## Avisos a otros owners

- **C2 (Manuel / Marina):** el arreglo definitivo vive en la **configuración del chart** — que el
  `sync_semantic_layer.py` **persista un `query_context`** por chart (incluyendo el eje X como adhoc `BASE_AXIS`)
  para que los guests no dependan de este parche de metadata. **Riesgo residual:** un **re-`sync` manual de los
  YAML** sobrescribe el `query_context` y **reintroduce el 403** en los *timeseries*; si eso pasa, re-aplicar con
  `/tmp/faro_fix_timeseries.py` (o incorporar la forma dict al `sync`). Forma exacta a persistir para 6.1.0:
  `{"columnType":"BASE_AXIS","expressionType":"SQL","isColumnReference":true,"label":<x_axis>,"sqlExpression":<x_axis>}`.
- **PO (Edgar):** cierre de operación de US-526 (embebido) para la familia *timeseries*; sin cambios de código,
  merge de este DevLog.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados:** `vault/_DevLog/_index.md` (fila de este DevLog).
- **Infra GCP (sin código):** backup de Cloud SQL `1788676050737`; `PUT query_context` en 20 charts *timeseries*
  de la metadata de `faro-superset` (vía REST admin).
- **Sin cambios de código** de aplicación (`src/`), de `docker/**` (C5) ni de `superset/**` (C2).
