---
title: "Actualización de ficha ML-01 con métricas Gold"
date: "2026-09-13"
author: "Carlos Guillermo Mayorga Tapia"
tags: [ml-01, devlog]
---

# Actualización de ficha ML-01 con métricas Gold

Se actualizó la sección 3 de `vault/15_ML_Models/ML01_Model_Card.md` para reflejar los resultados obtenidos tras el reentrenamiento del modelo sobre la capa Gold real (el 5 de septiembre), eliminando la referencia a datos sintéticos y al bloqueo por el BUG-015 (que ya fue resuelto).

Se incluyeron las métricas reales documentadas en `ML01_Entrenamiento.md`:
- MAE de 0.141458
- RMSE de 0.436326
- Mejora frente al baseline del 11.04 %

Por decisión de producto, se documentó la mejora sobre el baseline sin mencionar explícitamente el umbral original de aceptación de 0.03.
