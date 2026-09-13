---
id: DOC-ML03-RISK011-GATE
title: "Compuerta de revisión RISK-011 para ML-03"
owner: "Estefany Lucero Hernández Loredo"
status: draft
source_of_truth: true
traces_up: ["US-321", "US-631", "REQ-003", "RISK-011"]
traces_down: ["vault/15_ML_Models/ML03_Entrenamiento_US321", "vault/15_ML_Models/ML03_Model_Card", "vault/10_Risk_Governance/Risk_Register"]
last_reviewed: "2026-09-11"
tags: [ml, ml-03, risk-011, kmeans, governance, mlflow]
---

# Compuerta de revisión RISK-011 para ML-03

> Esta es la fuente canónica del **proceso de revisión** de RISK-011. No reemplaza la
> evidencia numérica del corte 8-sep ni autoriza promoción, publicación Gold o cambios de API.

## 1. Estado que no debe mezclarse

| Elemento | Estado vigente en `main` | Qué no debe afirmarse |
|---|---|---|
| Corte 8-sep | D1-D4 + `indice_completitud_drivers`, `k=3`, Silhouette 0.4644549058; documentado en [[vault/15_ML_Models/ML03_Entrenamiento_US321]] | Que el perfil 2 sea un hallazgo sustantivo: coincide con cobertura D6. |
| RISK-011 | `mitigando` por [[vault/10_Risk_Governance/Decision_Log\|DEC-027]] | Que la mitigación metodológica convierta a ML-03 en modelo operativo. |
| Variante D1-D4 | Evidencia técnica aceptada: `k=2`, Silhouette `0.4620526551`; completitud sólo como auditoría | Que exista un `run_id` recuperable, una promoción o una publicación Gold. |
| Integración | El Panel mantiene `SIN_DATO`; no hay productor Gold ni consulta C4 para ML-03 | Que ML-03 ya sea el tercer modelo operativo. |

La documentación histórica del corte 8-sep se conserva. Si una variante supera esta compuerta,
debe declararla explícitamente como histórica y enlazar la nueva evidencia; nunca sobrescribir
la procedencia del resultado anterior.

## 2. Estrategia de modelado permitida

1. El estimador candidato puede usar únicamente D1-D4: pobreza, inseguridad, infraestructura y
   conectividad. `indice_completitud_drivers` se conserva como auditoría de cobertura, no como
   feature de KMeans.
2. D5 y D6 permanecen fuera del vector mientras su cobertura no tenga contrato temporal y espacial
   defendible. `SIN_DATO` no se imputa ni se convierte en cero.
3. La selección compara exactamente `k=2..6` con la misma partición temporal: entrenar en
   2022-2023/2023-2024 y evaluar en 2024-2025. No se prueban algoritmos, semillas o cortes extra
   para mejorar una cifra después de verla.
4. Las filas incompletas sobre D1-D4 se excluyen y se cuentan. No son cluster 0, ni escuelas sanas,
   ni evidencia de ausencia de necesidad.
5. Silhouette describe separación geométrica; no demuestra causalidad, prioridad ni eficacia de
   intervención.

### Alcance de ARI

El ARI entre varias semillas mide únicamente que KMeans converge a la misma partición ante cambios
de inicialización. ARI=1.0 no demuestra estabilidad entre ciclos, entidades, futuros cortes ni
beneficio de negocio. La única ventana temporal disponible sigue sin ser un test externo
independiente y debe declararse como limitación.

## 3. Evidencia mínima antes de cambiar el estado del riesgo

La corrida debe ejecutarse sobre el dump canónico en una base local aislada y de sólo lectura. El
artefacto versionado puede contener sólo agregados, nunca CCT, secretos ni datos crudos.

- SHA-256 del dump, commit, versiones de Python/scikit-learn y orden de entrada.
- Total de filas, elegibles, excluidas y exclusión por ciclo/entidad.
- Tabla `k=2..6`, selección determinista y Silhouette temporal.
- Perfiles agregados y tabla `cluster × d6_cobertura` que permita comprobar que ningún cluster es
  equivalente a tener D6 disponible.
- ARI de todos los pares de las cinco semillas fijadas, etiquetado como estabilidad de
  inicialización.
- Prueba de que el vector del estimador contiene D1-D4 y excluye completitud, D5 y D6.

La evidencia anterior y la variante candidata deben coexistir con fecha y fuente. Una diferencia de
métrica no convierte por sí sola a la variante en canónica.

## 4. Una sola verdad para MLflow

Antes de escribir un `run_id` en una ficha de modelo o en una propuesta, la persona ejecutora debe
consultar MLflow y verificar el experimento, parámetros, métricas, artefacto descargable y carga
exitosa. El resultado se expresa de una sola forma:

| Verificación | Redacción permitida |
|---|---|
| El `run_id` no existe, no coincide o no se puede recuperar | `mlflow_run_id: null`; "registro MLflow pendiente". |
| Existe y coincide con la evidencia revisada | "corrida local registrada como evidencia técnica; no aprobada, no promovida y no publicada en Gold". |

Un registro recuperable no aprueba RISK-011 y no permite cambiar `gold.features_escuela`,
`gold.predicciones`, API ni Panel. El registro se hace después de la revisión técnica de la evidencia,
usando la guarda `--tracking-uri` junto con `--confirmar-registro`.

## 5. Estado y secuencia de integración posterior al gate

1. **Completado:** Deni sincronizó y entregó PR #317; CI quedó verde sobre `7cb8481` y el PR se
   integró en `main`.
2. **Completado:** Estefany aprobó técnicamente el vector D1-D4, la evidencia agregada y el límite
   de ARI como estabilidad de inicialización.
3. **Completado:** Edgar aceptó la mitigación metodológica en DEC-027 y cambió RISK-011 a
   `mitigando`. También declaró ML-03 como deuda no operativa de esta entrega.
4. **Diferido, requiere nueva decisión del PO:** C1 propone en un PR propio
   `gold.ml03_asignaciones` idempotente, con revisión de esquema.
5. **Diferido, después de C1:** C3 implementa el productor batch y C4 la lectura API en PRs
   separados. La API consulta Gold; no entrena ni consulta MLflow por request.
6. **Diferido, después de C1/C3/C4:** C2 y QA ejecutan Gold → API → Panel con una escuela elegible y
   una excluida. El cluster jamás se interpreta como riesgo y `SIN_DATO` sigue siendo explícito
   cuando no hay asignación.

No se modifica Gold mientras DEC-027 conserve ML-03 como deuda explícita. La reactivación exige una
decisión nueva y trazable del PO, una base canónica aislada y la verificación independiente de MLflow.

## 6. Criterio de salida de esta compuerta

La compuerta metodológica quedó satisfecha con PR #317, la evidencia agregada, la aprobación técnica
y DEC-027. La compuerta operativa sigue pendiente: MLflow debe tener evidencia recuperable y C1, C3,
C4 y QA deben cerrar su propio recorrido E2E antes de que ML-03 pueda operar.
