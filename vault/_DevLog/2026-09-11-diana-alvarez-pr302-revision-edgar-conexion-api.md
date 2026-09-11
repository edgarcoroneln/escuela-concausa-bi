---
project: "FARO"
date: "2026-09-11"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — pruebas manuales de PR #302 en navegador (bug real encontrado y corregido), conexión de tabs del expediente, y la ronda completa de cambios pedidos por Edgar en la revisión del PR antes de mergear."
touches: ["US-641", "REQ-002", "REQ-004", "REQ-005", "ADR-012", "BUG-064", "SEC-006"]
tags: [devlog, equipo-5, frontend, react, pr-302, ownership]
---

# DevLog — 2026-09-11 — PR #302: bug real en producción, tabs del expediente, y ronda de revisión de Edgar

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]] ·
[[vault/08_CICD_DevOps/PLAN_TRABAJO_E5|Plan de trabajo E5]] · [[vault/08_CICD_DevOps/Arquitectura_Frontend_React|Arquitectura Frontend React]]

## Contexto

`PR #302` (US-641, ADR-012) llegó a "All checks have passed" el 10-sep, bloqueado solo por revisión de
código-dueño. Esta sesión cubre dos cosas separadas: primero, pruebas manuales en navegador que
encontraron y cerraron un bug real; después, la ronda completa de cambios que Edgar pidió antes de
poder mergear.

## Parte 1 — Pruebas manuales y BUG-064

Al correr `npm run dev` y probar "Los 7 casos" en el navegador, la pantalla quedaba en blanco sin
ningún error visible. Diagnóstico: `getEscuelasEnRiesgo()` (`frontend/src/lib/api.js`) no desenvolvía
el sobre de paginación del endpoint de lista (`Page[EscuelaOut]`: `{items, total, page, size}`), así
que el resto del código recibía el objeto completo en vez del arreglo — `escuelas.length` de un objeto
es `undefined`. Corregido desenvolviendo `data.items` dentro de la misma función. Documentado en
`PLAN_TRABAJO_E5.md` y `Arquitectura_Frontend_React.md`, con evidencia agregada al cuerpo del PR.

Aprovechando la sesión de pruebas, se conectaron los tabs Drivers/Predicción/Recomendación del
expediente de escuela (antes "pendiente de conectar"), verificados en navegador con datos reales.

## Parte 2 — Revisión de Edgar sobre PR #302

Edgar pidió, antes de mergear: limpiar lo que no es producto (PoC de Angular, `comparativa-stacks`,
dependencias/assets sin uso), decidir pantalla por pantalla qué se conecta ya vs. qué espera al gap de
contrato, autohospedar Inter (el CSP de `nginx-unprivileged` bloquea Google Fonts en prod), corregir
comentarios desactualizados sobre `.env.production`, ratificar `ADR-012`, llenar la fila de evidencia
de `US-641` en `Traceability_Matrix.md`, limpiar del cuerpo del PR las notas ya resueltas sobre
`ownership.yml`, y pedir aprobación explícita de Luis (regla 7) sobre las rutas críticas que el PR
toca. Un punto adicional (botón de login) queda marcado explícitamente como **no bloqueante** para este
merge, crítico para el viernes.

**Limpieza ejecutada** (confirmada por Diana: "Sí, borra todo"): `frontend-angular-poc/` completo
(269M), `ComparativaStacks.jsx` + su ruta + `src/comparativa/`, assets sin referencias
(`icons.svg`, `react.svg`, `vite.svg`, `hero.png`), y 5 dependencias de `package.json`
(`react-simple-maps`, `@observablehq/plot`, `prop-types`, `react-is` — señaladas por Edgar —, más
`topojson-client`, confirmada sin uso tras eliminar `MapaSimpleMaps.jsx`). `npm ci` corre limpio sin
`--legacy-peer-deps` después de la limpieza (0 vulnerabilidades, 0 conflictos de peers) — la bandera
solo hacía falta por esas 4 dependencias.

**Decisión pantalla por pantalla** (confirmada por Diana: "EnConstruccion en las 4 + conectar Vista
general"): `MapaCasos`, `MatrizDrivers`, `ComparacionTerritorial` y `Comparativa` muestran
`EnConstruccion` con la nota del gap puntual de cada una (lat/lon y nombre de municipio/entidad
ausentes del contrato; sin endpoint de lote para `d1..d6`; sin serie histórica de matrícula) en vez de
mock sin rotular. `VistaGeneral` se conectó parcialmente: el bloque "El diferenciador" ya llama al API
real para el par `15DPR0920D`/`15DPR2254O` — confirmado en `Guion_Demo_US006.md` que es el mismo par
real que Marina García eligió el 6-sep sobre el Gold rematerializado, no un valor inventado para el
mockup.

**Inter autohospedado** vía `@fontsource/inter` (pendiente de que Diana corra `npm install
@fontsource/inter` en su entorno — no ejecutado en esta sesión, ver Bloqueantes).

**`ADR-012` ratificado**: `status: proposed` → `accepted`, a pedido explícito de Edgar en esta misma
revisión (mismo proceso que `ADR-010`/`ADR-011`). Se agregó también la nota de dónde debe arrancar el
botón de login (origen de la API, no el proxy del frontend — el detalle vive en el ADR).

**Hallazgo propio, no pedido por Edgar.** Al corregir el comentario de `.env.production` en
`docker/frontend-react.Dockerfile`, se encontró que `docker/.dockerignore` probablemente no se aplica:
el `docker build` real usa la raíz del repo como contexto (`.`), no `docker/`, y Docker busca el
`.dockerignore` en la raíz del contexto, no junto al Dockerfile. No se movió ni se duplicó — ambos
archivos están bajo el alcance crítico de Luis (`docker/**`) — se deja documentado para su revisión
junto con la aprobación de regla 7 que ya se le va a pedir.

## Excepción documentada al patrón de una rama por persona

El commit `62751e2` ("feat(deploy): nginx del front con proxy_pass mismo origen + headers CSP/X-Frame
(US-641)") aparece en `dev/diana-alvarez` con autoría de Luis Téllez Domínguez. Es intencional: es la
parte de Luis del gate de auth E5 (`PLAN_TRABAJO_E5` §2.2, `ADR-012`) — el proxy y los headers de
seguridad viven en el mismo Dockerfile/config que este PR ya estaba tocando, así que se coordinó
aplicarlo directo sobre esta rama en vez de abrir una rama aparte para un solo commit que de todos
modos iba a mergearse junto. Queda esta nota como el registro explícito de la excepción.

## Pruebas ejecutadas

```
Verificación manual en navegador (npm run dev, Diana):
  - "Los 7 casos": en blanco antes del fix de BUG-064 -> con datos reales después.
  - Expediente de escuela: tabs Drivers/Predicción/Recomendación con datos reales
    (ej. Ciclo 2024-2025, índice 0.52, driver Inseguridad, recomendación de seguridad pública).
  - docker build / docker run / curl -sI -> 200 OK (sesión previa, 10-sep).

No se corrió en este entorno (bash de edición, no el de Diana):
  - npm run dev / npm ci sin --legacy-peer-deps -> corrido y confirmado por Diana
    (0 vulnerabilidades, 0 conflictos de peers) tras la limpieza de dependencias.
  - npm install @fontsource/inter -> pendiente, ver Bloqueantes.
  - pytest tests/ -q -> sin cambios de Python en esta sesión, no se re-corrió.
```

## Bloqueantes

- `npm install @fontsource/inter` pendiente de que Diana lo corra en su entorno — los imports en
  `src/index.css` y el `<link>` retirado de `index.html` ya están, pero el paquete no está instalado
  todavía.
- Aprobación explícita de Luis Téllez (regla 7) sobre `docker/**` y `vault/08_CICD_DevOps/**`
  pendiente de solicitarse.

## Próximos pasos

Diana corre `npm install @fontsource/inter` y verifica visualmente la tipografía en su navegador;
limpia del cuerpo del PR #302 las notas ya resueltas sobre `ownership.yml`; pide a Luis su aprobación
de regla 7 (incluyendo el hallazgo de `docker/.dockerignore`); y una vez todo eso cerrado, re-solicita
revisión de Edgar y Luis sobre el PR actualizado.
