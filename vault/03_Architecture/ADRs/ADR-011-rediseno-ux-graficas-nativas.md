---
id: ADR-011
title: "ADR-011 — Rediseño UX/UI narrativo con gráficas nativas como experiencia principal"
owner: "Edgar Edmundo Coronel Navarrete"
status: accepted
traces_up: ["DEC-023", "US-621", "US-641", "REQ-002", "vault/01_Product/PRD"]
traces_down: ["vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO", "US-651"]
supersedes: ["ADR-002 (sólo la obligación de embeber Superset como experiencia principal)"]
tags: [architecture, adr, frontend, ux, storytelling, dataviz, s7]
date: "2026-09-10"
---

# ADR-011 — Rediseño UX/UI narrativo con gráficas nativas como experiencia principal

## Contexto

La evaluación del 9-sep no aceptó satisfactoriamente el frontend, las gráficas de Superset ni la
ausencia de storytelling. Conservar la experiencia anterior como restricción obligaría al Equipo 3
a decorar el mismo recorrido rechazado y mantendría dos direcciones incompatibles para UX.

## Decisión

1. La propuesta del PR #297 y
   [[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] definen la dirección de diseño de S7.
2. FARO Web tendrá una experiencia narrativa propia y gráficas nativas consumiendo API/Gold. Los
   tableros de Superset permanecen disponibles como evidencia analítica y respaldo, pero dejan de
   ser la navegación principal obligatoria.
3. Se autoriza rediseñar identidad, pantallas, navegación, componentes y visualizaciones desde cero.
   Un cambio total de framework sólo se acepta si conserva despliegue, autenticación, pruebas y plazo.
4. Siguen siendo no negociables: PRD, contratos de datos/API, OAuth2/JWT y RBAC, WCAG 2.1 AA,
   `SIN_DATO`, filtros de ciclo/entidad/nivel, no causalidad, pruebas y trazabilidad por PR.
5. No se inventarán `prioridad`, bandas, métricas o endpoints. Una dependencia aún no integrada se
   representa explícitamente y continúa en el plan de cierre; no se elimina del alcance.

## Consecuencias

- El frontend puede responder directamente a la evaluación del profesor y Superset deja de imponer
  sus límites visuales al recorrido principal.
- El Equipo 5 asume mayor implementación antes del domingo y QA debe validar narrativa,
  accesibilidad, datos y regresión funcional.
- Se conservan API, autenticación, servicios desplegados y Superset como plan de respaldo.

## Peticiones del PR #297

| Petición | Resolución |
|---|---|
| P-04 | Resuelta: gráficas nativas y narrativa propia son la experiencia principal |
| P-06 | Resuelta por el PO: el paquete `FARO_Storytelling_UX` gobierna el diseño de S7 |
| P-01 | Abierta: no mostrar `prioridad` hasta que contrato y corte sean coherentes |
| P-02 | Abierta: usar valor numérico sin banda hasta registrar su definición |
| P-03 | Abierta: mantener “chat FARO” hasta decidir un nombre sin ambigüedad |
| P-05 | Abierta: Equipo 5 debe confirmar `escuelas_en_riesgo` en la API |

## Validación requerida

`US-651` debe demostrar sobre la URL candidata: recorrido completo, datos correctos, narrativa
comprensible sin explicación oral, accesibilidad, autenticación, chat, ML y estados explícitos.
