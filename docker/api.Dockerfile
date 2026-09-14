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

# Hornea el modelo de embeddings del agente (paraphrase-multilingual-MiniLM-L12-v2, ~470 MB) en la
# imagen: así la 1.ª consulta RAG no depende de HuggingFace en runtime. Cloud Run usa instancias
# efímeras; sin esto, cada arranque en frío re-descargaría el modelo (lento y con dependencia de
# red). Se cachea en /root/.cache/huggingface y en runtime se sirve OFFLINE (ver HF_HUB_OFFLINE
# abajo). Va antes de COPY src/ para no depender del código y quedar cacheado.
#
# CRÍTICO: el nombre DEBE coincidir con el default de src/agente/recuperacion.py
# (NOMBRE_MODELO_EMBEDDINGS) y con el que indexó la colección de ChromaDB (indexar_esquema.py).
# Como runtime es OFFLINE, solo puede cargar un modelo ya cacheado aquí; si se hornea uno distinto
# del que pide el código, la carga offline falla -> ErrorRecuperacion -> el chat responde "El
# contexto de FARO no está disponible temporalmente" (bug detectado en la entrega 2026-09-14).
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Copiar código fuente
COPY src/ ./src/

# Assets geográficos que la sección "Cómo funciona / Modelo de datos" (US-601) lee del disco en
# runtime (src/api/v1/about.py: municipios_scope.geojson + mexico_silueta.geojson). Viven FUERA de
# src/, así que hay que copiarlos aparte; sin esto GET /api/v1/about/secciones/modelo-datos da 500
# (FileNotFoundError) y la pantalla "Cómo funciona" del front se rompe (bug de la entrega 2026-09-14).
COPY superset/assets/geojson/ ./superset/assets/geojson/

# Configuracion de logs (US-524a)
COPY docker/log_config.json ./log_config.json

# Puerto de Cloud Run
ENV PORT=8080
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# El modelo de embeddings ya está horneado (capa de arriba): en runtime se sirve SIEMPRE desde la
# cache local, sin tocar la red (Cloud Run egress = private-ranges-only).
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

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
