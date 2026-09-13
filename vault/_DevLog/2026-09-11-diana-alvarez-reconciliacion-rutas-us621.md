---
project: "FARO"
date: "2026-09-11"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — confirmación de la reconciliación de rutas pendiente que dejó Oscar Quiroz en el handoff de 01_UX_Architecture.md (PR #319): comparación de main.jsx contra las 7 pantallas P0-P6 del documento final, hallazgo de desfase y plan de reconciliación."
touches: ["US-621", "REQ-002"]
tags: [devlog, equipo-5, frontend, react, ux, reconciliacion]
---

# DevLog — 2026-09-11 — Reconciliación de rutas contra `01_UX_Architecture.md` (US-621)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/04_UX_Design/FARO_Storytelling_UX/01_UX_Architecture|01_UX_Architecture]]

## Contexto

`01_UX_Architecture.md` de Oscar Quiroz (versión final, PR #319 ya mergeado) dejó como pendiente de
handoff formal: *"falta que Diana Alvarez (Equipo 5) confirme si ya reconcilió sus rutas construidas
contra las 7 pantallas de este documento"*. Se revisó `frontend/src/main.jsx` contra el mapa de
navegación del documento.

## Qué se encontró

**No está reconciliado.** El documento define exactamente 7 pantallas —
`Login(P0)→Entrada(P1)→Panorama(P2)→Selección(P3)→Expediente(P4)→Conclusión Top 3(P5)→Exploración(P6)`
— con **una sola** P6 ("Explorador de escuelas", en `/explorador`, con los 3 filtros obligatorios
ciclo/entidad/nivel, reutilizando las gráficas del expediente) y P4 en `/escuela/{cct}` (URL directa,
§1 del documento).

`main.jsx` tiene otra estructura: `/casos/:cct` en vez de `/escuela/{cct}`, y **cuatro** rutas
separadas donde el plan pide una sola — `/mapa` (`MapaCasos`), `/drivers` (`MatrizDrivers`),
`/comparacion-territorial` (`ComparacionTerritorial`) y `/comparativa` (`Comparativa`) — sin ningún
`/explorador`.

**No es un descuido: las 4 páginas ya estaban documentadas como bloqueadas** por el gap de contrato
del API (no existe un endpoint agregado equivalente al `/explorador` único que describe P6). La
estructura actual de rutas predata la versión final del documento de Oscar, construida cuando el plan
todavía no consolidaba estas vistas en una sola pantalla.

## Plan de reconciliación

1. **Sin dependencia de API, se puede hacer ya:** renombrar `/casos/:cct` → `/escuela/:cct` para que
   la URL directa coincida con la que especifica el documento.
2. **Con dependencia del gap de API (bloqueado):** consolidar `/mapa`, `/drivers`,
   `/comparacion-territorial` y `/comparativa` en una sola ruta `/explorador`, con los 3 filtros
   obligatorios y reutilizando las gráficas de `ExpedienteEscuela.jsx` como indica P6. No se puede
   completar hasta que exista el endpoint agregado que sostenga esa pantalla única.

## Bloqueantes

El mismo gap de contrato de API que ya bloqueaba estas 4 páginas por separado (documentado en
evidencia anterior de Fase 2). Consolidarlas en una no lo resuelve — sigue siendo trabajo de
quien tenga ese endpoint en su alcance.

## Próximos pasos

Ejecutar el paso 1 (renombrar `/casos/:cct` → `/escuela/:cct`) en cuanto se confirme; el paso 2 queda
declarado como deuda explícita hasta que se resuelva el gap de API.
