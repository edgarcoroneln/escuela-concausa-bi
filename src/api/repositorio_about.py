"""Repositorio de solo lectura para la sección "Cómo funciona" de FARO Web (US-601).

De las siete secciones de `src/api/v1/about.py`, esta es la única con dato **vivo**: el conteo de
filas por tabla de bronze/silver/gold que alimenta el bloque de métricas de la sección `capas`.
Todo el resto del contenido de la sección es texto fijo (ver `about.py`). Mismo patrón
Protocol + implementación Postgres que `repositorio_gold.py`, para que la suite rápida del
contrato pueda sustituir esta clase con un fake en memoria (`tests/fixtures_about.py`) sin
Postgres real.
"""
from __future__ import annotations

import logging
import re
import threading
from typing import Protocol

from cachetools import TTLCache
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, OperationalError

from src.api.config import get_settings
from src.api.db import get_engine

_logger = logging.getLogger(__name__)

#: Sentinel de ausencia para `TTLCache.get`. Hace falta uno propio porque `x in cache` seguido de
#: `cache[x]` consulta el reloj DOS veces y la entrada puede expirar entre ambas (mismo hallazgo
#: que documenta `cache_predicciones.py`). El candado protege el estado, no detiene el tiempo.
_AUSENTE = object()

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

    def hubo_error_de_conexion(self) -> bool:
        """`True` si el último `conteos_capas()` falló por conexión, no por tabla ausente.

        Permite a la sección declarar la causa una vez arriba en lugar de repetirla en cada fila.
        Los dobles de prueba que no lo implementen se tratan como "sin error" (ver
        `_hubo_error_de_conexion` en `v1/about.py`), para no obligarlos a crecer por esto.
        """
        ...


class RepositorioAboutPostgres:
    """Implementación real vía SQLAlchemy Core (mismo estilo que `repositorio_gold.py`).

    **Cache y timeout (US-601, revisión de Edgar Coronel al PR #350).** `conteos_capas()` dispara
    ~30 `COUNT(*)`, uno por tabla, y lo hace desde un endpoint **público**. Sin cache, cada visita
    los repite todos; con `TTLCache` se pagan una vez por ventana. Cada consulta corre además con
    `SET LOCAL statement_timeout`, mismo patrón que `repositorio_modelos.py`: su efecto muere con
    la transacción, así que nunca fuga al motor compartido cuando la conexión vuelve al pool.

    **`no disponible` ≠ `no existe`.** Antes las dos condiciones caían en el mismo `except
    DBAPIError` y la página decía *"Tabla no materializada todavía"* aunque la base estuviera
    caída — una afirmación falsa sobre el esquema cuando el problema era la conexión. Ahora
    `OperationalError` (base inalcanzable, timeout) se distingue del resto de `DBAPIError`
    (tabla/esquema ausente), y `hubo_error_de_conexion()` deja que la sección lo declare arriba en
    vez de repetir 30 notas equivocadas. Es la misma regla `SIN_DATO` del proyecto aplicada al
    motivo: no saber por qué falta un dato no autoriza a inventar la causa.
    """

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine or get_engine()
        ajustes = get_settings()
        self._timeout_ms = int(ajustes.about_timeout_ms)
        self._cache: TTLCache = TTLCache(
            maxsize=int(ajustes.about_cache_max_entradas),
            ttl=int(ajustes.about_cache_ttl_segundos),
        )
        # Las rutas de `v1/about.py` son `def` síncronas, así que Starlette las corre en su
        # threadpool: hay concurrencia real de hilos sobre esta instancia. `TTLCache` no es
        # thread-safe por sí solo. Mismo criterio que `cache_predicciones.py`.
        self._candado = threading.Lock()
        # Se levanta cuando una consulta falla por CONEXIÓN, no por tabla ausente. Lo consulta
        # `hubo_error_de_conexion()` para que la sección lo declare una vez arriba.
        self._error_de_conexion = False

    def _contar(self, esquema: str, tabla: str) -> tuple[int | None, str | None]:
        if not (_IDENTIFICADOR_SEGURO.match(esquema) and _IDENTIFICADOR_SEGURO.match(tabla)):
            # No debería pasar nunca con las constantes de este módulo; es el último resguardo
            # antes de construir SQL con un identificador que no viene de una petición.
            return None, "Nombre de tabla inválido."
        try:
            # `begin()` y no `connect()`: `SET LOCAL` sólo vive dentro de una transacción, y es
            # justo lo que se quiere — el timeout no debe seguir a la conexión al pool.
            with self._engine.begin() as conexion:
                conexion.execute(text(f"SET LOCAL statement_timeout = {self._timeout_ms}"))
                total = conexion.execute(
                    text(f'SELECT COUNT(*) FROM "{esquema}"."{tabla}"')
                ).scalar_one()
            return int(total), None
        except OperationalError as exc:
            # Base inalcanzable o consulta cancelada por el timeout. **No** es "la tabla no
            # existe": afirmar eso sería inventar la causa.
            self._error_de_conexion = True
            _logger.warning(
                "conteo de %s.%s no disponible (%s)", esquema, tabla, type(exc).__name__
            )
            return None, "No se pudo consultar: la base de datos no respondió."
        except DBAPIError:
            # Cualquier otro error del driver sobre una consulta tan simple es, en la práctica,
            # tabla o esquema ausente (`ProgrammingError` / `UndefinedTable`).
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
        except OperationalError as exc:
            self._error_de_conexion = True
            _logger.warning("catálogo de bronze no disponible (%s)", type(exc).__name__)
            return []
        except DBAPIError:
            return []
        return [n for n in nombres if any(n.startswith(p) for p in PREFIJOS_BRONZE)]

    #: Clave única del cache: hoy se cachea la lista completa de una sola vez.
    _CLAVE_CACHE = "conteos_capas"

    def hubo_error_de_conexion(self) -> bool:
        """`True` si el último `conteos_capas()` falló por conexión y no por tabla ausente.

        Lo consume `_seccion_capas` para declarar la causa **una vez arriba**, en vez de repetir
        treinta notas que dirían mal por qué falta cada número.
        """
        return self._error_de_conexion

    def conteos_capas(self) -> list[dict]:
        with self._candado:
            en_cache = self._cache.get(self._CLAVE_CACHE, _AUSENTE)
        if en_cache is not _AUSENTE:
            return en_cache

        resultado = self._contar_todas_las_capas()

        # Un resultado producido con la base caída NO se cachea: si se guardara, la página
        # seguiría diciendo "no disponible" hasta que venza el TTL aunque Postgres ya hubiera
        # vuelto. Mismo criterio que `cache_predicciones.py`, que nunca cachea errores.
        if not self._error_de_conexion:
            with self._candado:
                self._cache[self._CLAVE_CACHE] = resultado
        return resultado

    def _contar_todas_las_capas(self) -> list[dict]:
        # Cada llamada parte de cero: el error es del intento actual, no de uno viejo.
        self._error_de_conexion = False
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
