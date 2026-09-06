"""Guarda del agrupado de charts en filas del layout de Superset (BUG-049).

**El defecto que impiden que vuelva.** `_layout_grilla()` ponía cada chart en su PROPIA
fila, así que el `ancho` declarado en los YAML no servía para nada: cuatro tarjetas de
`ancho: 3` —escritas para ir lado a lado y sumar 12— se apilaban una debajo de otra, cada
una ocupando 3/12 de la fila con nueve doceavos vacíos a su derecha. El tablero quedaba
como una tira vertical de un chart por pantalla.

Verificado contra el Superset desplegado antes de tocar nada: DB-03 tenía **11 charts en
11 filas**, con anchos 3,3,3,3,6,6,12,6,6,6,6.

Consecuencia práctica, no solo estética: las columnas del final de las tablas —las de
drill-down de US-214a— quedaban tras un scroll largo, y por eso los casos 1.9 y 1.10 del
plan de US-215a no se pudieron probar en la primera pasada de navegador.

`_layout_grilla()` la usan **8 tableros** (DB-01, DB-02, DB-03, DB-04, DB-06, DB-07,
DB-09, DB-10); DB-05 y DB-08 van por `_layout_tabs()`, que no se toca. Por eso hay guardas
de invariantes, no solo del caso de DB-03.

Validación estática: no necesita Superset ni base de datos.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def sync():
    ruta = RAIZ / "superset" / "sync_semantic_layer.py"
    spec = importlib.util.spec_from_file_location("sync_layout_bug049", ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("sync_layout_bug049", modulo)
    spec.loader.exec_module(modulo)
    return modulo


def _charts(anchos: list[int]) -> list[tuple[int, str, int, int]]:
    return [(i, f"chart {i}", a, 50) for i, a in enumerate(anchos)]


# --------------------------------------------------------- el caso que motivó el bug


def test_cuatro_tarjetas_de_ancho_3_van_en_una_sola_fila(sync) -> None:
    """El caso exacto de DB-03/DB-04: 3+3+3+3 = 12, una fila."""
    filas = sync._agrupar_en_filas(_charts([3, 3, 3, 3]))
    assert len(filas) == 1, f"se generaron {len(filas)} filas en vez de 1"
    assert len(filas[0]) == 4


def test_el_patron_real_de_db03_agrupa_como_fue_declarado(sync) -> None:
    """Los anchos reales de DB-03: 3,3,3,3 | 6,6 | 12 | 6,6 | 6,6."""
    filas = sync._agrupar_en_filas(_charts([3, 3, 3, 3, 6, 6, 12, 6, 6, 6, 6]))
    assert [len(f) for f in filas] == [4, 2, 1, 2, 2]
    assert len(filas) == 5, "DB-03 debe pasar de 11 filas a 5"


# --------------------------------------------------------- invariantes (8 tableros)


@pytest.mark.parametrize(
    "anchos",
    [
        [3, 3, 3, 3, 6, 6, 12, 6, 6, 6, 6],          # DB-03
        [3, 3, 3, 3, 12, 6, 6, 4, 4, 4, 4, 4, 4],    # DB-04
        [12],                                         # un solo chart ancho
        [4, 4, 4, 4],                                 # 4+4+4 = 12, luego uno solo
        [7, 7],                                        # ninguno cabe con el otro
        [1] * 25,                                      # muchos chicos
    ],
)
def test_ninguna_fila_excede_la_grilla(sync, anchos: list[int]) -> None:
    """Invariante duro: si una fila suma más de 12, Superset desborda el layout."""
    for i, fila in enumerate(sync._agrupar_en_filas(_charts(anchos))):
        suma = sum(c[2] for c in fila)
        assert suma <= sync.ANCHO_GRILLA, f"fila {i} suma {suma}, excede {sync.ANCHO_GRILLA}"


@pytest.mark.parametrize(
    "anchos",
    [[3, 3, 3, 3], [3, 3, 3, 3, 6, 6, 12, 6, 6, 6, 6], [12], [7, 7], [1] * 25],
)
def test_no_se_pierde_ni_se_duplica_ningun_chart(sync, anchos: list[int]) -> None:
    """Agrupar no puede perder charts: es reordenar en filas, no filtrar."""
    charts = _charts(anchos)
    planos = [c for fila in sync._agrupar_en_filas(charts) for c in fila]
    assert planos == charts, "el agrupado alteró, perdió o duplicó charts"


def test_se_respeta_el_orden_declarado(sync) -> None:
    """El orden del YAML es la lectura que diseñó su autora: no se reordena."""
    charts = _charts([6, 3, 3, 6, 6])
    planos = [c[0] for fila in sync._agrupar_en_filas(charts) for c in fila]
    assert planos == [0, 1, 2, 3, 4]


def test_un_chart_de_ancho_12_ocupa_su_fila_solo(sync) -> None:
    filas = sync._agrupar_en_filas(_charts([12, 12]))
    assert [len(f) for f in filas] == [1, 1]


def test_lista_vacia_no_revienta(sync) -> None:
    assert sync._agrupar_en_filas([]) == []


# --------------------------------------------------------- el árbol que consume Superset


def test_el_position_json_mantiene_el_arbol_que_espera_el_frontend(sync) -> None:
    """Agrupar no puede romper la estructura ROOT_ID → GRID_ID → ROW → CHART."""
    pos = sync._layout_grilla(_charts([3, 3, 3, 3, 12]))

    assert pos["ROOT_ID"]["children"] == ["GRID_ID"]
    filas = pos["GRID_ID"]["children"]
    assert filas == ["ROW-0", "ROW-1"], "las filas deben ir numeradas y en orden"

    for row_id in filas:
        assert pos[row_id]["type"] == "ROW"
        assert pos[row_id]["parentId"] == "GRID_ID"
        for comp_id in pos[row_id]["children"]:
            assert pos[comp_id]["type"] == "CHART"
            assert pos[comp_id]["parentId"] == row_id, (
                "cada CHART debe apuntar a SU fila; con el parentId cruzado el "
                "DashboardBuilder no monta el componente"
            )


def test_los_ids_de_chart_no_se_repiten(sync) -> None:
    """Con dos charts en la misma fila, el índice ya no puede venir del índice de fila."""
    pos = sync._layout_grilla(_charts([3, 3, 3, 3, 6, 6]))
    ids = [k for k in pos if k.startswith("CHART-")]
    assert len(ids) == len(set(ids)) == 6
