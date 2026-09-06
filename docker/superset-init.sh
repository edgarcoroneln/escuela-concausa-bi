#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# FARO — Script de Inicialización de Superset
# ═══════════════════════════════════════════════════════════════════════
# Ejecuta las migraciones de base de datos, crea el usuario admin
# (si no existe) e inicia el servidor de Superset.
#
# Creado: 2026-08-15
# Owner: Luis Téllez Domínguez (Célula 5)
# Historia: US-502
# ═══════════════════════════════════════════════════════════════════════

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 FARO — Inicializando Superset"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Mostrar warning si está en modo desarrollo
if [ "${ENVIRONMENT:-local}" = "local" ]; then
    cat << 'EOF'

⚠️  ADVERTENCIA DE SEGURIDAD — Modo DESARROLLO

   Configuración actual:
   • Autenticación: ✅ Sí (login requerido)
   • Cifrado TLS: ❌ No (tráfico HTTP en texto plano)
   • Rate limiting: ❌ No (vulnerable a brute force)
   • SECRET_KEY: Estático (sin rotación)

   ⚠️  NO USAR EN PRODUCCIÓN

   Para producción:
   ✅ SSL/TLS con certificados válidos
   ✅ Rate limiting en login
   ✅ Rotación automática de SECRET_KEY
   ✅ WAF (Cloud Armor en GCP)

   Ver: docker/README-SECURITY.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
fi

# ═══════════════════════════════════════════════════════════════════════
# 1. MIGRAR BASE DE DATOS
# ═══════════════════════════════════════════════════════════════════════
echo "📦 Ejecutando migraciones de base de datos..."
superset db upgrade
echo "✅ Migraciones completadas"

# ═══════════════════════════════════════════════════════════════════════
# 2. CREAR USUARIO ADMIN (si no existe)
# ═══════════════════════════════════════════════════════════════════════
echo "👤 Verificando usuario admin..."

# Intentar crear el admin (falla silenciosamente si ya existe)
superset fab create-admin \
  --username "${SUPERSET_ADMIN_USERNAME}" \
  --firstname FARO \
  --lastname Admin \
  --email "${SUPERSET_ADMIN_EMAIL}" \
  --password "${SUPERSET_ADMIN_PASSWORD}" 2>&1 | grep -v "already exists" || true

echo "✅ Usuario admin configurado"

# ═══════════════════════════════════════════════════════════════════════
# 3. INICIALIZAR SUPERSET (roles, permisos)
# ═══════════════════════════════════════════════════════════════════════
echo "🔐 Inicializando roles y permisos..."
superset init
echo "✅ Superset inicializado"

# ═══════════════════════════════════════════════════════════════════════
# 4. ARRANCAR SERVIDOR
# ═══════════════════════════════════════════════════════════════════════
# Dos modos según ENVIRONMENT:
#   • production/prod → gunicorn (servidor de producción) en $PORT (Cloud Run
#     inyecta PORT; default 8088 si no está). Un worker con varios threads
#     mantiene la caché de /tmp consistente mientras no haya Redis.
#   • local (default) → `superset run --reload` (servidor de desarrollo, igual
#     que hasta hoy; no cambia el flujo de docker-compose).
if [ "${ENVIRONMENT:-local}" = "production" ] || [ "${ENVIRONMENT:-local}" = "prod" ]; then
    PORT="${PORT:-8088}"
    WORKERS="${SERVER_WORKER_AMOUNT:-1}"
    THREADS="${SERVER_THREADS_AMOUNT:-20}"
    TIMEOUT="${GUNICORN_TIMEOUT:-120}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🏭 Superset en PRODUCCIÓN — gunicorn en :${PORT} (workers=${WORKERS}, threads=${THREADS})"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exec gunicorn \
        --bind "0.0.0.0:${PORT}" \
        --workers "${WORKERS}" \
        --worker-class gthread \
        --threads "${THREADS}" \
        --timeout "${TIMEOUT}" \
        --keep-alive 65 \
        --limit-request-line 0 \
        --limit-request-field_size 0 \
        --access-logfile - \
        --error-logfile - \
        "superset.app:create_app()"
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Superset listo (desarrollo) — escuchando en puerto 8088"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exec superset run -h 0.0.0.0 -p 8088 --with-threads --reload
fi
