---
id: DOC-ML03-CARD
title: "Ficha de Modelo: ML-03 (Clustering de Escuelas)"
owner: "Carlos Guillermo Mayorga Tapia"
status: in_review
source_of_truth: false
traces_up: ["US-324", "US-321", "US-631", "REQ-003"]
tags: [ml, ml-03, clustering, no-supervisado, model-card]
---

# Ficha de Modelo: ML-03 (Clustering de Escuelas)

> → [[vault/15_ML_Models/_index|Volver a _index]]

## 1. Propósito
El objetivo de **ML-03** es un agrupamiento no supervisado (clustering) para encontrar perfiles similares de escuelas. Se utiliza para identificar bolsas de escuelas con problemáticas comunes independientemente de su región geográfica o su índice de riesgo directo de ML-01. (Ver: [[vault/15_ML_Models/ML_Strategy]]).

## 2. Features de entrada

- **Vector ratificado:** `d1_pobreza`, `d2_inseguridad`, `d3_infraestructura`,
  `d4_conectividad` e `indice_completitud_drivers`.
- **Exclusiones deliberadas:** `cct`, municipio, ciclo y target de ML-01 no participan. D5/D6
  tampoco: D5 no tuvo observaciones y D6 tuvo cobertura residual en el corte canónico. Su
  ausencia se conserva como auditoría, nunca se transforma en cero.
- **Preproceso:** `StandardScaler` y `KMeans` viven en el mismo pipeline. Cada scaler se ajusta
  sólo con ciclos anteriores a la ventana de validación.

## 3. Métrica obtenida y procedencia

- **Métrica principal:** coeficiente de **Silhouette** temporal.
- **Corte vigente (8-sep-2026):** `k=3`, **Silhouette = 0.4644549058**, por encima de la
  referencia exploratoria de 0.30.
- **Protocolo:** se entrenó con 2022-2023 y 2023-2024; se validó con 2024-2025. Se comparó
  `k=2..6`, sin selección aleatoria ni búsqueda adicional de semillas/algoritmos.
- **Cobertura:** 114,200 observaciones elegibles y 21,846 excluidas de 136,046; la exclusión se
  debe a ausencias en el vector operativo, no a D5/D6 de manera directa.

La fuente numérica canónica es [[vault/15_ML_Models/ML03_Entrenamiento_US321]] y
[ML03_Evidencia_20260908.json](ML03_Evidencia_20260908.json). El resultado histórico `0.1086`
pertenece a un fixture/protocolo anterior y no describe la corrida actual.

## 4. Limitaciones conocidas
- Carece de una "verdad absoluta" al ser no supervisado; los clústeres resultantes requieren interpretación y etiquetado de negocio (ej. "Escuelas rurales sin conectividad", "Escuelas urbanas saturadas").
- Sólo hay una ventana temporal disponible; no es un test externo independiente ni demuestra
  estabilidad entre ciclos o semillas.
- `RISK-011` sigue abierto: el cluster 2 coincide con la disponibilidad de D6 a través de
  `indice_completitud_drivers`. No se debe presentar como un perfil sustantivo de necesidad
  escolar hasta la revisión técnica.
- No existe aún una corrida MLflow aprobada, productor Gold, endpoint C4 ni exposición real en
  la UI. El resultado analítico no equivale a modelo productivo.

## 5. Contextos de no uso
- **NO usar para estimar series de tiempo** (ej. proyectar matrículas a futuro). Para eso existe ML-01.
- **NO usar para clasificar directamente el riesgo de un alumno**. Los clústeres agrupan condiciones estructurales, no el destino final de un estudiante individual.
- **NO recomendar intervenciones ni asignar prioridad/riesgo** a partir del número de cluster.
- **NO mostrar un cluster de cobertura como hallazgo de negocio** mientras `RISK-011` permanezca
  abierto.

## 6. Estado de integración

ML-03 tiene evidencia reproducible y una explicación para S7, pero permanece sin promoción:
`mlflow_run_id` es nulo para este corte y el Panel debe conservar `SIN_DATO`. La integración
posterior requiere un productor C3 aprobado, esquema Gold de C1 y lectura de C4, cada uno en su
propio PR y con revisión humana. La explicación de demostración está en
[[vault/15_ML_Models/ML03_Explicacion_US631]].
