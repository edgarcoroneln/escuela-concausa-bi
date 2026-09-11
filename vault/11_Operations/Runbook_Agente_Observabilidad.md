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
```powershell
& "C:\Users\Alejandro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="faro-api"' --limit=50 --format="json" --project=faro-escuela-sensor
```

---

## 3. Filtros Operativos Útiles (`jsonPayload`)

Los siguientes campos estructurados son los definidos como campos esperados para la instrumentación en `src/agente/servicio.py` y `src/api/v1/agente.py`:

| Evento a Monitorear | Consulta en Cloud Logging | Severidad | Propósito / Acción |
|---|---|---|---|
| **Rechazos por Guardrail** | `resource.labels.service_name="faro-api"`<br>`jsonPayload.event_type="guardrail_blocked"` | `WARNING` / `INFO` | Intentos de órdenes destructivas de escritura o preguntas fuera de alcance de FARO. |
| **Reintentos Auto-corrección SQL** | `resource.labels.service_name="faro-api"`<br>`jsonPayload.event_type="sql_retry"` | `WARNING` | Fallas iniciales de ejecución SQL que el agente intentó corregir automáticamente devolviendo el error al LLM. |
| **Consultas Exitosas** | `resource.labels.service_name="faro-api"`<br>`jsonPayload.event_type="query_success"` | `INFO` | Monitoreo de uso y métricas de satisfacción del chat. |
| **Errores de Infraestructura/LLM** | `resource.labels.service_name="faro-api"`<br>`severity>=ERROR` | `ERROR` | Caídas de ChromaDB sidecar, timeouts con Anthropic API o errores no controlados. |

---

## 4. Estructura y Significado de Campos

Cada entrada de log en Cloud Logging contiene:
* **`severity`:** Nivel del evento (`INFO`, `WARNING`, `ERROR`).
* **`timestamp`:** Momento exacto de la petición.
* **`message`:** Descripción legible del evento (sin exponer secretos, tokens ni PII).
* **`jsonPayload.event_type`:** Tipo canónico del evento (`guardrail_blocked`, `sql_retry`, `query_success`, `rag_error`).
* **`jsonPayload.reason`:** Causa del bloqueo o fallo (ej. `solo_lectura`, `pregunta_referencial_sin_contexto`, `tabla_no_existe`).
* **`jsonPayload.attempt`:** Número de intento en auto-corrección (1 o 2).

---

## 5. Prácticas de Seguridad (Secrets Policy)
- **Nunca registrar credenciales:** Las claves `ANTHROPIC_API_KEY` y cadenas de conexión nunca deben figurar en el `message` ni en `extra={...}`.
- **SQL Sanitizado:** No imprimir SQL que contenga datos privados de usuarios en texto plano si no corresponden al esquema público `gold.*`.
