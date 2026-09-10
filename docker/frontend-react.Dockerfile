# FARO Frontend (React) - Dockerfile
# Build multi-stage: compila el SPA con Vite y lo sirve estático con nginx.
# Reemplaza al frontend de Streamlit (src/frontend) para el rediseño pedido
# por el Dr. (100% custom, cero Superset/Streamlit visible).

# --- Etapa 1: build ---
FROM node:22-alpine AS build
WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps

COPY frontend/ .
# Usa frontend/.env.production (VITE_API_BASE_URL apuntando a faro-api de prod).
RUN npm run build

# --- Etapa 2: runtime (nginx sirviendo estáticos, non-root) ---
# nginx-unprivileged: mismo nginx oficial, pero corre como usuario "nginx" (uid 101)
# en vez de root. Pedido de Christian en la revisión de seguridad del gate (10-sep):
# el frontend.Dockerfile viejo (el de Streamlit) corre root; este no debe.
FROM nginxinc/nginx-unprivileged:1.27-alpine

USER root

COPY docker/nginx-frontend.conf.template /etc/nginx/nginx.conf.template
COPY docker/frontend-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

COPY --from=build /app/dist /usr/share/nginx/html

# El entrypoint escribe /etc/nginx/nginx.conf en runtime (envsubst de $PORT),
# así que el usuario nginx necesita permiso de escritura ahí, no solo lectura.
RUN chown -R nginx:nginx /usr/share/nginx/html /etc/nginx

USER nginx

# Cloud Run inyecta PORT en runtime (default 8080 en local/build).
ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null "http://localhost:${PORT}/" || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
