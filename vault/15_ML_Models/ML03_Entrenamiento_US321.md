---
id: DOC-ML03-ENTRENAMIENTO-US321
title: "US-321 — Entrenamiento temporal de ML-03"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
traces_up: ["US-321", "REQ-003", "vault/15_ML_Models/ML_Strategy"]
traces_down: ["US-324", "US-412"]
tags: [ml, ml-03, clustering, kmeans, silhouette]
---

# US-321 — Entrenamiento temporal de ML-03

> Implementación: `src/modelos/entrenar_ml03.py`.

## Entrega

- KMeans con `StandardScaler` dentro del mismo pipeline.
- Selección de `k` por Silhouette en ventanas walk-forward.
- El scaler y KMeans se ajustan sólo con ciclos anteriores a cada evaluación.
- Perfiles por cluster con los drivers promedio y una descripción determinista en lenguaje de
  negocio.
- Integración MLflow mediante el helper compartido de Célula 3, con versión canónica
  `ML03_ClusteringEscuelas` en Model Registry.

## Separación respecto al diagnóstico

US-322/US-325 se revisan en otro PR porque producen evidencia de calidad y cobertura, mientras
US-321 toma decisiones de entrenamiento. Mezclarlos obligaría a revalidar el diagnóstico cada vez
que cambie la política de imputación y ocultaría qué aprobación desbloquea cada historia.

## Política provisional de ausencia

El pipeline sólo acepta `casos_completos`. Las filas con cualquier driver ausente se contabilizan
y excluyen; nunca se rellenan con cero. Esta política permite verificar KMeans, Silhouette,
partición temporal y perfiles sin inventar el fallback que aún deben ratificar Célula 1 y el Tech
Lead de ML.

No es la política final: puede concentrar el entrenamiento en territorios con mayor cobertura. Por
eso registrar una versión no autoriza promoverla como modelo productivo ni interpretarla sobre
escuelas reales.

## Criterio pendiente para cierre

El PR #197 (mergeado el 3-sep-2026) eliminó el bloqueo de disponibilidad reproducible de Bronze para
DS-01/DS-02 y añadió sus suites de Great Expectations. No cierra esta historia automáticamente:
falta ejecutar `dbt run && dbt test`, verificar `gold.features_escuela` y repetir el entrenamiento.
El plan y prompt de ejecución están en
[[vault/15_ML_Models/Plan_Cierre_Estefany_US321_US322_US325]].

- Ratificar mediana municipal y fallback cuando un municipio no tenga observaciones suficientes.
- Repetir backtesting y selección de `k` con la política aprobada.
- Ejecutar sobre `gold.features_escuela` con al menos tres ciclos disponibles para ML; debido a que
  Gold descarta el primer ciclo al construir el target, esto requiere al menos cuatro en Bronze
  (BUG-026).
- Ejecutar la corrida final en MLflow y actualizar la ficha ML-03 con el Silhouette real.
