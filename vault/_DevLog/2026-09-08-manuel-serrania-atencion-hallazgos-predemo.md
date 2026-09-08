---
project: "FARO"
date: "2026-09-08"
author_human: "Manuel Alejandro Serranía Reinada"
agent: "OpenCode"
model: "big-pickle"
session_duration: "1 sesión — atender los hallazgos de la QA pre-demo que tocan a C2: formalizar dueño/reviewer de BUG-064/066, registrar las deudas BUG-070/071, preparar el código inerte del formato `porcentaje_3` (0.015% visible) y dar acuse de recibo de US-305; sincronización de la rama con `main` al arrancar"
touches: ["US-203", "US-204", "US-212", "US-213", "US-207", "US-526", "US-006", "US-305", "REQ-002", "BUG-064", "BUG-066", "BUG-070", "BUG-071"]
tags: [devlog, celula-2, bugs, qa, superset, semantic, demo, agente]
---

# DevLog — 2026-09-08 — Atención a los hallazgos de la pre-demo que tocan a C2

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|Bug Register]] · [[vault/06_Quality_Testing/QA_Logs/2026-09-07-oscar-quiroz-qa-pre-demo|QA Óscar (BUG-064/066)]] · [[vault/06_Quality_Testing/QA_Logs/_index|QA Logs (Diana: BUG-070/071)]]

## Estado de entrada

- Rama `dev/manuel-serrania` sincronizada con `origin/main` (`7e514b8`, incluye el merge del QA de Óscar, PR #285). Solo quedan los untracked raíz conocidos (`PLAN_US206_EMBEBIDO.md`, `avisosequipo.md`, `plan7diasporpersona.md`, `gx/`).
- Ventana `DEC-020` vigente: **no correr `superset/sync_semantic_layer.py` ni tocar `src/frontend/**` antes del 9-sep** (riesgo de regresar el embebido, BUG-061, y de borrar el parche de 20 charts de Luis, PR #275).

## Formalización de BUG-064 y BUG-066 (dueño/reviewer)

Ambas filas decían "Sin dueño asignado todavía". Se formalizó en el registro (decisión 2026-09-08, criterio BUG-037):

- **BUG-064** (DB-01: leyenda paginada/truncada, eje X del driver dominante sin etiquetas): dueño C2, código compartido `db01_ejecutivo.yaml` + `sync_semantic_layer.py`, reviewer Manuel Serranía.
- **BUG-066** (DB-04/05: eje Y sin decimales 0-1, eje X sin nombres; mismo `_params_chart()`): dueño C2 (código compartido de Célula 2), reviewer Manuel Serranía.

Ambos con **fix post-9**: dentro de la ventana está prohibido sincronizar, y el fix es de la herramienta de sync (no verificable contra producción hasta el re-sync).

## BUG-070 (nueva deuda 🟢) — "% escuelas en riesgo" marca "0.0%"

Hallazgo de Diana: DB-04 muestra "0.0%" cuando la medición real es **0.0155%** (7 de 45 276). Causa: `pct_escuelas_en_riesgo` usa `formato: porcentaje_1` = d3 `",.1%"`; un solo decimal no puede representar valores bajo 0.1%.

**Arreglo identificado y preparado (código inerte en la rama, aplica solo con el re-sync):**

- `FORMATO_D3` (`superset/sync_semantic_layer.py`) += `"porcentaje_3": ",.3%"`.
- `formato: porcentaje_3` en los 4 `pct_escuelas_en_riesgo`: `metrics_db01_db02.yaml` (×2), `metrics_db03_db04.yaml`, `metrics_db06_db09.yaml`.

Resultado esperado: "0.015%" visible. Cubre DB-02 y DB-09 (misma métrica compartida). Cumple la guarda `tests/test_sync_formato_d3_cobertura.py` (todo `formato:` debe existir en `FORMATO_D3`).

## BUG-071 (nueva deuda 🟢) — Panel ML: CCTs de ejemplo ajenos al par de la demo

Diana: `src/frontend/pages/2_Panel_ML.py` muestra `15DJN0049A`/`09DSN0042A` en `EJEMPLOS` (:59) y `placeholder` (:268); el par oficial de `US-006` es `15DPR0920D`/`15DPR2254O`. Solo se registró — **no se toca `src/frontend/**` dentro de la ventana**; fix de 2 líneas para el siguiente deploy (post-demo).

## Acuse de recibo de US-305 (contrato de `contexto_conversacional`)

Imanol/C4 mergeó el PR #283 (contrato del contexto conversacional, retrocompatible). Acuse a pegar en el canal por Manuel: CCT en MAYÚSCULAS `^[0-9A-Z]{10}$` (minúsculas → 422), resumen en una sola línea de máx 300 caracteres (el cliente normalizará saltos), máx 200 CCTs y 10 filtros; retrocompatible confirmado (el frontend actual no rompe). El cliente C2 se conectará **cuando Edgar autorice** la entrada a la demo; de lo contrario queda listo para post-demo.

## Qué NO se tocó a propósito

- Texto Panel ML (BUG-071), ejes de DB-01/04/05 (BUG-064/066): post-9.
- BUG-065 (filtro duplicado DB-03): fuera de tanda, lo decide el PO.
- Rol `ciudadano` de Diana en el Panel ML (requiere `ANALISTA_EMAILS`): C4.

## Pruebas ejecutadas

- `tests/test_sync_formato_d3_cobertura.py` (verde) — la guarda que exige el mapeo completo.
- Batería semántica de `tests/test_semantic_*.py` (sin cambios de contrato).
- `ruff check` y `vault_lint` limpios dentro del diff.
- Auditoría de seguridad pre-commit aplicada.