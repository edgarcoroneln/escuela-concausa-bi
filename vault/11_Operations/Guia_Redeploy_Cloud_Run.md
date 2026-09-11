---
id: DOC-GUIA-REDEPLOY-CLOUD-RUN
title: "Guía de Re-despliegue a Cloud Run — API y ChromaDB Sidecar"
author: "Alejandro Velázquez Mendoza"
date: "2026-09-10"
status: active
traces_up: ["US-304b", "REQ-005"]
tags: [cloud-run, deploy, gcp, docker, celula-5]
---

# Guía de Re-despliegue a Cloud Run — API y ChromaDB Sidecar

→ [[vault/11_Operations/_index|Volver a Operaciones]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy Base §4.6]]

Esta guía detalla el procedimiento operativo para compilar, publicar y re-desplegar los contenedores del servicio `faro-api` en Google Cloud Run cuando se integren cambios al agente conversacional (Fases 1, 2, 3 o 4).

---

## 1. Re-despliegue de la API (`faro-api`)

Aplica cuando hay cambios en `src/agente/**`, `src/api/**` o `docker/`:

### Paso 1: Sincronización local
```bash
git fetch origin
git merge origin/main
```

### Paso 2: Construcción de la imagen Docker sellada
Exportar el SHA del commit actual para sellar la imagen (verificable en `/api/v1/version`):
```bash
GIT_SHA=$(git rev-parse HEAD)
docker build -f docker/api.Dockerfile \
  --build-arg GIT_SHA=$GIT_SHA \
  -t us-central1-docker.pkg.dev/faro-escuela-sensor/faro-repo/faro-api:$GIT_SHA \
  -t us-central1-docker.pkg.dev/faro-escuela-sensor/faro-repo/faro-api:latest .
```

### Paso 3: Push a Artifact Registry
```bash
docker push us-central1-docker.pkg.dev/faro-escuela-sensor/faro-repo/faro-api:$GIT_SHA
docker push us-central1-docker.pkg.dev/faro-escuela-sensor/faro-repo/faro-api:latest
```

### Paso 4: Actualización en Cloud Run
```bash
gcloud run deploy faro-api \
  --image=us-central1-docker.pkg.dev/faro-escuela-sensor/faro-repo/faro-api:$GIT_SHA \
  --region=us-central1 \
  --project=faro-escuela-sensor
```

---

## 2. Re-indexado y Persistencia en ChromaDB

> ℹ️ **Arquitectura de ChromaDB:** ChromaDB corre directamente sobre la imagen oficial inmutable `chromadb/chroma:latest` (no existe ni se requiere un `Dockerfile` en `docker/`). Las colecciones y embeddings residen en un volumen persistente (`chroma-data:/chroma/data`, con variable de entorno `IS_PERSISTENT: 1`). El índice vectorial **no** se hornea dentro de una imagen Docker personalizada.

Cuando Andrés modifique `src/agente/indexar_esquema.py` o cambie la estructura de la capa Gold (`dbt/models/gold/`), no se reconstruye ninguna imagen de ChromaDB; en su lugar, se re-ejecuta el script de indexación contra la instancia activa.

### Paso 1: Ejecución del script de indexación
El script `src/agente/indexar_esquema.py` lee su configuración mediante variables de entorno (`CHROMA_HOST` y `CHROMA_PORT` vía `os.getenv`). Su punto de entrada (`__main__`) no acepta banderas de línea de comando (`--host`/`--port`). El puerto predeterminado en el código es `8001`:

```bash
# Ejecución local estándar contra el servicio de docker-compose (puerto 8001):
CHROMA_HOST=localhost CHROMA_PORT=8001 python -m src.agente.indexar_esquema
```

Si se requiere ejecutar contra un host o puerto distinto:
```bash
CHROMA_HOST="127.0.0.1" CHROMA_PORT=8001 python -m src.agente.indexar_esquema
```

El script genera los embeddings con `all-MiniLM-L6-v2` y realiza un `upsert` idempotente en la colección `faro_gold_schema`.

### Paso 2: Verificación de estado del servicio
Confirmar la disponibilidad de ChromaDB antes o después de la indexación:
```bash
curl -f -s http://localhost:8001/api/v2/heartbeat
```
*Salida esperada:* `{"nanosecond heartbeat": ...}`

### Paso 3: Estrategia de Rollback de ChromaDB
Dado que el índice reside en un volumen de datos persistente y no en una revisión versionada de imagen Docker:
- **Si el nuevo esquema genera alucinaciones o errores de SQL en el agente:** Revertir los cambios en `src/agente/indexar_esquema.py` al commit anterior y re-ejecutar el script de indexado:
  ```bash
  git checkout <COMMIT_ANTERIOR> -- src/agente/indexar_esquema.py
  CHROMA_HOST=localhost CHROMA_PORT=8001 python -m src.agente.indexar_esquema
  ```
- **Si se requiere regenerar el volumen desde cero en desarrollo local:**
  ```bash
  docker compose stop chromadb
  docker volume rm faro-chroma-data
  docker compose up -d chromadb
  CHROMA_HOST=localhost CHROMA_PORT=8001 python -m src.agente.indexar_esquema
  ```

---

## 3. Verificación Post-Deploy (Smoke Tests)

### 1. Healthcheck y versión
```bash
curl -f -s https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/health
curl -f -s https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/version
```
*Salida esperada:* `{"status":"ok"}` y el commit SHA coincidente con el commit desplegado.

### 2. Smoke test del Agente Conversacional
Ejecutar consulta de verificación contra el endpoint en vivo:
```bash
curl -X POST https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/agente/consulta \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Cuántas escuelas están registradas en el sistema?"}'
```
*Salida esperada:* `fuera_de_alcance: false`, `sql_generado` no nulo con consulta SELECT sobre `gold.*`, y redacción en español.

---

## 4. Procedimiento de Rollback Inmediato de la API

Si una nueva revisión de `faro-api` presenta errores de latencia, fallas de LLM o regresiones no detectadas:
1. Listar las últimas revisiones activas:
   ```bash
   gcloud run revisions list --service=faro-api --region=us-central1 --project=faro-escuela-sensor
   ```
2. Revertir el 100% del tráfico a la revisión previa estable (ejemplo `faro-api-00018-gjx`):
   ```bash
   gcloud run services update-traffic faro-api \
     --to-revisions=REVISION_ESTABLE_ANTERIOR=100 \
     --region=us-central1 \
     --project=faro-escuela-sensor
   ```
