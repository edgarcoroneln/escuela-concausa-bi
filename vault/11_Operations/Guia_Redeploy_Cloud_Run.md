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

## 2. Re-despliegue del Sidecar de ChromaDB

> ⚠️ **Importante:** El índice vectorial de ChromaDB está **horneado dentro de la imagen del sidecar** (no se indexa en runtime por políticas de seguridad y velocidad de cold start). Si Andrés modifica `src/agente/indexar_esquema.py` o agrega nuevos chunks al esquema Gold, se debe regenerar la imagen del sidecar:

1. Generar nuevo índice localmente:
   ```bash
   python -m src.agente.indexar_esquema
   ```
2. Reconstruir imagen con índice horneado:
   ```bash
   docker build -f docker/chromadb.Dockerfile -t us-central1-docker.pkg.dev/faro-escuela-sensor/faro-repo/faro-chromadb:latest .
   docker push us-central1-docker.pkg.dev/faro-escuela-sensor/faro-repo/faro-chromadb:latest
   ```
3. Re-desplegar la revisión multi-contenedor en Cloud Run especificando la nueva imagen del contenedor `chromadb`.

---

## 3. Verificación Post-Deploy (Smoke Tests)

### 1. Healthcheck y versión
```bash
curl -f -s https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/health
curl -f -s https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/version
```
*Salida esperada:* `{"status":"ok"}` y el commit SHA coincidente con el commit desplegado.

### 2. Smoke test del Agente Conversacional
Ejecutar consulta de verificación contra el endpoint en vivo (utilizando token o en lectura pública):
```bash
curl -X POST https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/agente/consulta \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Cuántas escuelas están registradas en el sistema?"}'
```
*Salida esperada:* `fuera_de_alcance: false`, `sql_generado` no nulo con consulta SELECT sobre `gold.*`, y redacción en español.

---

## 4. Procedimiento de Rollback Inmediato

Si una nueva revisión presenta errores de latencia, fallas de LLM o regresiones no detectadas:
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
