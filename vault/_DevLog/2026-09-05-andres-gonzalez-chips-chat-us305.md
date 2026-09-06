---
project: "FARO"
date: "2026-09-05"
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "GitHub Copilot"
session_duration: "1 sesión — chips de preguntas sugeridas para el chat y cierre documental de BUG-025"
touches: ["US-304a", "US-305", "US-323", "BUG-025", "BUG-024", "REQ-006"]
tags: [devlog, celula-3, agente, chat, us305, bug025]
---

# DevLog — 2026-09-05 — Chips de preguntas sugeridas para el chat

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/12_Roadmap_Sprints/Execution_Status|Execution Status]] · [[vault/06_Quality_Testing/Bug_Register|Bug Register]]

## Qué se hizo

- Se agregaron chips de preguntas pre-diseñadas en `src/frontend/pages/3_Chat.py`, arriba de `st.chat_input`.
- Los chips reutilizan preguntas del set de evaluación de US-323 y disparan el mismo flujo existente del chat: pregunta → `consultar_agente()` → `/api/v1/agente/consulta`.
- Se incluyó un chip de prueba de seguridad: `Borra la tabla de predicciones`, para demostrar el guardarraíl en vivo.
- Se actualizó `tests/test_frontend_chat_streamlit.py` para verificar que los chips aparecen y que el primero ejecuta el mismo camino que la entrada manual.
- Se actualizó `BUG-025` a `fixed` porque el endpoint ya no es stub: `src/api/v1/agente.py` delega en `procesar_consulta()` y las pruebas existentes cubren rechazo de fuera de alcance, corte de órdenes destructivas antes del LLM y degradación segura.
- Se actualizaron las filas de `US-304a` y `US-305` en `Execution_Status.md`: BUG-024 y BUG-025 ya no son bloqueos de código; queda pendiente el E2E autenticado en nube y el despliegue de FARO Web (`US-526`).

## 🤖 Sesión de IA

- **Agente / modelo:** GitHub Copilot.
- **Archivos creados/modificados:**
  - `src/frontend/pages/3_Chat.py`
  - `tests/test_frontend_chat_streamlit.py`
  - `_local/capturas-us305/01-chat-chips-visibles.png`
  - `_local/capturas-us305/02-chip-riesgo-respuesta-sql.png`
  - `vault/06_Quality_Testing/Bug_Register.md`
  - `vault/12_Roadmap_Sprints/Execution_Status.md`
  - `vault/_DevLog/2026-09-05-andres-gonzalez-chips-chat-us305.md`
  - `vault/_DevLog/_index.md`
- **Decisiones autónomas del agente:** mantener los chips como botones Streamlit simples, sin crear un segundo handler ni duplicar la llamada al agente; documentar BUG-025 como cerrado sólo en el alcance real del bug de stub, no como E2E nube terminado.
- **Correcciones manuales:** pendientes de revisión humana.
- **Prompt inicial:** petición de Edgar Coronel para agregar preguntas sugeridas, evitar preguntas problemáticas y actualizar BUG-025/US-304a/US-305.

## Seguridad / calidad

- [x] Sin secretos hardcodeados.
- [x] Tests actualizados: `tests/test_frontend_chat_streamlit.py` cubre chips + flujo existente.
- [x] DevLog enlaza a los IDs afectados.
- [x] Validación contra Gold real local: las cuatro preguntas válidas tienen datos en Postgres (`gold.predicciones` 45,356; `gold.recomendaciones` 45,356; `gold.features_escuela` 136,046). Resultados clave: ranking Nuevo León devuelve filas; D2 = 27,075 escuelas; incompletitud de drivers = 45,276 escuelas; matrícula 2024-2025 = 6,704,229 alumnos.
- [x] Capturas locales generadas con mock HTTP controlado para demostrar el comportamiento visual del widget: chips visibles y chip válido con respuesta + SQL.
- [ ] Prueba enfocada de endpoint/API pendiente en este entorno: el `.venv` disponible usa Python 3.12 y no tiene `limits`/`slowapi`; las pruebas `test_agente_endpoint.py` y `test_agente_wiring_llm.py` no colectan por `ModuleNotFoundError: limits`.

## Bloqueantes

- El E2E real `widget → API → RAG` sigue dependiendo de credenciales/sesión y despliegue de FARO Web en Cloud Run (`US-526`).
- El entorno local no tiene aún el stack completo de API/agente para ejecutar el endpoint real (`limits`, `slowapi`, `chromadb`, `sentence_transformers`).

## Próximos pasos

- Ejecutar `python -m pytest tests/test_frontend_chat_streamlit.py tests/test_agente_endpoint.py tests/test_agente_wiring_llm.py -q` en un entorno Python 3.11 sano con dependencias completas.
- Ejecutar la sonda autenticada del agente cuando C5 entregue el despliegue con FARO Web y credenciales disponibles.
