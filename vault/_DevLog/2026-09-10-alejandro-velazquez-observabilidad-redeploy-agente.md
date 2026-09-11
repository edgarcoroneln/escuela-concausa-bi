---
id: DEVLOG-2026-09-10-ALEJANDRO-VELAZQUEZ-OBSERVABILIDAD-REDEPLOY-AGENTE
title: "Runbooks de observabilidad y re-despliegue del agente en Cloud Run (Fase 4)"
author: "Alejandro Velázquez Mendoza"
date: "2026-09-10"
traces_up: [US-304b, REQ-005, REQ-006]
tags: [devlog, operations, cloud-logging, cloud-run, agente, fase4, celula-5]
---

# DevLog — 2026-09-10 — Runbooks de observabilidad y re-despliegue del agente en Cloud Run (Fase 4)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/11_Operations/Runbook_Agente_Observabilidad|Runbook Observabilidad]] · [[vault/11_Operations/Guia_Redeploy_Cloud_Run|Guía Re-deploy]]

## Qué se hizo

En continuidad con los entregables de **Célula 5 / Infraestructura** para la **Fase 4 (Robustez y observabilidad)** del plan de mejora del agente conversacional:

1. **Runbook de Observabilidad (`vault/11_Operations/Runbook_Agente_Observabilidad.md`):**
   - Documentación de la arquitectura de logs estructurados desde Uvicorn con `docker/log_config.json` hacia GCP Cloud Logging.
   - Separación explícita entre filtros activos hoy (`severity>=ERROR`, Uvicorn access logs `jsonPayload.status_code`, búsqueda textual) y el contrato objetivo estructurado (`jsonPayload.event_type` como `guardrail_blocked`, `sql_retry`, `query_success`), aclarando que este último está pendiente de instrumentación en código por el equipo de desarrollo.
   - Sustitución de comandos locales por sintaxis portable de `gcloud logging read`.
   - Políticas de seguridad para evitar registro de credenciales o SQL no sanitizado.

2. **Guía de Re-despliegue (`vault/11_Operations/Guia_Redeploy_Cloud_Run.md`):**
   - Procedimiento de compilación con sellado de commit (`GIT_SHA`) y push a Artifact Registry para `faro-api`.
   - Documentación fiel de la arquitectura de ChromaDB: corre sobre la imagen oficial inmutable `chromadb/chroma:latest` con persistencia en volumen (`chroma-data:/chroma/data`, `IS_PERSISTENT: 1`) sin Dockerfile personalizado.
   - Re-indexación mediante `CHROMA_HOST=localhost CHROMA_PORT=8001 python -m src.agente.indexar_esquema` (sin banderas CLI inexistentes, respetando `os.getenv` y puerto por defecto 8001).
   - Protocolo de verificación post-despliegue (healthchecks y smoke test del agente) y estrategia de rollback operativo.

3. **MOC de Operaciones (`vault/11_Operations/_index.md`):**
   - Registro de ambos documentos operativos en el índice correspondiente.

## Contexto y coordinación del equipo

- **Andrés González Habib:** Concluyó Fase 1 y tomará Fase 3 (streaming). La guía documenta el re-indexado contra ChromaDB persistente si actualiza el esquema RAG.
- **Karla Monter:** Concluyó Fase 2 (historial en contrato de API). El runbook de observabilidad formaliza los nombres canónicos de `event_type` que se integrarán en código para Cloud Logging.
- **Edgar (PM / Code Owner):** Solicitó cambios en PR #309 para alinear la documentación con la realidad del repositorio (ausencia de Dockerfile en ChromaDB, estado real de logs y comandos CLI portables).
- **Alejandro Velázquez Mendoza:** Cobertura de infraestructura, configuración de contenedores y runbooks operativos de despliegue y monitoreo en Cloud Run.

## 🤖 Sesión de IA

- **Agente / modelo:** Antigravity / Gemini 3.8 Flash
- **Archivos creados/modificados:**
  - `vault/11_Operations/Runbook_Agente_Observabilidad.md` (ajustado tras review PR #309)
  - `vault/11_Operations/Guia_Redeploy_Cloud_Run.md` (ajustado tras review PR #309)
  - `vault/11_Operations/_index.md` (actualizado con los 2 documentos)
  - `vault/_DevLog/2026-09-10-alejandro-velazquez-observabilidad-redeploy-agente.md` (DevLog)
  - `vault/_DevLog/_index.md` (registro de la entrada)
- **Decisiones autónomas del agente:** Ninguna; cambios realizados en zona verde de C5 y verificados estrictamente contra el código fuente real del repositorio.
- **Correcciones manuales:** Corrección de la arquitectura de ChromaDB (volumen persistente en lugar de Dockerfile inexistente), uso de env vars en `indexar_esquema.py` (puerto 8001), comando gcloud portable y delimitación de filtros activos hoy vs contrato objetivo en observabilidad.
- **Prompt inicial:** Elaboración de runbooks operativos de observabilidad y re-despliegue para Fase 4 y atención a revisión de PR #309.

## Seguridad / calidad

- [x] Documentos estrictamente en zona verde (`vault/11_Operations/**`, `vault/_DevLog/**`)
- [x] Sin secretos hardcodeados
- [x] Trazas documentadas (`US-304b`, `REQ-005`, `REQ-006`)
- [x] `vault_lint.py` verificado en limpio
- [x] Comandos y rutas verificados contra archivos reales del repositorio

## Bloqueantes

- Ninguno. Documentación operativa ajustada y lista para re-revisión de PR #309.

## Próximos pasos

- Obtener aprobación de Edgar en PR #309 y merge a `main`.
