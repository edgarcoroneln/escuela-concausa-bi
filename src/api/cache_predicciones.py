"""Cache TTL por fila para `RepositorioModelos` (US-416).

Decora cualquier implementación de `RepositorioModelos` (en producción, `RepositorioModelosPostgres`
con timeout, ver `repositorio_modelos.py`) con un cache en memoria compartido entre
`obtener_prediccion` (unitario) y `listar_predicciones` (batch), clave `(cct, id_ciclo)`.

**Por qué cache por fila y no de lote completo:** cachear la respuesta completa de un batch bajo
la clave "tupla exacta de CCTs pedidos" solo tiene cache-hit si un cliente repite exactamente la
misma lista dentro del TTL -- poco probable en uso real (analistas pidiendo subconjuntos
distintos, paginación, etc.). Con cache por fila, un batch que se solapa parcialmente con uno
anterior solo consulta Postgres por los CCT faltantes, y el unitario y el batch comparten los
mismos datos con la misma frescura. Decisión no confirmada con Karla Monter/Manuel Serranía por
falta de tiempo -- ver DevLog de esta historia.

**Cache negativo:** un CCT confirmado sin fila en `gold.predicciones` se marca con el sentinel
`_SIN_FILA` para no volver a golpear Postgres por él dentro del TTL (nunca se devuelve el sentinel
al llamador, siempre se traduce de vuelta a `None`/omitido).

**Errores nunca se cachean:** `RepositorioModelosNoDisponible` (timeout de Postgres) se propaga
siempre -- el `TTLCache` solo se escribe después de una respuesta exitosa del repo delegado.

**Timeout de un batch es atómico:** si la consulta por los CCT faltantes de un `listar_predicciones`
lanza `RepositorioModelosNoDisponible`, toda la petición falla (503) aunque algunos CCT ya
estuvieran en cache. Es intencional: preferible fallar todo el batch antes que devolver una página
parcial que parezca completa sin indicarlo (misma regla SIN_DATO -- nunca degradar en silencio).

**Concurrencia:** las rutas de `v1/predicciones.py` son `def` síncronas, así que Starlette las
corre en su threadpool -- sí hay concurrencia real de hilos sobre la instancia singleton de
`get_repositorio_modelos()` (`@lru_cache`, un cache por proceso). `cachetools.TTLCache` no es
thread-safe por sí solo, así que todo acceso va protegido por un `threading.Lock`.

Toda lectura del cache es **una sola** llamada (`.get(clave, _AUSENTE)`), nunca `in` seguido de
`[]`. `TTLCache` consulta el reloj en cada una de esas operaciones por separado, así que el par
`in`/`[]` tiene una ventana real -- microsegundos, pero real -- en la que la entrada expira entre
ambas y el `[]` lanza `KeyError`, que subiría como 500. Sostener el `Lock` no lo evita: protege el
estado compartido, no detiene el reloj. Cubierto por
`tests/test_cache_predicciones.py::test_entrada_que_expira_entre_dos_lecturas_no_revienta`.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from cachetools import TTLCache

from src.api.repositorio_modelos import RepositorioModelos

_SIN_FILA = object()  # sentinel: "confirmado sin fila", nunca se expone al llamador
# Sentinel de ausencia para `TTLCache.get`. Hace falta uno propio porque `None` es un valor
# legitimo aqui, y porque `x in cache` seguido de `cache[x]` consulta el reloj DOS veces: una
# entrada vigente en el `in` puede haber expirado en el `[]` y lanzar `KeyError` (comprobado en
# cachetools 7.1.8). El `Lock` no protege de eso: guarda el estado, no detiene el tiempo.
_AUSENTE = object()


class RepositorioModelosCacheado:
    """Decora un `RepositorioModelos` con cache TTL en memoria por `(cct, id_ciclo)`."""

    def __init__(
        self,
        repo: RepositorioModelos,
        ttl_segundos: float,
        max_entradas: int,
        timer: Callable[[], float] = time.monotonic,
    ) -> None:
        self._repo = repo
        self._cache: TTLCache = TTLCache(maxsize=max_entradas, ttl=ttl_segundos, timer=timer)
        self._lock = threading.Lock()

    def obtener_prediccion(self, cct: str, id_ciclo: str) -> dict | None:
        clave = (cct, id_ciclo)
        with self._lock:
            valor = self._cache.get(clave, _AUSENTE)
        if valor is not _AUSENTE:
            return None if valor is _SIN_FILA else valor

        resultado = self._repo.obtener_prediccion(cct, id_ciclo)

        with self._lock:
            self._cache[clave] = _SIN_FILA if resultado is None else resultado
        return resultado

    def listar_predicciones(self, ccts: list[str], id_ciclo: str) -> list[dict]:
        if not ccts:
            return []

        encontrados: dict[str, dict] = {}
        faltantes: list[str] = []
        with self._lock:
            for cct in ccts:
                valor = self._cache.get((cct, id_ciclo), _AUSENTE)
                if valor is _AUSENTE:
                    if cct not in faltantes:  # `ccts` puede traer repetidos
                        faltantes.append(cct)
                elif valor is not _SIN_FILA:
                    encontrados[cct] = valor

        if faltantes:
            # Propaga RepositorioModelosNoDisponible sin capturarla -- falla todo el batch,
            # aunque `encontrados` ya tuviera resultados (ver docstring del módulo).
            filas = self._repo.listar_predicciones(faltantes, id_ciclo)
            filas_por_cct = {fila["cct"]: fila for fila in filas}
            with self._lock:
                for cct in faltantes:
                    fila = filas_por_cct.get(cct)
                    self._cache[(cct, id_ciclo)] = fila if fila is not None else _SIN_FILA
                    if fila is not None:
                        encontrados[cct] = fila

        vistos: set[str] = set()
        resultado: list[dict] = []
        for cct in ccts:
            if cct in encontrados and cct not in vistos:
                vistos.add(cct)
                resultado.append(encontrados[cct])
        return resultado
