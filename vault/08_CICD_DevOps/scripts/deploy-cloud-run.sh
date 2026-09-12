#!/bin/bash
# FARO - Deploy to Cloud Run (Fase 2: API conectada a Cloud SQL privado)
#
# Redespliega el API FastAPI conectándolo a la base Gold en Cloud SQL a través de
# la red privada aprovisionada en Fase 1 (US-504), curando BUG-020 en producción:
#   - Corre con la service account de MÍNIMO PRIVILEGIO `faro-api-sa` (no la SA por
#     defecto de Compute, que estaba sobre-privilegiada).
#   - Alcanza Cloud SQL por su IP privada vía el Serverless VPC connector.
#   - Toma JWT_SECRET_KEY y la contraseña de la DB desde Secret Manager en runtime
#     (ya NO como env var en texto plano -> cierra la violación de Secrets_Policy.md).
# Mantiene el API público (--allow-unauthenticated) porque la rúbrica exige URL
# pública viva; las UIs admin NO son públicas (van tras IAP en Fase 3).
set -euo pipefail

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
PROJECT_ID=$(gcloud config get-value project 2>/dev/null) || {
  echo "❌ Error: No se pudo obtener PROJECT_ID"
  exit 1
}

REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-faro-api}"
IMAGE_NAME="${IMAGE_NAME:-faro-api}"
IMAGE_TAG="${1:-latest}"

# --- Fase 1 (US-504): recursos privados a los que se conecta el API ---
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-faro-api-sa@${PROJECT_ID}.iam.gserviceaccount.com}"
VPC_CONNECTOR="${VPC_CONNECTOR:-faro-connector}"
VPC_EGRESS="${VPC_EGRESS:-private-ranges-only}"   # solo el tráfico RFC1918 va por el connector

# Conexión a Cloud SQL (IP privada; la contraseña llega por Secret Manager, no aquí)
POSTGRES_HOST="${POSTGRES_HOST:-172.21.0.3}"       # IP privada de faro-postgres
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-faro}"
POSTGRES_USER="${POSTGRES_USER:-faro_app}"

# OAuth2 con Google (US-402, desbloquea a C4). El client_id y el redirect son PÚBLICOS (viajan en
# la URL de consentimiento del navegador) -> env vars. El client_secret es sensible -> Secret Manager.
GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID:-526490367142-gctkloa4dsnp7m56r0fu62n7ehuhpkcs.apps.googleusercontent.com}"
GOOGLE_REDIRECT_URI="${GOOGLE_REDIRECT_URI:-https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/auth/callback}"

# FRONTEND_REDIRECT_URIS: allowlist de orígenes del front a los que /auth/login vuelve tras el login
# con Google (US-405, ADR-012). La API compara el `redirect` recibido por COINCIDENCIA EXACTA, no por
# prefijo (src/api/config.py -> frontend_redirect_list; src/api/v1/auth.py:100). El React manda
# `window.location.origin` (SIN barra final ni ruta) -> el valor debe ser el ORIGEN EXACTO del front,
# sin `/` al final. Público (viaja en la URL) -> env var, no secreto. El default es la URL canónica de
# FARO Web (README / PROJECT_INDEX "entrada principal"); Cloud Run también responde en el alias con
# número de proyecto (faro-frontend-526490367142.us-central1.run.app) y `window.location.origin`
# refleja el que el usuario abra, así que si el recorrido usará ese alias u otro origen, AÑÁDELO. Para
# VARIOS orígenes son valores separados por coma; como --set-env-vars ya separa pares por coma, fíjalo
# aparte con delimitador alterno (--update-env-vars="^|^FRONTEND_REDIRECT_URIS=https://a,https://b").
FRONTEND_REDIRECT_URIS="${FRONTEND_REDIRECT_URIS:-https://faro-frontend-eanzfglvyq-uc.a.run.app}"

# ANALISTA_EMAILS: allowlist del rol `analista` (US-403). DUEÑO: PO/Edgar (correo definido).
# Se LEE del entorno y se pasa en --set-env-vars de abajo. NO se versiona ningún correo aquí
# (dato personal -> Secrets_Policy.md). Vacío por defecto => todos `ciudadano`. Para desplegar
# con analistas, inyéctalo EFÍMERO al invocar el script (no queda en el repo, solo en la revisión):
#   ANALISTA_EMAILS=<correo-del-analista> ./deploy-cloud-run.sh
# OJO con la coma: --set-env-vars separa pares por ",". Con UN correo va directo; para VARIOS usa
# el delimitador alterno de gcloud (--set-env-vars="^@^K1=v1@ANALISTA_EMAILS=a@x,b@y") o --update-env-vars.
ANALISTA_EMAILS="${ANALISTA_EMAILS:-}"

# Secretos inyectados en runtime desde Secret Manager (nunca en la imagen ni en env plano)
SECRETS="JWT_SECRET_KEY=jwt-secret-key:latest,POSTGRES_PASSWORD=db-password:latest,GOOGLE_CLIENT_SECRET=google-client-secret:latest"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/faro-images/${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${BLUE}🚀 Desplegando FARO API a Cloud Run...${NC}"
echo "   Project: ${PROJECT_ID}"
echo "   Region: ${REGION}"
echo "   Service: ${SERVICE_NAME}"
echo "   Image: ${IMAGE_URL}"
echo "   Service Account: ${SERVICE_ACCOUNT}"
echo "   VPC Connector: ${VPC_CONNECTOR} (egress: ${VPC_EGRESS})"
echo "   Cloud SQL: ${POSTGRES_USER}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
echo "   OAuth Google: redirect=${GOOGLE_REDIRECT_URI} (client_secret desde Secret Manager)"
echo "   Front redirect allowlist: ${FRONTEND_REDIRECT_URIS}"
echo ""

gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URL} \
  --platform=managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --service-account=${SERVICE_ACCOUNT} \
  --vpc-connector=${VPC_CONNECTOR} \
  --vpc-egress=${VPC_EGRESS} \
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300s \
  --set-env-vars="ENVIRONMENT=production,POSTGRES_HOST=${POSTGRES_HOST},POSTGRES_PORT=${POSTGRES_PORT},POSTGRES_DB=${POSTGRES_DB},POSTGRES_USER=${POSTGRES_USER},GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID},GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI},FRONTEND_REDIRECT_URIS=${FRONTEND_REDIRECT_URIS},ANALISTA_EMAILS=${ANALISTA_EMAILS}" \
  --set-secrets="${SECRETS}"

echo ""
echo -e "${GREEN}✅ Deploy completado${NC}"
echo ""
echo -e "${GREEN}🌐 URL del servicio:${NC}"
gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)'
