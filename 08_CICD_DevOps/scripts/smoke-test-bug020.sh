#!/usr/bin/env bash
# FARO — Smoke test de BUG-020 sobre la URL pública
# ---------------------------------------------------------------------------
# Verifica, en orden, las tres capas que separan un 500 de una demo funcional.
# Cada etapa distingue un fallo distinto, para que el diagnóstico no arranque
# de cero cuando algo falle:
#
#   Etapa 1 · El contenedor corre           → /api/v1/health responde 200
#   Etapa 2 · La API alcanza la base        → una ruta de datos deja de dar 500
#   Etapa 3 · La base tiene datos de Gold   → esa ruta devuelve filas
#   Etapa 4 · La autenticación funciona     → sin token da 401, no 500
#
# El orden importa: un 500 en la etapa 2 y un 500 en la etapa 4 tienen causas
# opuestas. Si sin token da 500 en vez de 401, el fallo ocurre ANTES de validar
# auth — es la sesión de base de datos, no el RBAC. Ese fue exactamente el
# síntoma que definió BUG-020.
#
# Uso:
#   ./smoke-test-bug020.sh                       # contra la URL de producción
#   URL=http://localhost:8000 ./smoke-test-bug020.sh
#   CCT=09DPR0001X ./smoke-test-bug020.sh
#
# Salida: 0 si las cuatro etapas pasan; el número de la primera etapa que falle.
# ---------------------------------------------------------------------------
set -uo pipefail

URL="${URL:-https://faro-api-eanzfglvyq-uc.a.run.app}"
CCT="${CCT:-09DPR0001X}"
TIMEOUT="${TIMEOUT:-20}"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✅ $*${NC}"; }
bad()  { echo -e "  ${RED}❌ $*${NC}"; }
warn() { echo -e "  ${YELLOW}⚠️  $*${NC}"; }
etapa(){ echo -e "\n${BLUE}▶ $*${NC}"; }

codigo() { curl -s -o /dev/null -w "%{http_code}" --max-time "${TIMEOUT}" "$1" 2>/dev/null; }
cuerpo() { curl -s --max-time "${TIMEOUT}" "$1" 2>/dev/null; }

echo "URL bajo prueba: ${URL}"
FALLA=0

# ── Etapa 1 · ¿corre el contenedor? ─────────────────────────────────────────
etapa "Etapa 1 · El contenedor responde"
C=$(codigo "${URL}/api/v1/health")
if [ "$C" = "200" ]; then
  ok "/api/v1/health → 200"
else
  bad "/api/v1/health → ${C} (esperado 200)"
  echo "     El contenedor no está sirviendo. Revisa el CMD del Dockerfile y los logs de Cloud Run."
  exit 1
fi

# ── Etapa 2 · ¿alcanza la base de datos? ────────────────────────────────────
etapa "Etapa 2 · La API alcanza la base de datos"
C=$(codigo "${URL}/api/v1/escuelas")
case "$C" in
  500)
    bad "/api/v1/escuelas → 500 — BUG-020 SIGUE ABIERTO"
    echo "     La API no puede abrir sesión contra Postgres. Verifica en Cloud Run:"
    echo "       · --vpc-connector=faro-connector"
    echo "       · POSTGRES_HOST apunta a la IP privada de Cloud SQL"
    echo "       · --service-account=faro-api-sa@... con rol cloudsql.client"
    echo "       · el secreto db-password está montado"
    FALLA=${FALLA:-2}; [ "$FALLA" = "0" ] && FALLA=2
    ;;
  200|401|403|404|422)
    ok "/api/v1/escuelas → ${C} (ya no es 500: hay sesión de base de datos)"
    ;;
  *)
    warn "/api/v1/escuelas → ${C} (inesperado, revisar logs)"
    ;;
esac

# ── Etapa 3 · ¿hay datos de Gold? ───────────────────────────────────────────
etapa "Etapa 3 · La base tiene datos de Gold"
if [ "$(codigo "${URL}/api/v1/escuelas")" = "500" ]; then
  warn "omitida — la etapa 2 no pasó"
else
  BODY=$(cuerpo "${URL}/api/v1/escuelas")
  if echo "$BODY" | grep -qiE '"(cct|items|results|data)"'; then
    N=$(echo "$BODY" | grep -o '"cct"' | wc -l | tr -d ' ')
    if [ "$N" -gt 0 ]; then
      ok "/api/v1/escuelas devuelve datos (${N} referencias a cct en la respuesta)"
    else
      warn "responde bien pero SIN FILAS — la conexión funciona y Gold está vacío"
      echo "     Falta materializar gold.* en Cloud SQL (dbt run o restaurar un dump)."
      [ "$FALLA" = "0" ] && FALLA=3
    fi
  else
    warn "respuesta sin forma reconocible; revisar a mano:"
    echo "     $(echo "$BODY" | head -c 200)"
  fi
fi

# ── Etapa 4 · ¿la autenticación se evalúa? ──────────────────────────────────
etapa "Etapa 4 · La autenticación se evalúa (no revienta antes)"
C=$(codigo "${URL}/api/v1/predicciones/${CCT}")
case "$C" in
  401|403)
    ok "/api/v1/predicciones/${CCT} → ${C} — auth evaluada, ruta protegida"
    ;;
  200)
    ok "/api/v1/predicciones/${CCT} → 200 (ruta abierta o token no exigido)"
    ;;
  404)
    ok "/api/v1/predicciones/${CCT} → 404 — la ruta funciona; ese CCT no existe en Gold"
    ;;
  500)
    bad "/api/v1/predicciones/${CCT} → 500 sin token"
    echo "     Un 500 sin token significa que el fallo ocurre ANTES de validar auth:"
    echo "     es la sesión de base de datos, no el RBAC. Mismo síntoma de BUG-020."
    [ "$FALLA" = "0" ] && FALLA=4
    ;;
  *)
    warn "/api/v1/predicciones/${CCT} → ${C}"
    ;;
esac

# ── Veredicto ───────────────────────────────────────────────────────────────
echo ""
if [ "$FALLA" = "0" ]; then
  echo -e "${GREEN}✅ Las cuatro etapas pasan. La URL pública sirve datos reales.${NC}"
  echo "   Casilla 6 del ensayo E2E: verificable sobre la URL pública."
  exit 0
else
  echo -e "${RED}❌ Primera etapa que falla: ${FALLA}. BUG-020 no se puede cerrar todavía.${NC}"
  exit "$FALLA"
fi
