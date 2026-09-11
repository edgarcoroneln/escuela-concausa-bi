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

La corrida del 10-sep-2026 usó el dump Gold canónico en una base local aislada y de sólo lectura.
El vector es **D1–D4** (pobreza, inseguridad, infraestructura, conectividad); `indice_completitud_drivers`
ya no participa del entrenamiento -- se retiró para mitigar `RISK-011` (ver más abajo) y se conserva
sólo como atributo de auditoría de cobertura. D5 y D6 se dejaron fuera del clustering por ausencia
estructural. No se imputó `SIN_DATO` como cero.

KMeans se evaluó temporalmente: entrenó con 2022-2023 y 2023-2024, y validó en 2024-2025. Entre
`k=2..6`, se seleccionó `k=2` por su Silhouette temporal de **0.4620526551** (`≈0.4621`).
Participaron 114,200 observaciones elegibles; 21,846 se excluyeron por no tener completos los
campos del vector operativo. La estabilidad se midió con el Índice de Rand Ajustado (ARI) entre
cinco semillas (7, 21, 42, 84, 2026): mínimo y promedio `1.0`, reproducible con
`evaluar_estabilidad_semillas()`. La evidencia agrega resultados: no contiene CCT individuales ni
credenciales.

> El corte anterior (8-sep-2026) usaba `D1–D4 + indice_completitud_drivers`, seleccionaba `k=3`
> con Silhouette `0.4644549058` y describía tres grupos. Ese corte queda **superado** -- ver la
> sección siguiente.

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

**`RISK-011` sigue abierto en `Risk_Register.md`.** Lo anterior es la mitigación a nivel de
código, ya implementada y con evidencia reproducible
([ML03_Comparacion_RISK011_20260910.json](ML03_Comparacion_RISK011_20260910.json),
[[vault/15_ML_Models/Propuesta_Cierre_ML03_D1_D4]]); el **cierre formal** del riesgo requiere la
revisión técnica de Estefany Hernández Loredo y la decisión explícita de Edgar Coronel. Hasta que
eso ocurra, ML-03 permanece `SIN_DATO` en producción. El resultado demuestra que el entrenamiento
funciona, pero no autoriza una lectura operativa, recomendación ni prioridad.

## Qué falta para que sea extremo a extremo

1. Revisión técnica de Estefany sobre el vector D1-D4 (ya implementado en código) y cierre formal
   de `RISK-011` por Edgar.
2. Corrida MLflow autorizada, con `run_id` recuperable; la guarda
   `--tracking-uri --confirmar-registro` evita hacerla accidentalmente.
3. Productor C3 y esquema `gold.ml03_asignaciones` implementados por C1 bajo Regla 7.
4. Lectura C4 desde esa tabla y prueba del contrato/UI sobre una candidata desplegada.

Estas cuatro fases son dependencias visibles, no promesas implícitas de este documento. Este PR no
escribe Gold, no toca API ni modifica el Panel.
