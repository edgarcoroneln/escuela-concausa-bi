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
- La prueba del cliente ahora usa un fake con `__enter__`/`__exit__` y recibe un callable `stream`, de modo que la prueba reproduce la forma real de consumo.
- Se conserva el contrato de eventos del backend: `meta`, uno o más `fragmento` y `fin`; los fragmentos se envían al callback para render incremental y se concatenan para el historial.

## Archivos modificados
- `src/frontend/agente_client.py`
- `tests/test_frontend_agente_client.py`

## Seguridad / calidad
- [x] No se agregaron secretos ni permisos nuevos.
- [x] La petición conserva el Bearer opcional y el límite de 3–500 caracteres.
- [x] Diagnósticos estáticos de los dos archivos: sin errores.
- [x] `pytest tests/test_frontend_agente_client.py -q` → 12 passed.
- [x] `pytest tests/test_agente_endpoint.py -q` → 11 passed.
- [x] `pytest tests/test_agente_servicio.py -q` → 19 passed.

## Estado real
El defecto de integración identificado queda corregido en código y la prueba ahora detectaría el uso incorrecto de `httpx.post`. Las 42 pruebas enfocadas de cliente, endpoint y servicio están verdes; la Fase 3 queda cerrada en código y pruebas locales. La validación contra la API candidata queda como paso de despliegue, no como bloqueo de esta implementación.

## Próximo paso
Coordinar el redeploy de la candidata y hacer el smoke test visual del widget; la implementación y las pruebas locales de la Fase 3 están terminadas.
