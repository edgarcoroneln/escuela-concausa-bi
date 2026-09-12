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
   - Filtros activos hoy limitados estrictamente a los campos que `log_config.json` emite: `severity>=ERROR` y búsqueda en `jsonPayload.message`. Eliminados `jsonPayload.status_code` y `textPayload` (no existen en el output real del formateador).
   - Contrato objetivo de `jsonPayload.event_type` (`guardrail_blocked`, `sql_retry`, `query_success`) marcado explícitamente como pendiente de instrumentación en código — con advertencia al on-call de que las consultas retornarán 0 resultados hoy.
   - Sintaxis portable de `gcloud logging read` (eliminada ruta local de Windows).
   - Políticas de seguridad para evitar registro de credenciales o SQL no sanitizado.

2. **Guía de Re-despliegue (`vault/11_Operations/Guia_Redeploy_Cloud_Run.md`):**
   - Separación explícita entre procedimiento **local** (docker-compose, volumen `faro-chroma-data`, `chromadb/chroma:latest`, `CHROMA_PORT=8001`) y procedimiento de **producción** (sidecar con índice horneado, digest amd64 inmutable, `gcloud run services replace` con spec YAML multi-contenedor).
   - Build con `docker buildx --platform linux/amd64` y Artifact Registry `faro-images` (corregido de `faro-repo`).
   - Eliminado `gcloud run deploy --image` genérico; reemplazado por `gcloud run services replace` referenciando Cloud_Run_Deploy.md §4.6d como fuente canónica.
   - Smoke tests corregidos para validar autenticación: 401 sin token (SEC-006) y respuesta del agente con token válido.
   - Documentados como **pendientes operativos de Luis Téllez**: (a) versionado de la spec YAML multi-contenedor y (b) Dockerfile/script reproducible para la imagen del sidecar.

3. **MOC de Operaciones (`vault/11_Operations/_index.md`):**
   - Registro de ambos documentos operativos en el índice correspondiente.

4. **Trazabilidad (`vault/02_Requirements/Traceability_Matrix.md`):**
   - Fila `REQ-005` S7: columna DevLog actualizada con referencia al presente DevLog.

## Contexto y coordinación del equipo

- **Luis Téllez (TL C5 / Owner deploy):** Los runbooks referencian Cloud_Run_Deploy.md como fuente canónica. Se documentaron dos pendientes operativos suyos: versionado del YAML multi-contenedor y script reproducible del sidecar. Se solicita su revisión explícita por regla 7 del vault.
- **Andrés González Habib:** Concluyó Fase 1 y tomará Fase 3. La guía documenta el re-indexado local y los pasos (pendientes) para actualizar el sidecar en producción.
- **Karla Monter:** Concluyó Fase 2. El runbook formaliza los nombres canónicos de `event_type` que se integrarán en código para Cloud Logging.
- **Edgar (PM / Code Owner):** Solicitó dos rondas de cambios en PR #309 para alinear la documentación con la realidad del repositorio y la arquitectura de producción.
- **Alejandro Velázquez Mendoza:** Cobertura de infraestructura, configuración de contenedores y runbooks operativos.

## 🤖 Sesión de IA

- **Agente / modelo:** Antigravity / Claude Opus 4.6
- **Archivos creados/modificados:**
  - `vault/11_Operations/Runbook_Agente_Observabilidad.md` (ajustado tras review PR #309 round 2)
  - `vault/11_Operations/Guia_Redeploy_Cloud_Run.md` (ajustado tras review PR #309 round 2)
  - `vault/11_Operations/_index.md` (actualizado con los 2 documentos)
  - `vault/_DevLog/2026-09-10-alejandro-velazquez-observabilidad-redeploy-agente.md` (DevLog)
  - `vault/_DevLog/_index.md` (registro de la entrada)
  - `vault/02_Requirements/Traceability_Matrix.md` (fila REQ-005 S7)
- **Decisiones autónomas del agente:** Ninguna; cada campo, comando y ruta verificado contra archivos reales del repositorio.
- **Correcciones manuales:**
  - Round 1: Arquitectura ChromaDB (volumen vs Dockerfile inexistente), env vars en indexar_esquema, gcloud portable, filtros activos vs pendientes.
  - Round 2: Separación local/producción, `services replace` vs `deploy`, Artifact Registry `faro-images`, smoke tests con auth (SEC-006), eliminación de `status_code`/`textPayload` inexistentes, trazabilidad, pendientes operativos de Luis.
- **Prompt inicial:** Runbooks de observabilidad y re-despliegue para Fase 4.

## Seguridad / calidad

- [x] Documentos estrictamente en zona verde (`vault/11_Operations/**`, `vault/_DevLog/**`) + 1 celda en Traceability_Matrix
- [x] Sin secretos hardcodeados — smoke test indica `<TOKEN_DE_SESION>` sin valor real
- [x] Trazas documentadas (`US-304b`, `REQ-005`, `REQ-006`)
- [x] `vault_lint.py` verificado en limpio
- [x] Cada comando, campo y ruta verificado contra archivos reales del repositorio

## Bloqueantes

- Ninguno. Documentación operativa ajustada y lista para re-revisión de PR #309 (round 2).

## Próximos pasos

- Obtener aprobación de Edgar y de Luis Téllez (regla 7) en PR #309 y merge a `main`.
- Luis versiona la spec YAML multi-contenedor y el procedimiento de build del sidecar.
