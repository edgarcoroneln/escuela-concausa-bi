---
id: DOC-CLOUD-RUN-DEPLOY
title: "Procedimiento de Deploy a Cloud Run"
owner: "Luis Téllez Domínguez"
status: active
version: "1.1"
traces_up: ["US-501", "US-505", "REQ-005"]
tags: [devops, gcp, cloud-run, deployment, sprint-1, fase-2]
date: "2026-08-09"
---

# Deploy a Cloud Run — FARO API

> Procedimiento completo para desplegar la API de FARO a Google Cloud Run.
> Implementado en Sprint 1 (US-501).

---

## 1. Requisitos Previos

### Herramientas instaladas
- ✅ Docker Desktop
- ✅ gcloud CLI (versión 579.0.0+)
- ✅ Git

### Configuración de GCP
- ✅ Cuenta de Google con acceso a GCP
- ✅ Organización: `luis-g-roses-org` (ID: 196009726606)
- ✅ Proyecto: `faro-escuela-sensor`
- ✅ Billing habilitado

---

## 2. Configuración Inicial de GCP (Una sola vez)

### 2.1 Autenticación

```bash
# Autenticar con tu cuenta de Google
gcloud auth login

# Verificar cuenta activa
gcloud auth list
```

### 2.2 Configurar proyecto

```bash
# Seleccionar proyecto
gcloud config set project faro-escuela-sensor

# Configurar región por defecto
gcloud config set run/region us-central1

# Verificar configuración
gcloud config list
```

**Salida esperada:**
```
[core]
account = luis.g.roses@gmail.com
project = faro-escuela-sensor

[run]
region = us-central1
```

### 2.3 Habilitar APIs necesarias

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

**Tiempo:** ~1-2 minutos

### 2.4 Crear Artifact Registry

```bash
gcloud artifacts repositories create faro-images \
  --repository-format=docker \
  --location=us-central1 \
  --description="FARO Docker images repository"
```

**Verificar:**
```bash
gcloud artifacts repositories list --location=us-central1
```

### 2.5 Configurar Docker para Artifact Registry

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

Esto modifica `~/.docker/config.json` para autenticarse automáticamente.

---

## 3. Build y Push de Imagen Docker

### 3.1 Usando el script automatizado (Recomendado)

```bash
cd /Users/luistellez/Documents/BI/escuela-concausa-bi

# Build y push con tag específico
./08_CICD_DevOps/scripts/build-and-push.sh v0.1.0-s1

# O con el tag latest (por defecto)
./08_CICD_DevOps/scripts/build-and-push.sh
```

**¿Qué hace el script?**
1. Build de la imagen Docker para arquitectura `linux/amd64`
2. Tag como: `us-central1-docker.pkg.dev/faro-escuela-sensor/faro-images/faro-api:TAG`
3. Push a Artifact Registry
4. También taguea como `:latest` si no es el tag actual

### 3.2 Comandos manuales (si el script falla)

```bash
# Variables
PROJECT_ID=faro-escuela-sensor
REGION=us-central1
IMAGE_NAME=faro-api
IMAGE_TAG=v0.1.0-s1

# Build para arquitectura amd64 (Cloud Run requirement)
docker buildx build --platform linux/amd64 \
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/faro-images/${IMAGE_NAME}:${IMAGE_TAG} \
  -f docker/api.Dockerfile \
  --push \
  .
```

**Tiempo estimado:** 3-5 minutos (primera vez), ~30 segundos (builds siguientes con caché)

---

## 4. Deploy a Cloud Run

### 4.1 Usando el script automatizado (Recomendado)

```bash
# Deploy con tag específico
./08_CICD_DevOps/scripts/deploy-cloud-run.sh v0.1.0-s1

# O con latest (por defecto)
./08_CICD_DevOps/scripts/deploy-cloud-run.sh
```

### 4.2 Comando manual

```bash
gcloud run deploy faro-api \
  --image=us-central1-docker.pkg.dev/faro-escuela-sensor/faro-images/faro-api:v0.1.0-s1 \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --timeout=300s \
  --set-env-vars="ENVIRONMENT=production"
```

**Parámetros clave:**
- `--allow-unauthenticated`: Acceso público (Sprint 1)
- `--port=8080`: Puerto estándar de Cloud Run
- `--memory=512Mi`: Suficiente para FastAPI
- `--cpu=1`: 1 vCPU
- `--max-instances=1`: **Límite de seguridad** (proyecto académico)
- `--min-instances=0`: Scale to zero cuando no hay tráfico
- `--timeout=300s`: 5 minutos máximo por request

**Tiempo estimado:** 1-2 minutos

### 4.3 Deploy productivo — Fase 2 (US-505): API ↔ Cloud SQL privado

A partir de Fase 2, el deploy **conecta el API a la base Gold en Cloud SQL** por la
red privada de Fase 1 (US-504) y toma los secretos de **Secret Manager**. El script
`deploy-cloud-run.sh` ya incluye estos parámetros por defecto (overridables por env):

```bash
# Redeploy productivo con la imagen conocida (no requiere rebuild si sólo cambia config)
./08_CICD_DevOps/scripts/deploy-cloud-run.sh v0.2.1-hotfix-bug008
```

Comando equivalente:

```bash
gcloud run deploy faro-api \
  --image=us-central1-docker.pkg.dev/faro-escuela-sensor/faro-images/faro-api:v0.2.1-hotfix-bug008 \
  --platform=managed --region=us-central1 --allow-unauthenticated \
  --service-account=faro-api-sa@faro-escuela-sensor.iam.gserviceaccount.com \
  --vpc-connector=faro-connector --vpc-egress=private-ranges-only \
  --port=8080 --memory=512Mi --cpu=1 --min-instances=0 --max-instances=10 --timeout=300s \
  --set-env-vars="ENVIRONMENT=production,POSTGRES_HOST=172.21.0.3,POSTGRES_PORT=5432,POSTGRES_DB=faro,POSTGRES_USER=faro_app" \
  --set-secrets="JWT_SECRET_KEY=jwt-secret-key:latest,POSTGRES_PASSWORD=db-password:latest"
```

**Parámetros nuevos vs. Sprint 1:**
- `--service-account=faro-api-sa`: **mínimo privilegio** (ya no la SA por defecto de Compute).
- `--vpc-connector=faro-connector` + `--vpc-egress=private-ranges-only`: el API alcanza
  Cloud SQL por **IP privada** (`172.21.0.3`); la DB nunca se expone a Internet.
- `--set-secrets=...`: `JWT_SECRET_KEY` y `POSTGRES_PASSWORD` se inyectan desde Secret
  Manager en runtime → **ya no viajan como env var en texto plano** (cierra la violación
  de `07_Security/Secrets_Policy.md`).
- `--set-env-vars` sólo lleva parámetros **no sensibles** de conexión.

**Poblar Gold en Cloud SQL (una vez, antes del primer redeploy productivo):** como la
instancia sólo tiene IP privada, se pobló con IP pública **temporal** + Cloud SQL Auth
Proxy (contenedor oficial, token OAuth efímero) reusando la vía de fixtures Bronze +
`dbt run` acotado; se quitó la IP pública al terminar. Detalle en el DevLog
[[_DevLog/2026-08-29-luis-tellez-us505-fase2-gold-cloudsql-redeploy]].

### 4.4 Redeploy con **imagen nueva** (cambia el código, no sólo la config)

Cuando el cambio está en `src/` (p.ej. desplegar en prod un fix ya mergeado a `main`),
el §4.3 no basta: hay que **reconstruir y publicar** la imagen antes de desplegar.

> ⚠️ **Arquitectura:** `build-and-push.sh` usa `docker build` sin `--platform`, así que en
> un Mac Apple Silicon (arm64) produciría una imagen que Cloud Run **rechaza** (`Container
> manifest type ... not supported`, ver §10). Construye siempre con `buildx --platform
> linux/amd64`.

```bash
# 1) Build + push (amd64) con un tag inmutable nuevo
docker buildx build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/faro-escuela-sensor/faro-images/faro-api:<TAG> \
  -f docker/api.Dockerfile --push .

# 2) Deploy: el script preserva SA / VPC connector / secretos de Fase 2 (§4.3)
./08_CICD_DevOps/scripts/deploy-cloud-run.sh <TAG>
```

**Ejemplo real (BUG-025):** el fix de `src/api/v1/agente.py` (PR #142, C4) estaba en `main`
pero prod seguía sirviendo el stub porque corría la imagen `v0.2.1-hotfix-bug008` (Fase 2 no
hizo rebuild). Se reconstruyó como **`v0.2.2-bug025`** y se desplegó → revisión
**`faro-api-00006-q8f`**. Verificado en prod: `/agente/consulta` ya **no** es el stub (degrada
seguro, `sql_generado:null`, la frase destructiva ya no se acepta) y `/escuelas` sigue 200 con
25 escuelas. El RAG real sigue pendiente de C3 (LLM) + añadir `chromadb`/`sentence-transformers`
a la imagen. Detalle en [[_DevLog/2026-08-29-luis-tellez-bug025-redeploy-agente-prod]].

---

## 5. Verificación del Deploy

### 5.1 Obtener la URL del servicio

```bash
gcloud run services describe faro-api \
  --region=us-central1 \
  --format='value(status.url)'
```

**URL actual:**
```
https://faro-api-eanzfglvyq-uc.a.run.app
```

### 5.2 Probar endpoints

```bash
# Endpoint raíz
curl https://faro-api-eanzfglvyq-uc.a.run.app

# Health check
curl https://faro-api-eanzfglvyq-uc.a.run.app/health

# Info del proyecto
curl https://faro-api-eanzfglvyq-uc.a.run.app/info

# Swagger UI (abrir en navegador)
open https://faro-api-eanzfglvyq-uc.a.run.app/docs
```

**Respuesta esperada del endpoint raíz:**
```json
{
  "message": "Hello World from FARO",
  "project": "Escuela como Sensor Social",
  "description": "Plataforma de BI end-to-end para predicción de matrícula escolar",
  "timestamp": "2026-08-09T23:53:37.270629",
  "environment": "production",
  "version": "0.1.0",
  "sprint": "S1",
  "status": "operational"
}
```

### 5.3 Verificar logs

```bash
# Logs en tiempo real
gcloud run services logs tail faro-api --region=us-central1

# Logs recientes
gcloud run services logs read faro-api --region=us-central1 --limit=50
```

---

## 6. Configuración de Seguridad

### 6.1 Límite de instancias (Ya configurado)

```bash
# Verificar límite actual
gcloud run services describe faro-api \
  --region=us-central1 \
  --format='value(spec.template.spec.containerConcurrency,spec.template.metadata.annotations.autoscaling\.knative\.dev/maxScale)'
```

**Configurado:** `maxScale = 1` (una instancia máxima)

**Razón:** Proyecto académico, protección contra costos inesperados.

### 6.2 Alertas de presupuesto (Recomendado)

Ve a: https://console.cloud.google.com/billing/budgets

1. Crear presupuesto: $10/mes
2. Alertas al 50%, 90%, 100%
3. Notificaciones por email

---

## 7. Actualización del Servicio

### 7.1 Flujo completo de actualización

```bash
# 1. Build nueva imagen con nuevo tag
./08_CICD_DevOps/scripts/build-and-push.sh v0.2.0

# 2. Deploy nueva versión
./08_CICD_DevOps/scripts/deploy-cloud-run.sh v0.2.0

# 3. Cloud Run hace rolling update automáticamente
# (0 downtime)
```

### 7.2 Rollback a versión anterior

```bash
# Listar revisiones
gcloud run revisions list --service=faro-api --region=us-central1

# Volver a revisión anterior
gcloud run services update-traffic faro-api \
  --region=us-central1 \
  --to-revisions=faro-api-00001=100
```

**Tiempo de rollback:** ~30 segundos

---

## 8. Monitoreo y Observabilidad

### 8.1 Cloud Logging

**URL:** https://console.cloud.google.com/logs

**Filtro para FARO API:**
```
resource.type="cloud_run_revision"
resource.labels.service_name="faro-api"
```

### 8.2 Cloud Monitoring

**URL:** https://console.cloud.google.com/monitoring

**Métricas clave:**
- Request count
- Request latency (p50, p95, p99)
- Instance count
- Memory utilization
- CPU utilization

### 8.3 Uptime checks (Sprint 2)

Pendiente de configuración en próximo sprint.

---

## 9. Costos

### 9.1 Free Tier de Cloud Run (mensual)

- ✅ 2,000,000 requests GRATIS
- ✅ 360,000 GB-seconds GRATIS
- ✅ 180,000 vCPU-seconds GRATIS

### 9.2 Estimación de costos para FARO (Sprint 1)

**Configuración actual:**
- Memory: 512 Mi
- CPU: 1 vCPU
- Max instances: 1
- Tráfico estimado: 100-500 requests/día

**Costo mensual estimado:**
- Cloud Run: $0 (dentro de free tier)
- Artifact Registry: $0 (0.5 GB, dentro de free tier)
- Cloud Build: $0 (dentro de free tier)

**Total:** $0/mes ✅

### 9.3 Proyección futura (Sprint 4-6)

Cuando se agregue Cloud SQL y mayor tráfico:
- Cloud Run: $2-5/mes
- Cloud SQL (db-f1-micro): $30-40/mes
- Artifact Registry: $0.50/mes
- **Total estimado:** $35-50/mes

---

## 10. Troubleshooting

### Error: "API not enabled"

**Solución:**
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

### Error: "Permission denied"

**Causa:** Tu cuenta no tiene permisos suficientes.

**Solución:**
1. Verificar roles en la consola de IAM
2. Requiere al menos: `roles/run.admin`, `roles/artifactregistry.admin`

### Error: "Container manifest type not supported"

**Causa:** Imagen construida para arquitectura incorrecta (arm64 en Mac M1/M2).

**Solución:**
```bash
# Build específico para amd64
docker buildx build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/faro-escuela-sensor/faro-images/faro-api:TAG \
  -f docker/api.Dockerfile \
  --push \
  .
```

### Servicio no responde

**Diagnóstico:**
```bash
# Ver logs de error
gcloud run services logs read faro-api --region=us-central1 --limit=100

# Ver detalles del servicio
gcloud run services describe faro-api --region=us-central1
```

### Cold start lento (>3 segundos)

**Causa:** `min-instances=0` (scale to zero)

**Solución (Sprint 4):**
```bash
gcloud run services update faro-api \
  --region=us-central1 \
  --min-instances=1
```

**Costo adicional:** ~$10-15/mes por mantener 1 instancia siempre activa.

---

## 11. Recursos y Referencias

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/best-practices)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [[03_Architecture/System_Design]] — Diseño completo del sistema
- [build-and-push.sh](scripts/build-and-push.sh) — Script de build y push
- [deploy-cloud-run.sh](scripts/deploy-cloud-run.sh) — Script de deploy

---

## 12. Próximos Pasos (Sprints futuros)

**Sprint 2:**
- CI/CD automatizado con GitHub Actions
- Deploy automático en cada merge a `main`

**Sprint 4:**
- Cloud SQL provisionado
- VPC peering (Cloud Run ↔ Cloud SQL)
- Secret Manager para credenciales
- Autenticación OAuth2/JWT

**Sprint 6:**
- Uptime checks y alertas
- Observabilidad completa
- Runbooks de operación
- Sistema productivo estable para demo del 9 de septiembre

---

**Última actualización:** 2026-08-29 (v1.1 · §4.3 deploy productivo Fase 2, US-505)  
**Sprint:** S1 (base) · S4 (Fase 2)  
**Owner:** Luis Téllez Domínguez  
**Status:** ✅ Completado y verificado (BUG-020 curado en prod)
