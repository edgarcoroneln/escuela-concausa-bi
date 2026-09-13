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
from dataclasses import dataclass, field
from functools import lru_cache
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

#: SQLSTATE de `query_canceled`: Postgres abortó la consulta por `statement_timeout`. psycopg2 lo
#: reporta como `OperationalError`, igual que una caída — pero **no es lo mismo** y confundirlos
#: hace que una tabla lenta se declare como base caída. `bronze.sesnsp` tiene 12.5 M de filas y su
#: `COUNT(*)` puede exceder el timeout con la base perfectamente sana (hallazgo de Edgar Coronel al
#: revisar el PR #350).
_SQLSTATE_CONSULTA_CANCELADA = "57014"


def _es_timeout(exc: Exception) -> bool:
    """`True` si el `OperationalError` viene de `statement_timeout` y no de una caída."""
    return getattr(getattr(exc, "orig", None), "pgcode", None) == _SQLSTATE_CONSULTA_CANCELADA


@dataclass(frozen=True)
class ConteosCapas:
    """Resultado de `conteos_capas()`, con el motivo del fallo **dentro** del propio resultado.

    Antes el motivo vivía en un atributo de instancia (`self._error_de_conexion`) que la sección
    leía después. Con `get_repositorio_about()` bajo `@lru_cache` el repositorio es un **singleton
    compartido entre hilos**, así que ese atributo se volvía una carrera: dos peticiones
    concurrentes podían pisarse la bandera y una acabaría declarando una caída que le pasó a la
    otra. Viajando con el resultado no hay estado mutable que compartir.
    """

    filas: list[dict] = field(default_factory=list)
    #: La base no respondió. **No** cubre "la tabla no existe" ni "la consulta tardó demasiado".
    base_no_disponible: bool = False
    #: Tablas cuyo `COUNT(*)` excedió el `statement_timeout`. El dato existe, sólo tardó — por eso
    #: no cuenta como caída y no impide cachear el resto.
    tablas_lentas: tuple[str, ...] = ()

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
    def conteos_capas(self) -> ConteosCapas:
        """`[{capa, tabla, filas, nota}]` de bronze/silver/gold.

        `filas` es `None` cuando la tabla todavía no está materializada -- disponibilidad
        ausente, no un `0` inventado, mismo espíritu que el `SIN_DATO` de cobertura de drivers.
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
            if _es_timeout(exc):
                # La tabla existe y la base está sana: el `COUNT(*)` no cupo en el timeout.
                # Declararlo como caída sería inventar la causa, igual que decir que no existe.
                _logger.info("conteo de %s.%s excedió el timeout", esquema, tabla)
                return None, "No se pudo contar: la tabla es grande y la consulta excedió su tiempo."
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
            _logger.warning("catálogo de bronze no disponible (%s)", type(exc).__name__)
            raise
        except DBAPIError:
            return []
        return [n for n in nombres if any(n.startswith(p) for p in PREFIJOS_BRONZE)]

    #: Clave única del cache: hoy se cachea la lista completa de una sola vez.
    _CLAVE_CACHE = "conteos_capas"

    def conteos_capas(self) -> ConteosCapas:
        with self._candado:
            en_cache = self._cache.get(self._CLAVE_CACHE, _AUSENTE)
        if en_cache is not _AUSENTE:
            return en_cache

        try:
            resultado = self._contar_todas_las_capas()
        except OperationalError as exc:
            # El catálogo de Bronze no se pudo leer: sin él no hay barrido que valga. Se responde
            # con el motivo, no con una lista vacía que parecería "no hay nada materializado".
            _logger.warning("barrido de capas abortado (%s)", type(exc).__name__)
            return ConteosCapas(filas=[], base_no_disponible=not _es_timeout(exc))

        # Un resultado producido con la base caída NO se cachea: si se guardara, la página
        # seguiría diciendo "no disponible" hasta que venza el TTL aunque Postgres ya hubiera
        # vuelto. Mismo criterio que `cache_predicciones.py`, que nunca cachea errores.
        #
        # Una tabla **lenta** sí se cachea: el resultado es legítimo —el resto de los conteos
        # salieron— y repetir el barrido cada visita para volver a chocar con el mismo timeout
        # es justo la carga que este cache existe para evitar.
        if not resultado.base_no_disponible:
            with self._candado:
                self._cache[self._CLAVE_CACHE] = resultado
        return resultado

    def _contar_todas_las_capas(self) -> ConteosCapas:
        resultado: list[dict] = []
        caida = False
        lentas: list[str] = []

        def _anotar(capa: str, tabla: str) -> None:
            filas, nota = self._contar(capa, tabla)
            resultado.append({"capa": capa, "tabla": tabla, "filas": filas, "nota": nota})
            if nota and "no respondió" in nota:
                nonlocal caida
                caida = True
            elif nota and "excedió su tiempo" in nota:
                lentas.append(f"{capa}.{tabla}")

        bronze_existentes = self._tablas_bronze_existentes()
        for nombre in bronze_existentes:
            _anotar("bronze", nombre)
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
            _anotar("silver", tabla)

        for tabla in TABLAS_GOLD:
            _anotar("gold", tabla)

        return ConteosCapas(
            filas=resultado, base_no_disponible=caida, tablas_lentas=tuple(lentas)
        )


@lru_cache
def get_repositorio_about() -> RepositorioAbout:
    """Dependencia de FastAPI (`Depends(get_repositorio_about)`). Las pruebas rápidas la
    sustituyen con `app.dependency_overrides` (ver `tests/fixtures_about.py`).

    **`@lru_cache` no es un detalle: sin él el cache de `conteos_capas()` no sirve de nada.**
    FastAPI llama a esta función en **cada petición**, así que sin el singleton cada una
    estrenaba su propio `TTLCache` vacío y volvía a hacer el barrido completo de ~30 `COUNT(*)`.
    Medido por Edgar Coronel al revisar el PR #350: 3 `GET` daban 3 barridos; con `@lru_cache`
    dan 1. Es el mismo patrón que hace funcionar a `cache_predicciones.py`, que depende del
    `@lru_cache` de `get_repositorio_modelos()`.

    Consecuencia que el `ConteosCapas` resuelve: el repositorio pasa a ser **compartido entre
    hilos**, así que ningún motivo de fallo puede vivir en un atributo de instancia.
    """
    return RepositorioAboutPostgres()
