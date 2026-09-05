"""Cache TTL de `RepositorioGoldPostgres._ciclo_mas_reciente()` (BUG-044).

Pide un motor de Postgres real solo por firma (`RepositorioGoldPostgres.__init__` acepta
`engine: Engine | None`, ver `src/api/db.py`); estas pruebas pasan un motor falso que solo cuenta
cuántas veces se ejecuta el `SELECT MAX(id_ciclo)`, así que corren sin Postgres, igual que
`tests/fixtures_gold.py`.
"""
from __future__ import annotations

from typing import Self

import pytest

from src.api.repositorio_gold import RepositorioGoldPostgres


class _ResultadoFake:
    def __init__(self, valor: str | None) -> None:
        self._valor = valor

    def scalar_one_or_none(self) -> str | None:
        return self._valor


class _ConexionFake:
    def __init__(self, valor: str | None, contador: dict) -> None:
        self._valor = valor
        self._contador = contador

    def execute(self, _consulta) -> _ResultadoFake:
        self._contador["consultas"] += 1
        return _ResultadoFake(self._valor)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc) -> bool:
        return False


class _EngineFake:
    """Cuenta cuántas veces alguien abre una conexión y ejecuta algo -- eso es lo único que
    `_ciclo_mas_reciente()` necesita del motor real."""

    def __init__(self, valor: str | None) -> None:
        self._valor = valor
        self.contador = {"consultas": 0}

    def connect(self) -> _ConexionFake:
        return _ConexionFake(self._valor, self.contador)


@pytest.fixture(autouse=True)
def _limpia_cache_de_ciclo():
    """El cache es a nivel de clase (BUG-044, a propósito: sobrevive entre instancias, que es
    justo lo que necesita `get_repositorio_gold()` creando una instancia nueva por petición) --
    hay que resetearlo entre pruebas para que no se contaminen entre sí."""
    RepositorioGoldPostgres._ciclo_cache = None
    yield
    RepositorioGoldPostgres._ciclo_cache = None


def test_no_repite_la_consulta_dentro_del_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    reloj = {"ahora": 1_000.0}
    monkeypatch.setattr("src.api.repositorio_gold.time.monotonic", lambda: reloj["ahora"])

    engine = _EngineFake("2024-2025")
    repo = RepositorioGoldPostgres(engine=engine)

    assert repo._ciclo_mas_reciente() == "2024-2025"
    assert repo._ciclo_mas_reciente() == "2024-2025"
    assert engine.contador["consultas"] == 1  # la segunda llamada no vuelve a tocar Postgres


def test_recalcula_pasado_el_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    reloj = {"ahora": 1_000.0}
    monkeypatch.setattr("src.api.repositorio_gold.time.monotonic", lambda: reloj["ahora"])

    engine = _EngineFake("2024-2025")
    repo = RepositorioGoldPostgres(engine=engine)
    repo._ciclo_mas_reciente()

    reloj["ahora"] += 301  # un segundo después de los 300s de TTL
    engine._valor = "2025-2026"  # simula que dbt corrió y materializó un ciclo nuevo
    assert repo._ciclo_mas_reciente() == "2025-2026"
    assert engine.contador["consultas"] == 2


def test_el_cache_se_comparte_entre_instancias(monkeypatch: pytest.MonkeyPatch) -> None:
    """`get_repositorio_gold()` crea una `RepositorioGoldPostgres` nueva en cada petición
    (`Depends`, ver `src/api/v1/gold.py`): un cache de instancia no serviría de nada. Tiene que
    vivir a nivel de clase para que la segunda petición no vuelva a pagar el `SELECT MAX`."""
    reloj = {"ahora": 2_000.0}
    monkeypatch.setattr("src.api.repositorio_gold.time.monotonic", lambda: reloj["ahora"])

    engine_primera_peticion = _EngineFake("2024-2025")
    RepositorioGoldPostgres(engine=engine_primera_peticion)._ciclo_mas_reciente()

    engine_segunda_peticion = _EngineFake("no-deberia-usarse")
    valor = RepositorioGoldPostgres(engine=engine_segunda_peticion)._ciclo_mas_reciente()

    assert valor == "2024-2025"
    assert engine_segunda_peticion.contador["consultas"] == 0
