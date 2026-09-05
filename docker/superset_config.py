# ═══════════════════════════════════════════════════════════════════════
# FARO — Configuración de Superset (metadata, caché, proxy, SSO Google, rol público)
# ═══════════════════════════════════════════════════════════════════════
# Owner: Luis Téllez Domínguez (Célula 5 · Cloud & DevOps)
# Historia: US-502 · Fase 2 (Superset → GCP)
#
# Superset carga sus defaults desde `superset.config` y LUEGO aplica este
# archivo como override (mecanismo `from superset_config import *`, vía
# SUPERSET_CONFIG_PATH). Aquí solo definimos lo que cambia respecto al default.
#
# Sirve para AMBOS ambientes con las MISMAS variables DATABASE_* que ya usa
# docker-compose:
#   • local (docker-compose, ENVIRONMENT=local)   → mismo comportamiento de hoy
#   • prod  (Cloud Run,      ENVIRONMENT=production) → metadata en Cloud SQL
#
# NUNCA se hardcodean secretos: todo sale de variables de entorno (inyectadas
# desde Secret Manager en Cloud Run, desde .env en local).
# ═══════════════════════════════════════════════════════════════════════
import os
from urllib.parse import quote_plus

# Constantes de Flask-AppBuilder (modo de autenticación); se usan en §6 (SSO).
from flask_appbuilder.security.manager import AUTH_DB, AUTH_OAUTH

_ENVIRONMENT = os.environ.get("ENVIRONMENT", "local").lower()
_IS_PROD = _ENVIRONMENT in ("production", "prod")


# ── 1. Metadata DB (SQLAlchemy URI armada desde DATABASE_*) ──────────────
# La imagen oficial arma la URI desde DATABASE_*; la replicamos explícitamente
# para no depender de detalles internos de `apache/superset:latest` y para
# codificar de forma segura una contraseña con caracteres especiales.
_DB_DIALECT = os.environ.get("DATABASE_DIALECT", "postgresql")
_DB_USER = os.environ.get("DATABASE_USER", "superset")
_DB_PASSWORD = os.environ.get("DATABASE_PASSWORD", "")
_DB_HOST = os.environ.get("DATABASE_HOST", "db")
_DB_PORT = os.environ.get("DATABASE_PORT", "5432")
_DB_NAME = os.environ.get("DATABASE_DB", "superset")

SQLALCHEMY_DATABASE_URI = (
    f"{_DB_DIALECT}://{_DB_USER}:{quote_plus(_DB_PASSWORD)}"
    f"@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}"
)

# Cloud SQL corta conexiones ociosas: validar/reciclar antes de usarlas evita
# errores intermitentes de "server closed the connection unexpectedly".
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}


# ── 2. SECRET_KEY (firma sesiones y CIFRA credenciales de conexiones) ────
# Rotarla invalida sesiones y exige `superset re-encrypt-secrets`. Por eso
# debe ser estable y venir de Secret Manager en prod.
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY")
if not SECRET_KEY:
    if _IS_PROD:
        raise RuntimeError(
            "SUPERSET_SECRET_KEY es obligatorio en producción "
            "(inyectar desde Secret Manager)."
        )
    # Solo desarrollo local: valor explícitamente inseguro para poder arrancar.
    SECRET_KEY = "faro-dev-secret-solo-local-no-usar-en-produccion"


# ── 3. Caché de resultados ───────────────────────────────────────────────
# Sin Redis en la ventana de demo: caché en filesystem. En Cloud Run con una
# sola instancia (min=max=1) /tmp es consistente entre workers de esa instancia.
# Migrar a Redis/Memorystore es follow-up post-demo (ver docker/README-SECURITY.md).
_CACHE_BASE = {
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 24,  # 24 h
}
CACHE_CONFIG = {**_CACHE_BASE, "CACHE_DIR": "/tmp/superset_cache"}
DATA_CACHE_CONFIG = {**_CACHE_BASE, "CACHE_DIR": "/tmp/superset_data_cache"}
FILTER_STATE_CACHE_CONFIG = {**_CACHE_BASE, "CACHE_DIR": "/tmp/superset_filter_cache"}
EXPLORE_FORM_DATA_CACHE_CONFIG = {**_CACHE_BASE, "CACHE_DIR": "/tmp/superset_explore_cache"}


# ── 4. Detrás del proxy TLS de Cloud Run ─────────────────────────────────
# Cloud Run termina TLS en su borde y reenvía HTTP al contenedor. ProxyFix
# hace que Superset respete X-Forwarded-Proto/Host y genere URLs https://.
ENABLE_PROXY_FIX = True

# Talisman fuerza HTTPS a nivel de app: con Cloud Run (que YA garantiza HTTPS
# en el borde) forzarlo aquí crea un bucle de redirección, porque el contenedor
# solo ve HTTP interno. El endurecimiento HTTP (CSP, HSTS, rate-limit, WAF) es
# follow-up post-demo documentado en docker/README-SECURITY.md.
TALISMAN_ENABLED = False

# Protección CSRF de formularios: se mantiene ACTIVA (default de Superset).
WTF_CSRF_ENABLED = True


# ── 5. Rol público de solo lectura (demo sin login) — APAGADO por defecto ─
# Compuerta del PO (misma lógica que ANALISTA_EMAILS en la API): activar la
# lectura pública anónima lo decide Edgar. Pre-cableado como INTERRUPTOR DE
# ENTORNO para que encenderlo sea `SUPERSET_PUBLIC_READONLY=true` en el deploy,
# NO un cambio de código. Default seguro: cero exposición anónima.
SUPERSET_PUBLIC_READONLY = os.environ.get(
    "SUPERSET_PUBLIC_READONLY", "false"
).lower() in ("1", "true", "yes", "on")

if SUPERSET_PUBLIC_READONLY:
    # El rol Public hereda de una plantilla de solo lectura. El endurecimiento
    # fino (solo `can read` sobre Dashboard/Chart/Dataset, SIN SQL Lab ni
    # upload, acceso solo a DB-01…DB-10) se aplica en el bootstrap (Bloque 2),
    # que es donde ya existen los datasets. Aquí queda el interruptor.
    PUBLIC_ROLE_LIKE = os.environ.get("SUPERSET_PUBLIC_ROLE_LIKE", "Gamma")


# ── 6. Autenticación: Google SSO (OAuth2 / OIDC vía Flask-AppBuilder) ─────
# Interruptor de entorno (mismo criterio que el resto del archivo): si están
# las credenciales del OAuth Client DEDICADO de Superset, se activa Google SSO;
# si NO están, se cae al login nativo usuario/contraseña (AUTH_DB), que es el
# piso seguro para local y un rollback sin cambiar código (basta quitar las
# env-vars del deploy). El SSO de Superset es INDEPENDIENTE del OAuth del API.
#
# Decisiones de seguridad (2026-09-05, Luis + C5):
#   • Client OAuth DEDICADO a Superset (separado del API/C4).
#   • Acceso restringido por LISTA BLANCA de correos (fail-closed: lista vacía
#     ⇒ nadie entra). Mismo patrón que ANALISTA_EMAILS en la API.
#   • SSO OBLIGATORIO, sin acceso anónimo ⇒ NO se enciende el rol público
#     (dejar SUPERSET_PUBLIC_READONLY en su default `false`).
_SSO_CLIENT_ID = os.environ.get("SUPERSET_GOOGLE_CLIENT_ID", "").strip()
_SSO_CLIENT_SECRET = os.environ.get("SUPERSET_GOOGLE_CLIENT_SECRET", "").strip()
_SSO_ENABLED = bool(_SSO_CLIENT_ID and _SSO_CLIENT_SECRET)

# Lista blanca de correos autorizados (coma-separada, normalizada a minúsculas).
_SSO_ALLOWED_EMAILS = {
    e.strip().lower()
    for e in os.environ.get("SUPERSET_SSO_ALLOWED_EMAILS", "").split(",")
    if e.strip()
}
# Subconjunto que además recibe rol Admin (el resto entra como rol de lectura).
_SSO_ADMIN_EMAILS = {
    e.strip().lower()
    for e in os.environ.get("SUPERSET_SSO_ADMIN_EMAILS", "").split(",")
    if e.strip()
}
# Rol por defecto (solo lectura) para quien entra por SSO y no es admin. El
# afinado fino del rol de lectura se hace en el bootstrap (Bloque 2), igual que
# el rol público.
_SSO_VIEWER_ROLE = os.environ.get("SUPERSET_SSO_VIEWER_ROLE", "Gamma")

if _SSO_ENABLED:
    AUTH_TYPE = AUTH_OAUTH
    # Auto-alta en el primer login (ya validado contra la lista blanca en el
    # SecurityManager); rol de lectura por defecto.
    AUTH_USER_REGISTRATION = True
    AUTH_USER_REGISTRATION_ROLE = _SSO_VIEWER_ROLE
    # Sincroniza roles en CADA login según los `role_keys` que inyecta el
    # SecurityManager ⇒ promover/expulsar admins por correo sin tocar la BD.
    AUTH_ROLES_SYNC_AT_LOGIN = True
    AUTH_ROLES_MAPPING = {"faro_admin": ["Admin"], "faro_viewer": [_SSO_VIEWER_ROLE]}

    OAUTH_PROVIDERS = [
        {
            "name": "google",
            "icon": "fa-google",
            "token_key": "access_token",
            "remote_app": {
                "client_id": _SSO_CLIENT_ID,
                "client_secret": _SSO_CLIENT_SECRET,
                # OIDC discovery: authlib deriva authorize/token/userinfo/jwks.
                "server_metadata_url": (
                    "https://accounts.google.com/.well-known/openid-configuration"
                ),
                "client_kwargs": {"scope": "openid email profile"},
            },
        }
    ]

    # El redirect_uri que el Client dedicado de Google debe tener autorizado es:
    #   https://<url-de-superset-en-cloud-run>/oauth-authorized/google
    # (se registra en la consola tras el primer deploy, cuando se conoce la URL).

    from superset.security import SupersetSecurityManager
    class FaroSsoSecurityManager(SupersetSecurityManager):
        """Restringe el SSO a la lista blanca y asigna rol según el correo."""

        def oauth_user_info(self, provider, response=None):
            if provider != "google":
                return {}
            me = self.appbuilder.sm.oauth_remotes[provider].get("userinfo").json()
            email = (me.get("email") or "").strip().lower()
            # Puerta 1: correo presente y verificado por Google.
            if not email or not me.get("email_verified", False):
                return {}
            # Puerta 2: lista blanca (fail-closed: si está vacía, nadie entra).
            if email not in _SSO_ALLOWED_EMAILS:
                return {}
            role_keys = ["faro_admin"] if email in _SSO_ADMIN_EMAILS else ["faro_viewer"]
            return {
                "username": email,
                "email": email,
                "first_name": me.get("given_name", ""),
                "last_name": me.get("family_name", ""),
                "role_keys": role_keys,
            }

    CUSTOM_SECURITY_MANAGER = FaroSsoSecurityManager
else:
    # Sin credenciales SSO ⇒ login nativo usuario/contraseña (local y rollback).
    AUTH_TYPE = AUTH_DB
