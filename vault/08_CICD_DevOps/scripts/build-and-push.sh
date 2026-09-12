#!/bin/bash
# FARO - Build and Push Docker Image to Artifact Registry
set -euo pipefail

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Obtener PROJECT_ID de gcloud
PROJECT_ID=$(gcloud config get-value project 2>/dev/null) || {
  echo "❌ Error: No se pudo obtener PROJECT_ID"
  echo "   Ejecuta: gcloud config set project TU_PROJECT_ID"
  exit 1
}

REGION="${REGION:-us-central1}"
IMAGE_NAME="${IMAGE_NAME:-faro-api}"
IMAGE_TAG="${1:-latest}"

# Sello de la imagen: SHA del commit construido. Lo lee /api/v1/version (ENV GIT_COMMIT
# en el Dockerfile) para saber qué imagen corre en prod. Sin git, cae a "dev".
GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo dev)"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/faro-images/${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${BLUE}🔨 Building Docker image...${NC}"
echo "   Project: ${PROJECT_ID}"
echo "   Region: ${REGION}"
echo "   Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "   Commit: ${GIT_SHA}"
echo ""

# Cloud Run ejecuta linux/amd64. En hosts arm64 (Docker Desktop en Mac Apple Silicon)
# sin --platform se construye una imagen arm64 que Cloud Run no puede correr (exec
# format error). Forzamos amd64 siempre; en CI/hosts amd64 es no-op (BUG-080).
docker build --platform linux/amd64 --build-arg GIT_SHA="${GIT_SHA}" -t ${IMAGE_URL} -f docker/api.Dockerfile .

echo ""
echo -e "${BLUE}📤 Pushing to Artifact Registry...${NC}"
docker push ${IMAGE_URL}

# También actualizar 'latest' si no es el tag actual
if [ "${IMAGE_TAG}" != "latest" ]; then
  LATEST_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/faro-images/${IMAGE_NAME}:latest"
  echo ""
  echo -e "${BLUE}🏷️  Tagging as latest...${NC}"
  docker tag ${IMAGE_URL} ${LATEST_URL}
  docker push ${LATEST_URL}
fi

echo ""
echo -e "${GREEN}✅ Imagen lista: ${IMAGE_URL}${NC}"
