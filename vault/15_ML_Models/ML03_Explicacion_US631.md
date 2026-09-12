---
id: DOC-ML03-EXPLICACION-US631
title: "US-631 — Explicación verificable de ML-03"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
source_of_truth: false
traces_up: ["US-631", "US-321", "REQ-003", "RISK-011"]
traces_down: ["vault/15_ML_Models/ML03_Model_Card", "vault/15_ML_Models/ML03_Entrenamiento_US321"]
tags: [ml, ml-03, clustering, explicacion, sprint-7]
---

# US-631 — Explicación verificable de ML-03

> Material de demostración de S7. No sustituye la evidencia numérica canónica de
> [[vault/15_ML_Models/ML03_Entrenamiento_US321]] ni autoriza publicar resultados.

## Qué responde ML-03

ML-03 agrupa escuelas con perfiles parecidos en los drivers disponibles. A diferencia de ML-01,
no predice una variación de matrícula; y a diferencia de ML-02, no decide cuál driver explica un
riesgo ni recomienda una intervención. El número de cluster es una etiqueta técnica, no un nivel
de riesgo, prioridad ni diagnóstico individual.

## Cómo se construyó la evidencia actual

La corrida del 8-sep-2026 usó el dump Gold canónico en una base local aislada y de sólo lectura.
El vector fue `D1–D4 + indice_completitud_drivers`; D5 y D6 se dejaron fuera del clustering por
ausencia estructural y se conservaron únicamente como evidencia de cobertura. No se imputó
`SIN_DATO` como cero.

KMeans se evaluó temporalmente: entrenó con 2022-2023 y 2023-2024, y validó en 2024-2025. Entre
`k=2..6`, se seleccionó `k=3` por su Silhouette temporal de **0.4644549058**. Participaron 114,200
observaciones elegibles; 21,846 se excluyeron por no tener completos los campos del vector
operativo. La evidencia agrega resultados: no contiene CCT individuales ni credenciales.

## Qué puede decirse en la demostración

- Hay tres grupos descriptivos y la separación geométrica del corte supera la referencia de 0.30.
- El grupo 0 muestra principalmente brecha de conectividad y carencias de infraestructura.
- El grupo 1 concentra mejores servicios medios, con inseguridad como presión relativa dominante.
- La etiqueta del cluster no sustituye ML-01 ni ML-02; la historia de riesgo y recomendación sigue
  viniendo de esos modelos.

## Límite que debe decirse antes de mostrar resultados

El grupo 2 no puede presentarse como un tercer perfil de necesidad escolar. Las 1,648
observaciones elegibles que tienen D6 disponible coinciden exactamente con ese cluster, a través
de `indice_completitud_drivers`. Esa vía indirecta de cobertura está abierta como `RISK-011`.

Por ello ML-03 permanece `SIN_DATO` en producción. El resultado demuestra que el entrenamiento
funciona, pero no autoriza una lectura operativa, recomendación ni prioridad hasta que Andrés
revise el riesgo y Edgar decida su uso.

## Variante candidata y criterio de revisión

Una variante D1-D4 que retire `indice_completitud_drivers` puede ser una mitigación técnicamente
razonable, pero no sustituye este corte ni cambia el estado del riesgo por sí sola. Hasta que se
sincronice, tenga CI verde y sea revisada, sus métricas, ARI y cualquier `run_id` son evidencia
candidata, no estado canónico. La fuente del proceso y de la redacción permitida para MLflow es
[[vault/15_ML_Models/ML03_RISK011_Gate]].

## Qué falta para que sea extremo a extremo

1. Revisión técnica de `RISK-011` y decisión explícita sobre el vector/uso.
2. Corrida MLflow autorizada, con `run_id` recuperable; la guarda
   `--tracking-uri --confirmar-registro` evita hacerla accidentalmente.
3. Productor C3 y esquema `gold.ml03_asignaciones` implementados por C1 bajo Regla 7.
4. Lectura C4 desde esa tabla y prueba del contrato/UI sobre una candidata desplegada.

Estas cuatro fases son dependencias visibles, no promesas implícitas de este documento. Este PR no
escribe Gold, no toca API ni modifica el Panel.
