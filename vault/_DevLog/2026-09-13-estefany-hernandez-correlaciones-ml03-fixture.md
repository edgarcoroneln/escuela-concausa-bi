---
id: DEVLOG-20260913-ESTEFANY-CORRELACIONES-ML03-FIXTURE
title: "Correlaciones seguras y preparación local de ML-03"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
date: "2026-09-13"
author_human: "Estefany Lucero Hernández Loredo"
agent: "Codex"
touches: ["US-321", "US-322", "US-631", "REQ-003", "RISK-011", "DEC-027"]
traces_up: ["vault/15_ML_Models/ML03_Preflight_US631", "vault/15_ML_Models/ML03_RISK011_Gate"]
traces_down: ["src/modelos/analizar_features.py", "tests/test_analizar_features.py"]
tags: [devlog, ml03, eda, correlations, fixture, risk-011]
---

# DevLog — correlaciones seguras y preparación local de ML-03

## Objetivo

Eliminar los avisos de correlación que impedían una corrida local limpia y dejar explícito qué
validaciones del fixture son útiles antes de una futura activación operativa de ML-03.

## Cambios

- `resumen_eda()` y `correlaciones_drivers()` ya verifican que cada par tenga al menos dos valores
  distintos después de retirar nulos. Cuando Pearson no está definido, el reporte agregado emite
  `null`; no inventa una correlación cero ni altera el vector D1-D4.
- Una prueba trata `RuntimeWarning` como error y verifica que una feature constante conserve la
  cobertura declarada y produzca correlaciones nulas sin ensuciar la ejecución.
- El preflight añade la preparación local del fixture: conservar la comparación `k=2..6`, revisar
  perfiles y parsimonia cuando el mejor Silhouette sea cercano a otro candidato, y no usar ARI como
  validación temporal.

## Evidencia local y límites

- La corrida local sobre `gold.features_escuela` restaurada desde el fixture sintético completó
  D1-D4 con `k=6`, Silhouette `0.3728730666` y ARI de inicialización mínimo/promedio `1.0`.
- Esa salida no contiene CCT individuales, no registró MLflow y no escribió Gold, API ni Panel.
- Es evidencia de ejecución reproducible del código, no la nueva evidencia canónica: el fixture es
  sintético, sólo tiene una ventana temporal y la diferencia con `k=3` debe evaluarse por
  interpretabilidad antes de una decisión futura.
- DEC-027 conserva RISK-011 como `mitigando`; esta sesión no autoriza operación ni cambia el vector
  canónico D1-D4, `k=2`, Silhouette `0.4620526551`.

## Validación

- `python -m pytest tests/test_analizar_features.py tests/test_preflight_ml03.py tests/test_entrenar_ml03.py tests/test_ejecutar_cierre_ml03.py -q -W error::RuntimeWarning` → 41 passed.
- `python vault/_Meta/scripts/vault_lint.py .` → limpio; 11 posibles huérfanos preexistentes.
- `git diff --check` → limpio.
- Ejecución local sin `--tracking-uri`, con `--estabilidad --semillas-estabilidad 7 21 42 84 2026` → sin warnings; evidencia agregada temporal fuera del repositorio.

## Siguiente acción recomendada

Esperar la decisión explícita del PO para la reactivación y, entonces, repetir el preflight sobre
la base canónica aislada, registrar una corrida nueva y verificable en MLflow y entregar por PRs
separados el contrato Gold, el productor, la lectura API y el E2E.

→ [[vault/_DevLog/_index|Volver al índice]]
