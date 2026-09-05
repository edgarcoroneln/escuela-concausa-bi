"""Pruebas del drill-down cruzado de DB-03 y DB-04 (US-214a).

El drill-down entre tableros de Superset se apoya en un detalle fragil: los IDs de
filtro nativo (`NATIVE_FILTER-US203-{indice}`) los genera `_filtros_nativos()` **por
posicion** en `filtros_globales` del tablero destino. Nadie valida esa correspondencia
en tiempo de ejecucion:

* Si alguien **reordena o inserta** un filtro, el link sigue existiendo y sigue
  navegando — pero preselecciona la **columna equivocada**. No hay error en el sync,
  ni en la API, ni en la consola del navegador. El tablero simplemente miente.
* Si el `<a href>` viaja sin `allow_render_html`, la celda muestra el HTML crudo.
* Si una ruta del contrato declara una llave que el cubo de origen **no tiene**, la
  ruta es indeclarable — y eso fue exactamente el defecto de `DB-04 -> DB-03`, que
  US-211a escribio con llave `cct` cuando DEC-008 dejo ese cubo al grano
  [cve_mun, nivel, id_ciclo], sin columna `cct`.

Estas pruebas cubren las tres **clases** de error, no las tres instancias.

Validacion estatica: no necesita Superset ni base de datos.
Contrato: `superset/semantic/metrics_db03_db04.yaml` (bloque `drill_down`).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SEMANTIC = RAIZ / "superset" / "semantic"
DASHBOARDS = RAIZ / "superset" / "dashboards"

SQL_POR_CUBO = {
    "db03": SEMANTIC / "db03_cubo_escuela_360.sql",
    "db04": SEMANTIC / "db04_cubo_comparador_municipio.sql",
}
YAML_POR_TABLERO = {
    "DB-03": DASHBOARDS / "db03_ficha_escuela.yaml",
    "DB-04": DASHBOARDS / "db04_comparador_municipio.yaml",
}

# Tableros que son DESTINO de un link pero no de esta historia: no se validan sus
# charts ni sus filtros propios, solo que el indice al que apunta el link exista y
# tenga la columna que el link dice. Desbloqueados por el PR #215 de Manuel Serrania.
YAML_DESTINO_AJENO = {
    "DB-06": DASHBOARDS / "db06_predicciones.yaml",
    "DB-09": DASHBOARDS / "db09_recomendaciones.yaml",
}
YAML_METRICAS = SEMANTIC / "metrics_db03_db04.yaml"

# Cada link declarado: en que SQL vive y a que tablero apunta.
LINKS = {
    "link_db04": {"origen": "db03", "destino": "DB-04", "slug": "db04-comparador-municipio"},
    "link_db03": {"origen": "db04", "destino": "DB-03", "slug": "db03-ficha-escuela"},
    "link_db06": {"origen": "db03", "destino": "DB-06", "slug": "db06-predicciones"},
    "link_db09": {"origen": "db03", "destino": "DB-09", "slug": "db09-recomendaciones"},
}

ESTADOS_VALIDOS = {"implementado", "bloqueado", "ajeno"}

# `NATIVE_FILTER-US203-<indice>:(extraFormData:(filters:!((col:<columna>,`
PAR_FILTRO = re.compile(
    r"NATIVE_FILTER-US203-(?P<indice>\d+):\(extraFormData:\(filters:!\(\(col:(?P<columna>\w+),"
)


def leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8")


def _bloque_del_link(sql: str, columna_link: str) -> str:
    """Devuelve solo el fragmento de SQL que construye `columna_link`.

    Un mismo .sql puede definir varios links (DB-03 define tres). Cada uno lleva sus
    propios `NATIVE_FILTER-US203-N`, asi que validar contra el archivo completo
    compara los indices de un link con los filtros del tablero de otro.
    """
    fin = sql.index(f"AS {columna_link}")
    ini = sql.rindex("<a href=", 0, fin)
    return sql[ini:fin]


def sin_comentarios(sql: str) -> str:
    """Quita los comentarios `--` para que las reglas no se cumplan 'de mentiras' en la prosa.

    Mismo helper que `test_semantic_db03_db04.py`, y por la misma razon exacta: la
    primera version de `test_ninguna_ruta_declara_una_llave_que_el_cubo_de_origen_no_tiene`
    buscaba la llave en el texto crudo y pasaba con la llave imposible `cct`, porque la
    palabra aparece en el comentario que explica por que `cct` es imposible. La prueba
    parecia correcta y no probaba nada.
    """
    return "\n".join(linea.split("--")[0] for linea in sql.splitlines())


@pytest.fixture(scope="module")
def yaml_mod():
    """`pyyaml` no esta en requirements.txt: si falta, se omite (igual que las de US-211a)."""
    return pytest.importorskip("yaml", reason="pyyaml no esta en requirements.txt")


@pytest.fixture(scope="module")
def tableros(yaml_mod) -> dict[str, dict]:
    """El primer (y unico) dashboard declarado en cada YAML de tablero."""
    return {
        nombre: yaml_mod.safe_load(leer(ruta))["dashboards"][0]
        for nombre, ruta in {**YAML_POR_TABLERO, **YAML_DESTINO_AJENO}.items()
    }


@pytest.fixture(scope="module")
def drill_down(yaml_mod) -> list[dict]:
    return yaml_mod.safe_load(leer(YAML_METRICAS))["drill_down"]


# --------------------------------------------------------- la guarda que de verdad importa


@pytest.mark.parametrize("columna_link", sorted(LINKS))
def test_los_indices_del_link_apuntan_a_la_columna_que_dicen(
    columna_link: str, tableros: dict[str, dict]
) -> None:
    """Cada NATIVE_FILTER-US203-<i> debe caer en el filtro <i> del tablero destino.

    Esta es la prueba que hace que reordenar `filtros_globales` falle en CI en vez de
    romper la navegacion en silencio. Si falla: no toques el link, mueve el filtro de
    vuelta al final de la lista.
    """
    cfg = LINKS[columna_link]
    filtros = tableros[cfg["destino"]]["filtros_globales"]

    # ACOTAR AL BLOQUE DE ESTE LINK, no al archivo entero: db03_cubo_escuela_360.sql
    # define tres links (a DB-04, DB-06 y DB-09) y cada uno usa sus propios indices.
    # Escanear todo el archivo mezclaba los indices de un link con los de otro, y la
    # prueba fallaba contra el tablero equivocado. Lo cazo ella misma al agregar el
    # tercer link (2026-09-04).
    sql = _bloque_del_link(leer(SQL_POR_CUBO[cfg["origen"]]), columna_link)

    pares = PAR_FILTRO.findall(sql)
    assert pares, f"{columna_link}: no se encontro ningun NATIVE_FILTER en su bloque."

    for indice, columna in pares:
        i = int(indice)
        assert i < len(filtros), (
            f"{columna_link}: apunta al indice {i} pero {cfg['destino']} solo declara "
            f"{len(filtros)} filtros globales."
        )
        assert filtros[i]["columna"] == columna, (
            f"{columna_link}: el link fija `{columna}` en el indice {i}, pero "
            f"{cfg['destino']} tiene `{filtros[i]['columna']}` en esa posicion. "
            "Alguien reordeno filtros_globales: el drill-down esta preseleccionando "
            "la columna equivocada sin dar error."
        )


@pytest.mark.parametrize("columna_link", sorted(LINKS))
def test_el_link_apunta_al_slug_del_tablero_destino(columna_link: str, tableros: dict) -> None:
    cfg = LINKS[columna_link]
    sql = _bloque_del_link(leer(SQL_POR_CUBO[cfg["origen"]]), columna_link)
    assert f"/superset/dashboard/{cfg['slug']}/" in sql, (
        f"{columna_link}: no apunta al slug `{cfg['slug']}`."
    )
    assert tableros[cfg["destino"]]["slug"] == cfg["slug"], (
        f"{cfg['destino']}: el slug del YAML cambio y el link quedo colgado."
    )


@pytest.mark.parametrize("columna_link", sorted(LINKS))
def test_los_valores_del_link_van_citados(columna_link: str) -> None:
    """`cve_mun` ('09002') e `id_ciclo` ('2024-2025') tienen forma que RISON obliga a citar.

    Sin `%27` el filtro se arma con un valor invalido y aterriza sin preseleccion.
    """
    cfg = LINKS[columna_link]
    bloque = _bloque_del_link(leer(SQL_POR_CUBO[cfg["origen"]]), columna_link)
    assert "val:!(%27" in bloque, f"{columna_link}: valores sin citar con %27 en `val`."
    assert "value:!(%27" in bloque, f"{columna_link}: valores sin citar con %27 en `filterState`."


# --------------------------------------------------------- render del HTML


@pytest.mark.parametrize("nombre_tablero", sorted(YAML_POR_TABLERO))
def test_todo_chart_con_link_declara_allow_render_html(
    nombre_tablero: str, tableros: dict[str, dict]
) -> None:
    """Sin `allow_render_html` la celda pinta el <a href> como texto plano."""
    for chart in tableros[nombre_tablero]["charts"]:
        columnas_link = [d for d in chart.get("dimensiones", []) if d.startswith("link_")]
        if not columnas_link:
            continue
        extra = chart.get("params_extra") or {}
        assert extra.get("allow_render_html") is True, (
            f"{nombre_tablero} · '{chart['nombre']}': muestra {columnas_link} pero no "
            "declara `allow_render_html: true`; el link saldria como texto."
        )


@pytest.mark.parametrize("nombre_tablero", sorted(YAML_POR_TABLERO))
def test_toda_columna_link_existe_en_el_sql_de_su_dataset(
    nombre_tablero: str, tableros: dict[str, dict]
) -> None:
    """Un chart no puede pedir una columna que su cubo no produce."""
    sqls = {ruta.stem: leer(ruta) for ruta in SQL_POR_CUBO.values()}
    for chart in tableros[nombre_tablero]["charts"]:
        for columna in chart.get("dimensiones", []):
            if not columna.startswith("link_"):
                continue
            sql = sqls.get(chart["dataset"])
            assert sql is not None, f"{nombre_tablero}: dataset desconocido {chart['dataset']}."
            assert f"AS {columna}" in sql, (
                f"{nombre_tablero} · '{chart['nombre']}': pide `{columna}` pero "
                f"{chart['dataset']}.sql no la produce."
            )


# --------------------------------------------------------- el contrato drill_down


def test_toda_ruta_declara_un_estado_valido(drill_down: list[dict]) -> None:
    for ruta in drill_down:
        estado = ruta.get("estado")
        assert estado in ESTADOS_VALIDOS, (
            f"{ruta['desde']} -> {ruta['hacia']}: estado `{estado}` no es uno de "
            f"{sorted(ESTADOS_VALIDOS)}."
        )


def test_ninguna_ruta_declara_una_llave_que_el_cubo_de_origen_no_tiene(
    drill_down: list[dict],
) -> None:
    """La clase de error de `DB-04 -> DB-03 llave: cct`.

    Solo se puede comprobar el origen cuando vive en esta historia (DB-03/DB-04); las
    rutas cuyo origen es de otra persona se omiten a proposito.
    """
    cubo_por_tablero = {"DB-03": "db03", "DB-04": "db04"}
    for ruta in drill_down:
        cubo = cubo_por_tablero.get(ruta["desde"])
        if cubo is None:
            continue
        # SIN comentarios: ver el docstring de `sin_comentarios`.
        sql = sin_comentarios(leer(SQL_POR_CUBO[cubo]))
        llaves = ruta["llave"] if isinstance(ruta["llave"], list) else [ruta["llave"]]
        for llave in llaves:
            assert re.search(rf"\b{re.escape(llave)}\b", sql), (
                f"{ruta['desde']} -> {ruta['hacia']}: declara la llave `{llave}`, pero "
                f"{cubo} no expone esa columna. La ruta no se puede construir tal como "
                "esta escrita — corrige el contrato, no el tablero."
            )


def test_toda_ruta_implementada_tiene_su_columna_link(drill_down: list[dict]) -> None:
    """`estado: implementado` tiene que ser verificable, no una afirmacion."""
    implementadas = {
        (r["desde"], r["hacia"]) for r in drill_down if r.get("estado") == "implementado"
    }
    esperadas = {
        (f"DB-{cfg['origen'][2:]}", cfg["destino"]) for cfg in LINKS.values()
    }
    assert implementadas == esperadas, (
        f"El contrato dice implementadas {sorted(implementadas)} pero el codigo tiene "
        f"{sorted(esperadas)}. Una de las dos miente."
    )


def test_las_rutas_bloqueadas_nombran_a_su_dueno(drill_down: list[dict]) -> None:
    """Un bloqueo sin dueño no se desbloquea: la regla de 24/48h necesita a quien escalar."""
    for ruta in drill_down:
        if ruta.get("estado") != "bloqueado":
            continue
        nota = ruta.get("nota", "")
        assert "Manuel" in nota or "Serrania" in nota, (
            f"{ruta['desde']} -> {ruta['hacia']}: bloqueada sin decir de quien se espera."
        )


# --------------------------------------------------------- AC-002.2


@pytest.mark.parametrize("nombre_tablero", sorted(YAML_POR_TABLERO))
def test_los_filtros_de_ac_002_2_siguen_presentes(
    nombre_tablero: str, tableros: dict[str, dict]
) -> None:
    """Ciclo, entidad y nivel aplican a los dos tableros (AC-002.2)."""
    columnas = {f["columna"] for f in tableros[nombre_tablero]["filtros_globales"]}
    for requerida in ("id_ciclo", "nombre_entidad", "nivel"):
        assert requerida in columnas, f"{nombre_tablero}: perdio el filtro `{requerida}`."


@pytest.mark.parametrize("nombre_tablero", sorted(YAML_POR_TABLERO))
def test_cve_mun_es_el_ultimo_filtro(nombre_tablero: str, tableros: dict[str, dict]) -> None:
    """Los filtros nuevos van AL FINAL: insertarlos antes corre los indices ya cableados."""
    filtros = tableros[nombre_tablero]["filtros_globales"]
    assert filtros[-1]["columna"] == "cve_mun", (
        f"{nombre_tablero}: `cve_mun` dejo de ser el ultimo filtro. Si se agrego otro "
        "despues, revisa que ningun link haya quedado apuntando al indice equivocado."
    )
