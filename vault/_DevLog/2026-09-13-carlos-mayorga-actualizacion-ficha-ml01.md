---
project: "FARO"
title: "Actualización de ficha ML-01 con métricas Gold"
date: "2026-09-13"
author_human: "Carlos Guillermo Mayorga Tapia"
agent: "pendiente de confirmar por el autor"
model: "pendiente de confirmar por el autor"
session_duration: "pendiente de confirmar por el autor"
touches: ["US-324", "ML-01", "BUG-015"]
tags: [ml-01, devlog, equipo-1]
---

# DevLog — 2026-09-13 — Actualización de ficha ML-01 con métricas Gold

→ [[vault/_DevLog/_index|Volver al índice]]

Se actualizó la sección 3 de `vault/15_ML_Models/ML01_Model_Card.md` para reflejar los resultados obtenidos tras el reentrenamiento del modelo sobre la capa Gold real (el 5 de septiembre), eliminando la referencia a datos sintéticos y al bloqueo por el BUG-015 (que ya fue resuelto).

Se incluyeron las métricas reales documentadas en `ML01_Entrenamiento.md`:
- MAE de 0.141458
- RMSE de 0.436326
- Mejora frente al baseline del 11.04 %

**El umbral de aceptación se declara incumplido.** `src/modelos/evaluar.py::UMBRALES` fija
`ML-01_mae: 0.03` y la corrida real da 0.141458 — **4.7× por encima**. La versión inicial de
esta ficha documentaba la mejora sobre el baseline sin mencionar el umbral; se corrige a
petición de Edgar Coronel para que la ficha diga lo mismo que las otras dos superficies que
ya lo declaran: [[vault/15_ML_Models/Publicacion_Gold]] §9 (`approved`) y la sección «Cómo
funciona» del portal. Un modelo que no alcanza su umbral no se presenta como si lo hiciera;
lo que sí se afirma es que le gana al baseline temporal por 11.04 %.
