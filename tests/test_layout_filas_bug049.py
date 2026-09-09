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

`_layout_grilla()` la usan **9 tableros** (DB-01, DB-02, DB-03, DB-04, DB-06, DB-07,
DB-08, DB-09, DB-10). Por eso hay guardas de invariantes, no solo del caso de DB-03.

**Corregido en US-213 (2026-09-05).** Este docstring afirmaba que "DB-05 y DB-08 van por
`_layout_tabs()`, que no se toca", y por eso la corrección de BUG-049 se acotó al camino
plano. Era falso en las dos mitades: DB-08 **no declara `tabs:`** —va por el camino plano,
y de hecho siempre agrupó bien— y **DB-05 es el único tablero con tabs**, así que fue el
único que se quedó como tira vertical. La creencia de que el defecto estaba cubierto en
dos tableros es lo que lo dejó vivo un mes en uno.

Ahora `_layout_tabs()` agrupa con la misma `_agrupar_en_filas()` que el camino plano, y
las guardas de abajo cubren **las dos rutas** para que no puedan volver a divergir.

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


# --------------------------------------------------------- el camino con tabs (US-213)
#
# DB-05 es el único tablero con `tabs:`. Cada tab lleva la nota de fuente del driver
# como MARKDOWN más su juego de charts.
#
# Estas pruebas ejercitan el ALGORITMO con un patrón fijo; los anchos que DB-05 declara
# hoy los vigila `test_cada_tab_de_db05_se_lee_en_horizontal_como_los_demas_tableros`
# en `test_semantic_db05_db08.py`, que lee el YAML real. La separación es a propósito:
# si mañana cambian los anchos del YAML, la guarda del algoritmo no debe volverse roja.


#: Patrón de tarjetas + charts a media fila. Es el caso que el defecto rompía: cuatro
#: `ancho: 3` que deben compartir fila y dos `ancho: 6` que deben ir apareados.
ANCHOS_TARJETAS_Y_MEDIAS = [3, 3, 3, 3, 6, 6]


def _tabs(anchos_por_tab: dict[str, list[int]], con_nota: bool = True):
    """Construye la tupla que consume `_layout_tabs()`, con ids de chart únicos."""
    tabs = []
    cid = 0
    for tab_id, anchos in anchos_por_tab.items():
        charts = []
        for ancho in anchos:
            charts.append((cid, f"{tab_id} · chart {cid}", ancho, 50))
            cid += 1
        tabs.append((tab_id, f"{tab_id} · etiqueta", charts, f"fuente de {tab_id}" if con_nota else None))
    return tabs


def test_un_tab_agrupa_sus_charts_igual_que_el_camino_plano(sync) -> None:
    """El defecto corregido en US-213: dentro de un tab cada chart iba en su propia fila.

    Guarda directa — con los anchos reales de un tab de DB-05, las cuatro tarjetas
    de `ancho: 3` deben compartir fila y la línea de tiempo debe ir junto a la tabla.
    """
    pos = sync._layout_tabs(_tabs({"D1": ANCHOS_TARJETAS_Y_MEDIAS}, con_nota=False))

    filas = pos["TAB-D1"]["children"]
    assert len(filas) == 2, f"un tab de DB-05 debe quedar en 2 filas, quedó en {len(filas)}"
    assert [len(pos[f]["children"]) for f in filas] == [4, 2]


def test_los_seis_tabs_de_db05_agrupan_por_igual(sync) -> None:
    """El usuario ve los 6 tabs, no solo el primero: la agrupación no puede aplicarse
    al primero y perderse en los demás."""
    ids = ["D1", "D2", "D3", "D4", "D5", "D6"]
    pos = sync._layout_tabs(_tabs({d: ANCHOS_TARJETAS_Y_MEDIAS for d in ids}))

    for tab_id in ids:
        filas = pos[f"TAB-{tab_id}"]["children"]
        # nota (MARKDOWN) + fila de 4 tarjetas + fila de 2 charts anchos
        assert len(filas) == 3, f"TAB-{tab_id} quedó en {len(filas)} filas, se esperaban 3"
        anchos_por_fila = [
            [pos[h]["meta"]["width"] for h in pos[f]["children"]] for f in filas
        ]
        assert anchos_por_fila == [[12], [3, 3, 3, 3], [6, 6]], (
            f"TAB-{tab_id} agrupó como {anchos_por_fila}"
        )


def test_la_nota_del_tab_no_se_mezcla_con_los_charts(sync) -> None:
    """La nota es `ancho: 12` y va sola arriba: si se agrupara con las tarjetas,
    la primera fila desbordaría la grilla."""
    pos = sync._layout_tabs(_tabs({"D1": ANCHOS_TARJETAS_Y_MEDIAS}))

    primera = pos["TAB-D1"]["children"][0]
    assert pos[primera]["children"] == ["MD-D1-0"]
    assert pos["MD-D1-0"]["type"] == "MARKDOWN"


@pytest.mark.parametrize(
    "anchos",
    [ANCHOS_TARJETAS_Y_MEDIAS, [12], [7, 7], [4, 4, 4, 4], [1] * 25, [3, 12, 3]],
)
def test_ninguna_fila_de_un_tab_excede_la_grilla(sync, anchos: list[int]) -> None:
    """Mismo invariante duro del camino plano, ahora también dentro de cada tab."""
    pos = sync._layout_tabs(_tabs({"D1": anchos}, con_nota=False))
    for row_id in pos["TAB-D1"]["children"]:
        suma = sum(pos[h]["meta"]["width"] for h in pos[row_id]["children"])
        assert suma <= sync.ANCHO_GRILLA, f"{row_id} suma {suma}, excede {sync.ANCHO_GRILLA}"


def test_agrupar_en_tabs_no_pierde_ni_duplica_charts(sync) -> None:
    """Los 36 charts de DB-05 (6 tabs × 6) deben seguir existiendo, una sola vez."""
    ids = ["D1", "D2", "D3", "D4", "D5", "D6"]
    pos = sync._layout_tabs(_tabs({d: ANCHOS_TARJETAS_Y_MEDIAS for d in ids}))

    chart_ids = [v["meta"]["chartId"] for v in pos.values()
                 if isinstance(v, dict) and v.get("type") == "CHART"]
    assert len(chart_ids) == 36
    assert len(set(chart_ids)) == 36, "el agrupado duplicó charts entre filas o tabs"


def test_los_ids_de_nodo_no_colisionan_entre_tabs(sync) -> None:
    """Las filas y los charts se numeran con contadores distintos; ninguno puede
    repetirse entre tabs o Superset monta el componente equivocado."""
    ids = ["D1", "D2", "D3", "D4", "D5", "D6"]
    pos = sync._layout_tabs(_tabs({d: ANCHOS_TARJETAS_Y_MEDIAS for d in ids}))

    for tipo, esperados in (("ROW", 18), ("CHART", 36)):
        nodos = [k for k, v in pos.items()
                 if isinstance(v, dict) and v.get("type") == tipo]
        assert len(nodos) == len(set(nodos)) == esperados

    for row_id in [k for k, v in pos.items()
                   if isinstance(v, dict) and v.get("type") == "ROW"]:
        for comp_id in pos[row_id]["children"]:
            assert pos[comp_id]["parentId"] == row_id, (
                "cada componente debe apuntar a SU fila; con el parentId cruzado el "
                "DashboardBuilder no monta el tab"
            )
