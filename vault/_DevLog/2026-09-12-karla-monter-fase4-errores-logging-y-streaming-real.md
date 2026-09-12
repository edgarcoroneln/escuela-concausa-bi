---
project: "FARO"
date: "2026-09-12"
author_human: "Karla Alejandra Monter Benitez"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1h"
touches: ["US-305", "REQ-006"]
tags: [devlog, agent, api, chat, streaming, logging, fase4]
---

# DevLog — 2026-09-12 (2) — Fase 4 (errores distinguibles + logging) y corrección: streaming real

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

- Al pedirme Fase 4 del plan (`DOC-DIAGNOSTICO-AGENTE-CHAT-2026-09-09`: "Distinguir mensajes de
  error... | Karla" y "Logging estructurado... | Karla + Alejandro"), **antes de escribir código
  encontré que la sesión anterior (misma tarde) había dejado el streaming a medias**: existe un
  pipeline real de streaming token a token (`procesar_consulta_stream`,
  `redactar_respuesta_stream_con_llm`) ya mergeado en `main` (parte de `5d26e01`, de Andrés), pero
  mi endpoint `/agente/consulta/stream` de la sesión anterior no lo usaba -- troceaba la respuesta
  ya completa en fragmentos fijos de 80 caracteres, ignorando la infraestructura real que ya
  existía. Corregido en esta misma sesión, antes de seguir con Fase 4.
- **`src/api/v1/agente.py`**: agregado `get_redactar_respuesta_stream` (proveedor inyectable, sin
  configurar por defecto, mismo patrón que los otros tres); `_resolver_consulta_stream` (paralelo a
  `_resolver_consulta`, llama a `procesar_consulta_stream`); `consulta_stream` reescrito para usar
  el pipeline real en vez de `_fragmentar` sobre un string ya resuelto. `_generar_eventos_sse` ahora
  distingue dos orígenes: fragmentos reales del redactor (se reenvían tal cual, sin re-trocear) vs.
  un mensaje fijo (rechazo de guardarraíl/degradación), que sí se trocea con `_fragmentar` solo para
  mantener la cadencia incremental.
- **`src/api/app.py`**: cablea `get_redactar_respuesta_stream` → `redactar_respuesta_stream_con_llm`
  cuando hay `ANTHROPIC_API_KEY`, igual que las otras dos dependencias del LLM.
- **Fase 4 -- mensajes de error distinguibles (`src/agente/servicio.py`):** la etapa final de
  redacción (`redactar_respuesta(...)` / `redactar_respuesta_stream(...)`) **no tenía ningún
  try/except** -- cualquier fallo ahí (LLM caído, timeout) se colaba sin degradar hasta el
  catch-all genérico de `agente.py`, indistinguible de un "no configurado". Se agregó manejo
  específico: mensaje propio (`MSG_ERROR_REDACCION`, invita a reintentar) en vez del genérico
  "no disponible en este entorno". En streaming, si el redactor falla **antes** de ceder cualquier
  fragmento, se cede ese mensaje como único fragmento (nunca deja el stream vacío, lo exige el
  cliente ya mergeado); si falla **a medias** (ya había texto real), el stream simplemente se
  detiene ahí -- se conserva la respuesta parcial en vez de pegarle un mensaje de error a media
  oración.
- **Fase 4 -- logging estructurado (`src/agente/servicio.py` + `src/api/v1/agente.py`):** logger
  por módulo (`faro.agente.servicio`, `faro.api.agente`). Se registra: rechazo de guardarraíl por
  intención de escritura, rechazo semántico fuera de alcance, RAG no disponible, SQL rechazado
  (`motivo` ya curado, nunca el SQL crudo del LLM), reintentos de auto-corrección agotados, fallo
  del redactor (sync y streaming), y el catch-all de última línea en `agente.py`. Nunca se registra
  la pregunta cruda del usuario. El *sink* real (Cloud Logging) es de Alejandro; aquí solo se
  emite con `logging` estándar.
- Regenerado `api/openapi.v1.json`, actualizado §3.5 de `API_Specification.md` para reflejar el
  streaming real (ya no dice "`procesar_consulta` no es un generador", que dejó de ser cierto).

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-sonnet-5
- **Archivos creados/modificados:**
  - `src/api/v1/agente.py`
  - `src/agente/servicio.py` (autorizado por el propio plan de Andrés, que asigna este archivo a
    Karla para el ítem de logging -- coordinación ya documentada, no un `git blame` a ciegas)
  - `src/api/app.py`
  - `tests/test_agente_endpoint.py`
  - `tests/test_agente_servicio.py`
  - `api/openapi.v1.json`
  - `vault/03_Architecture/API_Specification.md`
- **Decisiones autónomas del agente:**
  - Corregir primero el hallazgo del streaming simulado antes de construir Fase 4 encima de un
    diseño que ya sabía que estaba mal (Fase 4 afecta directamente cómo se manejan los errores del
    redactor, que es justo la pieza que cambió).
  - No inventar una distinción "timeout" vs. "LLM caído" que el código no puede sostener: ambas
    colapsan en `ErrorLLM` (`src/agente/llm.py`) sin subtipo propio, así que se optó por una
    distinción honesta de 2 vías -- "no configurado" (ya existía) vs. "falló en tiempo de
    ejecución, reintenta" (nueva) -- en vez de fabricar precisión que no existe en la capa de LLM.
  - En streaming, degradar con el mensaje de respaldo SOLO si no se emitió nada aún; con contenido
    parcial ya real, dejar que el stream simplemente termine (mejor UX que pegar un error a media
    oración).
- **Correcciones manuales:** ninguna todavía — pendiente de tu revisión línea por línea.
- **Prompt inicial:** "Fase 4 del plan... hagamos eso de una vez", tras compartir el documento
  completo del plan de fases (`DOC-DIAGNOSTICO-AGENTE-CHAT-2026-09-09`).

## Seguridad / calidad

- [x] Sin secretos hardcodeados; el logging nunca incluye la pregunta cruda ni SQL sin curar
- [x] Tests agregados/actualizados: 6 nuevos en `tests/test_agente_servicio.py` (fallos de
  redacción sync/stream, parcial vs. total, logging) + reescritura de la sección de streaming en
  `tests/test_agente_endpoint.py` para usar el redactor real en vez del síncrono
- [x] Suite completa: `pytest tests/ -q` → **1220 passed, 4 skipped**
- [x] `ruff check .` limpio (incluye una limpieza de deuda preexistente en `servicio.py`: 4
  `noqa: BLE001` que quedaron sin uso al dejar de ser "except ciego" -- ahora registran; y 5
  hallazgos `G201` nuevos, `.error(..., exc_info=True)` → `.exception(...)`) · `vault_lint.py` limpio
- [x] DevLog enlaza a los IDs afectados

## Próximos pasos

- Actualizar el `_index.md` de `vault/_DevLog/` y la fila de `Traceability_Matrix.md`.
- Avisar a Andrés que `/agente/consulta/stream` ya usa su pipeline real de streaming (antes lo
  ignoraba); y a Alejandro que el logging estructurado está listo del lado de código para que
  cablee el *sink* de Cloud Logging.
- Push de `dev/karla-monter` (pendiente de confirmación aparte).
