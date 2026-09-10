"""Repositorio de solo lectura para la sección "Cómo funciona" de FARO Web (US-601).

De las siete secciones de `src/api/v1/about.py`, esta es la única con dato **vivo**: el conteo de
filas por tabla de bronze/silver/gold que alimenta el bloque de métricas de la sección `capas`.
Todo el resto del contenido de la sección es texto fijo (ver `about.py`). Mismo patrón
Protocol + implementación Postgres que `repositorio_gold.py`, para que la suite rápida del
contrato pueda sustituir esta clase con un fake en memoria (`tests/fixtures_about.py`) sin
Postgres real.
"""
from __future__ import annotations

import re
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError

from src.api.db import get_engine

# Nombres fijos de tabla (Data_Model.md §3/§4). Son constantes del código, nunca llegan desde una
# petición -- este endpoint no acepta parámetros -- así que no hay superficie de inyección al
# interpolarlos en el SQL (a diferencia de un `order_by` de usuario, que sí pasa por whitelist en
# `src/api/v1/gold.py`).
TABLAS_SILVER: tuple[str, ...] = (
    "escuela",
    "matricula",
    "cemabe",
    "delitos_municipio",
    "aire_estacion",
    "agua_region",
    "rezago_municipio",
    "poblacion_municipio",
)

TABLAS_GOLD: tuple[str, ...] = (
    "dim_escuela",
    "dim_municipio",
    "dim_tiempo",
    "dim_driver",
    "fact_escuela_ciclo",
    "features_escuela",
    "predicciones",
    "recomendaciones",
    "cubo_matricula",
    "cubo_riesgo_territorial",
    "cubo_escuela_360",
    "cubo_comparador_municipio",
    "cubo_driver",
    "cubo_completitud",
    "cubo_pivot",
    "cubo_recomendaciones",
    "cubo_pipeline",
)

# Bronze se nombra `bronze.<fuente>_<periodo>` (Data_Model.md §2): el periodo cambia cada vez que
# corre una ingesta nueva, así que no hay un nombre de tabla exacto que se mantenga fijo toda la
# semana. Se resuelve por PREFIJO -- uno por fuente DS-01..DS-08, lista cerrada y conocida -- contra
# `information_schema`, nunca por enumeración abierta de todo el esquema.
PREFIJOS_BRONZE: tuple[str, ...] = (
    "formato911",
    "cct",
    "cemabe",
    "sesnsp",
    "sinaica",
    "conagua",
    "coneval_irs",
    "coneval_pobreza",
    "conapo",
)

_IDENTIFICADOR_SEGURO = re.compile(r"^[a-z][a-z0-9_]*$")


class RepositorioAbout(Protocol):
    def conteos_capas(self) -> list[dict]:
        """`[{capa, tabla, filas, nota}]` de bronze/silver/gold.

        `filas` es `None` cuando la tabla todavía no está materializada -- disponibilidad
        ausente, no un `0` inventado, mismo espíritu que el `SIN_DATO` de cobertura de drivers.
        """
        ...


class RepositorioAboutPostgres:
    """Implementación real vía SQLAlchemy Core (mismo estilo que `repositorio_gold.py`)."""

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine or get_engine()

    def _contar(self, esquema: str, tabla: str) -> tuple[int | None, str | None]:
        if not (_IDENTIFICADOR_SEGURO.match(esquema) and _IDENTIFICADOR_SEGURO.match(tabla)):
            # No debería pasar nunca con las constantes de este módulo; es el último resguardo
            # antes de construir SQL con un identificador que no viene de una petición.
            return None, "Nombre de tabla inválido."
        try:
            with self._engine.connect() as conexion:
                total = conexion.execute(
                    text(f'SELECT COUNT(*) FROM "{esquema}"."{tabla}"')
                ).scalar_one()
            return int(total), None
        except DBAPIError:
            return None, "Tabla no materializada todavía."

    def _tablas_bronze_existentes(self) -> list[str]:
        """Nombres reales en `bronze.*` que empiezan con alguno de `PREFIJOS_BRONZE`."""
        try:
            with self._engine.connect() as conexion:
                nombres = (
                    conexion.execute(
                        text(
                            "SELECT table_name FROM information_schema.tables "
                            "WHERE table_schema = 'bronze'"
                        )
                    )
                    .scalars()
                    .all()
                )
        except DBAPIError:
            return []
        return [n for n in nombres if any(n.startswith(p) for p in PREFIJOS_BRONZE)]

    def conteos_capas(self) -> list[dict]:
        resultado: list[dict] = []

        bronze_existentes = self._tablas_bronze_existentes()
        for nombre in bronze_existentes:
            filas, nota = self._contar("bronze", nombre)
            resultado.append({"capa": "bronze", "tabla": nombre, "filas": filas, "nota": nota})
        prefijos_cubiertos = {
            prefijo for prefijo in PREFIJOS_BRONZE
            for nombre in bronze_existentes
            if nombre.startswith(prefijo)
        }
        for prefijo in PREFIJOS_BRONZE:
            if prefijo not in prefijos_cubiertos:
                resultado.append(
                    {
                        "capa": "bronze",
                        "tabla": f"{prefijo}_*",
                        "filas": None,
                        "nota": "Todavía sin tabla ingerida para esta fuente.",
                    }
                )

        for tabla in TABLAS_SILVER:
            filas, nota = self._contar("silver", tabla)
            resultado.append({"capa": "silver", "tabla": tabla, "filas": filas, "nota": nota})

        for tabla in TABLAS_GOLD:
            filas, nota = self._contar("gold", tabla)
            resultado.append({"capa": "gold", "tabla": tabla, "filas": filas, "nota": nota})

        return resultado


def get_repositorio_about() -> RepositorioAbout:
    """Dependencia de FastAPI (`Depends(get_repositorio_about)`). Las pruebas rápidas la
    sustituyen con `app.dependency_overrides` (ver `tests/fixtures_about.py`)."""
    return RepositorioAboutPostgres()
