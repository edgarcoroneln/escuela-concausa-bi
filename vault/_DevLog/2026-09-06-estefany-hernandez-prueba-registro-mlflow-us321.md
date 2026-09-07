---
id: DEVLOG-20260906-ESTEFANY-PRUEBA-MLFLOW-US321
title: "US-321 — prueba segura de registro MLflow"
owner: "Estefany Lucero Hernández Loredo"
status: draft
date: "2026-09-06"
author_human: "Estefany Lucero Hernández Loredo"
agent: "Codex"
touches: ["US-321", "REQ-003", "ML-03"]
traces_up: ["vault/15_ML_Models/ML03_Entrenamiento_US321"]
tags: [devlog, ml-03, mlflow, prueba, coordinacion]
---

# DevLog — 2026-09-06 — Prueba segura de registro MLflow para US-321

## Qué se hizo

- Se verificó el dump local canónico `gold_bug048_final1_2026-09-05 1.sql`: SHA-256
  `07ECF29DEEE250732C38B252CA48794CCE413B5F295197E68804C337AC89D0BE`.
- Se añadió una compuerta explícita al ejecutor C3: `--tracking-uri` requiere
  `--confirmar-registro`. La corrida de evidencia ya no puede registrar MLflow por accidente antes
  de revisar `k`, Silhouette y perfiles agregados.
- Se añadieron pruebas del contrato de confirmación y se documentó el protocolo conjunto C3/C5:
  evidencia agregada primero, revisión de Andrés, registro único con `run_id` y decisión final de
  Edgar.
- No se restauró ni modificó ninguna base: esta estación no tiene Docker CLI ni `psql` disponibles.
  No se intentó instalar herramientas, copiar secretos ni simular un `run_id`.

## Alcance y coordinación

- Estefany conserva `src/modelos/**` y documentación ML; el cambio de pruebas es amarillo C3.
- C5 sólo confirma una ventana/URI de MLflow y su salud. C1 y C4 recibirán un contrato posterior en
  PRs separados; no se toca Gold, `dbt/**` ni `src/api/**` en esta prueba.
- La historia permanece `in_review`: faltan corrida temporal real, `k`, Silhouette, perfiles y
  `run_id` recuperable.

## Validaciones ejecutadas antes del push

- `python -m src.modelos.ejecutar_cierre_ml03 --help`: expone `--tracking-uri` y
  `--confirmar-registro`.
- `ruff check src/modelos/ejecutar_cierre_ml03.py tests/test_ejecutar_cierre_ml03.py`: PASS.
- `pytest tests/test_ejecutar_cierre_ml03.py tests/test_entrenar_ml03.py -q`: 14 passed; 2 warnings
  conocidas de NumPy en el fixture de correlación.
- `python vault/_Meta/scripts/vault_lint.py .`: Vault limpio; 7 avisos de posibles huérfanos
  preexistentes.
- `check_ownership.py --autor stephi-coder --rama dev/estefany-hernandez`: alcance correcto; la
  matriz requiere revisión explícita de Edgar por ser ruta crítica.

## Próximo paso recomendado

Solicitar a Luis Téllez una ventana de MLflow y ejecutar la fase T0 contra la base aislada; enviar a
Andrés únicamente la evidencia agregada para revisión antes de usar `--confirmar-registro`.

→ [[vault/_DevLog/_index|Volver al índice]]
