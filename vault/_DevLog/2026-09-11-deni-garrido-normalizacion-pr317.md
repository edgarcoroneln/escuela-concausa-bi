---
id: DEVLOG-20260911-DENI-NORMALIZACION-PR317
title: "Normalización de evidencia candidata ML-03 en PR #317"
owner: "Deni Garrido Fragoso"
status: in_review
date: "2026-09-11"
author_human: "Deni Garrido Fragoso"
agent: "Codex"
touches: ["US-631", "REQ-003", "RISK-011"]
traces_up: ["vault/15_ML_Models/ML03_RISK011_Gate", "vault/15_ML_Models/ML03_Comparacion_RISK011_20260910"]
tags: [devlog, ml03, risk-011, mlflow, pr-317]
---

# DevLog — normalización de evidencia candidata en PR #317

## Objetivo

Sincronizar `dev/deni-garrido` con `origin/main` mediante merge y eliminar afirmaciones que
presentaban la variante D1-D4 como canónica, aprobada o registrada en MLflow sin recuperación
independiente.

## Hallazgos verificados

- El PR #317 estaba detrás de `main`; la rama se sincronizó con merge, sin rebase.
- El servicio MLflow no era recuperable en este entorno: Docker no está disponible y
  `localhost:5001` rechazó conexión. Por la compuerta, el `mlflow_run_id` queda `null` y el
  registro se declara pendiente.
- La evidencia histórica del 8-sep se conserva. La candidata D1-D4 no reemplaza ni convierte en
  canónico ese corte antes de revisión técnica y decisión del PO.
- ARI entre semillas se describe exclusivamente como estabilidad de inicialización.

## Cambios

- Se normalizan la model card, explicación, propuesta, comparación JSON e índice ML para separar
  evidencia histórica, candidata, MLflow e integración productiva.
- Se documenta que el reporte de QA de fixtures requiere revisión por su dueño y no valida la
  lógica candidata ni cierra RISK-011.
- No se tocó Gold, dbt, API, Panel ni el código ejecutable de ML-03.

## Pendientes

- Ejecutar/revisar CI en el nuevo SHA sincronizado.
- Revisión técnica de Estefany y revisión QA de `Evaluacion_Modelos.md`.
- Recuperación independiente de MLflow, decisión explícita de Edgar sobre RISK-011 y, después del
  gate, Gold → API → Panel → QA E2E en PRs de sus respectivos dueños.

## Validación prevista

- `pytest tests/test_entrenar_ml03.py tests/test_ejecutar_cierre_ml03.py -q`
- `vault/_Meta/scripts/vault_lint.py .`
- Revisión de JSON y diff sin cambios Gold/dbt/API/Panel.
