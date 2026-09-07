# FARO API - Dockerfile
# Imagen optimizada para FastAPI en Cloud Run

FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Dependencias de runtime del AGENTE conversacional (US-304 / BUG-025): RAG + LLM.
# Fuente de verdad de los pines: requirements/celula-3.txt (Célula 3). Aquí se instala SOLO
# el subconjunto que la API necesita en runtime (no todo celula-3.txt, que arrastra mlflow,
# streamlit, etc. ajenos a la API). torch se toma CPU-only del índice de PyTorch para evitar
# la variante CUDA (~2 GB) en linux/amd64: Cloud Run no tiene GPU. Validado en local con
# chromadb 1.5.9 · sentence-transformers 5.7.0 · anthropic 1.4.0 · torch 2.14.0.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir \
      chromadb==1.5.9 \
      sentence-transformers==5.7.0 \
      "anthropic>=0.116"

# Copiar código fuente
COPY src/ ./src/

# Configuracion de logs (US-524a)
COPY docker/log_config.json ./log_config.json

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
CMD uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT} --log-config log_config.json
