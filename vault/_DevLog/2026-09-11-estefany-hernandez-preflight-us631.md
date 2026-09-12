---
id: DEVLOG-20260911-ESTEFANY-PREFLIGHT-US631
title: "Preflight de cierre seguro para ML-03"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
date: "2026-09-11"
author_human: "Estefany Lucero Hernández Loredo"
agent: "Codex"
touches: ["US-631", "REQ-003", "RISK-011", "BUG-030"]
traces_up: ["vault/15_ML_Models/ML03_RISK011_Gate", "vault/15_ML_Models/ML03_Preflight_US631"]
tags: [devlog, ml03, preflight, coverage, risk-011]
---

# DevLog — preflight de cierre seguro para ML-03

## Objetivo

Consolidar dependencias reales de datos e integración de US-631 y añadir un preflight que impida
usar D5/D6 o completitud como relleno, señal de cluster o afirmación prematura de cierre.

## Cambios

- Se agrega `src/modelos/preflight_ml03.py`: evidencia agregada por ciclo y entidad para el vector
  candidato D1--D4, sus exclusiones y la cobertura de D5/D6, sin exponer CCT.
- Se agregan dos pruebas de regresión: D5/D6 ausentes no alteran elegibilidad y D1--D4 incompleto
  sí queda medido como exclusión.
- Se documenta el plan y las exclusiones operativas de US-631 en
  [[vault/15_ML_Models/ML03_Preflight_US631]].

## Hallazgos

- `BUG-030` sigue abierto: la capacidad de presas de D5 no es una serie vigente de estrés hídrico;
  no se puede imputar ni usar para completar el vector.
- D6 conserva cobertura parcial por el radio fijo de 15 km de `ADR-006`; ampliar el radio sólo para
  elevar cobertura invalidaría el contrato.
- `RISK-011` queda abierto hasta que la evidencia canónica, MLflow, el diff de Gold/API y la
  decisión de Edgar satisfagan [[vault/15_ML_Models/ML03_RISK011_Gate]].

## Validación

- `python -m ruff check src/modelos/preflight_ml03.py tests/test_preflight_ml03.py`
- `python -m pytest tests/test_preflight_ml03.py tests/test_entrenar_ml03.py tests/test_ejecutar_cierre_ml03.py -q --disable-warnings`

## Siguiente acción recomendada

Ejecutar el preflight sobre el dump canónico, adjuntar su salida agregada a la evidencia de la
candidata y completar la compuerta de MLflow antes de cualquier promoción a Gold/API/Panel.
