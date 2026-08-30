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
| BLOCK-002 | US-113 / REQ-001 | Célula 1 (DS-07, CONEVAL) | Célula 1 (Diana) · Célula 3 (driver dominante) · Célula 2 (DB-04) | **DS-07 lleva cinco semanas en `draft` porque nunca se convirtió en tarea con fecha.** El sprint de Deni tiene US-111 a US-114 y **ningún `US-1XXa` para DS-07**, a diferencia de DS-06 que sí tuvo US-121a–124a asignadas a Emilio. La checklist §9 de la ficha sigue con las cinco casillas vacías y la URL en `PENDIENTE-CONFIRMAR`. Consecuencia: `bronze.coneval` sigue con la muestra de prueba, `gold.dim_municipio` cubre **10 municipios**, y varios tests de `relationships` pasan en verde contra un universo diminuto — el modo de falla de BUG-012 y BUG-026. **D1 es el driver de mayor peso en el target**, así que el driver dominante se calcula sobre cinco de seis | 2026-08-30 | **Tres vías en paralelo (DEC-014):** (1) Deni intenta la descarga con fecha compromiso antes del freeze; (2) C1 implementa en paralelo la cobertura parcial explícita de D1 con `SIN_DATO`, mismo patrón de BUG-009/BUG-030 con D5; (3) este registro. La demo no depende de que una sola persona entregue a tiempo | Deni Garrido Fragoso · red de seguridad: Diana Alvarez | mitigating |

## Convención

- Estado: `open` → `mitigating` → `resolved`.
- Todo bloqueo abierto debe apuntar a una `US-###` y tener dueño.
- A las 24 horas se escala al Tech Lead; a las 48 horas, al PO.
- Al resolverse se conserva la fila como historial y se enlaza la evidencia.
