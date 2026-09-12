# FARO Frontend (React) - Dockerfile
# Build multi-stage: compila el SPA con Vite y lo sirve estático con nginx.
# Reemplaza al frontend de Streamlit (src/frontend) para el rediseño pedido
# por el Dr. (100% custom, cero Superset/Streamlit visible).

# --- Etapa 1: build ---
FROM node:22-alpine AS build
WORKDIR /app

COPY frontend/package*.json ./
# --legacy-peer-deps retirado 11-sep (revisión de Edgar, PR #302): hacía falta
# por el choque de react-simple-maps/@observablehq/plot/prop-types/react-is
# contra React 19 -- las 4 se eliminaron esta misma revisión (no eran producto,
# ver Arquitectura_Frontend_React.md §9). `npm ci` corre limpio sin la bandera
# (verificado en local por Diana: 0 vulnerabilidades, 0 conflictos de peers).
RUN npm ci

COPY frontend/ .
# VITE_API_BASE_URL se queda vacío a propósito (corregido 11-sep, PR #302): las
# llamadas de DATOS van por rutas relativas al proxy_pass de este mismo nginx
# (mismo-origen, ADR-012). Su .env.production es local, no versionado
# (frontend/.gitignore), y un checkout limpio no lo necesita: cae al default ""
# de api.js. Eso NO se inyecta aquí.
#
# VITE_API_ORIGIN es DISTINTO y SÍ hay que hornearlo para prod (BUG-076): api.js
# lo usa SOLO para el botón de login (US-405), que debe navegar DIRECTO al origen
# de la API -- NO por el proxy del front -- o la cookie anti-CSRF `faro_oauth_state`
# se fija en el origen equivocado y el /callback responde 401 (ver api.js:20-29 y
# el hallazgo de Christian en el PR #304). Vite congela import.meta.env.VITE_* en
# build-time, así que el valor tiene que llegar como build-arg. Default "" =
# comportamiento de dev (el proxy de Vite cubre el login y las cookies locales no
# distinguen puerto); build-and-push-frontend.sh pasa el origen real de faro-api.
ARG VITE_API_ORIGIN=""
ENV VITE_API_ORIGIN=$VITE_API_ORIGIN
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
