"""Repositorio de datos para `/predicciones/{cct}` y `/predicciones/batch` (US-412, cierra BUG-010).

`src/api/v1/predicciones.py` leía `src/api/mock_data.py` -- un valor fabricado a mano, no la salida
de ningún modelo (BUG-010, `vault/06_Quality_Testing/Bug_Register.md`). `gold.predicciones` y
`gold.recomendaciones` ya están pobladas y verificadas contra Postgres (US-313, Héctor Morales):
el swap es leerlas, no invocar MLflow en cada request. `mlflow_run_id` viaja en la fila y conserva
el enlace auditable a la corrida que produjo el valor -- "3 modelos integrados vía API" (REQ-003)
no se debilita por leer la tabla precalculada en vez de invocar el modelo en vivo.

Mismo patrón `Depends` + Protocol que `RepositorioGold` (`src/api/repositorio_gold.py`, US-411):
los endpoints dependen de una abstracción, no de Postgres directo, así que la suite rápida del
contrato la sustituye por un fake en memoria (`tests/fixtures_modelos.py`) sin necesitar Postgres.

`cluster` (ML-03) no tiene productor todavía -- US-321 (Estefany Hernández) sin entregar. Se
declara explícitamente `None` en vez de inventar un entero, mismo criterio SIN_DATO que
`EscuelaOut.indice_riesgo`. Ver `src/api/schemas.py::PrediccionOut.cluster` y BUG-010.

**Timeout de Postgres (US-416):** cada consulta corre dentro de una transacción con
`SET LOCAL statement_timeout` -- su efecto muere con la transacción, así que nunca fuga al motor
compartido con `RepositorioGoldPostgres` (US-411) cuando la conexión vuelve al pool. Si Postgres
cancela la consulta, se traduce a `RepositorioModelosNoDisponible` (§`v1/predicciones.py` la
mapea a 503 `service_unavailable`, nunca a un 500 genérico ni a un valor inventado).
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Protocol

from sqlalchemy import select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.api.config import get_settings
from src.api.db import get_engine, get_tablas

_logger = logging.getLogger("faro.api")

MODELO_ML01 = "ML-01"
GRANO_ESCUELA = "escuela"

# Contribución SHAP de cada driver, en `gold.recomendaciones` (BUG-053). Viajan en la MISMA fila
# que la predicción a propósito: `/predicciones/{cct}/explicacion` reutiliza `obtener_prediccion`
# en vez de tener su propia consulta, así hereda gratis el cache TTL y la traducción a 503 de
# US-416, y no puede desincronizarse del `driver_dominante` que explica.
COLUMNAS_SHAP = tuple(f"shap_d{i}" for i in range(1, 7))


class RepositorioModelosNoDisponible(Exception):
    """Gold no está disponible para responder la predicción (US-416).

    Cubre dos casos que para el cliente son el mismo: Postgres no respondió dentro del
    `statement_timeout` configurado, **o** el esquema/tabla `gold.*` no existe o es inalcanzable
    en el despliegue (p. ej. la publicación de ML aún no corrió contra esa base).

    No es "el CCT no tiene predicción" (eso es un `None`/lista vacía, ver BUG-010) -- es "no
    pudimos saberlo". El llamador debe responder 503, nunca inventar un valor ni dejar caer un
    500 genérico.
    """


class RepositorioModelos(Protocol):
    """Lecturas sobre `gold.predicciones` + `gold.recomendaciones` que necesita `/predicciones/*`."""

    def obtener_prediccion(self, cct: str, id_ciclo: str) -> dict | None:
        """Predicción de una escuela × ciclo, o `None` si no hay fila en `gold.predicciones`.

        La fila incluye además `shap_d1..shap_d6` (contribución de cada driver, `None` = SIN_DATO),
        que es lo que sirve `/predicciones/{cct}/explicacion` -- ver `COLUMNAS_SHAP`.
        """
        ...

    def listar_predicciones(self, ccts: list[str], id_ciclo: str) -> list[dict]:
        """Predicciones de una lista de CCT para un ciclo. Omite los CCT sin fila -- nunca
        inventa una predicción para un CCT que `gold.predicciones` no cubre."""
        ...


class RepositorioModelosPostgres:
    """Implementación real sobre `gold.predicciones` × `gold.recomendaciones` vía SQLAlchemy Core
    (mismo estilo que `RepositorioGoldPostgres`)."""

    def __init__(self, engine: Engine | None = None, timeout_ms: int = 3000) -> None:
        self._engine = engine or get_engine()
        self._timeout_ms = int(timeout_ms)
        (_, _, _, _, self._predicciones, self._recomendaciones) = get_tablas()

    def _seleccion_prediccion(self):
        predicciones, recomendaciones = self._predicciones, self._recomendaciones
        return (
            select(
                predicciones.c.cct,
                predicciones.c.id_ciclo,
                predicciones.c.indice_riesgo,
                predicciones.c.mlflow_run_id,
                recomendaciones.c.driver_dominante,
                recomendaciones.c.recomendacion,
                *(recomendaciones.c[col] for col in COLUMNAS_SHAP),
            )
            .select_from(
                predicciones.join(
                    recomendaciones,
                    (predicciones.c.cct == recomendaciones.c.cct)
                    & (predicciones.c.id_ciclo == recomendaciones.c.id_ciclo),
                )
            )
            .where(predicciones.c.modelo == MODELO_ML01)
            .where(predicciones.c.grano == GRANO_ESCUELA)
        )

    @staticmethod
    def _fila_a_dict(fila) -> dict:
        datos = dict(fila)
        datos["cluster"] = None  # ML-03 sin productor (BUG-010, US-321)
        return datos

    def _con_timeout(self, consulta):
        """Ejecuta `consulta` con `statement_timeout` acotado a esta transacción (US-416).

        `SET LOCAL` (no `SET`) muere al salir de la transacción -- la conexión vuelve "limpia" al
        pool compartido con `RepositorioGoldPostgres`. El valor se interpola directo (no bind
        param): `SET` no acepta parámetros de protocolo extendido de forma confiable con
        psycopg2/poolers, y aquí es seguro porque sale de `Settings` (nunca de input de usuario) y
        ya pasó por `int()` en `__init__`.

        **Cualquier** fallo de SQLAlchemy se traduce a `RepositorioModelosNoDisponible` (→ 503),
        no solo el timeout (`OperationalError`): un `ProgrammingError` por esquema/tabla `gold`
        ausente en el despliegue -- caso real mientras la publicación de ML no haya corrido contra
        esa base -- se escapaba antes al handler genérico de `app.py` y se volvía un **500**. La
        excepción concreta se registra en el log; al cliente solo le llega el 503 uniforme.
        """
        try:
            with self._engine.begin() as conexion:
                conexion.execute(text(f"SET LOCAL statement_timeout = {self._timeout_ms}"))
                return conexion.execute(consulta).mappings().all()
        except SQLAlchemyError as exc:
            _logger.warning(
                "gold.predicciones no disponible (%s): %s", type(exc).__name__, exc
            )
            raise RepositorioModelosNoDisponible(
                f"Gold no disponible ({type(exc).__name__})."
            ) from exc

    def obtener_prediccion(self, cct: str, id_ciclo: str) -> dict | None:
        consulta = self._seleccion_prediccion().where(
            self._predicciones.c.cct == cct, self._predicciones.c.id_ciclo == id_ciclo
        )
        filas = self._con_timeout(consulta)
        return self._fila_a_dict(filas[0]) if filas else None

    def listar_predicciones(self, ccts: list[str], id_ciclo: str) -> list[dict]:
        if not ccts:
            return []
        consulta = self._seleccion_prediccion().where(
            self._predicciones.c.cct.in_(ccts), self._predicciones.c.id_ciclo == id_ciclo
        )
        filas = self._con_timeout(consulta)
        return [self._fila_a_dict(fila) for fila in filas]


@lru_cache
def get_repositorio_modelos() -> RepositorioModelos:
    """Dependencia de FastAPI (`Depends(get_repositorio_modelos)`). Las pruebas rápidas la
    sustituyen con `app.dependency_overrides[get_repositorio_modelos] = ...`
    (ver `tests/fixtures_modelos.py`) -- nunca con SQLite, mismo motivo que `RepositorioGold`.

    `@lru_cache` (mismo patrón que `get_engine`/`get_settings`, `src/api/db.py`/`config.py`): una
    sola instancia por proceso, para que el cache TTL de `RepositorioModelosCacheado` (US-416)
    persista entre requests en vez de reiniciarse en cada llamada.
    """
    from src.api.cache_predicciones import RepositorioModelosCacheado

    ajustes = get_settings()
    base = RepositorioModelosPostgres(timeout_ms=ajustes.predicciones_timeout_ms)
    return RepositorioModelosCacheado(
        base,
        ttl_segundos=ajustes.predicciones_cache_ttl_segundos,
        max_entradas=ajustes.predicciones_cache_max_entradas,
    )
