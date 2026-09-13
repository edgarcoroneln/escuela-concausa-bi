---
id: DEVLOG-20260910-DENI-ML03-D1-D4
title: "ML-03 con vector D1-D4 y evidencia explicable"
owner: "Deni Garrido Fragoso"
status: in_review
date: "2026-09-10"
author_human: "Deni Garrido Fragoso"
agent: "OpenCode / GPT-5.6 Sol"
touches: ["US-631", "US-321", "REQ-003", "RISK-011", "ML-03"]
traces_up: ["vault/15_ML_Models/Propuesta_Cierre_ML03_D1_D4", "vault/15_ML_Models/ML03_Comparacion_RISK011_20260910"]
tags: [devlog, ml03, clustering, risk-011, mlflow]
---

# ML-03 con vector D1-D4 y evidencia explicable

- **Objetivo:** entregar exclusivamente la variante correctiva de ML-03 con pobreza, inseguridad,
  infraestructura y conectividad; conservar completitud, D5 y D6 como auditoría fuera de KMeans.
- **Rama:** `dev/deni-garrido`. ML-03 se conserva en commits y documentos propios, separado de
  US-113 y sin modificar su implementación ni su evidencia.
- **Código:** `FEATURES_ML03` contiene exactamente D1-D4; los casos completos se ordenan por
  `id_ciclo, cct`; se generan perfiles y una salida descriptiva con pistas disponibles y pendientes.
- **Pruebas:** cubren exclusión de completitud/D5/D6/target, ausencia sin imputación, invariancia al
  orden de entrada, nombres de perfiles, evidencia insuficiente y metadatos MLflow.
- **Corrida canónica:** 136,046 filas totales, 114,200 elegibles, 21,846 excluidas, `k=2` y
  Silhouette temporal `0.46205265511063737`.
- **Estabilidad:** semillas 7, 21, 42, 84 y 2026; ARI mínimo y promedio `1.0`.
- **Perfiles:** presión por inseguridad (83,275 observaciones, 28,143 escuelas) y presión por
  conectividad e infraestructura (30,925 observaciones, 10,365 escuelas).
- **MLflow:** `ML03_ClusteringEscuelas` v1; corrida `d971ab7271df45629c9a50c27514890f`
  `FINISHED`; versión `READY`; artefacto descargado y cargado nuevamente con `mlflow.pyfunc`.
- **RISK-011:** mitigación técnica implementada al retirar completitud del vector y eliminar el grupo
  equivalente a disponibilidad de D6. El cierre formal sigue sujeto a decisión de Edgar.
- **Alcance excluido:** no se modificaron D5/D6, ingesta, dbt, Gold, API, frontend, despliegue ni E2E.
- **Validación:** 33 pruebas enfocadas en verde; dos warnings NumPy conocidos. El JSON de evidencia
  es válido y `git diff --check` no reporta errores.
- **Revisión humana:** se revisaron línea por línea los cambios generados. No se compartieron datos
  reales, credenciales ni archivos `.env`.

→ [[vault/_DevLog/_index|Volver al índice]]
