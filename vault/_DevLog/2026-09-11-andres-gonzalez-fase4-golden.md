---
id: DEVLOG-2026-09-11-ANDRES-GONZALEZ-FASE4-GOLDEN
title: "Runner golden real para Fase 4 del agente"
owner: "Andrés González Habib"
status: active
traces_up: ["US-304a", "US-304b", "US-323", "REQ-006"]
traces_down: ["src/agente/evaluar_golden.py", "TEST-AGENTE-GOLDEN"]
tags: [devlog, agent, fase-4, evaluacion, golden, llm]
project: "FARO"
date: "2026-09-11"
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "GitHub Copilot"
session_duration: "30m"
touches: ["US-304a", "US-304b", "US-323", "REQ-006"]
---

# DevLog — 2026-09-11 — Runner golden real de Fase 4

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

- Se agregó `src/agente/evaluar_golden.py`, un runner opt-in que ejecuta el fixture de 20 preguntas contra el pipeline real: ChromaDB, Anthropic y el ejecutor read-only de Gold.
- El runner valida expectativas por categoría: preguntas válidas deben producir SQL y respuesta; preguntas fuera de alcance deben rechazarse sin SQL; preguntas inseguras nunca deben producir SQL.
- El reporte de consola no imprime respuestas completas, SQL ni secretos. Con `--salida` guarda únicamente estados, categoría, flags y errores sanitizados.
- Se agregó `tests/test_agente_evaluar_golden.py` para validar el fixture y las reglas del runner sin llamadas de red ni costo de LLM.

## Ejecución real

Desde la raíz del repositorio, con `ANTHROPIC_API_KEY`, `DATABASE_URL_READ_ONLY` y ChromaDB configurados:

```text
python -m src.agente.evaluar_golden --salida _local/golden-report.json
```

El runner no se ejecuta en CI por defecto porque consume el LLM y requiere servicios reales.

## Validación

- Diagnósticos del editor en runner y prueba: sin errores.
- `python -m py_compile src/agente/evaluar_golden.py tests/test_agente_evaluar_golden.py`: sin salida de error.
- La ejecución real queda pendiente de un ambiente local con Anthropic, ChromaDB y Postgres read-only disponibles.

## Estado y próximos responsables

- Andrés: ejecutar el runner real y corregir regresiones de prompt/RAG que encuentre.
- Karla: instrumentar eventos de logging y completar los mensajes distinguibles de API.
- Alejandro/Luis: redeploy y validación en Cloud Run una vez integrados los cambios.
- Edgar: agregar esta evidencia a la matriz de trazabilidad.

## Seguridad / calidad

- [x] No se agregaron credenciales ni datos reales.
- [x] El runner reutiliza el ejecutor SQL read-only existente.
- [x] Las pruebas por defecto son offline.
- [ ] Evaluación real de 20 casos ejecutada con servicios disponibles.

→ [[vault/_DevLog/_index|Volver al índice]]
