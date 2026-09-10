---
project: "FARO"
date: "2026-09-10"
author_human: "Karla Alejandra Monter Benitez"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1h"
touches: ["US-305", "REQ-004", "SEC-003"]
tags: [devlog, agent, api, chat, historial]
---

# DevLog — 2026-09-10 — historial de turnos en el contrato de /agente/consulta (Fase 2 del rediseño del chat)

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo
- Se recibió de Andrés el plan de rediseño del chat en 4 fases (post-cierre, autorizado por el PO
  pese a `DEC-021`). Fase 2 (memoria conversacional) es mi alcance: `src/api/**`.
- Antes de tocar código se verificó que la nota de Andrés ("el soporte interno ya existe, solo
  falta el campo en el contrato") ya no aplicaba tal cual: `US-305` (contexto estructurado
  `ccts`/`ciclo`/`filtros`/`resumen`) ya estaba en `main` desde el 27-28 de agosto, y su Fase 1
  (guardrail híbrido, auto-corrección, respuesta sin SQL) estaba commiteada en
  `dev/andres-gonzalez` sin PR abierto aún. Se sincronizó `dev/karla-monter` con `main`
  (324 commits de diferencia) antes de empezar.
- Se agregó `HistorialTurnoIn` (pregunta/respuesta) y el campo `historial` (opcional,
  retrocompatible, máx. 10 turnos) a `AgenteConsultaIn` en `src/api/schemas.py`, con el mismo
  criterio de entrada hostil que `ContextoConversacionalIn`: `extra="forbid"`, límites de tamaño
  por turno, y rechazo de caracteres de control (un salto de línea en un turno falsificaría el
  bloque de historial dentro del prompt).
- En `src/api/v1/agente.py` se agregó `_construir_contexto_conversacional`, que fusiona `contexto`
  e `historial` en el único `Mapping` que `procesar_consulta` ya acepta, bajo la clave
  `"historial"` — sin tocar `src/agente/**` (fuera de mi alcance; `construir_prompt_sistema`
  todavía no lee esa clave, queda coordinado con Andrés).
- Se regeneró `api/openapi.v1.json` (`scripts/export_openapi.py`) para reflejar el modelo nuevo.
- 20 pruebas nuevas en `tests/test_agente_historial.py` (contrato, límites, caracteres de control,
  fusión con `contexto`, retrocompatibilidad, no ablanda guardarraíles).

## 🤖 Sesión de IA
- **Agente / modelo:** Claude Code / claude-sonnet-5
- **Archivos creados/modificados:**
  - `src/api/schemas.py`
  - `src/api/v1/agente.py`
  - `api/openapi.v1.json`
  - `tests/test_agente_historial.py` (nuevo)
  - `.gitignore` (aparte, sin relación: ignora config local de herramientas de IA)
- **Decisiones autónomas del agente:**
  - No modificar `src/agente/**`: el historial viaja fusionado en `contexto_conversacional["historial"]`
    en vez de pedir una firma nueva a `procesar_consulta`, para respetar el alcance de Andrés.
  - Verificar contra el repo real (no contra la nota de handoff) el estado de `US-305` antes de
    diseñar, porque la nota describía un estado ya superado.
- **Correcciones manuales:** ninguna; Karla aprobó el diseño acotado y el alcance en el chat antes
  de implementar (confirmación explícita, no implícita).
- **Prompt inicial:** "estamos rediseñando el agente de chat, esta son las fases... a mí me toca la
  fase 2" + markdown de diagnóstico y plan compartido por Andrés (`DOC-DIAGNOSTICO-AGENTE-CHAT-2026-09-09`).

## Seguridad / calidad
- [x] Sin secretos hardcodeados
- [x] Tests agregados/actualizados (20 casos nuevos en `tests/test_agente_historial.py`)
- [x] DevLog enlaza a los IDs afectados

## Bloqueantes
- `construir_prompt_sistema` (`src/agente/prompt.py`, alcance de Andrés) todavía no lee la clave
  `"historial"` del `contexto_conversacional` — el campo llega validado a la API pero no tiene
  efecto end-to-end hasta que él lo consuma. Falta avisarle explícitamente.
- El PR de Andrés con su Fase 1 (`dev/andres-gonzalez`, commit `6c9ed2b`) sigue sin abrirse.

## Próximos pasos
- Avisar a Andrés que `historial` ya llega bajo `contexto_conversacional["historial"]`.
- Actualizar `vault/02_Requirements/Traceability_Matrix.md` y el `_index.md` correspondiente.
- Push de `dev/karla-monter` y apertura del PR (pendiente de confirmación aparte).
