# ═══════════════════════════════════════════════════════════════════════
# FARO Web — Dockerfile del shell Streamlit (US-526)
# ═══════════════════════════════════════════════════════════════════════
# Owner: Luis Téllez Domínguez (Célula 5 · Cloud & DevOps)
#
# Shell unificado de una sola URL: login OAuth vía la API (US-405) + dashboards
# de Superset embebidos (US-206) + panel de ML (US-207) + chat del agente (US-305).
# El CÓDIGO del shell (src/frontend/) es propiedad de la Célula 2 (Manuel Serranía);
# aquí solo se conteneriza para servirlo, igual que docker/api.Dockerfile con la API.
#
# La MISMA imagen corre en ambos ambientes:
#   • local (docker compose)          → PORT=8501
#   • prod  (Cloud Run, inyecta $PORT) → PORT=8080
# ═══════════════════════════════════════════════════════════════════════
FROM python:3.11-slim

WORKDIR /app

# Solo las dependencias del shell (streamlit + httpx). Archivo propio de C5 para no
# arrastrar todo requirements.txt raíz a un contenedor que únicamente sirve Streamlit.
COPY docker/frontend-requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Código del shell (propiedad de C2; se copia tal cual, no se modifica aquí).
COPY src/frontend/ ./src/frontend/

# Streamlit headless: sin abrir navegador, sin telemetría, sin banner de correo.
# Por ENV para que valga igual si algún día se arranca a mano dentro del contenedor.
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV PYTHONUNBUFFERED=1

# Puerto: default local 8501; Cloud Run lo sobreescribe con $PORT (8080).
ENV PORT=8501

# Sello de la imagen con el SHA del commit (mismo patrón que api.Dockerfile).
# Se pasa con --build-arg GIT_SHA=$(git rev-parse HEAD); sin él queda "dev".
# Va DESPUÉS de los COPY para no invalidar la capa de pip install.
ARG GIT_SHA=dev
ENV GIT_COMMIT=${GIT_SHA}

EXPOSE 8501

# Health check con la sonda propia de Streamlit (/_stcore/health → "ok"); en python
# para no depender de curl en la imagen slim (mismo criterio que api.Dockerfile, BUG-006).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python3 -c "import urllib.request,os; urllib.request.urlopen('http://localhost:'+os.environ.get('PORT','8501')+'/_stcore/health').read()" || exit 1

# El script vive en src/frontend/ y hace `from auth import ...` (import plano): Streamlit
# añade el directorio del script a sys.path, así que arranca por ruta sin tocar PYTHONPATH.
# CORS/XSRF quedan en su default de Streamlit (activos); si el websocket no conectara
# detrás del proxy TLS de Cloud Run, se evalúa --server.enableCORS=false en el deploy.
CMD ["sh", "-c", "streamlit run src/frontend/app.py --server.port ${PORT} --server.address 0.0.0.0"]
