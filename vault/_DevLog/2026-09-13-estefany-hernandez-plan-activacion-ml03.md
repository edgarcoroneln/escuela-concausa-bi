---
id: DEVLOG-20260913-ESTEFANY-PLAN-ACTIVACION-ML03
title: "Plan de activación diferida de ML-03 tras DEC-027"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
date: "2026-09-13"
author_human: "Estefany Lucero Hernández Loredo"
agent: "Codex"
touches: ["US-321", "US-631", "REQ-003", "RISK-011", "DEC-027"]
traces_up: ["vault/10_Risk_Governance/Decision_Log", "vault/15_ML_Models/ML03_RISK011_Gate"]
traces_down: ["vault/15_ML_Models/ML03_Preflight_US631", "vault/15_ML_Models/Propuesta_Cierre_ML03_D1_D4"]
tags: [devlog, ml03, activation-plan, risk-011]
---

# DevLog — plan de activación diferida de ML-03

## Objetivo

Mantener una sola ruta operativa de ML-03 después de que DEC-027 aceptó la mitigación metodológica
de RISK-011 y declaró el modelo como deuda no operativa de esta entrega.

## Cambios

- Se actualiza la compuerta canónica: #317, la revisión técnica y DEC-027 quedan como pasos
  completados; Gold, productor batch, API y E2E quedan diferidos.
- Se actualiza el preflight con el orden de reactivación: MLflow verificable, autorización nueva del
  PO, contrato Gold, productor C3, lectura C4 y E2E C2/QA.
- Se alinean la propuesta D1-D4, el índice ML y la matriz de trazabilidad con el estado
  `mitigando`, sin afirmar operación ni un `run_id` recuperable.

## Decisiones y límites

- D1-D4, `k=2` y Silhouette `0.4620526551` son evidencia metodológica aceptada; D5, D6 y
  completitud permanecen fuera del estimador.
- La recuperación de MLflow no se infiere de un servicio disponible: requiere experimento,
  parámetros, métrica, artefacto descargable y carga exitosa de una corrida real.
- No se modifican Gold, API, Panel, esquema ni CI en este PR.

## Validación

- `python -m pytest tests/test_preflight_ml03.py tests/test_entrenar_ml03.py tests/test_ejecutar_cierre_ml03.py -q --disable-warnings`
- `python vault/_Meta/scripts/vault_lint.py .`
- `git diff --check`

## Siguiente acción recomendada

Mantener ML-03 como deuda explícita hasta que el PO autorice la reactivación. Entonces ejecutar la
secuencia del preflight sobre una base canónica aislada y abrir PRs separados por C1, C3, C4 y C2/QA.
