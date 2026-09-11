---
id: DEVLOG-2026-09-10-ALEJANDRO-VELAZQUEZ-ENV-VARS-AGENTE-DOCKER
title: "Reenvío de variables de entorno del agente en docker-compose (Fase 4)"
author: "Alejandro Velázquez Mendoza"
date: "2026-09-10"
traces_up: [US-304b, REQ-006]
tags: [devlog, docker, agente, fase4, celula-5]
---

# DevLog — 2026-09-10 — Reenvío de variables de entorno del agente en docker-compose (Fase 4)

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

En el marco del **Plan de Recuperación del Agente Conversacional** (Fase 4 — Robustez y observabilidad):

1. **Configuración local (`docker-compose.yml`):**
   Se agregaron al bloque `environment` del servicio `api` (FastAPI backend) las variables necesarias para el funcionamiento del agente conversacional:
   - `ANTHROPIC_API_KEY`: Secreto para activar el LLM de Anthropic (`src/agente/llm.py`).
   - `AGENTE_MODELO`: Selección del modelo LLM a utilizar.
   - `DATABASE_URL_READ_ONLY`: Cadena de conexión con privilegios de solo lectura sobre `gold.*` para el ejecutor seguro (`src/api/ejecutor_gold.py`).
   - `CHROMA_HOST=chromadb`: Host del contenedor de ChromaDB en la red interna de Docker (`faro-network`).
   - `CHROMA_PORT=8000`: Puerto interno del servicio ChromaDB.

2. **Propósito:**
   Habilitar que cualquier integrante del equipo pueda levantar y probar el agente en entorno local con el LLM real y ChromaDB (`docker compose up api chromadb`), eliminando la degradación a stubs en desarrollo local.

## Contexto y coordinación del equipo

- **Andrés González Habib (Fase 1 completa):** Implementó la puerta híbrida semántica, enriquecimiento de prompt few-shot, auto-corrección de SQL y respuesta directa conceptual en `src/agente/**` (PR integrado).
- **Karla Monter (Fase 2 en progreso):** Trabajando en el contrato de la API (`src/api/schemas.py` y `src/api/v1/agente.py`) para soportar `historial` y memoria conversacional.
- **Alejandro Velázquez Mendoza (Fase 4 & Despliegue):** Cobertura de infraestructura local (`docker-compose.yml`), soporte de observabilidad/Cloud Logging y preparación para el re-despliegue de imágenes a Cloud Run cuando se consoliden Fases 2 y 3.

## 🤖 Sesión de IA

- **Agente / modelo:** Antigravity / Gemini 3.8 Flash
- **Archivos creados/modificados:**
  - `docker-compose.yml` (modificado: 5 variables de entorno agregadas a `api`)
  - `vault/_DevLog/2026-09-10-alejandro-velazquez-env-vars-agente-docker.md` (creado: este DevLog)
  - `vault/_DevLog/_index.md` (registro de la entrada)
- **Decisiones autónomas del agente:** Ninguna; cada paso y diff fue presentado y validado previamente.
- **Correcciones manuales:** Ajuste de campos del frontmatter para total consistencia canónica (`author`, `title`, `traces_up`).
- **Prompt inicial:** Instrucciones del plan de mejora del chat (Fase 4) y asignación de tareas a Alejandro Velázquez.

## Seguridad / calidad

- [x] Sin secretos hardcodeados (las variables se interpolan desde `.env` local, gitignored)
- [x] Variables sensibles vacías por defecto (`:-`) para no romper entornos sin LLM
- [x] DevLog enlaza a los IDs afectados (`US-304b`, `REQ-006`)
- [x] `vault_lint.py` verificado

## Bloqueantes

- Ninguno para esta tarea local. El re-despliegue a producción esperará a que Karla complete el contrato de Fase 2 o a solicitud de sync del equipo.

## Próximos pasos

- Registrar entrada en `vault/_DevLog/_index.md`.
- Realizar commit con `feat(docker): reenviar variables de entorno del agente al contenedor api (US-304b)`.
- Coordinar con Karla la definición de campos estructurados para Cloud Logging (Fase 4).
