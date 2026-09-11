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

> ⚠️ **Fuente canónica de deploy:** [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Cloud_Run_Deploy.md]] (owner: Luis Téllez). Esta guía complementa ese documento con los procedimientos operativos frecuentes; ante discrepancia, **manda Cloud_Run_Deploy.md**.

---

## 1. Re-despliegue de la API (`faro-api`)

Aplica cuando hay cambios en `src/agente/**`, `src/api/**` o `docker/`:

### Paso 1: Sincronización local
```bash
git fetch origin
git merge origin/main
```

### Paso 2: Construcción de la imagen Docker sellada
Construir **siempre** con `buildx --platform linux/amd64` (Cloud Run rechaza imágenes arm64, ver Cloud_Run_Deploy.md §10). Sellar con el SHA del commit para verificar en `/api/v1/version`:

```bash
GIT_SHA=$(git rev-parse HEAD)
docker buildx build --platform linux/amd64 \
  -f docker/api.Dockerfile \
  --build-arg GIT_SHA=$GIT_SHA \
  -t us-central1-docker.pkg.dev/faro-escuela-sensor/faro-images/faro-api:$GIT_SHA \
  -t us-central1-docker.pkg.dev/faro-escuela-sensor/faro-images/faro-api:latest \
  --push .
```

### Paso 3: Actualización en Cloud Run (multi-contenedor)

> ⚠️ **No usar `gcloud run deploy faro-api --image=...`:** El servicio `faro-api` es multi-contenedor (API + sidecar ChromaDB). Un `gcloud run deploy` genérico destruye el segundo contenedor, pierde los secretos de Secret Manager, el VPC connector `faro-connector`, la SA `faro-api-sa` y las `container-dependencies`. Se debe usar **`gcloud run services replace`** con la especificación YAML del servicio (Cloud_Run_Deploy.md §4.6d).

```bash
gcloud run services replace <SPEC_YAML> --region=us-central1
```

> ⚠️ **Pendiente operativo (Luis Téllez):** La especificación YAML multi-contenedor (`faro_api_deploy.yaml`) **no está versionada en el repositorio**. Luis la usó manualmente en el deploy inicial. Hasta que se versione, consultar a Luis para obtener la spec vigente o exportarla con `gcloud run services describe faro-api --format=export --region=us-central1`.

Para cambios que **no** requieren reconstruir la imagen (ej. cambio de variable de entorno):
```bash
gcloud run services update faro-api --region=us-central1 \
  --container=api --update-env-vars <VARIABLE>=<VALOR>
```

---

## 2. ChromaDB — Arquitectura Local vs Producción

### 2.1 Entorno local (docker-compose)

En desarrollo local, ChromaDB corre sobre la imagen `chromadb/chroma:latest` (etiqueta **mutable**) con persistencia en un volumen Docker nombrado (`chroma-data:/chroma/data`, `IS_PERSISTENT: 1`). El índice vectorial se genera contra la instancia activa.

**Re-indexación local:**

El script `src/agente/indexar_esquema.py` lee su configuración mediante variables de entorno (`CHROMA_HOST` y `CHROMA_PORT` vía `os.getenv`). Su punto de entrada (`__main__`) no acepta banderas de línea de comando. El puerto predeterminado en el código es `8001`:

```bash
CHROMA_HOST=localhost CHROMA_PORT=8001 python -m src.agente.indexar_esquema
```

El script genera embeddings con `all-MiniLM-L6-v2` y realiza un `upsert` idempotente en la colección `faro_gold_schema`.

**Verificación local:**
```bash
curl -f -s http://localhost:8001/api/v2/heartbeat
```

**Rollback local:** Si el nuevo esquema genera problemas, revertir el código y re-indexar:
```bash
git checkout <COMMIT_ANTERIOR> -- src/agente/indexar_esquema.py
CHROMA_HOST=localhost CHROMA_PORT=8001 python -m src.agente.indexar_esquema
```

Para regenerar desde cero:
```bash
docker compose stop chromadb
docker volume rm faro-chroma-data
docker compose up -d chromadb
CHROMA_HOST=localhost CHROMA_PORT=8001 python -m src.agente.indexar_esquema
```

### 2.2 Producción (Cloud Run — sidecar con índice horneado)

En producción, ChromaDB corre como **sidecar** (2.º contenedor en el servicio `faro-api`, comunicación por `localhost:8000` sin TLS). El índice vectorial está **horneado dentro de la imagen del sidecar** — no se indexa en runtime (Cloud_Run_Deploy.md §4.6b).

La imagen del sidecar se construye sobre el **digest amd64** de `chromadb/chroma` (inmutable, no la etiqueta `:latest`), copiando el directorio `faro_chroma_index/` capturado desde un ChromaDB local ya indexado.

**Procedimiento para actualizar el índice en producción:**
1. Indexar localmente con el script (§2.1)
2. Capturar el directorio `faro_chroma_index/` del volumen local
3. Construir y publicar una nueva imagen sellada del sidecar
4. Actualizar la especificación YAML multi-contenedor con la nueva imagen
5. `gcloud run services replace` **sin tráfico** (revisión canary)
6. Validar con smoke tests (§3)
7. Promover el 100% del tráfico a la nueva revisión

> ⚠️ **Pendiente operativo (Luis Téllez):** No existe en el repositorio un `Dockerfile` ni un script reproducible para construir la imagen del sidecar. El procedimiento actual (§4.6b de Cloud_Run_Deploy.md) fue ejecutado manualmente por Luis. Hasta que se automatice, la reconstrucción del sidecar requiere coordinación directa con él.

**Rollback de producción:** Regresar el tráfico a la revisión anterior (§4 de esta guía). **No** borrar volúmenes locales — el volumen local no afecta producción.

---

## 3. Verificación Post-Deploy (Smoke Tests)

### 3.1 Healthcheck y versión (públicos)
```bash
curl -f -s https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/health
curl -f -s https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/version
```
*Salida esperada:* `{"status":"ok"}` y el commit SHA coincidente con la imagen desplegada.

### 3.2 Validación de autenticación (SEC-006)
Con `AUTH_LECTURA_PUBLICA=false`, las rutas de datos y del agente exigen sesión autenticada:
```bash
# Sin token → debe responder 401 (confirma SEC-006):
curl -s -o /dev/null -w '%{http_code}' \
  -X POST https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/agente/consulta \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "test"}'
# Salida esperada: 401
```

### 3.3 Smoke test del Agente Conversacional (con autenticación)
Obtener un token de sesión válido vía el flujo OAuth (`/api/v1/auth/login`) y ejecutar:
```bash
curl -X POST https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/agente/consulta \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN_DE_SESION>" \
  -d '{"pregunta": "¿Cuántas escuelas están registradas en el sistema?"}'
```
*Salida esperada:* `fuera_de_alcance: false`, `sql_generado` no nulo con consulta SELECT sobre `gold.*`, SQL de sólo lectura, y redacción en español.

> ⚠️ **Nunca incluir tokens reales** en este documento ni en el historial de git.

---

## 4. Procedimiento de Rollback Inmediato

Si una nueva revisión de `faro-api` presenta errores de latencia, fallas de LLM o regresiones:
1. Listar las últimas revisiones activas:
   ```bash
   gcloud run revisions list --service=faro-api --region=us-central1 --project=faro-escuela-sensor
   ```
2. Revertir el 100% del tráfico a la revisión previa estable:
   ```bash
   gcloud run services update-traffic faro-api \
     --to-revisions=REVISION_ESTABLE_ANTERIOR=100 \
     --region=us-central1 \
     --project=faro-escuela-sensor
   ```
