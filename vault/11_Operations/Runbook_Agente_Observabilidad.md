---
id: DOC-RUNBOOK-AGENTE-OBSERVABILIDAD
title: "Runbook de Observabilidad y Cloud Logging — Agente FARO"
author: "Alejandro Velázquez Mendoza"
date: "2026-09-10"
status: active
traces_up: ["US-304b", "REQ-006"]
tags: [runbook, observabilidad, cloud-logging, agente, celula-5]
---

# Runbook de Observabilidad y Cloud Logging — Agente FARO

→ [[vault/11_Operations/_index|Volver a Operaciones]] · [[vault/15_ML_Models/Diagnostico_Chat_Agente_2026-09-09|Diagnóstico del Agente]]

Este runbook documenta cómo monitorear, auditar e inspeccionar los eventos y errores del agente conversacional FARO en Google Cloud Logging (GCP), correspondiente a la **Fase 4 (Robustez y Observabilidad)**.

---

## 1. Arquitectura de Logging (Docker → GCP)

1. **Captura en contenedor:** La API corre bajo Uvicorn utilizando `docker/log_config.json`.
2. **Formateador estructurado:** La librería `python-json-logger` procesa las llamadas estándar de logging de Python (`logger.info`, `logger.warning`, `logger.error`).
3. **Mapeo para Cloud Logging:**
   - `rename_fields: {"levelname": "severity", "asctime": "timestamp"}` transforma los niveles a `severity` (`INFO`, `WARNING`, `ERROR`, `CRITICAL`).
   - `timestamp` se formatea en ISO 8601 con zona horaria (`%Y-%m-%dT%H:%M:%S%z`).
   - Los campos pasados vía `extra={...}` en el código Python se inyectan automáticamente en la raíz del payload JSON (`jsonPayload`).
4. **Ingesta en Cloud Run:** Cloud Run ingiere el `stdout` del contenedor y parsea cada línea JSON como una entrada de log estructurada de primer nivel.

---

## 2. Acceso a Logs en Google Cloud Platform

### Vía Google Cloud Console
1. Ir a **Cloud Logging → Logs Explorer** en el proyecto `faro-escuela-sensor`.
2. Filtro base del servicio de API:
   ```text
   resource.type="cloud_run_revision"
   resource.labels.service_name="faro-api"
   ```

### Vía gcloud CLI
```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="faro-api"' \
  --limit=50 \
  --format="json" \
  --project=faro-escuela-sensor
```

---

## 3. Consultas y Filtros Operativos en Cloud Logging

### A. Filtros Activos Hoy (Disponibles en Producción)

Los siguientes filtros operan sobre los logs emitidos actualmente por Uvicorn y FastAPI mediante `docker/log_config.json`:

| Caso Operativo | Consulta en Logs Explorer | Severidad | Propósito / Acción |
|---|---|---|---|
| **Errores no controlados / LLM / ChromaDB** | `resource.type="cloud_run_revision"`<br>`resource.labels.service_name="faro-api"`<br>`severity>=ERROR` | `ERROR` / `CRITICAL` | Detecta caídas de conexión a ChromaDB, fallos de Anthropic API o excepciones 500 no capturadas. |
| **Peticiones HTTP fallidas (4xx / 5xx)** | `resource.type="cloud_run_revision"`<br>`resource.labels.service_name="faro-api"`<br>`jsonPayload.status_code>=400` | `WARNING` / `ERROR` | Acceso a endpoints del agente con error de cliente o servidor en Uvicorn. |
| **Búsqueda por texto libre en logs** | `resource.type="cloud_run_revision"`<br>`resource.labels.service_name="faro-api"`<br>`textPayload =~ "(guardrail|retry|fallback|chroma)"` | Todas | Rastreo de eventos clave en el cuerpo del mensaje mientras no haya campos estructurados dedicados. |

Comando rápido en terminal:
```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="faro-api" AND severity>=ERROR' \
  --limit=20 \
  --format="table(timestamp,severity,textPayload,jsonPayload.message)" \
  --project=faro-escuela-sensor
```

### B. Contrato Objetivo (Pendiente Instrumentación en Código)

> ⚠️ **Nota para guardia / On-Call:** Los filtros por `jsonPayload.event_type` listados a continuación corresponden al **contrato estructurado objetivo** definido para la Fase 4. Actualmente `src/agente/servicio.py` no emite estos campos todavía (en desarrollo por Karla y Andrés). **No usar `event_type` en incidentes en vivo hasta que se complete la instrumentación de aplicación**, ya que la consulta retornará 0 resultados.

| Evento Objetivo | Filtro Futuro (`jsonPayload`) | Severidad Prevista | Propósito |
|---|---|---|---|
| **Guardrail Bloqueado** | `resource.labels.service_name="faro-api"`<br>`jsonPayload.event_type="guardrail_blocked"` | `WARNING` / `INFO` | Preguntas destructivas o fuera de alcance de FARO. |
| **Auto-corrección SQL** | `resource.labels.service_name="faro-api"`<br>`jsonPayload.event_type="sql_retry"` | `WARNING` | Reintentos automáticos tras error de PostgreSQL devolviendo el error al LLM. |
| **Consulta Exitosa** | `resource.labels.service_name="faro-api"`<br>`jsonPayload.event_type="query_success"` | `INFO` | Métrica de satisfacción y uso de consultas resueltas satisfactoriamente. |

---

## 4. Estructura y Significado de Campos

### Campos activos hoy en producción:
* **`severity`:** Nivel del evento transformado por `docker/log_config.json` a partir de `levelname` (`INFO`, `WARNING`, `ERROR`, `CRITICAL`).
* **`timestamp`:** Marca temporal ISO 8601 con zona horaria (`%Y-%m-%dT%H:%M:%S%z`).
* **`jsonPayload.message` / `textPayload`:** Descripción textual del evento o línea de log de Uvicorn (sin secretos).
* **`jsonPayload.status_code`:** Código de respuesta HTTP registrado en logs de acceso de Uvicorn.

### Campos del contrato objetivo (al instrumentar con `extra={...}` en código Python):
* **`jsonPayload.event_type`:** Tipo canónico del evento (`guardrail_blocked`, `sql_retry`, `query_success`, `rag_error`).
* **`jsonPayload.reason`:** Causa del bloqueo o fallo (ej. `solo_lectura`, `pregunta_referencial_sin_contexto`, `tabla_no_existe`).
* **`jsonPayload.attempt`:** Número de intento en auto-corrección (1 o 2).

---

## 5. Prácticas de Seguridad (Secrets Policy)
- **Nunca registrar credenciales:** Las claves `ANTHROPIC_API_KEY` y cadenas de conexión nunca deben figurar en el `message` ni en `extra={...}`.
- **SQL Sanitizado:** No imprimir SQL que contenga datos privados de usuarios en texto plano si no corresponden al esquema público `gold.*`.
