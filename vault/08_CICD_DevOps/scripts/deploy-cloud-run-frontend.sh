#!/bin/bash
# FARO - Deploy Frontend (React) to Cloud Run
#
# A diferencia del API, el frontend es un SPA estático servido por nginx:
#   - No lleva Secret Manager ni VPC connector (no toca la DB directo).
#   - Camino B (ADR-012): el navegador habla con el API por el MISMO origen
#     vía proxy_pass de nginx (/api, /auth) -> NO usa CORS ni VITE_API_BASE_URL.
#     El origen del API se hornea en build-time (VITE_API_ORIGIN, BUG-076) solo
#     para el botón de login, que navega directo al origen del API.
#   - CPU: nginx es request-driven, no necesita CPU siempre asignada. Se fija
#     --cpu-throttling (CPU solo durante requests) -> 256Mi basta. Sin el flag,
#     el deploy hereda el --no-cpu-throttling del Streamlit previo y Cloud Run
#     exige >=512Mi con la CPU siempre asignada.
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID=$(gcloud config get-value project 2>/dev/null) || {
  echo "❌ Error: No se pudo obtener PROJECT_ID"
  exit 1
}

REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-faro-frontend}"
IMAGE_NAME="${IMAGE_NAME:-faro-frontend}"
IMAGE_TAG="${1:-latest}"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/faro-images/${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${BLUE}🚀 Desplegando FARO Frontend a Cloud Run...${NC}"
echo "   Project: ${PROJECT_ID}"
echo "   Region: ${REGION}"
echo "   Service: ${SERVICE_NAME}"
echo "   Image: ${IMAGE_URL}"
echo ""

gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URL} \
  --platform=managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --port=8080 \
  --memory=256Mi \
  --cpu=1 \
  --cpu-throttling \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60s

echo ""
echo -e "${GREEN}✅ Deploy completado${NC}"
echo ""
echo -e "${GREEN}🌐 URL del servicio:${NC}"
gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)'
