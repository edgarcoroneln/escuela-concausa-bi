---
project: "FARO"
date: "2026-09-10"
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "Claude Sonnet 5"
session_duration: "3h"
touches: ["US-304", "US-304a", "US-304b", "US-305", "REQ-006"]
tags: [devlog, agent, guardrails, rag, llm, fase1]
---

# DevLog — 2026-09-10 — Fase 1 del plan de mejora del chat: validada con el LLM real

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/15_ML_Models/Diagnostico_Chat_Agente_2026-09-09|Diagnóstico y plan]]

## Qué se hizo

El profesor calificó el chat de "basura"; el diagnóstico (documento enlazado arriba) identificó
que la barrera real era una whitelist rígida de vocabulario, cero transparencia sobre cobertura de
datos, un bug conocido en preguntas de Nuevo León, y falta de auto-corrección/respuesta directa.
Fase 1 (100% en `src/agente/**`) implementa las correcciones:

- **`guardrails.py`**: vocabulario de `PALABRAS_AMBITO` ampliado (~140 palabras/sinónimos).
  Al ampliarlo se reabrió la regresión de seguridad ya corregida el 8 de septiembre (`Modifica el
  nivel de la primaria X` volvía a colarse porque "primaria" ya no está sola en la whitelist);
  se cerró en la raíz agregando los sustantivos de negocio nuevos que son columnas reales de Gold
  (`nivel`, `prioridad`, `cobertura`, `completitud`, `sostenimiento`, `cluster`, `perfil`,
  `matricula`, `recomendacion(es)`, `prediccion(es)`) a `OBJETOS_DE_DATOS`, en vez de volver a
  angostar el vocabulario.
- **`recuperacion.py`**: `top_k` 3→5 y umbral de distancia coseno configurable
  (`AGENTE_RAG_UMBRAL_DISTANCIA`) para que el RAG sirva de señal semántica real de relevancia.
- **`servicio.py`**: puerta híbrida (si el vocabulario no reconoce el tema, se intenta el RAG como
  respaldo semántico antes de rechazar — la intención de escritura sigue siendo un corte duro sin
  tocar RAG/LLM), rama de respuesta directa sin SQL para preguntas conceptuales, y auto-corrección
  (1 reintento) cuando el SQL generado falla al ejecutarse.
- **`prompt.py`**: cobertura de las 4 entidades explicada en el `SYSTEM_PROMPT`, sentinel
  `NO_SQL_NECESARIO`, y ejemplos few-shot — incluyendo el patrón de join
  (`dim_escuela.cve_ent` + `grano='escuela'` + `modelo='ML-01'`) que corrige el bug de Nuevo León.
- **`llm.py`**: el prompt del redactor ya explica cómo responder cuando la fila trae
  `contexto_faro` en vez de resultados de SQL.
- Tests actualizados (`tests/test_agente_servicio.py`, `tests/test_agente_evaluacion.py`): los
  casos de "fuera de alcance"/"insegura" que antes exigían que `recuperar_contexto` nunca se
  llamara se reescribieron para permitir la llamada pero exigir que el RAG confirme "no relevante"
  (`ContextoNoEncontrado`) — la garantía real de seguridad (nunca se genera/ejecuta SQL) se
  preserva y se sigue probando explícitamente.

## Validación

- **61/61 pruebas de `src/agente/**` en verde, `ruff check` limpio.**
- **Validación manual con el LLM real** (Anthropic + ChromaDB + Postgres local, rol read-only
  `faro_agente_ro`): 5 preguntas — Nuevo León (bug conocido), vocabulario libre sin palabra exacta
  de la whitelist, pregunta conceptual sin SQL, pregunta fuera de cobertura (Oaxaca), y orden de
  escritura. Las 5 se comportaron como se esperaba: el bug de Nuevo León generó el SQL correcto con
  datos reales, el vocabulario libre pasó por el respaldo semántico, la pregunta conceptual se
  respondió sin tocar la base de datos, Oaxaca se explicó como límite de diseño (no error), y la
  orden de escritura se rechazó sin generar SQL.

## 🤖 Sesión de IA
- **Agente / modelo:** GitHub Copilot / Claude Sonnet 5
- **Archivos creados/modificados:**
  - `src/agente/guardrails.py`, `src/agente/recuperacion.py`, `src/agente/servicio.py`,
    `src/agente/prompt.py`, `src/agente/llm.py`, `src/agente/indexar_esquema.py`
  - `tests/test_agente_servicio.py`, `tests/test_agente_evaluacion.py`
  - `vault/15_ML_Models/Diagnostico_Chat_Agente_2026-09-09.md` (diagnóstico + plan de 4 fases)
  - `vault/15_ML_Models/_index.md`
- **Decisiones autónomas del agente:**
  - Reorganizar el gate híbrido en `servicio.py` en vez de cambiar la firma de `pregunta_en_alcance`,
    para no romper los tests unitarios existentes de `guardrails.py`.
  - Cerrar la regresión de seguridad ampliando `OBJETOS_DE_DATOS` en vez de retirar palabras de
    `PALABRAS_AMBITO`.
  - No tocar `src/api/**` (alcance de Karla, C4) ni `docker-compose.yml`/`docker/**` (alcance de
    Alejandro, C5); las Fases 2-3 quedan para ellos.
- **Correcciones manuales:** ninguna — el usuario proporcionó la `ANTHROPIC_API_KEY` real
  directamente en su `.env` local (nunca compartida por chat) tras corregir dos intentos con el
  valor equivocado (el ID de la key en vez del secreto).
- **Prompt inicial:** diagnóstico completo del chat + plan de mejora por fases, luego implementar
  y validar la Fase 1 con el LLM real.

## Seguridad / calidad
- [x] Sin secretos hardcodeados (la API key vive solo en `.env` local, gitignored)
- [x] Tests agregados/actualizados y en verde (61/61), `ruff check` limpio
- [x] DevLog enlaza a los IDs afectados
- [x] Validado con LLM real antes de dar la fase por cerrada

## Bloqueantes
- El esquema de ChromaDB en producción está **horneado en la imagen del sidecar** (no se indexa en
  runtime, ver DevLog 2026-09-07 de Luis §4.6). El nuevo chunk de "cobertura geográfica" no aparece
  en prod hasta que Alejandro reconstruya esa imagen, no solo la de la API.
- Fase 2 (memoria conversacional, Karla) y Fase 3 (streaming, Alejandro) no han arrancado.

## Próximos pasos
- Abrir PR de esta rama con el ID de historia correspondiente.
- Coordinar con Alejandro el redeploy (imagen de la API **y** del sidecar de ChromaDB).
- Avisar a Karla que puede arrancar la Fase 2: el soporte interno de `contexto_conversacional` ya
  existe en `servicio.py`/`prompt.py`, solo falta que el contrato de la API (`src/api/schemas.py`,
  `src/api/v1/agente.py`) lo reciba y se lo pase.
