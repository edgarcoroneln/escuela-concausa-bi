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

## Historias de control por equipo

> Estas historias representan **frentes colectivos**, no tareas personales. El nombre del líder
> aparece como responsable para cumplir la regla de un dueño por US; el desglose interno se agregará
> sólo cuando cada equipo lo acuerde y lo presente en una sesión de las 18:00.

| US | Equipo | Responsable de coordinación | Resultado común esperado | Dependencia / entrega a |
|---|---|---|---|---|
| `US-601` | E1 · Componentes | Héctor Rafael Morales Marbán | Documentación de componentes, datos, capas, filtros, cubos, ER y memoria técnica | entrega a E3/E5/E6 |
| `US-611` | E2 · Chat IA | Andrés González Habib | Chat natural, contextual, seguro y demostrable | entrega a E5/E6 |
| `US-621` | E3 · UX/UI y storytelling | Marina García del Buey | Propuesta visual, gráficas, pantallas y storytelling | recibe E1; entrega a E5/E6 |
| `US-631` | E4 · ML-03 | Estefany Lucero Hernández Loredo | ML-03 funcional y explicación mejorada de los tres modelos | entrega a E3/E5/E6 |
| `US-641` | E5 · Frontend y deploy | Diana Aracely Alvarez Varela | Frontend integrado y candidata desplegada en producción | recibe E1–E4; entrega a E6 |
| `US-651` | E6 · QA | Edward Ulysses Ruiz Bustillos | Metodología, criterios, ejecución y dictamen integral | recibe de E1–E5; entrega al PO |
| `US-654` | Gobierno | Edgar Edmundo Coronel Navarrete | Trazabilidad, revisiones diarias y decisión go/no-go | integra el estado de E1–E6 |

## Padrón operativo S7 — participación, no asignación de tareas

| Persona | Equipo | Participación acordada |
|---|---|---|
| Héctor Rafael Morales Marbán | E1 · Componentes | Líder |
| Manuel Alejandro Serranía Reinada | E1 · Componentes | Integrante |
| Carlos Guillermo Mayorga Tapia | E1 · Componentes | Integrante |
| Andrés González Habib | E2 · Chat IA | Líder |
| Karla Alejandra Monter Benitez | E2 · Chat IA | Integrante |
| Alejandro Velázquez Mendoza | E2 · Chat IA | Integrante |
| Marina García del Buey | E3 · UX/UI y storytelling | Líder |
| Oscar Antonio Quiroz Lázaro | E3 · UX/UI y storytelling | Integrante |
| Juan Carlos Macías Mayen | E3 · UX/UI y storytelling | Integrante |
| Monserrat Xcaret Miranda Olivas | E3 · UX/UI y storytelling | Integrante · storytelling |
| Estefany Lucero Hernández Loredo | E4 · ML-03 | Líder |
| Deni Garrido Fragoso | E4 · ML-03 | Integrante |
| Luis Enrique García Vázquez | E4 · ML-03 | Integrante |
| Diana Aracely Alvarez Varela | E5 · Frontend y deploy | Líder |
| Luis Téllez Domínguez | E5 · Frontend y deploy | Integrante |
| Christian Imanol Ruiz Hurtado | E5 · Frontend y deploy | Integrante |
| Edward Ulysses Ruiz Bustillos | E6 · QA | Líder |
| Emilio Galnares Ruiz | E6 · QA | Integrante |
| Edgar Ulises Jiménez López | E6 · QA | Integrante |
| Eloisa González Rubio | E6 · QA | Integrante |
| Edgar Edmundo Coronel Navarrete | E6 · QA | Comodín QA y PO |

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
