# FARO API - Dockerfile
# Imagen optimizada para FastAPI en Cloud Run

FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/

# Puerto de Cloud Run
ENV PORT=8080
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# Sello de la imagen: el SHA del commit con el que se construyó.
# Se pasa con `--build-arg GIT_SHA=$(git rev-parse HEAD)` y lo lee /api/v1/version
# vía la variable de entorno GIT_COMMIT. Sin el build-arg queda "dev" (build local
# sin sellar). Va DESPUÉS de los COPY para no invalidar la capa de `pip install`.
ARG GIT_SHA=dev
ENV GIT_COMMIT=${GIT_SHA}

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/api/v1/health').read()" || exit 1

# Comando de inicio
CMD uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT}
