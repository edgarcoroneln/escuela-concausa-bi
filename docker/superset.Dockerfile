# Usamos la imagen oficial que pidió el equipo
FROM apache/superset:latest

# Cambiamos a usuario root temporalmente para poder instalar paquetes y copiar
USER root

# Instalamos el conector de Postgres y Authlib.
# IMPORTANTE: apache/superset ejecuta Superset desde el venv /app/.venv,
# gestionado con `uv` (el venv no tiene pip y el Python del sistema es otro).
# Con `pip install` a secas el paquete cae en /usr/local y Postgres nunca
# conecta ("No module named 'psycopg2'" al crear cualquier dataset).
#   • psycopg2-binary → conexión a Postgres (metadata y datasets).
#   • authlib → REQUERIDO por Flask-AppBuilder al activar AUTH_TYPE=AUTH_OAUTH
#     (Google SSO). Esta imagen base NO lo incluye; sin él, arrancar con SSO
#     falla con "ModuleNotFoundError: No module named 'authlib'" (cazado en
#     smoke local antes del deploy).
RUN uv pip install --python /app/.venv/bin/python --no-cache psycopg2-binary authlib

# Configuración de FARO (metadata desde DATABASE_*, SECRET_KEY, caché, ProxyFix,
# rol público tras flag). Superset la aplica como override de sus defaults.
COPY docker/superset_config.py /app/pythonpath/superset_config.py
ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

# Entrypoint self-contained: en Cloud Run NO hay volúmenes, así que el script
# de arranque va DENTRO de la imagen (en docker-compose además se monta por
# volumen sobre la misma ruta; el contenido es idéntico).
COPY docker/superset-init.sh /app/superset-init.sh
RUN chmod +x /app/superset-init.sh

# Regresamos al usuario seguro de superset
USER superset

# Arranque por defecto (Cloud Run lo usa tal cual; docker-compose lo repite en
# su `command:`). El script decide dev vs prod según ENVIRONMENT.
CMD ["/bin/bash", "/app/superset-init.sh"]
