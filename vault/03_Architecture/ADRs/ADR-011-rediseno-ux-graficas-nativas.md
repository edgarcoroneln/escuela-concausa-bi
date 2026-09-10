---
id: ADR-011
title: "ADR-011 — Rediseño UX/UI narrativo con gráficas nativas como experiencia principal"
owner: "Edgar Edmundo Coronel Navarrete"
status: accepted
traces_up: ["DEC-023", "DEC-024", "US-621", "US-641", "REQ-002", "vault/01_Product/PRD"]
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
5. El frontend deriva un **nivel de atención de presentación** desde el `indice_riesgo` ya
   contratado: **alta `>= 0.50`**, **media `>= 0.30 y < 0.50`**, **baja `< 0.30`**. Reutiliza
   `LINEA_DE_ALERTA` (`DEC-019`) y `RIESGO_ESTABLE`; no consume ni reinterpreta la columna Gold
   `prioridad` mientras siga calculada con el ancla histórica `0.60`.
6. El nombre de producto del chat es **Asistente FARO**. No se usa “Watson”.
7. Los equipos construyen y prueban en paralelo contra contratos versionados. La ausencia temporal
   de una implementación se representa con fixture contractual o `SIN_DATO`, pero no detiene el
   diseño, las pruebas de componentes ni la integración continua de las demás superficies.

## Consecuencias

- El frontend puede responder directamente a la evaluación del profesor y Superset deja de imponer
  sus límites visuales al recorrido principal.
- Front, Chat, ML y QA trabajan en paralelo; QA incorpora pruebas desde el primer componente y no
  espera a que la aplicación completa esté ensamblada.
- Se conservan API, autenticación, servicios desplegados y Superset como plan de respaldo.
- Las únicas compuertas permanecen: rama personal, PR, CI, una aprobación humana y QA de la
  candidata. La coordinación entre equipos deja de ser una compuerta secuencial.

## Peticiones del PR #297

| Petición | Resolución |
|---|---|
| P-04 | Resuelta: gráficas nativas y narrativa propia son la experiencia principal |
| P-06 | Resuelta por el PO: el paquete `FARO_Storytelling_UX` gobierna el diseño de S7 |
| P-01 | Resuelta por `DEC-024`: mostrar **nivel de atención**, derivado de `indice_riesgo`; no consumir `gold.recomendaciones.prioridad` |
| P-02 | Resuelta: alta `>= 0.50`, media `>= 0.30 y < 0.50`, baja `< 0.30` |
| P-03 | Resuelta: nombre oficial **Asistente FARO** |
| P-05 | Resuelta a nivel de contrato/código: `KpisOut`, OpenAPI, repositorio Gold, mock y pruebas usan `escuelas_en_riesgo` con `LINEA_DE_ALERTA = 0.50`; la comprobación de cada despliegue pertenece al smoke continuo de QA, no bloquea construcción |

## Validación requerida

`US-651` debe demostrar sobre la URL candidata: recorrido completo, datos correctos, narrativa
comprensible sin explicación oral, accesibilidad, autenticación, chat, ML y estados explícitos.
