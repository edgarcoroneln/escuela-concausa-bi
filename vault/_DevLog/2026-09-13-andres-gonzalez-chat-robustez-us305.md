---
id: DEVLOG-2026-09-13-ANDRES-GONZALEZ-CHAT-ROBUSTEZ-US305
title: "Robustez del chat FARO y demo local"
owner: "Andrés González Habib"
status: active
traces_up: ["US-304a", "US-304b", "US-305", "US-611", "REQ-006"]
traces_down: ["tests/test_agente_servicio.py", "tests/test_frontend_chat_streamlit.py"]
tags: [devlog, agente, rag, chat, frontend, demo-local]
project: "FARO"
date: "2026-09-13"
author_human: "Andrés González Habib"
agent: "Claude Code"
model: "claude-sonnet-5"
touches: ["US-304a", "US-304b", "US-305", "US-611", "REQ-006"]
---

# DevLog — 2026-09-13 — Robustez del chat FARO

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué hizo Andrés (PR #351, `dev/andres-gonzalez`)

- Carga perezosa de `chromadb`/`sentence-transformers` (antes se importaban al cargar el módulo;
  ahora solo cuando se necesitan), para que el proceso no falle al arrancar si no están instalados.
- `AGENTE_RAG_STATIC=true`: modo de recuperación sin ChromaDB, sirve el catálogo Gold estático
  directo desde `ESQUEMA_GOLD`, para poder correr el chat en local sin levantar embeddings.
- Se ocultó el SQL generado en la UI de Streamlit (se sigue devolviendo en el contrato de la API).
- `FARO_API_TIMEOUT_S` configurable (antes hardcodeado a 15s en el cliente HTTP).
- Se agregó respuesta explícita de fuera-de-alcance geográfico para preguntas sobre entidades
  fuera de `SCOPE_ENTIDADES` (Oaxaca, Chiapas, Puebla, Yucatán).

## Correcciones aplicadas por Edgar Coronel (PM/QA), 2026-09-13 — Andrés no disponible, corregido
sobre la misma rama `dev/andres-gonzalez` para no bloquear el arranque del despliegue de Luis Téllez

Revisión completa en el comentario del PR #351 (2026-09-13). Los tres hallazgos con impacto en
comportamiento del chat, corregidos en este mismo PR:

1. **`_preparacion_sin_sql` dejó de usar el contexto RAG recuperado.** La versión de Andrés
   reemplazó el paso directo del contexto al redactor (`contexto_faro`, el diseño original de la
   Fase 1) por una lista de 5 frases escritas a mano; cualquier otra pregunta conceptual —
   verificado con "¿Qué mide el driver D3?", "¿Cómo se calcula el índice de riesgo?", "¿Qué es el
   D1?"— caía en un mensaje genérico aunque el RAG sí traía la respuesta. Se restauró el paso de
   `contexto_faro` como comportamiento por defecto, conservando la única adición nueva que sí vale
   la pena (la lista de entidades fuera de alcance, ahora con Guerrero agregado — el propio Edgar
   lo señaló como faltante). La prueba que Andrés había reescrito para validar el mensaje fijo
   (`test_stream_respuesta_directa_sin_sql_transmite_desde_contexto_faro`) se devolvió a su
   aserción original. Prueba nueva: `test_pregunta_conceptual_sin_frase_fija_tambien_usa_el_contexto_rag`.
2. **`MAX_FILAS_REDACTOR` recortaba a 10 filas sin decirle al redactor cuántas había en total.**
   Con 237 filas reales, el redactor solo veía 10 y podía responder "hay 10 escuelas". Se agrega
   una fila de metadato `_muestra_de_total` cuando se recorta, y se actualizó el prompt del
   redactor (`src/agente/llm.py`, versión síncrona y streaming) para que la use en vez de asumir
   que la muestra es el total. Prueba nueva: `test_redactor_recibe_el_total_real_cuando_la_muestra_se_recorta`.
3. **`FARO_LOCAL_PUBLIC` se retiró del PR**, no se corrigió. Bypaseaba el login por completo en
   `current_user()` (`src/frontend/auth.py`) sin restricción de host, sin aviso visible de demo y
   sin declararse en la sección de Seguridad del PR — cambio de autenticación (regla 7). Se quitó
   de `auth.py`, `agente_client.py` (forzaba además el cliente síncrono en vez de streaming) y
   `3_Chat.py`, volviendo esos tres archivos al comportamiento de `main` salvo por lo que sí es de
   Andrés (timeout configurable, SQL oculto en la UI). Si se quiere una demo local sin login real,
   debe proponerse por separado con las cuatro condiciones que se le pidieron: acotada a localhost,
   aviso visible, declarada en Seguridad y documentada.

No se tocó `indexar_esquema.py`, `recuperacion.py` (carga perezosa, `AGENTE_RAG_STATIC`) ni el
resto de `agente_client.py`/`3_Chat.py` (timeout, SQL oculto): esos cambios de Andrés son correctos
y no estaban en los cuatro puntos de la revisión.

## Descripción y Definition of Filed del PR — correcciones

- `US-305` no estaba "cerrada por completo": la Traceability_Matrix la traía como 🟡 en progreso;
  se corrige a avance parcial.
- `BUG-048` (Gold empobrecido en producción) no aplica a este PR; se quita la referencia.
- El DevLog original decía que pytest no se había corrido por falta del módulo, mientras la
  descripción del PR afirmaba "14 passed" — contradicción sin resolver. Corrido ahora de verdad:
  ver Validación.
- La descripción del PR estaba envuelta en un bloque ` ```md `, se veía como código en GitHub; se
  quita el bloque.

## Validación

```
pytest tests/ -q
1248 passed, 10 skipped, 10 warnings

ruff check src/ tests/
All checks passed!
```

## Pendiente, no de este PR

- Fixture local `fixture_gold_chat_andres 1/` (mencionado en el DevLog original de Andrés):
  confirmado que no viaja en el PR, sigue fuera hasta que Andrés pida aprobación de alcance/datos.
- Alinear el comportamiento de "SQL oculto en Streamlit" con React, que sí lo muestra a petición —
  señalado como sugerencia no bloqueante en la revisión; queda para Andrés o quien tome `US-305`.
