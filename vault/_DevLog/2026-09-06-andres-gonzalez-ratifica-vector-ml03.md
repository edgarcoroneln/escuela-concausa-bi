---
project: "FARO"
date: "2026-09-06"
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "GitHub Copilot"
session_duration: "1 sesión — ratificación técnica del vector operativo de ML-03"
touches: ["US-321", "US-322", "US-325", "REQ-003", "ML-03"]
tags: [devlog, celula-3, ml-03, clustering, cobertura-parcial]
---

# DevLog — 2026-09-06 — Ratificación técnica del vector operativo de ML-03

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/15_ML_Models/ML03_Entrenamiento_US321]]

## Qué se hizo

- Se ratificó para C3 el vector operativo de ML-03: D1-D4 + `indice_completitud_drivers`.
- D5 (`d5_agua`) y D6 (`d6_aire`) se conservan como evidencia de cobertura parcial, pero quedan fuera del vector de KMeans.
- La política sigue siendo `casos_completos` sobre el vector operativo: D1-D4 o completitud ausentes excluyen la fila; D5/D6 ausentes no excluyen ni se imputan.
- Se actualizó `src/modelos/entrenar_ml03.py` para exponer `DRIVERS_OPERATIVOS_ML03` y usarlo en `FEATURES_ML03`, perfiles y registro MLflow.
- Se actualizaron pruebas de `tests/test_entrenar_ml03.py` para cubrir que D5/D6 no bloquean el vector operativo y que los drivers operativos sí mantienen la regla de no imputación.
- Se documentó la decisión en `vault/15_ML_Models/ML03_Entrenamiento_US321.md`.

## 🤖 Sesión de IA

- **Agente / modelo:** GitHub Copilot.
- **Archivos creados/modificados:**
  - `src/modelos/entrenar_ml03.py`
  - `tests/test_entrenar_ml03.py`
  - `vault/15_ML_Models/ML03_Entrenamiento_US321.md`
  - `vault/_DevLog/2026-09-06-andres-gonzalez-ratifica-vector-ml03.md`
  - `vault/_DevLog/_index.md`
- **Decisiones autónomas del agente:** avanzar sólo la parte de C3 que destraba a Estefany: política/vector. No se tocaron `dbt/**`, `src/api/**`, matriz ni `Execution_Status`.
- **Correcciones manuales:** pendientes de revisión humana.
- **Prompt inicial:** petición de Andrés para avanzar lo que le toca tras los PRs recientes del equipo.

## Seguridad / calidad

- [x] Sin secretos hardcodeados.
- [x] No se suben dumps ni datos reales pesados.
- [x] No se ejecutan operaciones destructivas sobre datos.
- [x] Tests enfocados actualizados para el vector operativo.
- [x] `tests/test_entrenar_ml03.py::test_d5_d6_no_bloquean_el_vector_operativo -vv`: 1 passed.
- [ ] Suite completa ML-03 pendiente de salida estable en esta terminal; la sesión de PowerShell alternó entre ejecución correcta y error de parser con `&`.

## Bloqueantes

- US-321 no cierra con esta ratificación: falta que Estefany ejecute la corrida temporal real, seleccione `k`, reporte Silhouette y registre MLflow con `run_id` real.
- Persistir `gold.ml03_asignaciones` requiere C1/Edgar por cambio de esquema; exponerlo en API requiere C4.

## Próximos pasos

- Estefany puede reintentar ML-03 con D1-D4 + completitud.
- Si la corrida produce asignaciones válidas, registrar MLflow y pedir a C1/C4 sus PRs separados de esquema/API.
