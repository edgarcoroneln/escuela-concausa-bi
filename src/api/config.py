"""Configuración tipada de la API FARO (US-402).

Lee variables de entorno (opcionalmente desde `.env`) con `pydantic-settings`. **Nunca** contiene
secretos reales: solo valores por defecto seguros para desarrollo local. En producción los valores
llegan por variables de entorno / Secret Manager (Célula 5); ver `07_Security/Secrets_Policy.md`.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Secreto por defecto SOLO para desarrollo/tests. En producción es obligatorio sobreescribirlo:
# la app se niega a arrancar en `production` con este valor (ver assert_production_ready()).
_DEV_SECRET_INSEGURO = "dev-insecure-secret-change-me-please-0000000000000000"


class Settings(BaseSettings):
    """Parámetros de la API. Los nombres mapean a variables de entorno en MAYÚSCULAS."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # el .env del proyecto tiene muchas otras vars (Airflow, Superset, etc.)
    )

    environment: str = "local"  # local | staging | production

    # ---- JWT propio (HS256 por ahora; RS256 en prod, ver ADR-004) ----
    jwt_secret_key: str = _DEV_SECRET_INSEGURO
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # ---- OAuth2 con Google (credenciales las provee la Célula 5 / GCP; vacías en local) ----
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/callback"
    google_authorization_endpoint: str = "https://accounts.google.com/o/oauth2/v2/auth"

    # ---- Política de rol (PROVISIONAL; la definitiva la decide Edgar/PO) ----
    # Allowlist de correos con rol `analista`. Mínimo privilegio: vacío => todos ciudadano.
    analista_emails: str = ""

    # ---- RBAC de lectura (US-403) ----
    # Interruptor híbrido: mientras el login Google no esté operativo (credenciales pendientes de
    # Célula 5), la LECTURA de datos (gold, predicciones, agente) queda pública para no bloquear la
    # URL viva de la demo. La escritura/admin SIEMPRE exige `analista`, sin importar este flag.
    # Cuando C5 entregue credenciales, se pone AUTH_LECTURA_PUBLICA=false y la lectura pasa a exigir
    # sesión `ciudadano` sin re-tocar código. Ver ADR-004 §RBAC.
    auth_lectura_publica: bool = True

    # ---- Postgres / Gold (US-411) ----
    # Nombres alineados a las vars POSTGRES_* que ya usan Airflow/MLflow/dbt en el .env
    # del equipo (ver .env.example) — una sola fuente de verdad para la conexión local.
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "escuela_concausa_db"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    # ---- Airflow (US-413) ----
    # El webserver ya corre en docker-compose.yml (puerto 8080); reutiliza las credenciales de
    # bootstrap _AIRFLOW_WWW_USER_* del .env del equipo para autenticar la API REST de Airflow.
    airflow_base_url: str = "http://localhost:8080"
    airflow_www_user_username: str = "airflow"
    airflow_www_user_password: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def analista_email_set(self) -> set[str]:
        return {e.strip().lower() for e in self.analista_emails.split(",") if e.strip()}

    @property
    def secret_es_inseguro(self) -> bool:
        """True si el secreto es el de desarrollo o es demasiado corto para HS256."""
        return self.jwt_secret_key == _DEV_SECRET_INSEGURO or len(self.jwt_secret_key) < 32

    def assert_production_ready(self) -> None:
        """Falla rápido si se intenta correr en producción con un secreto inseguro.

        Evita el error clásico de desplegar con la clave de ejemplo. Se invoca al arrancar la app
        cuando `ENVIRONMENT=production`.
        """
        if self.environment.lower() == "production" and self.secret_es_inseguro:
            raise RuntimeError(
                "JWT_SECRET_KEY inseguro en producción: define una clave propia de ≥32 caracteres "
                "(genera una con scripts/generate-keys.py)."
            )


@lru_cache
def get_settings() -> Settings:
    """Settings cacheados (una sola lectura del entorno por proceso)."""
    return Settings()
