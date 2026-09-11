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
   - Definición de consultas operativas por `jsonPayload` para monitorear eventos clave: `guardrail_blocked`, `sql_retry`, `query_success`, y errores con `severity>=ERROR`.
   - Especificación de campos esperados para la instrumentación en código de Karla (`src/api/v1/agente.py`) y Andrés (`src/agente/servicio.py`).
   - Políticas de seguridad para evitar registro de credenciales o SQL no sanitizado.

2. **Guía de Re-despliegue (`vault/11_Operations/Guia_Redeploy_Cloud_Run.md`):**
   - Procedimiento de compilación con sellado de commit (`GIT_SHA`) y push a Artifact Registry para `faro-api`.
   - Proceso especial para regeneración y horneado del índice ChromaDB en la imagen del sidecar (`chromadb.Dockerfile`) cuando cambie `indexar_esquema.py`.
   - Protocolo de verificación post-despliegue (healthchecks y smoke test del agente).
   - Receta de rollback inmediato redireccionando el 100% del tráfico a la revisión anterior estable.

3. **MOC de Operaciones (`vault/11_Operations/_index.md`):**
   - Registro de ambos documentos operativos en el índice correspondiente.

## Contexto y coordinación del equipo

- **Andrés González Habib:** Concluyó Fase 1 y tomará Fase 3 (streaming). La guía documenta cómo regenerar el sidecar si actualiza el esquema RAG.
- **Karla Monter:** Concluyó Fase 2 (historial en contrato de API). El runbook de observabilidad formaliza los nombres canónicos de `event_type` que se integrarán para Cloud Logging.
- **Alejandro Velázquez Mendoza:** Cobertura de infraestructura, configuración de contenedores y runbooks operativos de despliegue y monitoreo en Cloud Run.

## 🤖 Sesión de IA

- **Agente / modelo:** Antigravity / Gemini 3.8 Flash
- **Archivos creados/modificados:**
  - `vault/11_Operations/Runbook_Agente_Observabilidad.md` (nuevo)
  - `vault/11_Operations/Guia_Redeploy_Cloud_Run.md` (nuevo)
  - `vault/11_Operations/_index.md` (actualizado con los 2 documentos)
  - `vault/_DevLog/2026-09-10-alejandro-velazquez-observabilidad-redeploy-agente.md` (nuevo DevLog)
  - `vault/_DevLog/_index.md` (registro de la entrada)
- **Decisiones autónomas del agente:** Ninguna; cambios realizados en zona verde de C5 y revisados por el auditor.
- **Correcciones manuales:** Ajuste de `status: active` en frontmatter de ambos documentos operativos.
- **Prompt inicial:** Elaboración de runbooks operativos de observabilidad y re-despliegue para Fase 4.

## Seguridad / calidad

- [x] Documentos estrictamente en zona verde (`vault/11_Operations/**`, `vault/_DevLog/**`)
- [x] Sin secretos hardcodeados
- [x] Trazas documentadas (`US-304b`, `REQ-005`, `REQ-006`)
- [x] `vault_lint.py` verificado en limpio

## Bloqueantes

- Ninguno. Documentación activa lista para consulta y operación.

## Próximos pasos

- Mantener la coordinación con Andrés y Karla para ejecutar el re-despliegue a Cloud Run en cuanto ensamble la Fase 3.
