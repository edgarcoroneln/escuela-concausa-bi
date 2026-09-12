---
id: DEVLOG-20260911-ESTEFANY-GATE-RISK011
title: "Compuerta de revisión ML-03 y RISK-011"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
date: "2026-09-11"
author_human: "Estefany Lucero Hernández Loredo"
agent: "Codex"
touches: ["US-321", "US-631", "REQ-003", "RISK-011"]
traces_up: ["vault/15_ML_Models/ML03_RISK011_Gate", "vault/15_ML_Models/ML03_Explicacion_US631"]
tags: [devlog, ml03, risk-011, governance, mlflow]
---

# DevLog — 2026-09-11 — compuerta ML-03 / RISK-011

## Objetivo

Evitar que la variante D1-D4 propuesta en PR #317 se confunda con el corte canónico del 8-sep,
RISK-011 se cierre por narrativa o un `run_id` de MLflow no verificado se documente como hecho.

## Trabajo realizado

- Se sincronizó `dev/estefany-hernandez` con `origin/main` mediante merge/fast-forward; no hubo
  push y se preservó la auditoría local preexistente fuera de este trabajo.
- Se revisó la Regla 7 y `ownership.yml`: las rutas `src/modelos/**` y
  `vault/15_ML_Models/**` requieren revisión explícita de Estefany cuando otro integrante las
  modifica.
- Se verificó que RISK-011 en `main` sigue abierto y enlaza evidencia existente. PR #317 está
  abierto, `DIRTY` y sin CI sobre su commit final; por ello su variante D1-D4 no es canónica.
- Se creó [[vault/15_ML_Models/ML03_RISK011_Gate]] con estrategia de modelado, límites del ARI,
  evidencia mínima, una sola redacción para MLflow y secuencia Gold → API → Panel posterior a la
  decisión del PM.
- Se actualizó [[vault/15_ML_Models/ML03_Explicacion_US631]] para impedir que una métrica,
  estabilidad de semillas o `run_id` candidato se presente como aprobación.

## Decisiones y límites

- El corte 8-sep D1-D4 + completitud (`k=3`, Silhouette 0.4644549058) permanece como evidencia
  histórica canónica hasta que la variante supere la compuerta.
- D1-D4 es una mitigación candidata: completitud se audita, pero no debe entrar al estimador;
  D5/D6 nunca se imputan ni pasan a cero.
- ARI entre semillas mide estabilidad de inicialización, no validación temporal externa.
- No se tocaron Gold, dbt, API, Panel, MLflow, `Risk_Register.md` ni la matriz de trazabilidad.

## Validación pendiente antes de push

- `vault_lint.py`, `git diff --check` y las pruebas focalizadas de ML-03 sobre los archivos finales.
- Registrar esta entrada en el índice DevLog sin incorporar la auditoría local preexistente.
- Solicitar aprobación de Edgar una vez que el PR documental esté completo; no se solicitará el
  cierre de RISK-011 desde este cambio.

## Próximo paso recomendado

Completar los checks de documentación y abrir un PR documental separado. En paralelo, Deni debe
sincronizar PR #317 y aportar CI/evidencia final; sólo después procede la revisión técnica de la
variante y la decisión de Edgar.

→ [[vault/_DevLog/_index|Volver al índice]]
