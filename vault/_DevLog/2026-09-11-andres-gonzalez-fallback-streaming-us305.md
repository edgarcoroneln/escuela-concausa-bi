---
id: DEVLOG-2026-09-11-ANDRES-GONZALEZ-FALLBACK-STREAMING-US305
title: "Corrección de fallback y memoria conversacional de US-305"
owner: "Andrés González Habib"
status: active
traces_up: ["US-305", "US-611", "REQ-006"]
traces_down: ["TEST-FRONTEND-AGENTE-CLIENT", "RISK-STREAM-ENDPOINT"]
tags: [devlog, agent, frontend, chat, streaming, historial]
project: "FARO"
date: "2026-09-11"
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "GitHub Copilot"
session_duration: "20m"
touches: ["US-305", "US-611", "REQ-006"]
---

# DevLog — 2026-09-11 — Fallback de streaming y memoria de US-305

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

- Se corrigió `preparar_historial()` para recorrer todos los mensajes antes de devolver la lista.
- Se agregó una prueba con 12 conversaciones que confirma que se conservan únicamente los 10 turnos más recientes y se excluye la pregunta actual.
- `consultar_agente_stream()` conserva el camino SSE cuando existe y usa explícitamente `/api/v1/agente/consulta` ante una respuesta HTTP 404.
- El fallback síncrono reenvía el historial normalizado y conserva el Bearer, el contrato de respuesta y los errores de autorización.
- Se agregó una prueba que reproduce la ruta inexistente de streaming y verifica la respuesta síncrona.

## Archivos modificados

- `src/frontend/agente_client.py`
- `tests/test_frontend_agente_client.py`
- `vault/_DevLog/2026-09-11-andres-gonzalez-fallback-streaming-us305.md`
- `vault/_DevLog/_index.md`

## Validación

- `.venv\\Scripts\\python.exe -m pytest tests/test_frontend_agente_client.py -q` → 16 passed.
- `.venv\\Scripts\\python.exe -m pytest tests/test_frontend_agente_client.py tests/test_frontend_chat_streamlit.py -q` → 16 passed; la suite Streamlit se omitió porque la dependencia no está instalada.
- `python -m py_compile src/frontend/agente_client.py tests/test_frontend_agente_client.py` → correcto.
- Diagnósticos del editor en los dos archivos de código → sin errores.

## Revisión pendiente

`gh` no está disponible en el entorno, por lo que no se pudo publicar automáticamente la solicitud de revisión. Se debe pedir a Diana Alvarez aprobación explícita de los cambios en `src/frontend/**` antes del merge.

## Próximo paso

Solicitar la aprobación explícita de Diana y pedir al PM que agregue esta evidencia a la fila de `REQ-006`/`US-611` en `Traceability_Matrix.md`.
