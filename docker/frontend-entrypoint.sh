#!/bin/sh
set -eu
# Solo sustituye $PORT (nunca las variables propias de nginx como $uri) para
# no romper el bloque `try_files` del SPA fallback.
envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
exec nginx -g "daemon off;"
