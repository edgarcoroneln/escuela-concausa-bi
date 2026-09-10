---
id: ADR-012
title: "ADR-012 — Retiro del embebido de Superset/Streamlit: frontend nativo en React"
owner: "Diana Álvarez / Luis Téllez (Equipo 5: Frontend y despliegue)"
status: proposed
traces_up: ["REQ-002", "REQ-004", "REQ-006", "REQ-005", "ADR-011-rediseno-ux-graficas-nativas"]
supersedes: ["ADR-002"]
traces_down: ["US-206", "US-207", "US-305", "US-405"]
date: "2026-09-10"
tags: [architecture, adr, frontend, react, streamlit, equipo-5]
---

# ADR-012 — Retiro del embebido de Superset/Streamlit: frontend nativo en React

→ [[vault/03_Architecture/ADRs/_index|Volver a ADRs]] · [[vault/03_Architecture/ADRs/ADR-002-frontend-streamlit|ADR-002]] ·
[[vault/03_Architecture/ADRs/ADR-011-rediseno-ux-graficas-nativas|ADR-011]] ·
[[vault/08_CICD_DevOps/Arquitectura_Frontend_React|Arquitectura_Frontend_React]]

> Este ADR opera bajo `ADR-011` (Edgar, `accepted`, 10-sep): ese ADR autoriza el rediseño narrativo
> con gráficas nativas como experiencia principal a nivel de producto; éste cubre la decisión técnica
> específica de E5 (retirar el embebido de Streamlit/Superset, stack React) y su implementación. No
> hay conflicto entre los dos `supersedes: ADR-002` — el de Edgar es parcial (solo la obligación de
> embeber Superset como principal), el de este ADR es sobre la herramienta que reemplaza esa capa.

## Contexto

`ADR-002` (aceptado, 7-ago) definió el frontend del proyecto como **FARO Web**, una app Streamlit que
embebe los 10 dashboards de Superset por guest token, hospeda el panel de ML interactivo (US-207) y el
widget de chat del agente (US-305). `US-206` ("Construir FARO Web: shell, navegación y embebido de los
10 dashboards") se cerró sobre esa base.

Tras la demo en vivo del 9-sep, el Dr. pidió explícitamente **retirar todo lo que se vea como
Superset o Streamlit** y rehacer el frontend 100% custom, con estética propia y gráficas nativas
(D3.js donde aporte control real, además de una librería de charts estándar para el resto del
catálogo). El equipo de UX/UI (Equipo 3, liderado por Marina) ya está construyendo el nuevo
storytelling de 7 pantallas ("7 casos por investigar") sobre esa premisa — su plan de trabajo
(`vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO.md`) asume que este ADR existe, porque sin él
no pueden implementar su diseño sin contradecir `US-206`, que sigue cerrada tal como está redactada.

## Decisión

Se retira el embebido de Superset/Streamlit como interfaz del producto. `FARO Web` deja de ser una
app Streamlit; el frontend pasa a ser una **SPA en React 18 + Vite**, servida como estático (nginx)
en Cloud Run, que consume el API real (`api/openapi.v1.json`) directamente desde el navegador.

- Gráficas estándar del catálogo: **Recharts**.
- Pieza flagship (gauge de riesgo) y mapa de México: **D3.js** de forma dirigida — el punto explícito
  del Dr., no una reescritura completa a D3 puro (ver evaluación comparativa abajo).
- Panel de ML interactivo (US-207) y widget de chat (US-305) se reconstruyen como componentes React
  dentro de esta misma SPA, en vez de vivir dentro de la sesión de Streamlit.
- Superset **no se retira como motor de cubos/BI interno** — sigue siendo válido para consumo interno
  del equipo si se necesita; lo que se retira es su exposición embebida al usuario final.

Detalle de estructura, rutas y deploy: [[vault/08_CICD_DevOps/Arquitectura_Frontend_React]].

## Alternativas consideradas

Antes de comprometer el stack, Equipo 5 construyó y corrió (no solo comparó en el papel) 5
combinaciones candidatas: la misma gráfica de matrícula 3 veces (Recharts / D3 a mano / Observable
Plot) y el mismo mapa de México 2 veces (D3-geo a mano / react-simple-maps), más un quinto candidato
completo (Angular + ngx-charts + D3) montado desde cero.

| Opción | Pros | Contras |
|---|---|---|
| **React + Recharts + D3 dirigido (elegida)** | Ya en producción; menor fricción en la prueba real; D3 visible donde el Dr. lo pidió (gauge, mapa) | Recharts no es D3 "puro" para el resto del catálogo |
| React + D3 100% a mano | El D3 más "puro" posible | El doble de código por gráfica (74 vs 37 líneas para el mismo resultado); replicarlo en ~9 piezas no cabe en el timeline al sábado |
| React + Observable Plot + D3 | Código más corto que Recharts | Sigue siendo una librería de charts encima de D3, no D3 puro — no le suma nada distinto al Dr. |
| React + react-simple-maps + D3 | Menos código para el mapa | Trajo 4 dependencias nuevas que rompieron el build 3 veces en la prueba real (`prop-types`, `react-is`, imports fallidos) |
| Angular + ngx-charts + D3 | — | Proyecto completo aparte (`ng new`, CLI fuera del PATH, librería aún no standalone); duplica infraestructura de build/deploy sin ganancia visual |
| Mantener Streamlit + Superset embebido (ADR-002 vigente) | Cero retrabajo | Contradice directamente el pedido del Dr. post-demo |

## Consecuencias

**Positivas.** El frontend queda desacoplado del backend en release (SPA estática vs. servicio con
estado); el D3 que pidió el Dr. es visible y defendible en el gauge de riesgo y el mapa; Cloud Run del
frontend es más liviano (256Mi/1 CPU, sin Secret Manager ni VPC connector). El storytelling de UX/UI
(Equipo 3) puede construir sin restricción de layout impuesta por Superset.

**Negativas / costos.** US-207 (panel de ML) y US-305 (widget de chat) se reconstruyen como React en
vez de reutilizar lo ya hecho en Streamlit — trabajo no trivial contra el mismo deadline del sábado.

**Auth — decisión cerrada 10-sep (Luis Téllez + Christian Ruiz, gate E5).** Se descarta la primera
propuesta de este ADR (Bearer en navegador tras canjear el código de `ADR-010`): expone el token a
JS y baja CIS v8 Control 16 de ~9 a ~7. También se descarta BFF (servicio nuevo, destino de deploy
nuevo). **Se adopta cookie `httpOnly` de un solo origen:**

1. `nginx` del frontend hace `proxy_pass` de `/api/*` hacia la API — el navegador ve un solo origen,
   el propio de `faro-frontend`.
2. `POST /auth/exchange` responde con `Set-Cookie` **sin** atributo `Domain` — al llegar a través del
   proxy, el navegador la guarda host-only para el origen del frontend (no choca con `BUG-059`: ahí
   el problema era una cookie compartida entre subdominios bajo `.run.app`, que sí está en la Public
   Suffix List; aquí es host-only de un solo origen).
3. `deps.py` (C4) gana un fallback: sin header `Authorization`, lee el token de la cookie. Bearer
   sigue vivo para clientes no-navegador y pruebas.
4. El frontend **no maneja tokens en absoluto** — ni los guarda, ni los refresca, ni los adjunta.
   Solo llama a `/api/...` con `credentials: "same-origin"`.

`ADR-010` (código de un solo uso) se conserva intacto — sigue siendo el mecanismo de canje, solo
cambia qué hace el navegador con la respuesta. Riesgo residual: CSRF vía cookie, mitigado con
`SameSite=Lax` (bloquea POST cross-site; los POST del sistema son `/agente/consulta`, `/auth/*`,
`/admin/*`) — documentado en `Threat_Model` como residual, no como resuelto (dueño: Christian).

**CORS deja de ser un bloqueante de deploy.** Con `/api/*` servido por el mismo origen vía proxy, el
navegador nunca cruza orígenes — el punto que este ADR marcaba como "bloqueante real, no resuelto"
queda resuelto por diseño, no por configuración de CORS en la API. Ver
[[vault/08_CICD_DevOps/Arquitectura_Frontend_React]] §7-8 (a actualizar).

## Trazabilidad

- Requisitos: REQ-002, REQ-004, REQ-006 (mismos que ADR-002) + REQ-005 (frontend/deploy)
- Historias impactadas: US-206 (cerrada bajo la premisa vieja — su implementación real ahora vive en
  React, no en el embebido de Streamlit), US-207, US-305, US-405 (bridge OAuth — mecanismo final:
  cookie `httpOnly` de un solo origen vía proxy, ratificado 10-sep con Christian)
- Supersede: [[vault/03_Architecture/ADRs/ADR-002-frontend-streamlit|ADR-002]]
- Diseño: [[vault/08_CICD_DevOps/Arquitectura_Frontend_React]]
- UX: `vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO.md` (Equipo 3, Marina) — su plan asume
  este ADR como contexto oficial una vez ratificado

> Pendiente de ratificación del PO (Edgar Coronel) — mientras `status: proposed`, Equipo 5 construye
> bajo la premisa de que el pedido del Dr. es la instrucción vigente, pero la ratificación formal
> queda pendiente como con cualquier otro ADR de este vault (mismo proceso que ADR-010).
