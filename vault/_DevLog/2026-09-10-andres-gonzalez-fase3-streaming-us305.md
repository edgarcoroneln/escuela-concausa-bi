---
project: "FARO"
date: "2026-09-10"
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "claude-sonnet-5"
session_duration: "30m"
touches: ["US-305", "US-611", "REQ-006"]
tags: [devlog, agent, chat, streaming, sse]
---

# DevLog — 2026-09-10 — Corrección del transporte SSE de la Fase 3

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo
- Se verificó que el widget de Streamlit ya llamaba `consultar_agente_stream`, pero el cliente intentaba usar `httpx.post(..., stream=True)`.
- Se corrigió el cliente para usar `httpx.stream("POST", ...)` como context manager, que es el contrato real de HTTPX para respuestas SSE.
- El cliente SSE ahora acepta `historial` como turnos `{pregunta, respuesta}` y Streamlit construye los turnos completos anteriores antes de agregar la pregunta actual.
- El historial se limita a los últimos 10 turnos, normaliza caracteres no imprimibles y acota cada campo a 500 caracteres.
- La prueba del cliente ahora usa un fake con `__enter__`/`__exit__` y recibe un callable `stream`, de modo que la prueba reproduce la forma real de consumo.
- Se conserva el contrato de eventos del backend: `meta`, uno o más `fragmento` y `fin`; los fragmentos se envían al callback para render incremental y se concatenan para el historial.

## Archivos modificados
- `src/frontend/agente_client.py`
- `src/frontend/pages/3_Chat.py`
- `tests/test_frontend_agente_client.py`

## Seguridad / calidad
- [x] No se agregaron secretos ni permisos nuevos.
- [x] La petición conserva el Bearer opcional y el límite de 3–500 caracteres.
- [x] Diagnósticos estáticos de los dos archivos: sin errores.
- [x] `pytest tests/test_frontend_agente_client.py tests/test_frontend_chat_streamlit.py -q` → 16 passed.
- [x] Ruff sobre cliente, página y pruebas: limpio.

## Estado real
El frontend de la Fase 3 queda listo en código y pruebas locales. La historia no se declara cerrada end-to-end: falta que el dueño de API incorpore `/api/v1/agente/consulta/stream`, OpenAPI y la prueba real del endpoint. Sin esa ruta, el cliente recibiría 404 aunque el frontend esté preparado.

## Próximo paso
Coordinar con Juan Macías o Christian Ruiz el PR de API; después sincronizar esta rama con `origin/main`, ejecutar la integración real y hacer el smoke test visual.
