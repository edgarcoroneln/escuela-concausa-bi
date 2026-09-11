---
id: DOC-FARO-UX-DATAVIZ
title: "Data Visualization Spec — qué dato demuestra la historia"
owner: "Monserrat Xcaret Miranda Olivas"
status: draft
traces_up: ["US-621", "REQ-002", "vault/04_UX_Design/FARO_Storytelling_UX/00_Storytelling_Scope"]
traces_down: ["US-641", "vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity"]
last_reviewed: "2026-09-10"
tags: [ux, dataviz, storytelling, s7, us-621]
---

# Data Visualization Spec — qué dato demuestra la historia

> Documento de Monserrat Xcaret Miranda Olivas. Fija **qué datos y gráficas demuestran** la historia.
> Libertad creativa para reorganizar las visualizaciones, dentro de los datos y endpoints existentes.
> → [[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] ·
> [[vault/04_UX_Design/FARO_Storytelling_UX/00_Storytelling_Scope]]

**Estado:** borrador.

## 1. Regla de sustento

Cada gráfica de este documento declara el endpoint que la sostiene. **Si no hay endpoint, no hay
gráfica.** El mapeo verificado está en §10 del plan; lo que no aparezca ahí se tramita como petición
en §11 antes de dibujarse.

## 2. Pregunta → dato → gráfica

<!-- Una fila por pantalla. La pregunta es la del usuario, no la del analista. -->

| Pantalla | Pregunta que responde | Dato | Endpoint | Gráfica propuesta |
|---|---|---|---|---|
| P2 — Panorama |  |  |  |  |
| P3 — Selección |  |  |  |  |
| P4 — Expediente |  |  |  |  |
| P5 — Conclusión |  |  |  |  |
| P6 — Exploración |  |  |  |  |

## 3. Visualización principal de la Pantalla 2

<!-- Es la decisión más visible del documento. Justificar por qué esa forma y no otra. -->

## 4. Gráfica comparativa de los 6 drivers (Pantalla 4)

<!-- Cómo se representan d1..d6 juntos, cómo se destaca el dominante y cómo se dibuja un driver
     SIN_DATO sin que parezca un cero. Fuente: GET /api/v1/escuelas/{cct}. -->

## 5. Cómo se obtiene y comunica el Top 3

<!-- Se calcula en Front sobre el conjunto completo de escuelas en riesgo, no sobre lo filtrado.
     Documentar el conteo exacto: cuántas escuelas tienen cada driver como dominante, y cómo se
     expresa (número, proporción o ambos). -->

## 6. Tratamiento de SIN_DATO y cobertura parcial

<!-- indice_completitud_drivers y es_estimado_por_grupo existen en la API y deben verse.
     D5 y D6 tienen cobertura parcial por diseño: eso se comunica, no se esconde. -->

## 7. Ejemplos de visualizaciones

<!-- Bocetos o capturas. Se entregan a Juan para que los integre a la identidad visual. -->

## 8. Lo que NO se puede graficar hoy

<!-- prioridad (P-01) y las bandas Alto/Medio/Bajo (P-02). Dejar dicho qué se haría si se aprueban
     y qué se hace mientras tanto. -->
