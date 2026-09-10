---
id: PLAN-RECUPERACION-2026-09-09
title: "Plan de recuperación — entrega del 14 de septiembre"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
version: "1.0"
source_of_truth: true
traces_up: ["RPT-REVISION-PROFESOR-2026-09-09", "DEC-022", "PRD"]
traces_down: ["PLAN-EXEC-STATUS", "DOC-RACI", "US-601", "US-611", "US-621", "US-631", "US-641", "US-651"]
last_reviewed: "2026-09-10"
tags: [roadmap, sprint-7, recovery, teams, delivery]
---

# Plan de recuperación — jueves 10 a lunes 14 de septiembre

> Plan operativo canónico de S7. La numeración anterior (3, 5, 6, 8, 9 y 10) se normaliza a
> **Equipos 1 a 6** sin cambiar integrantes. → [[vault/13_Reports/Revision_Profesor_2026-09-09]]

## Objetivo y regla de integración

Entregar el lunes a primera hora una versión que **demuestre**, no sólo documente, la corrección de
las brechas observadas. Cada persona trabaja exclusivamente en `dev/{identidad}`, sincroniza mediante
`git merge origin/main`, abre PR y adjunta DevLog, pruebas y trazabilidad. La rama remota
`componentes-back` no cumple la política: no se crea trabajo nuevo allí; cualquier cambio útil debe
migrarse a la rama personal de su autor mediante un PR trazable.

## Equipos renumerados y entregables

| Equipo | Frente | Líder | Integrantes | Gate jueves 10, antes de 18:00 | Criterio final domingo 13 |
|---|---|---|---|---|---|
| 1 | Componentes y memoria técnica | **Héctor Morales** | Manuel Serranía, Carlos Mayorga | Bosquejo enlazado: componentes, datos actuales, filtros Bronze/Silver/Gold, cubos, ER y memoria técnica | Documento completo, diagramas legibles y recorrido técnico que alimenta storytelling |
| 2 | Chat IA natural | **Andrés González** | Karla Monter, Alejandro Velázquez | Chat responde en lenguaje natural sobre un set representativo y plan de arquitectura/observabilidad | Conversación natural y auditable en la URL candidata, guardarraíles y regresión aprobados |
| 3 | UX/UI y storytelling | **Marina García** | Oscar Quiroz, Juan Macías, Monserrat Miranda | Marina confirma sistema visual, división de pantallas, gráficas y storyboard; **sin código productivo en este gate** | Prototipo y especificación aceptados, implementados por Equipo 5 y recorrido completo ensayado |
| 4 | ML-03 y explicación ML | **Estefany Hernández** | Deni Garrido, Luis García | Plan ya acordado convertido en tareas, datos/criterios y primera evidencia reproducible | ML-03 funciona de extremo a extremo; tres modelos explicados con métricas, límites y valor |
| 5 | Frontend y despliegue | **Diana Alvarez** | Luis Téllez, Christian Imanol Ruiz | Arquitectura de frontend/integración (incluido uso de RAG) y estrategia de despliegue/rollback | Integra UX, chat y tres modelos en producción; release identificable y rollback probado |
| 6 | QA integral | **Edward Ruiz** | Emilio Galnares, Edgar Jiménez, Eloisa González y Edgar Coronel como comodín | Metodología, requerimientos de prueba y criterios de aceptación por cada equipo | Matriz ejecutada sobre la misma candidata; cero defectos críticos/altos abiertos y go/no-go |

> **Confirmación del PO, 10-sep:** Edward dirige QA. Eloisa queda incorporada al Equipo 6 por
> continuidad con sus pruebas de API/chat/Auth; Edgar Coronel participa como comodín y conserva el go/no-go.

## Historias S7: una persona, una responsabilidad

| US | Responsable | Objetivo | Entregable verificable | Dependencia / entrega a |
|---|---|---|---|---|
| `US-601` | Héctor Rafael Morales Marbán | Dirigir la documentación de componentes | Arquitectura de componentes y recorrido backend | recibe repo; entrega a E3/E5/E6 |
| `US-602` | Manuel Alejandro Serranía Reinada | Explicar datos y transformación | Bronze→Silver→Gold, filtros, cubos y ER | entrega a E1/E3/E5 |
| `US-603` | Carlos Guillermo Mayorga Tapia | Consolidar memoria técnica | Memoria y resumen narrativo del backend | entrega a Monserrat |
| `US-611` | Andrés González Habib | Naturalizar la respuesta del agente | Orquestación conversacional y set de respuestas aceptado | recibe API/RAG; entrega a E5/E6 |
| `US-612` | Karla Alejandra Monter Benitez | Integrar contrato del chat | Contrato API, contexto y errores validados | entrega a Andrés/Diana |
| `US-613` | Alejandro Velázquez Mendoza | Operar el chat | Runtime, índices RAG, logs y smoke reproducible | entrega a Luis/QA |
| `US-621` | Marina García del Buey | Dirigir experiencia visual | Sistema visual y prototipo de pantallas | entrega a Diana |
| `US-622` | Oscar Antonio Quiroz Lázaro | Seleccionar visualizaciones | Catálogo gráfico justificado y especificaciones | entrega a Marina/Diana |
| `US-623` | Juan Carlos Macías Mayen | Diseñar flujos y pantallas | Wireframes, navegación, controles y estados | entrega a Marina/Diana |
| `US-624` | Monserrat Xcaret Miranda Olivas | Construir storytelling | Storyboard problema→datos→hallazgos→acción | recibe E1; entrega a E5/demo |
| `US-631` | Estefany Lucero Hernández Loredo | Corregir ML-03 | Entrenamiento, publicación e integración Gold/API/UI | entrega a Diana/QA |
| `US-632` | Deni Garrido Fragoso | Preparar datos de ML-03 | Features/cobertura y prueba de calidad reproducible | entrega a Estefany |
| `US-633` | Luis Enrique García Vázquez | Mejorar explicación ML | Fichas de tres modelos con métricas, límites e interpretación | entrega a E3/demo |
| `US-641` | Diana Aracely Alvarez Varela | Integrar el frontend | Arquitectura y frontend coherente con UX/storytelling | recibe E1–E4; entrega a QA |
| `US-642` | Luis Téllez Domínguez | Desplegar candidata | Release, URLs, observabilidad y rollback | recibe E2/E4/E5; entrega a QA |
| `US-643` | Christian Imanol Ruiz Hurtado | Integrar frontend/API/Auth | Contratos, sesión y manejo de errores E2E | entrega a Diana/QA |
| `US-651` | Edward Ulysses Ruiz Bustillos | Dirigir QA | Estrategia, matriz de aceptación y dictamen | recibe de todos; entrega al PO |
| `US-652` | Emilio Galnares Ruiz | Validar datos y ML | Pruebas de integridad, reproducibilidad y métricas | entrega a Edward |
| `US-653` | Edgar Ulises Jiménez López | Automatizar E2E | Regresión de frontend/chat/deploy | entrega a Edward |
| `US-654` | Edgar Edmundo Coronel Navarrete | Gobernar recuperación | Trazabilidad, revisiones diarias y go/no-go | integra todo y decide entrega |
| `US-655` | Eloisa González Rubio | Regresión API/chat/Auth | Suite y evidencia 200/401/403/422/conversación | entrega a Edward |

## Cadencia diaria y ruta crítica

| Fecha | 18:00 — salida obligatoria |
|---|---|
| Jue 10 | Gates de definición anteriores; criterios de aceptación ratificados y PR inicial por frente |
| Vie 11 | Primera integración E1→E3→E5, chat y ML-03 consumibles; QA ejecuta pruebas parciales |
| Sáb 12 | Candidata integrada en entorno de prueba, storytelling completo y defectos priorizados |
| Dom 13 | 18:00 ensayo final + QA; 20:00 *code freeze* de la candidata aprobada y decisión go/no-go |
| Lun 14 | Primera hora: healthchecks, entrega y cierre de `US-006`; sólo contingencia autorizada por PO |

Orden de integración: **E1 documentación/datos → E3 storytelling/UX → E5 frontend**;
**E4 ML-03 → E5**; **E2 chat → E5**; **E6 prueba continuamente todas las entregas**.

## Agenda de control de las 18:00 (30 minutos)

1. Demostración contra evidencia, no reporte verbal (5 min por frente crítico).
2. Estado de US/PR/checks y bloqueo con dueño y hora de resolución.
3. QA actualiza aceptación: verde, rojo o no ejecutado; nunca “casi”.
4. Confirmación de dependencias que entran al frontend al día siguiente.
5. Decisión del PO y actualización del tablero/DevLog.

## Definition of Done de recuperación

- PR aprobado y mergeado con CI, `vault_lint`, prueba del componente y DevLog.
- Evidencia enlazada REQ→US→prueba→PR/DevLog→release.
- Para superficies visibles, validación en la revisión desplegada que se entregará.
- Criterios del profesor demostrables en un recorrido de máximo 12 minutos.
- Sin secretos, mocks no rotulados, defectos críticos/altos o ramas paralelas no gobernadas.
