---
id: DOC-BLOCKERREG
title: "Blocker Register — FARO"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
source_of_truth: true
traces_up: ["12_Roadmap_Sprints/Execution_Status"]
traces_down: ["13_Reports/PM_Dashboard_Spec"]
last_reviewed: "2026-08-05"
tags: [blockers, dependencies, governance, dashboard]
---

# Blocker Register — FARO

> Registro único de impedimentos actuales. Un riesgo es algo que podría ocurrir; un bloqueo ya está
> impidiendo avanzar. → [[10_Risk_Governance/_index]]

| BLOCK | US | Proveedor | Consumidor | Descripción | Desde | Alternativa | Dueño | Estado |
|---|---|---|---|---|---|---|---|---|
| BLOCK-001 | US-311 | Célula 5 (infra MLflow) | Célula 3 (Héctor, Andrés, Estefany) | `docker/mlflow.Dockerfile` corre `mlflow==2.8.0` contra el cliente `3.15.1`: las corridas se ven en la UI pero el modelo **nunca llega al registry** → **AC-003.4 no cumplido**. Frena US-302/303 (Andrés), US-321 (Estefany) y US-313. **Fix mergeado (PR #45, MLflow→3.15.1); falta que C3 re-corra y confirme el registry end-to-end.** | 2026-08-18 | Entrenar y ver métricas en la UI sin registrar en el registry (no cierra AC-003.4) | Luis Téllez Domínguez | mitigating |
| BLOCK-002 | US-313, US-412, US-311 | Célula 1 (`gold.features_escuela`) | Célula 3 (ML-01, publicación) y Célula 4 (`/predicciones`) | **Paso 1 de ADR-007: normalizar `target_variacion_matricula` a fracción y reprocesar Gold.** ADR-007 quedó `accepted` el 29-ago (PR #147), pero **ratificar no cambia el dato**: [`features_escuela.sql:71`](dbt/models/gold/features_escuela.sql) sigue calculando `matricula_total - matricula_ciclo_anterior`, alumnos absolutos. Mientras siga así, `verificar_escala_variacion()` detiene la publicación —correctamente—, `gold.predicciones` queda vacío en producción, `/api/v1/predicciones/{cct}` responde 404 para toda CCT y **la demo de ML no tiene qué mostrar**. Bloquea además los pasos 2, 3 y 4 del propio ADR y mantiene **BUG-019** abierto | 2026-08-29 | Ninguna que preserve el contrato: normalizar al leer en C3 fue evaluada y rechazada en el ADR (opción C) porque dejaría Gold declarando una unidad y sirviendo otra | **SIN ASIGNAR — decisión del PM** | open |

## Convención

- Estado: `open` → `mitigating` → `resolved`.
- Todo bloqueo abierto debe apuntar a una `US-###` y tener dueño.
- A las 24 horas se escala al Tech Lead; a las 48 horas, al PO.
- Al resolverse se conserva la fila como historial y se enlaza la evidencia.
