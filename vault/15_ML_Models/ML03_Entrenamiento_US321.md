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

El vector operativo ratificado por C3 para la corrida final es **D1-D4 +
`indice_completitud_drivers`**. D5 (`d5_agua`) y D6 (`d6_aire`) se conservan en el diagnóstico de
cobertura, pero no entran al vector de KMeans: D5 está 100 % `SIN_DATO` en el Gold real post-BUG-048
y D6 tiene cobertura residual, por lo que incluirlos bloquearía `casos_completos` o empujaría una
imputación no aprobada.

La política sigue siendo `casos_completos` sobre el **vector operativo**: las filas con D1-D4 o
completitud ausentes se contabilizan y excluyen; D5/D6 ausentes no excluyen una escuela ni se
rellenan con cero. Esta política permite verificar KMeans, Silhouette, partición temporal y perfiles
sin inventar señal en los drivers de cobertura parcial.

Registrar una versión no autoriza promoverla como modelo productivo ni interpretarla fuera del
alcance de esa cobertura. Cualquier futura reincorporación de D5/D6 al vector requiere nueva
evidencia de cobertura y revisión humana.

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

## Ejecución reproducible desde Gold

El punto de entrada `python -m src.modelos.ejecutar_cierre_ml03` lee la tabla real desde
`DATABASE_URL`, conserva la comparación walk-forward de `k=2..6` y sólo registra en MLflow cuando
se indica `--tracking-uri`. Si D5 u otro driver está totalmente ausente, `casos_completos` puede
dejar cero filas: el comando lo reporta como bloqueo y no sustituye ausencias ni registra un modelo.

La ejecución real sigue pendiente porque el ambiente usado el 4-sep-2026 no tenía Docker ni una
base Gold configurada. Esto no cambia el estado ni reemplaza la ratificación humana de la política.
