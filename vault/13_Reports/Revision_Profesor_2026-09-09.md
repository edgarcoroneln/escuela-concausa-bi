---
id: RPT-REVISION-PROFESOR-2026-09-09
title: "Retroalimentación del profesor y reapertura — 9 de septiembre de 2026"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
version: "1.0"
traces_up: ["PRD", "PRD-GENERAL", "RPT-CIERRE-PROYECTO-2026-09-08", "US-006"]
traces_down: ["DEC-022", "PLAN-RECUPERACION-2026-09-09", "US-601", "US-611", "US-621", "US-631", "US-641", "US-651"]
last_reviewed: "2026-09-10"
tags: [reports, professor-feedback, recovery, reopening]
---

# Retroalimentación del profesor y reapertura — 9 de septiembre de 2026

> Fuente canónica del resultado de la revisión final del 9-sep. Este documento complementa el PRD:
> no cambia la rúbrica, registra la evaluación externa que invalida el cierre operativo anterior.
> → [[vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09]] · [[vault/10_Risk_Governance/Decision_Log]]

## Resultado

El profesor **no aceptó el producto como una entrega satisfactoria** y concedió una ventana de mejora
hasta el **lunes 14 de septiembre de 2026, a primera hora**. Por `DEC-022`, el desarrollo queda
reabierto del jueves 10 al domingo 13; el corte del 8-sep se conserva sólo como evidencia histórica.

## Hallazgos y efecto sobre el alcance

| Área | Observación del profesor | Brecha verificable | REQ reabierto | Trabajo de recuperación |
|---|---|---|---|---|
| Frontend | La experiencia visual no fue satisfactoria | FARO Web no guía al usuario por una narrativa ni integra con suficiente calidad las superficies | `REQ-002` | Equipos 3/5 · `US-621`, `US-641` |
| Gráficas | Las visualizaciones de Superset no comunicaron valor | Selección y composición de gráficas sin narrativa ejecutiva convincente | `REQ-002` | Equipo 3 · `US-621` |
| Storytelling | No hubo una historia de negocio/datos | Falta un recorrido problema→datos→hallazgo→predicción→acción | `REQ-002`, `REQ-007` | Equipos 1/3/5 · `US-601`, `US-621`, `US-641` |
| Componentes | Faltó explicar cómo funciona el backend | No se presentó de forma clara el paso Bronze→Silver→Gold, filtros, cubos, componentes y modelo E-R | `REQ-001`, `REQ-004`, `REQ-007` | Equipo 1 · `US-601` |
| Chat IA | No responde como conversación en lenguaje natural | El cierre anterior ya reconocía una UI *single-turn*; la explicación no debe reducirse a mostrar SQL | `REQ-006` | Equipo 2 · `US-611` |
| ML-03 | No funciona en el producto | El cierre anterior lo declaró entrenado pero sin promoción a Gold/API/UI | `REQ-003` | Equipo 4 · `US-631` |
| Explicación ML | Demasiado básica | Faltan narrativa, métricas, limitaciones, interpretación y vínculo con decisiones | `REQ-003` | Equipo 4 · `US-631` |
| QA | La aceptación previa no representó la experiencia evaluada | Se necesitan criterios por equipo y una pasada integral sobre la candidata de entrega | `REQ-007` | Equipo 6 · `US-651` |

> **Decisión del PO, 10-sep:** el PR #297 fue aprobado y mergeado. `DEC-023` y `ADR-011` autorizan
> que los Equipos 3 y 5 redefinan UX/UI, storytelling, navegación y gráficas sin conservar el
> frontend rechazado ni Superset como experiencia principal. Los contratos de datos, seguridad,
> accesibilidad, PRD y QA permanecen obligatorios.

## Corrección del dictamen anterior

Las cifras **91/92 `done`** eran un cierre administrativo y no una prueba de satisfacción externa.
Desde esta revisión no deben utilizarse para afirmar que el producto está terminado. Los estados
vigentes viven en [[vault/12_Roadmap_Sprints/Execution_Status]] y el plan operativo en
[[vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09]].

## Condición de nueva entrega

La candidata del lunes sólo puede declararse lista si:

1. los seis equipos entregan evidencia enlazada a su US de S7;
2. QA ejecuta la matriz integral contra la misma revisión desplegada;
3. ML-03 y el chat se demuestran en la URL candidata, no sólo en local;
4. el recorrido de storytelling explica componentes, datos, modelos, hallazgos y acciones;
5. el PO registra el *go/no-go* del domingo y la entrega del lunes en `US-006`.
