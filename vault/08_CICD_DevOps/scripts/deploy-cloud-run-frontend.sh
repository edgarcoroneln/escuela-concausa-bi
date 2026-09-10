#!/bin/bash
# FARO - Deploy Frontend (React) to Cloud Run
#
# A diferencia del API, el frontend es un SPA estático servido por nginx:
#   - No lleva Secret Manager ni VPC connector (no toca la DB directo).
#   - Llama al API real (faro-api) por su URL pública desde el navegador
#     (VITE_API_BASE_URL, ver frontend/.env.production) -> requiere que el
#     API tenga CORS habilitado para el origin de este servicio (pendiente
#     de confirmar con C4/Christian si no está ya abierto).
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
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60s

echo ""
echo -e "${GREEN}✅ Deploy completado${NC}"
echo ""
echo -e "${GREEN}🌐 URL del servicio:${NC}"
gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)'
