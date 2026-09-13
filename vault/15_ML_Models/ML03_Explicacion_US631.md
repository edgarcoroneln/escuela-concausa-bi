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

La evidencia candidata del 10-sep-2026 declara un corte Gold aislado y de sólo lectura. Propone el
vector **D1–D4** (pobreza, inseguridad, infraestructura, conectividad); `indice_completitud_drivers`
queda como auditoría de cobertura y no como feature. D5 y D6 quedan fuera del clustering por
ausencia estructural. No se imputa `SIN_DATO` como cero. Esta descripción está pendiente de la
revisión técnica y no sustituye la evidencia histórica canónica.

KMeans se evaluó temporalmente: entrenó con 2022-2023 y 2023-2024, y validó en 2024-2025. Entre
`k=2..6`, la evidencia candidata reporta `k=2` con Silhouette temporal de **0.4620526551**
(`≈0.4621`). Reporta 114,200 observaciones elegibles y 21,846 excluidas por no tener completos
los campos del vector. El ARI entre cinco semillas (7, 21, 42, 84, 2026) tiene mínimo y promedio
`1.0`: sólo mide estabilidad de inicialización, no estabilidad temporal, territorial ni valor de
negocio. La evidencia agrega resultados: no contiene CCT individuales ni credenciales.

> El corte histórico del 8-sep-2026 usaba `D1–D4 + indice_completitud_drivers`, seleccionaba
> `k=3` con Silhouette `0.4644549058` y describía tres grupos. Se conserva como evidencia
> histórica; no queda reemplazado ni cerrado por la variante candidata.

## Qué puede decirse en la demostración

- Hay **dos** grupos descriptivos y la separación geométrica del corte supera la referencia de 0.30.
- El grupo 0 (83,275 observaciones) tiene como presión principal la inseguridad, con
  conectividad e infraestructura relativamente mejores.
- El grupo 1 (30,925 observaciones) tiene como presión principal la brecha de conectividad,
  seguida de carencias de infraestructura.
- La etiqueta del cluster no sustituye ML-01 ni ML-02; la historia de riesgo y recomendación sigue
  viniendo de esos modelos. Los números de cluster son etiquetas sin orden: no significan riesgo
  alto/bajo ni prioridad automática.

## Por qué cambió de tres grupos a dos (`RISK-011`)

El corte del 8-sep (`D1-D4 + indice_completitud_drivers`) producía un tercer grupo (cluster 2) que
coincidía **exactamente** con las 1,648 observaciones elegibles que tenían D6 disponible.
Completitud estaba separando disponibilidad de dato, no un perfil real de escuela -- narrarlo como
perfil sustantivo de necesidad escolar habría sido engañoso. Esa es la mitigación técnica de
`RISK-011`: retirar completitud del vector. Al hacerlo, `k=2` deja de reproducir ese grupo
espurio; la caída de Silhouette (`0.4645` → `0.4621`, `-0.0024`) es el costo de esa corrección.

**`RISK-011` sigue abierto en `Risk_Register.md`.** La variante candidata propone retirar
completitud del vector y aporta evidencia para revisión
([ML03_Comparacion_RISK011_20260910.json](ML03_Comparacion_RISK011_20260910.json),
[[vault/15_ML_Models/Propuesta_Cierre_ML03_D1_D4]]). El **cierre formal** requiere la revisión
técnica de Estefany Hernández Loredo y la decisión explícita de Edgar Coronel. Hasta entonces,
ML-03 permanece `SIN_DATO` en producción y no autoriza una lectura operativa, recomendación ni
prioridad.

## Variante candidata y criterio de revisión

Una variante D1-D4 que retire `indice_completitud_drivers` puede ser una mitigación técnicamente
razonable, pero no sustituye este corte ni cambia el estado del riesgo por sí sola. Hasta que se
sincronice, tenga CI verde y sea revisada, sus métricas, ARI y cualquier `run_id` son evidencia
candidata, no estado canónico. La fuente del proceso y de la redacción permitida para MLflow es
[[vault/15_ML_Models/ML03_RISK011_Gate]].

## Qué falta para que sea extremo a extremo

1. Revisión técnica de Estefany sobre la variante D1-D4 y cierre formal de `RISK-011` por Edgar.
2. Corrida MLflow autorizada, con `run_id` recuperable; la guarda
   `--tracking-uri --confirmar-registro` evita hacerla accidentalmente.
3. Productor C3 y esquema `gold.ml03_asignaciones` implementados por C1 bajo Regla 7.
4. Lectura C4 desde esa tabla y prueba del contrato/UI sobre una candidata desplegada.

Estas cuatro fases son dependencias visibles, no promesas implícitas de este documento. Este PR no
escribe Gold, no toca API ni modifica el Panel.
