#!/bin/bash
# FARO - Build and Push Frontend (React) Docker Image to Artifact Registry
# Mismo patrón que build-and-push.sh (API), adaptado al frontend.
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID=$(gcloud config get-value project 2>/dev/null) || {
  echo "❌ Error: No se pudo obtener PROJECT_ID"
  echo "   Ejecuta: gcloud config set project TU_PROJECT_ID"
  exit 1
}

REGION="${REGION:-us-central1}"
IMAGE_NAME="${IMAGE_NAME:-faro-frontend}"
IMAGE_TAG="${1:-latest}"
GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo dev)"

# Origen ABSOLUTO del API, horneado en build-time para el botón de login (US-405,
# BUG-076). El login debe navegar directo al origen del API -- NO por el proxy del
# front -- o la cookie anti-CSRF `faro_oauth_state` se fija en el origen equivocado
# y el /callback da 401. Debe ser el MISMO valor (sin barra final) que la allowlist
# FRONTEND_REDIRECT_URIS del lado API (deploy-cloud-run.sh). Para otro entorno,
# exporta VITE_API_ORIGIN al invocar el script.
VITE_API_ORIGIN="${VITE_API_ORIGIN:-https://faro-api-eanzfglvyq-uc.a.run.app}"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/faro-images/${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${BLUE}🔨 Building Docker image (frontend)...${NC}"
echo "   Project: ${PROJECT_ID}"
echo "   Region: ${REGION}"
echo "   Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "   Commit: ${GIT_SHA}"
echo "   API origin (login): ${VITE_API_ORIGIN}"
echo ""

# --platform linux/amd64: Cloud Run corre amd64; en Mac Apple Silicon (arm64)
# Docker Desktop necesita esto explícito o hace un build que no arranca en prod.
docker build --platform linux/amd64 --build-arg VITE_API_ORIGIN="${VITE_API_ORIGIN}" -t ${IMAGE_URL} -f docker/frontend-react.Dockerfile .

echo ""
echo -e "${BLUE}📤 Pushing to Artifact Registry...${NC}"
docker push ${IMAGE_URL}

if [ "${IMAGE_TAG}" != "latest" ]; then
  LATEST_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/faro-images/${IMAGE_NAME}:latest"
  echo ""
  echo -e "${BLUE}🏷️  Tagging as latest...${NC}"
  docker tag ${IMAGE_URL} ${LATEST_URL}
  docker push ${LATEST_URL}
fi

echo ""
echo -e "${GREEN}✅ Imagen lista: ${IMAGE_URL}${NC}"
