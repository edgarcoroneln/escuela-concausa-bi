"""Pruebas del cache TTL de predicciones y del timeout de Postgres (US-416).

No usan Postgres real ni SQLite como sustituto (regla del proyecto: SQLite no modela el esquema
`gold` igual que Postgres, daría falsos verdes). El timeout se prueba mockeando el límite de
SQLAlchemy (`OperationalError`), no la base de datos.
"""

from __future__ import annotations

import pytest
from sqlalchemy.exc import OperationalError

from src.api.cache_predicciones import RepositorioModelosCacheado
from src.api.repositorio_modelos import (
    RepositorioModelosNoDisponible,
    RepositorioModelosPostgres,
)
from tests.fixtures_modelos import RepositorioModelosFake

CCT_CON_FILA = "09DPR0001A"
CCT_CON_FILA_2 = "19DES0007C"
CCT_SIN_FILA = "00XXXX0000Z"
CICLO = "2024-2025"


class _RepositorioEspia:
    """Envuelve un `RepositorioModelos` y cuenta cuántas veces se le llama de verdad."""

    def __init__(self, repo) -> None:
        self._repo = repo
        self.llamadas_obtener = 0
        self.llamadas_listar = 0
        self.args_listar: list[list[str]] = []

    def obtener_prediccion(self, cct: str, id_ciclo: str) -> dict | None:
        self.llamadas_obtener += 1
        return self._repo.obtener_prediccion(cct, id_ciclo)

    def listar_predicciones(self, ccts: list[str], id_ciclo: str) -> list[dict]:
        self.llamadas_listar += 1
        self.args_listar.append(list(ccts))
        return self._repo.listar_predicciones(ccts, id_ciclo)


class _RepositorioFallaNVeces:
    """Falla las primeras `n_fallos` llamadas a `obtener_prediccion`, luego responde `valor_exito`."""

    def __init__(self, n_fallos: int, valor_exito: dict) -> None:
        self.llamadas = 0
        self._n_fallos = n_fallos
        self._valor_exito = valor_exito

    def obtener_prediccion(self, cct: str, id_ciclo: str) -> dict | None:
        self.llamadas += 1
        if self.llamadas <= self._n_fallos:
            raise RepositorioModelosNoDisponible("Postgres no respondió.")
        return self._valor_exito

    def listar_predicciones(self, ccts: list[str], id_ciclo: str) -> list[dict]:
        raise NotImplementedError


class _RepositorioListarSiempreFalla:
    def __init__(self) -> None:
        self.llamadas = 0

    def obtener_prediccion(self, cct: str, id_ciclo: str) -> dict | None:
        raise NotImplementedError

    def listar_predicciones(self, ccts: list[str], id_ciclo: str) -> list[dict]:
        self.llamadas += 1
        raise RepositorioModelosNoDisponible("Postgres no respondió.")


class _RelojFalso:
    """Timer inyectable para `TTLCache` -- controla el paso del tiempo sin `sleep` real."""

    def __init__(self) -> None:
        self._ahora = 0.0

    def avanzar(self, segundos: float) -> None:
        self._ahora += segundos

    def __call__(self) -> float:
        return self._ahora


# --------------------------------------------------------------------------- #
# RepositorioModelosCacheado -- obtener_prediccion (unitario)
# --------------------------------------------------------------------------- #


def test_obtener_prediccion_cache_hit_evita_llamada_al_repo() -> None:
    espia = _RepositorioEspia(RepositorioModelosFake())
    cache = RepositorioModelosCacheado(espia, ttl_segundos=30, max_entradas=10)

    primero = cache.obtener_prediccion(CCT_CON_FILA, CICLO)
    segundo = cache.obtener_prediccion(CCT_CON_FILA, CICLO)

    assert primero == segundo
    assert espia.llamadas_obtener == 1


def test_obtener_prediccion_expira_por_ttl() -> None:
    reloj = _RelojFalso()
    espia = _RepositorioEspia(RepositorioModelosFake())
    cache = RepositorioModelosCacheado(espia, ttl_segundos=10, max_entradas=10, timer=reloj)

    cache.obtener_prediccion(CCT_CON_FILA, CICLO)
    reloj.avanzar(11)
    cache.obtener_prediccion(CCT_CON_FILA, CICLO)

    assert espia.llamadas_obtener == 2


class _RelojQueCorre:
    """Reloj que avanza en **cada** consulta.

    Un `_RelojFalso` normal se queda quieto entre llamadas, así que nunca reproduce la ventana en
    la que una entrada caduca *entre* dos lecturas seguidas del mismo cache. Este sí: cada vez que
    `TTLCache` mira la hora, el tiempo ya avanzó -- que es lo que hace un reloj de verdad.
    """

    def __init__(self, paso: float) -> None:
        self._ahora = 0.0
        self._paso = paso

    def __call__(self) -> float:
        self._ahora += self._paso
        return self._ahora


def test_entrada_que_expira_entre_dos_lecturas_no_revienta() -> None:
    """Regresión: leer el cache con `in` + `[]` consulta el reloj DOS veces y puede dar `KeyError`.

    Con `ttl=10` y un reloj que avanza 6 por consulta, la entrada se escribe en t=6 (caduca en 16).
    En la lectura siguiente, un `clave in cache` mira la hora en t=12 (vigente, dice `True`) y el
    `cache[clave]` de la línea de abajo la mira otra vez en t=18 -- ya caducada -- y lanza
    `KeyError`, que subiría al handler genérico como un **500**. Sostener el `Lock` no lo evita:
    protege el estado compartido, no detiene el reloj.

    Por eso el cache se lee con **una sola** llamada, `.get(clave, _AUSENTE)`. Esta prueba falla si
    alguien vuelve al patrón `in` + `[]`.
    """
    reloj = _RelojQueCorre(paso=6.0)
    espia = _RepositorioEspia(RepositorioModelosFake())
    cache = RepositorioModelosCacheado(espia, ttl_segundos=10, max_entradas=10, timer=reloj)

    esperado = cache.obtener_prediccion(CCT_CON_FILA, CICLO)
    assert esperado is not None

    # No debe lanzar: o el valor sigue vigente, o es un miss limpio que reconsulta al repo.
    assert cache.obtener_prediccion(CCT_CON_FILA, CICLO) == esperado


def test_listar_predicciones_con_entrada_al_filo_del_ttl_no_revienta() -> None:
    """La misma ventana existe en el camino del batch (`listar_predicciones`)."""
    reloj = _RelojQueCorre(paso=6.0)
    espia = _RepositorioEspia(RepositorioModelosFake())
    cache = RepositorioModelosCacheado(espia, ttl_segundos=10, max_entradas=10, timer=reloj)

    cache.obtener_prediccion(CCT_CON_FILA, CICLO)
    filas = cache.listar_predicciones([CCT_CON_FILA, CCT_CON_FILA_2], CICLO)

    assert [f["cct"] for f in filas] == [CCT_CON_FILA, CCT_CON_FILA_2]


def test_cache_negativo_no_repite_consulta_por_cct_sin_fila() -> None:
    """Un CCT confirmado sin predicción no vuelve a golpear el repo dentro del TTL."""
    espia = _RepositorioEspia(RepositorioModelosFake())
    cache = RepositorioModelosCacheado(espia, ttl_segundos=30, max_entradas=10)

    assert cache.obtener_prediccion(CCT_SIN_FILA, CICLO) is None
    assert cache.obtener_prediccion(CCT_SIN_FILA, CICLO) is None
    assert espia.llamadas_obtener == 1


def test_excepcion_nunca_se_cachea() -> None:
    valor_exito = {"cct": "X", "id_ciclo": CICLO}
    repo = _RepositorioFallaNVeces(n_fallos=1, valor_exito=valor_exito)
    cache = RepositorioModelosCacheado(repo, ttl_segundos=30, max_entradas=10)

    with pytest.raises(RepositorioModelosNoDisponible):
        cache.obtener_prediccion("X", CICLO)

    exito = cache.obtener_prediccion("X", CICLO)  # segunda llamada real: éxito, se cachea
    assert exito == valor_exito

    de_cache = cache.obtener_prediccion("X", CICLO)  # tercera: debe venir de cache
    assert de_cache == valor_exito
    assert repo.llamadas == 2  # la tercera no volvió a llamar al repo delegado


# --------------------------------------------------------------------------- #
# RepositorioModelosCacheado -- listar_predicciones (batch)
# --------------------------------------------------------------------------- #


def test_listar_predicciones_solo_consulta_los_ccts_faltantes() -> None:
    espia = _RepositorioEspia(RepositorioModelosFake())
    cache = RepositorioModelosCacheado(espia, ttl_segundos=30, max_entradas=10)

    cache.obtener_prediccion(CCT_CON_FILA, CICLO)  # precachea uno de los dos
    resultado = cache.listar_predicciones([CCT_CON_FILA, CCT_CON_FILA_2], CICLO)

    assert {p["cct"] for p in resultado} == {CCT_CON_FILA, CCT_CON_FILA_2}
    assert espia.llamadas_listar == 1
    assert espia.args_listar[0] == [CCT_CON_FILA_2]  # solo pidió el que faltaba

    # segunda llamada: ambos ya en cache, no debe volver a consultar al repo delegado
    cache.listar_predicciones([CCT_CON_FILA, CCT_CON_FILA_2], CICLO)
    assert espia.llamadas_listar == 1


def test_listar_predicciones_deduplica_ccts_repetidos() -> None:
    espia = _RepositorioEspia(RepositorioModelosFake())
    cache = RepositorioModelosCacheado(espia, ttl_segundos=30, max_entradas=10)

    resultado = cache.listar_predicciones([CCT_CON_FILA, CCT_CON_FILA], CICLO)

    assert len(resultado) == 1
    assert resultado[0]["cct"] == CCT_CON_FILA


def test_listar_predicciones_propaga_excepcion_sin_cachear() -> None:
    """El timeout de un batch es atómico: falla toda la petición, nunca queda a medias en cache."""
    repo = _RepositorioListarSiempreFalla()
    cache = RepositorioModelosCacheado(repo, ttl_segundos=30, max_entradas=10)

    with pytest.raises(RepositorioModelosNoDisponible):
        cache.listar_predicciones([CCT_CON_FILA], CICLO)
    with pytest.raises(RepositorioModelosNoDisponible):
        cache.listar_predicciones([CCT_CON_FILA], CICLO)

    assert repo.llamadas == 2  # el fallo anterior no dejó nada cacheado


# --------------------------------------------------------------------------- #
# RepositorioModelosPostgres -- traducción del timeout de Postgres
# --------------------------------------------------------------------------- #


class _ConexionFalsaQueExpiraPorTimeout:
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def execute(self, *args, **kwargs):
        raise OperationalError("SET LOCAL statement_timeout ...", None, Exception("query canceled"))


class _EngineFalsoQueExpiraPorTimeout:
    def begin(self):
        return _ConexionFalsaQueExpiraPorTimeout()


def test_repositorio_modelos_postgres_traduce_timeout_a_no_disponible() -> None:
    """Un `OperationalError` de Postgres (timeout) nunca llega crudo al router (US-416)."""
    repo = RepositorioModelosPostgres(engine=_EngineFalsoQueExpiraPorTimeout(), timeout_ms=1)

    with pytest.raises(RepositorioModelosNoDisponible):
        repo.obtener_prediccion(CCT_CON_FILA, CICLO)

    with pytest.raises(RepositorioModelosNoDisponible):
        repo.listar_predicciones([CCT_CON_FILA], CICLO)
