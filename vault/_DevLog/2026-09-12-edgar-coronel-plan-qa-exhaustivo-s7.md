---
project: "FARO"
date: "2026-09-12"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "Levantado el ambiente local completo (docker compose: db, mlflow, api), suite de
  pytest de ML y las 9 rutas del frontend recorridas con navegador real."
touches: ["US-621", "REQ-004", "REQ-005", "RISK-011", "DEC-027"]
tags: [devlog, qa, e2e, regresion, s7]
---

# DevLog — 2026-09-12 — Plan de QA exhaustivo y primera corrida de regresión completa (S7)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/QA_team_documentation/Plan_QA_Exhaustivo_S7|Plan_QA_Exhaustivo_S7]]

## Qué se hizo

1. Se identificó que ni el PR de Edward Ruiz ni ningún otro documento del vault contemplan pruebas
   automatizadas de regresión del frontend completo (navegación, botones, respuestas, ausencia de
   error). `frontend/package.json` no declara ningún test runner; `Test_Strategy.md` sigue con
   `<Playwright/Cypress>` como placeholder desde el inicio del proyecto.
2. Se escribió [[vault/06_Quality_Testing/QA_team_documentation/Plan_QA_Exhaustivo_S7]]: inventario
   verificado de las 9 rutas reales de `frontend/src/main.jsx`, checklist transversal por pantalla,
   pasos de verificación local de ML, y reparto de apoyo por frente para el fin de semana.
3. Se levantó el ambiente local (`docker compose up -d db mlflow api`, `frontend: npm run dev`) y se
   ejecutó una corrida real de regresión:
   - `pytest` de ML (`test_entrenar_ml03.py`, `test_ejecutar_cierre_ml03.py`, `test_publicar_gold.py`,
     `test_preflight_ml03.py`): **66/66 verdes**. Suite completa: **1241 passed, 4 skipped**.
   - Navegador real (Chromium vía herramienta de Claude Code) por las 9 rutas y las 5 pestañas del
     expediente de escuela: **cero excepciones de JavaScript no controladas**.
   - `http://localhost:5001` (MLflow) responde, pero el backend está **vacío** (solo el experimento
     `Default`, sin runs) — confirma desde un segundo entorno lo que ya documentó Deni Garrido sobre
     `DEC-027`: el `run_id` histórico no es recuperable con un levantamiento estándar.
   - `gold.recomendaciones` en el Postgres local del PO no tiene `shap_d1..shap_d6`, que
     `src/modelos/publicar_gold.py` sí declara — produce `503` en `/api/v1/predicciones/{cct}`.
     **Documentado como condición del entorno local, no registrado como `BUG` todavía**: falta
     confirmar si el ambiente compartido/producción tiene el mismo desfase antes de escalarlo.

## Qué NO se hizo

No se corrigió el desfase de esquema local ni se registró como bug — se reporta como hallazgo
abierto para que alguien lo confirme contra un ambiente que no sea el del PO antes de decidir si es
un defecto real o solo staleness de un volumen de Docker individual. No se tocó ningún archivo de
código; esta sesión es puramente de verificación y documentación.
