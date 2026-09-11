"""Fábrica de la app del **contrato v1** de FARO (US-401).

Esta app es la **implementación de referencia / stub** del contrato descrito en
`vault/03_Architecture/API_Specification.md`. Su propósito es doble:

1. Generar el `openapi.json` estable que se publica en `api/openapi.v1.json` (§6) y del que las
   Células 2 y 3 levantan sus mocks.
2. Servir respuestas de ejemplo (desde `src/api/mock_data.py`) para desarrollo desacoplado.

**No sustituye** al entrypoint de despliegue `src/api/main.py` (Célula 5, US-501). Ambas conviven:
`main.py` es el "hola mundo" del deploy temprano; esta app es el contrato. La unificación (montar
`/api/v1` dentro de `main.py`) se hará al implementar OAuth2/JWT en US-402 y se coordinará con
Cloud/DevOps.

Errores: todos los `4xx`/`5xx` se devuelven con la forma uniforme `ErrorOut` del §5, sin fugar
trazas, SQL ni rutas internas.
"""
from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from limits import parse as parse_limit
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.config import get_settings
from src.api.schemas import ErrorOut
from src.api.v1 import api_v1_router

API_PREFIX = "/api/v1"

_logger = logging.getLogger("faro.api")

# Código estable de error por status HTTP (§5). Lo no mapeado cae en internal_error.
_ERROR_POR_STATUS: dict[int, str] = {
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    422: "validation_error",  # literal para portabilidad entre versiones de Starlette
    status.HTTP_429_TOO_MANY_REQUESTS: "rate_limited",
    status.HTTP_503_SERVICE_UNAVAILABLE: "service_unavailable",  # timeout de Postgres, US-416
}

# Mensajes seguros para el cliente (sin detalle interno) por código de error.
_MENSAJE_SEGURO: dict[str, str] = {
    "unauthorized": "No hay credenciales válidas para esta operación.",
    "forbidden": "Tu rol no permite esta operación.",
    "not_found": "El recurso solicitado no existe o está fuera de alcance.",
    "validation_error": "La entrada no cumple el formato esperado.",
    "rate_limited": "Demasiadas peticiones. Intenta más tarde.",
    "service_unavailable": "El servicio de predicciones no respondió a tiempo. Intenta más tarde.",
    "internal_error": "Ocurrió un error interno. El equipo fue notificado.",
}


def _nuevo_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:8]}"


def _respuesta_error(status_code: int, error: str, request_id: str) -> JSONResponse:
    cuerpo = ErrorOut(
        error=error,
        message=_MENSAJE_SEGURO.get(error, _MENSAJE_SEGURO["internal_error"]),
        request_id=request_id,
    )
    return JSONResponse(status_code=status_code, content=cuerpo.model_dump())


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Falla rápido si se arranca en producción con un secreto JWT inseguro (US-402).
    get_settings().assert_production_ready()
    yield


def create_app() -> FastAPI:
    """Construye la app del contrato v1 con sus routers, hardening y manejadores uniformes (US-404)."""
    settings = get_settings()
    app = FastAPI(
        title="FARO API — Contrato v1",
        description=(
            "Contrato REST de FARO (Escuela como Sensor Social). Fuente de verdad: "
            "vault/03_Architecture/API_Specification.md. Este servicio publica el OpenAPI que "
            "consumen los mocks de las Células 2 y 3 (US-401)."
        ),
        version="1.0.0",
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
        openapi_url=f"{API_PREFIX}/openapi.json",
        lifespan=_lifespan,
    )

    # --- Rate limiting (US-404) ---
    # Límite por (IP, path) con el motor `limits` (dependencia de slowapi). NO se usa
    # `SlowAPIMiddleware`: su resolución de ruta no reconoce los routers incluidos de esta versión de
    # FastAPI (los deja como `_IncludedRouter`) y terminaría eximiendo todo. En su lugar, un
    # middleware propio devuelve directamente el `ErrorOut` 429. Es en memoria por proceso (1
    # instancia); para prod multi-instancia se migra a un backend compartido (Redis) — follow-up en
    # ADR-004. Se registra ANTES que CORS para que sus cabeceras acompañen también al 429.
    if settings.rate_limit_enabled:
        _rl_item = parse_limit(settings.rate_limit_default)
        _rl = MovingWindowRateLimiter(MemoryStorage())

        @app.middleware("http")
        async def _rate_limit_mw(request: Request, call_next):
            if not _rl.hit(_rl_item, get_remote_address(request), request.url.path):
                return _respuesta_error(
                    status.HTTP_429_TOO_MANY_REQUESTS, "rate_limited", _nuevo_request_id()
                )
            return await call_next(request)

    # --- CORS (US-404) ---
    # Orígenes configurables (C5 añade los de despliegue). Se omite si la lista está vacía.
    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type"],
        )

    app.include_router(api_v1_router, prefix=API_PREFIX)

    # --- Ejecutor SQL read-only del agente (US-404 / BUG-025) ---
    # Solo se cablea si hay DSN read-only configurado (C5 en Secret Manager). Sin él, el agente usa el
    # default seguro del seam (degrada) y CI/local no tocan Postgres.
    if settings.database_url_read_only:
        from src.api.ejecutor_gold import ejecutar_sql_read_only
        from src.api.v1.agente import get_ejecutar_sql

        app.dependency_overrides[get_ejecutar_sql] = lambda: ejecutar_sql_read_only

    # --- LLM del agente: text-to-SQL + redactor (BUG-025 / P-13) ---
    # Solo se cablea si hay ANTHROPIC_API_KEY (C5 en Secret Manager). Sin ella, el agente usa los
    # defaults seguros del seam (degrada "no configurado") y CI/local no llaman a Anthropic. El SQL
    # que genere el LLM pasa SIEMPRE por el filtro de intención de la pregunta (P-13) y por
    # `preparar_sql_seguro` (solo-lectura) antes de tocar la BD: el LLM nunca es la única capa.
    # Las firmas del adaptador (prompt, pregunta) y (pregunta, filas) ya casan con el seam.
    if settings.anthropic_api_key:
        from src.agente.llm import generar_sql_con_llm, redactar_respuesta_con_llm
        from src.api.v1.agente import get_generar_sql, get_redactar_respuesta

        app.dependency_overrides[get_generar_sql] = lambda: generar_sql_con_llm
        app.dependency_overrides[get_redactar_respuesta] = lambda: redactar_respuesta_con_llm

    @app.exception_handler(StarletteHTTPException)
    async def _http_exc(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        error = _ERROR_POR_STATUS.get(exc.status_code, "internal_error")
        return _respuesta_error(exc.status_code, error, _nuevo_request_id())

    @app.exception_handler(RequestValidationError)
    async def _validation_exc(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _respuesta_error(422, "validation_error", _nuevo_request_id())

    @app.exception_handler(Exception)
    async def _unhandled_exc(request: Request, exc: Exception) -> JSONResponse:
        # El detalle real se registra internamente (logs), NUNCA se devuelve al cliente.
        request_id = _nuevo_request_id()
        _logger.exception("Error no controlado [%s] en %s %s", request_id, request.method, request.url.path)
        return _respuesta_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", request_id)

    return app


app = create_app()
