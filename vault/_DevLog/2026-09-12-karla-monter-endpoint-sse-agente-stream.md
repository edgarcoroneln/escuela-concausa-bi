---
project: "FARO"
date: "2026-09-12"
author_human: "Karla Alejandra Monter Benitez"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1h30m"
touches: ["US-305", "REQ-004", "REQ-006"]
tags: [devlog, agent, api, chat, streaming, sse]
---

# DevLog — 2026-09-12 — `/agente/consulta/stream` (SSE) implementado; cierra el hueco de PR #313

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo
- Andrés (líder E2, Chat IA) pidió implementar/validar `POST /agente/consulta/stream` en `src/api/**`
  (mi alcance): el frontend ya lo consume (`consultar_agente_stream`,
  `src/frontend/agente_client.py`, PR #313, mergeado) con *fallback* a `/agente/consulta` ante 404,
  pero la ruta no existía en el código.
- **Antes de escribir código se investigó por qué faltaba**, en vez de asumir que era trabajo nuevo:
  `api/openapi.v1.json` en `main` ya describía `/agente/consulta/stream` con el contrato completo
  (eventos `meta`/`fragmento`/`fin`), pero `src/api/v1/agente.py` en `main` no tenía la ruta. El
  commit `5d26e01` ("feat(agent): complete conversational chat phases") sí la implementaba en
  `dev/andres-gonzalez`, pero el PR #313 finalmente mergeado ("Fallback síncrono y memoria
  conversacional del chat") **no toca `src/api/v1/agente.py` ni `api/openapi.v1.json`** — el
  endpoint se perdió en algún punto de esa rama (probablemente un merge de `origin/main` que
  resolvió el conflicto tomando la versión sin streaming), dejando el contrato documentado sin
  implementación real. Confirmado con `git log`/`git diff` contra `origin/main`, no por suposición.
- Se sincronizó `dev/karla-monter` con `main` (182 commits de diferencia — no se había hecho antes
  de empezar, corregido a media sesión) para no reconstruir a ciegas contra una base vieja.
- Se implementó `POST /agente/consulta/stream` en `src/api/v1/agente.py`:
  - Extrae `_resolver_consulta()` de la lógica que ya tenía `/consulta` (con su mismo
    try/except de degradación segura, BUG-025) para que **ambos** endpoints compartan un único
    punto de guardarraíles — el streaming nunca es una segunda puerta con reglas propias.
  - `procesar_consulta` no es un generador (no hay *streaming* token a token desde el LLM): se
    resuelve la respuesta completa primero y se trocea en fragmentos de `TAM_FRAGMENTO_SSE=80`
    caracteres para el evento `fragmento`.
  - Autenticación (`Authorization: Bearer`) y el interruptor híbrido de lectura pública se heredan
    gratis: la ruta vive en el mismo `router` que `/consulta`, que ya trae `require_lectura` a nivel
    de `src/api/v1/__init__.py`.
- **Verificado contra el contrato real del cliente ya mergeado**, no contra uno inventado: se leyó
  `consultar_agente_stream()` completo y se alineó el formato exacto (`event: `/`data: ` con salto de
  línea simple, JSON por línea) y un caso de borde que el cliente exige y que `range()` no cubre por
  sí solo: **al menos un evento `fragmento` siempre**, incluso con texto vacío (`if not fragmentos:
  raise ValueError(...)` en el cliente).
- Se regeneró `api/openapi.v1.json` y se documentó §3.5 de `API_Specification.md`.

## 🤖 Sesión de IA
- **Agente / modelo:** Claude Code / claude-sonnet-5
- **Archivos creados/modificados:**
  - `src/api/v1/agente.py`
  - `tests/test_agente_endpoint.py`
  - `api/openapi.v1.json`
  - `vault/03_Architecture/API_Specification.md`
  - `vault/02_Requirements/Traceability_Matrix.md`
- **Decisiones autónomas del agente:**
  - Investigar la causa raíz (por qué la ruta faltaba) antes de implementar, en vez de asumir
    "trabajo nuevo" — cambió el diseño: se alineó al contrato que el cliente **ya** esperaba en vez
    de inventar uno propio.
  - Compartir `_resolver_consulta()` entre `/consulta` y `/consulta/stream` en vez de duplicar el
    try/except de degradación, para que sea estructuralmente imposible que diverjan los guardarraíles.
  - Agregar una prueba de integración real contra `consultar_agente_stream` (no solo mocks
    aislados de cada lado), para detectar en CI si el contrato cliente↔servidor vuelve a
    desincronizarse.
  - No usar el ID `US-414` en la documentación nueva (closed, tema distinto — OpenAPI docs): se usó
    `US-305`, el ID real que ya usa todo el ecosistema mergeado (frontend, servicio, guardrails).
- **Correcciones manuales:** ninguna todavía — pendiente de tu revisión línea por línea antes del push.
- **Prompt inicial:** solicitud de Andrés (vía chat) para implementar/validar el endpoint SSE con el
  contrato que el frontend ya espera (`pregunta`/`historial`/`Authorization: Bearer` → eventos
  `meta`/`fragmento`/`fin`, con `sql_generado`/`fuera_de_alcance` en `meta`).

## Seguridad / calidad
- [x] Sin secretos hardcodeados
- [x] Tests agregados/actualizados (10 casos nuevos de streaming + 1 de integración con el cliente
  real del frontend, en `tests/test_agente_endpoint.py`)
- [x] Suite completa: `pytest tests/ -q` → **1210 passed, 4 skipped**
- [x] `ruff check .` limpio · `vault_lint.py` limpio
- [x] DevLog enlaza a los IDs afectados

## Bloqueantes / hallazgos para avisar
- **`RISK-STREAM-ENDPOINT`** aparece en `traces_down` del DevLog de Andrés del 2026-09-11
  (`2026-09-11-andres-gonzalez-fallback-streaming-us305.md`) pero **nunca se registró** en
  `vault/10_Risk_Governance/Risk_Register.md` — ID referenciado y jamás dado de alta. Se registra
  en este mismo PR, ya cerrado por este trabajo.
- No hay una historia de usuario propia para "implementar `/agente/consulta/stream`" (no es
  `US-414`, que ya está cerrada y es un tema distinto — documentación OpenAPI). Se trazó contra
  `US-305`/`REQ-006`, que es lo que el resto del ecosistema (frontend, DevLogs) ya usa para este
  trabajo. El PM puede decidir si amerita un ID propio.
- Avisar a Andrés que el endpoint ya existe: puede quitar la nota de "streaming aún no existe" del
  docstring de `consultar_agente_stream` si lo considera pertinente (no se tocó `src/frontend/**`,
  fuera de mi alcance).

## Próximos pasos
- Actualizar el `_index.md` de `vault/_DevLog/`.
- Push de `dev/karla-monter` y apertura del PR (pendiente de confirmación aparte).
- Avisar a Andrés/Alejandro para validación end-to-end desde el cliente real; Luis puede encargarse
  del redeploy cuando el PR esté mergeado.
