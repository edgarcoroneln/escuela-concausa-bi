---
id: ADR-011
title: "ADR-011 — Rediseño UX/UI narrativo con gráficas nativas como experiencia principal"
owner: "Edgar Edmundo Coronel Navarrete"
status: accepted
traces_up: ["DEC-023", "US-621", "US-641", "REQ-002", "vault/01_Product/PRD"]
traces_down: ["vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO", "vault/03_Architecture/Frontend_Architecture", "US-651"]
supersedes: ["ADR-002 (sólo la obligación de embeber Superset como experiencia principal)"]
tags: [architecture, adr, frontend, ux, storytelling, dataviz, s7]
date: "2026-09-10"
---

# ADR-011 — Rediseño UX/UI narrativo con gráficas nativas como experiencia principal

## Contexto

La evaluación del 9-sep no aceptó satisfactoriamente el frontend, las gráficas de Superset ni la
ausencia de storytelling. Conservar la experiencia anterior como restricción obligaría al Equipo 3
a decorar el mismo recorrido que fue rechazado y dejaría dos fuentes de verdad para UX.

La propuesta aprobada en el PR #297 define una historia problema → evidencia → hallazgo → acción,
una navegación nueva y visualizaciones diseñadas para esa historia. El Equipo 5 necesita autoridad
explícita para implementarla sin estar obligado a mantener los diez tableros embebidos como interfaz
principal.

## Decisión

1. `vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO.md` es el plan canónico de diseño para S7.
2. FARO Web tendrá una experiencia narrativa propia y gráficas nativas consumiendo la API/Gold. Los
   diez tableros de Superset permanecen disponibles como evidencia analítica y respaldo, pero dejan
   de ser la navegación principal obligatoria.
3. Se autoriza rediseñar identidad, pantallas, navegación, componentes y selección de gráficas desde
   cero. La implementación puede evolucionar la capa actual de `src/frontend/`; un cambio total de
   framework sólo se acepta si conserva el despliegue, autenticación, pruebas y plazo de S7.
4. Siguen siendo no negociables: PRD, contratos de datos/API, OAuth2/JWT y RBAC, WCAG 2.1 AA,
   `SIN_DATO` explícito, filtros de ciclo/entidad/nivel, no causalidad y trazabilidad por PR.
5. Ninguna pantalla inventará `prioridad`, bandas, métricas o endpoints. Cuando una dependencia no
   llegue, la experiencia degrada de forma explícita y QA registra la brecha.

## Consecuencias

- **Positivas:** el frontend puede responder directamente a la evaluación del profesor; storytelling
  y visualización se diseñan como una experiencia coherente; Superset ya no impone sus límites
  visuales al recorrido principal.
- **Costos/riesgos:** el Equipo 5 debe implementar y desplegar más interfaz antes del domingo; QA
  necesita validar narrativa, accesibilidad, datos y regresión funcional; se debe evitar duplicar
  lógica de negocio que ya vive en Gold/API.
- **Compatibilidad:** se conservan API, autenticación, seguridad y servicios desplegados. Superset no
  se elimina ni se desmantela durante S7; queda como superficie secundaria y plan de respaldo.

## Estado de las peticiones de PR #297

| Petición | Resolución |
|---|---|
| P-04 | Resuelta: gráficas nativas y narrativa propia son la experiencia principal; Superset queda secundario |
| P-06 | Resuelta: el paquete `FARO_Storytelling_UX` gobierna el diseño de S7 |
| P-01 | Abierta: no mostrar `prioridad` hasta que contrato y corte sean coherentes |
| P-02 | Abierta: usar valor numérico sin banda hasta registrar su definición |
| P-03 | Abierta: mantener “chat FARO” hasta decidir un nombre sin ambigüedad |
| P-05 | Abierta: Equipo 5 debe confirmar `escuelas_en_riesgo` en la API |

## Validación requerida

El cambio sólo se acepta como entregado cuando `US-651` demuestre sobre la URL candidata: recorrido
completo, datos correctos, narrativa comprensible sin explicación oral, accesibilidad, autenticación,
chat, ML y degradación explícita de dependencias faltantes.
