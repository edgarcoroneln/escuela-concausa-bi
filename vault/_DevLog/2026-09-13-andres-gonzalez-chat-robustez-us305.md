---
id: DEVLOG-2026-09-13-ANDRES-GONZALEZ-CHAT-ROBUSTEZ-US305
title: "Robustez del chat FARO y demo local"
owner: "Andrés González Habib"
status: active
traces_up: ["US-304a", "US-304b", "US-305", "US-611", "REQ-006"]
traces_down: ["TEST-AGENTE-GOLDEN", "TEST-FRONTEND-AGENTE-CLIENT"]
tags: [devlog, agente, rag, chat, frontend, demo-local]
project: "FARO"
date: "2026-09-13"
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "GitHub Copilot"
touches: ["US-304a", "US-304b", "US-305", "US-611", "REQ-006"]
---

# DevLog — 2026-09-13 — Robustez del chat FARO

## Qué se hizo

- Se corrigió la carga perezosa de Chroma y `sentence-transformers` para que la API no se bloquee al arrancar.
- Se reforzó el prompt y el flujo conversacional: las comparaciones y seguimientos consultan Gold; las preguntas conceptuales y fuera de alcance no exponen contexto RAG interno.
- Se ocultó el SQL generado en el frontend, conservándolo sólo en el contrato interno de la API.
- Se amplió el arranque local con el fixture Gold read-only y vistas locales para predicciones, features y recomendaciones.
- Se agregó soporte para preguntas conceptuales, cobertura geográfica, seguimiento D1/D2 y respuestas naturales de Anthropic con degradación sobre filas reales.
- Se corrigieron timeouts del cliente y se dejó la demo local con usuario público opt-in.

## Validación

- `py_compile` de los archivos modificados: correcto.
- Pruebas pytest enfocadas: no ejecutadas porque el intérprete `.venv` no tiene instalado `pytest` (`No module named pytest`).
- Smoke tests manuales: health API 200; matrícula, cobertura por entidad, Nuevo León, D1/D2, seguimiento conversacional y Oaxaca fuera de alcance respondieron con datos Gold.

## Riesgos y pendientes

- El fixture local `fixture_gold_chat_andres 1/` permanece fuera del PR hasta obtener aprobación explícita de alcance y datos.
- Instalar dependencias de desarrollo y repetir pytest antes de abrir el PR.
- Actualizar la matriz de trazabilidad con la evidencia final.

## Próximo paso

Sincronizar la rama con `origin/main`, instalar/validar la suite, hacer commit y abrir el PR desde `dev/andres-gonzalez`.
