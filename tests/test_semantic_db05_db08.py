"""Pruebas del contrato semántico de los cubos de DB-05 y DB-08 (US-211b, US-205).

Mismas reglas que `test_semantic_db03_db04.py`, ahora para el análisis por driver y el
explorador del cubo, más las reglas propias de este contrato (formato largo y repunteo a
cubos físicos):

* **`SIN_DATO` nunca es cero.** Si alguien —persona o IA— "arregla" un hueco con
  `COALESCE(<driver>, 0)` o con `COALESCE(valor, 0)`, el tablero afirmaría "aquí no hay
  problema" justo donde el Estado no está midiendo. Estas pruebas fallan si eso aparece.
* **Repunteo a cubos físicos (US-205):** `db05_cubo_driver` lee `gold.cubo_driver` (ML-02,
  re-escala US-205) y `db08_cubo_pivot` lee `gold.cubo_pivot` + `gold.dim_driver` — la
  capa semántica no agrega el hecho ni toca tablas crudas de ML.
* **DB-05 re-escalado a KPI-07:** analiza el **driver dominante de ML-02** con los
  denominadores reales del cubo (`escuelas_con_recomendacion` / `escuelas_sin_recomendacion`).
  El KPI-19 propuesto (driver observado) queda fuera de v1.
* **Formato largo:** una fila por driver (`id_driver`), ya armado por el cubo C1. Toda métrica
  que se sume debe agruparse o filtrarse por `id_driver`, o se infla ×6 (Cube_Specs §2.2/§3.6).
* **Las razones se guardan como numerador y denominador**, para que se puedan reagregar con
  cualquier combinación de los filtros globales (AC-002.2).

Validación **estática**: no necesita base de datos ni dependencias fuera de `requirements.txt`.
La validación contra datos reales queda pendiente de `gold.cubo_driver`/`gold.cubo_pivot`
(US-113, Célula 1).

Contrato: `vault/04_UX_Design/Cube_Specs_DB05_DB08.md` (DOC-CUBESPEC-DB0508, v1.1).
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SEMANTIC = RAIZ / "superset" / "semantic"

SQL_DB05 = SEMANTIC / "db05_cubo_driver.sql"
SQL_DB08 = SEMANTIC / "db08_cubo_pivot.sql"
YAML_METRICAS = SEMANTIC / "metrics_db05_db08.yaml"

DRIVERS = ("d1", "d2", "d3", "d4", "d5", "d6")

# Salidas de ML: viven en gold.predicciones / gold.recomendaciones. v1 de estos dos cubos no
# las lee (Cube_Specs §2.1) -- a diferencia de DB-03/DB-04.
SALIDAS_ML_TABLAS = ("gold.predicciones", "gold.recomendaciones")


# --------------------------------------------------------------------------- utilidades


def leer(ruta: Path) -> str:
    """Lee un artefacto de la capa semántica; falla con un mensaje útil si no está."""
    assert ruta.exists(), f"Falta el artefacto de la capa semántica: {ruta}"
    texto = ruta.read_text(encoding="utf-8")
    assert texto.strip(), f"{ruta.name} está vacío"
    return texto


def sin_comentarios(sql: str) -> str:
    """Quita los comentarios `--` para que las reglas no se cumplan 'de mentiras' en la prosa."""
    return "\n".join(linea.split("--")[0] for linea in sql.splitlines())


@pytest.fixture(scope="module")
def db05() -> str:
    return sin_comentarios(leer(SQL_DB05))


@pytest.fixture(scope="module")
def db08() -> str:
    return sin_comentarios(leer(SQL_DB08))


# --------------------------------------------------------------------------- R2: SIN_DATO nunca es cero


@pytest.mark.parametrize("cubo", ["db05", "db08"])
def test_ningun_driver_se_rellena_con_cero(cubo: str, request: pytest.FixtureRequest) -> None:
    """Prohibido `COALESCE(d#, 0)`: la ausencia de dato no es un cero (Data_Model §1)."""
    sql = request.getfixturevalue(cubo)
    for driver in DRIVERS:
        patron = rf"coalesce\s*\(\s*\w*\.?{driver}\b[^)]*,\s*0"
        assert not re.search(patron, sql, re.IGNORECASE), (
            f"{cubo}: `{driver}` se rellena con cero. SIN_DATO nunca es cero (regla R2)."
        )


@pytest.mark.parametrize("cubo", ["db05", "db08"])
def test_ningun_valor_agregado_se_rellena_con_cero(cubo: str, request: pytest.FixtureRequest) -> None:
    """El valor del driver (ya unpivoteado) tampoco se rellena con cero."""
    sql = request.getfixturevalue(cubo)
    for columna in ("valor", "suma_valor", "valor_driver"):
        patron = rf"coalesce\s*\(\s*\w*\.?{columna}\b[^)]*,\s*0"
        assert not re.search(patron, sql, re.IGNORECASE), (
            f"{cubo}: `{columna}` se rellena con cero. SIN_DATO nunca es cero (regla R2)."
        )


def test_db05_publica_los_denominadores_reales_del_driver(db05: str) -> None:
    """El KPI-07 se calcula sobre los denominadores reales de ML-02 (cubo C1): nunca sobre
    un total que incluya escuelas que no tienen recomendación."""
    for columna in ("escuelas_con_recomendacion", "escuelas_sin_recomendacion", "escuelas_driver", "total_escuelas"):
        assert columna in db05, (
            f"Falta `{columna}`: sin el denominador real, el % del driver se calcularía "
            "sobre escuelas sin recomendación."
        )


def test_db05_no_guarda_promedio_ya_calculado(db05: str) -> None:
    """Un promedio no se puede reagregar: el cubo guarda componentes, la razón vive en el YAML."""
    assert not re.search(r"\bavg\s*\(", db05, re.IGNORECASE), (
        "DB-05 guarda un promedio precalculado. Al quitar el filtro de nivel, Superset "
        "promediaría promedios y daría un número incorrecto (Cube_Specs §3)."
    )


def test_db05_expone_la_bandera_de_cobertura(db05: str) -> None:
    assert "cobertura_recomendacion" in db05, "Falta `cobertura_recomendacion` en DB-05 (ML-02)."


def test_db08_expone_la_bandera_de_cobertura(db08: str) -> None:
    assert "cobertura_driver" in db08, "Falta `cobertura_driver` en DB-08."


# --------------------------------------------------------------------------- repunteo a cubos (US-205)


@pytest.mark.parametrize("cubo", ["db05", "db08"])
def test_lee_el_cubo_fisico_del_c1(cubo: str, request: pytest.FixtureRequest) -> None:
    """Repunteo US-205: la capa semántica sirve los cubos físicos C1, no el hecho."""
    sql = request.getfixturevalue(cubo)
    fuentes = {
        "db05": ("gold.cubo_driver",),
        "db08": ("gold.cubo_pivot", "gold.dim_driver"),
    }[cubo]
    for fuente in fuentes:
        assert re.search(rf"\b{re.escape(fuente)}\b", sql, re.IGNORECASE), (
            f"{cubo}: falta la fuente {fuente}."
        )


@pytest.mark.parametrize("cubo", ["db05", "db08"])
def test_no_toca_tablas_crudas_de_ml(cubo: str, request: pytest.FixtureRequest) -> None:
    """Las salidas de ML se materializan dentro del cubo C1; aquí no se leen en crudo."""
    sql = request.getfixturevalue(cubo)
    for tabla in SALIDAS_ML_TABLAS:
        assert tabla not in sql.lower(), f"{cubo}: no debe leer {tabla} (vive en el cubo C1)."


def test_db08_enriquece_con_el_catalogo_dim_driver(db08: str) -> None:
    """fuente_driver / driver_nivel_geografico no viven en el cubo: vienen de gold.dim_driver."""
    assert re.search(r"left\s+join\s+gold\.dim_driver\b", db08, re.IGNORECASE), (
        "db08: debe unir gold.dim_driver para enrich fuente/nivel_geografico."
    )
    assert "fuente_driver" in db08 and "driver_nivel_geografico" in db08


# --------------------------------------------------------------------------- formato largo


@pytest.mark.parametrize("cubo", ["db05", "db08"])
def test_el_formato_largo_lo_arma_el_cubo(cubo: str, request: pytest.FixtureRequest) -> None:
    """Formato largo: el cubo C1 ya apila D1..D6; la capa semántica no repite el unpivot."""
    sql = request.getfixturevalue(cubo)
    assert not re.search(r"union\s+all", sql, re.IGNORECASE), (
        f"{cubo}: el formato largo ya lo resuelve el cubo C1; no se repite el unpivot."
    )


def test_el_yaml_declara_formato_largo(metricas: dict) -> None:
    for dataset in metricas["datasets"]:
        assert dataset.get("formato") == "largo", (
            f"{dataset['nombre']}: debe declarar formato: largo."
        )


# --------------------------------------------------------------------------- grano y filtros globales


def test_db05_lee_el_grano_declarado(db05: str, metricas: dict) -> None:
    """Grano id_driver × cve_mun × nivel × ciclo, servido por gold.cubo_driver (C1)."""
    cubo_driver = next(d for d in metricas["datasets"] if d["nombre"] == "cubo_driver")
    assert cubo_driver["grano"] == ["id_driver", "cve_mun", "nivel", "id_ciclo"]
    assert re.search(r"\bgold\.cubo_driver\b", db05, re.IGNORECASE)
    assert not re.search(r"\bgroup\s+by\b", db05, re.IGNORECASE), (
        "db05: el cubo C1 ya viene al grano; no se reagrega en la capa semántica."
    )


def test_db08_no_agrega_al_grano_de_detalle(db08: str) -> None:
    """DB-08 está al grano de detalle (cct × driver × ciclo): no debe agregar."""
    assert re.search(r"\bcct\b", db08), "db08: falta la columna cct del detalle."
    assert not re.search(r"\bgroup\s+by\b", db08, re.IGNORECASE), (
        "DB-08 está al grano del detalle: no debe agregar."
    )


@pytest.mark.parametrize("cubo", ["db05", "db08"])
def test_los_filtros_globales_tienen_columna(cubo: str, request: pytest.FixtureRequest) -> None:
    """Ciclo, entidad y nivel deben existir en ambos cubos (AC-002.2)."""
    sql = request.getfixturevalue(cubo)
    for columna in ("id_ciclo", "cve_ent", "nivel"):
        assert columna in sql, f"{cubo}: falta la columna del filtro global `{columna}`."


# --------------------------------------------------------------------------- capa semántica (YAML)


@pytest.fixture(scope="module")
def metricas() -> dict:
    """Carga el YAML de métricas. `pyyaml` no está en requirements.txt: si falta, se omite."""
    yaml = pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")
    return yaml.safe_load(leer(YAML_METRICAS))


def test_el_yaml_declara_los_dos_cubos(metricas: dict) -> None:
    nombres = {d["nombre"] for d in metricas["datasets"]}
    assert nombres == {"cubo_driver", "cubo_pivot"}


def test_el_yaml_declara_los_tres_filtros_globales(metricas: dict) -> None:
    """AC-002.2: ciclo, entidad y nivel aplican al conjunto de tableros."""
    nombres = {f["nombre"] for f in metricas["filtros_globales"]}
    assert nombres == {"ciclo", "entidad", "nivel"}


def test_el_grano_del_yaml_coincide_con_el_sql(metricas: dict) -> None:
    granos = {d["nombre"]: d["grano"] for d in metricas["datasets"]}
    assert granos["cubo_driver"] == ["id_driver", "cve_mun", "nivel", "id_ciclo"]
    assert granos["cubo_pivot"] == ["cct", "id_driver", "id_ciclo"]


@pytest.mark.parametrize("cubo", ["cubo_driver", "cubo_pivot"])
def test_declara_dimension_obligatoria_en_agregacion(cubo: str, metricas: dict) -> None:
    """Sin agrupar/filtrar por id_driver, las métricas del formato largo se inflan x6."""
    dataset = next(d for d in metricas["datasets"] if d["nombre"] == cubo)
    assert dataset.get("dimension_obligatoria_en_agregacion") == "id_driver"


def test_toda_razon_protege_la_division(metricas: dict) -> None:
    """Una división sin `NULLIF` revienta o miente cuando el denominador es cero."""
    for dataset in metricas["datasets"]:
        for metrica in dataset["metricas"]:
            expresion = metrica.get("expresion", "")
            if "/" in expresion:
                assert "NULLIF" in expresion.upper(), (
                    f"{dataset['nombre']}.{metrica['nombre']}: división sin NULLIF."
                )


def test_ninguna_metrica_rellena_con_cero(metricas: dict) -> None:
    for dataset in metricas["datasets"]:
        for metrica in dataset["metricas"]:
            assert "COALESCE" not in metrica.get("expresion", "").upper(), (
                f"{dataset['nombre']}.{metrica['nombre']}: no se rellenan huecos con COALESCE."
            )


def test_kpi07_es_la_metrica_principal_de_db05(metricas: dict) -> None:
    """Re-escala US-205: DB-05 reusa KPI-07 (driver dominante ML-02, oficial del catálogo);
    el KPI-19 propuesto (driver observado) queda fuera de v1."""
    cubo_driver = next(d for d in metricas["datasets"] if d["nombre"] == "cubo_driver")
    por_nombre = {m["nombre"]: m for m in cubo_driver["metricas"]}
    metrica = por_nombre["pct_escuelas_por_driver"]
    assert metrica["kpi"] == "KPI-07"
    assert metrica["cobertura"] == "cobertura_recomendacion"

    propuestos = {
        kpi["id"]
        for dataset in metricas["datasets"]
        for kpi in dataset.get("kpis_propuestos", [])
    }
    assert "KPI-20" in propuestos, "KPI-20 (db08) sigue propuesto."
    assert "KPI-19" not in propuestos, "KPI-19 quedó fuera de v1 por la re-escala US-205."


def test_db05_no_usa_la_metrica_de_driver_observado(metricas: dict) -> None:
    """No debe sobrevivir la semántica del driver observado (valor_promedio_driver /
    pct_escuelas_sin_dato de KPI-19/KPI-06) en el dataset re-escalado."""
    cubo_driver = next(d for d in metricas["datasets"] if d["nombre"] == "cubo_driver")
    nombres = {m["nombre"] for m in cubo_driver["metricas"]}
    assert not {"valor_promedio_driver", "pct_escuelas_sin_dato"} & nombres, (
        "db05: métricas del driver observado fuera de v1."
    )


def test_cubo_driver_declara_grano_canonico_y_cambio_solicitado(metricas: dict) -> None:
    """`cubo_driver` documenta el grano canónico y el cambio solicitado (resuelto en US-205);
    `cubo_pivot` no lo necesita (Cube_Specs §8.2)."""
    cubo_driver = next(d for d in metricas["datasets"] if d["nombre"] == "cubo_driver")
    assert cubo_driver.get("grano_canonico_actual") == ["id_driver", "cve_mun", "id_ciclo"]
    assert cubo_driver.get("cambio_de_grano_solicitado_a"), (
        "cubo_driver debe documentar a quién se le solicitó el cambio de grano."
    )
    cubo_pivot = next(d for d in metricas["datasets"] if d["nombre"] == "cubo_pivot")
    assert "cambio_de_grano_solicitado_a" not in cubo_pivot


def test_ninguna_metrica_porcentaje_duplica_el_escalado(metricas: dict) -> None:
    """El formato `porcentaje_*` (d3 `%`) ya multiplica por 100 al mostrar (convención US-202).
    Si la expresión SQL también multiplica por 100, el valor se muestra x100 de más (ej. "3,180.0%"
    en vez de "31.8%") -- bug real encontrado por Manuel Serranía en la revisión de US-211b."""
    for dataset in metricas["datasets"]:
        for metrica in dataset["metricas"]:
            formato = metrica.get("formato", "")
            expresion = metrica.get("expresion", "")
            if formato.startswith("porcentaje"):
                assert not re.search(r"\*\s*100\b", expresion), (
                    f"{dataset['nombre']}.{metrica['nombre']}: usa formato '{formato}' (ya "
                    "multiplica x100 al mostrar) pero la expresión también multiplica por 100 -- "
                    "doble escalado."
                )


def test_cada_metrica_de_valor_declara_su_cobertura(metricas: dict) -> None:
    """Toda métrica que dependa de ML-02/driver expone su bandera de cobertura (R2)."""
    cubo_driver = next(d for d in metricas["datasets"] if d["nombre"] == "cubo_driver")
    por_nombre = {m["nombre"]: m for m in cubo_driver["metricas"]}
    assert por_nombre["pct_escuelas_por_driver"]["cobertura"] == "cobertura_recomendacion"
    assert por_nombre["escuelas_por_driver"]["cobertura"] == "cobertura_recomendacion"

    cubo_pivot = next(d for d in metricas["datasets"] if d["nombre"] == "cubo_pivot")
    metrica_pivot = next(m for m in cubo_pivot["metricas"] if m["nombre"] == "valor_driver")
    assert metrica_pivot["cobertura"] == "cobertura_driver"


# --------------------------------------------------------------------------- layout de tabs (US-213)
#
# DB-05 pide "un tab por driver D1-D6" (US-213), algo que el layout plano de
# _layout_grilla() (ROOT_ID→GRID_ID→ROW→CHART) no soporta. _layout_tabs() es
# la función hermana, aditiva, revisada por Manuel Serranía antes de escribir
# los 6 tabs reales: ROOT_ID(ROOT)→TABS-ROOT→TAB-<id>→ROW→CHART (árbol
# corregido en BUG-038: sin GRID intermedio). Estas
# pruebas validan la forma del árbol con datos sintéticos, sin Superset ni
# red -- la validación contra el schema real de Superset es el siguiente paso
# (un chart manual, antes de generar los 6 juegos).


@pytest.fixture(scope="module")
def sync():
    """Importa superset/sync_semantic_layer.py como módulo (sin red en import)."""
    ruta = RAIZ / "superset" / "sync_semantic_layer.py"
    spec = importlib.util.spec_from_file_location("sync_semantic_layer", ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("sync_semantic_layer", modulo)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture
def tabs_sinteticos() -> list[tuple[str, str, list[tuple[int, str, int, int]], str | None]]:
    """Dos tabs de juguete (D1 con nota, D2 sin nota) -- alcanza para probar
    la forma del árbol (charts + markdown opcional) sin los 6 drivers reales."""
    return [
        (
            "D1", "D1 · Pobreza y rezago social",
            [(101, "D1 · KPI-19", 3, 38), (102, "D1 · tabla", 12, 55)],
            "CONEVAL/CONAPO (DS-07/DS-08) · medido a nivel municipio",
        ),
        ("D2", "D2 · Inseguridad del entorno", [(201, "D2 · KPI-19", 3, 38)], None),
    ]


def test_layout_tabs_root_es_root_y_cuelga_del_contenedor_de_tabs(sync, tabs_sinteticos) -> None:
    """ROOT_ID es `ROOT` con un único hijo `TABS`, no un `TABS` él mismo (BUG-038).

    Guarda de regresión del defecto 1: cuando ROOT_ID se declaraba `type: "TABS"`
    con los TAB colgando directo, Superset no dibujaba la barra de navegación y
    D2-D6 quedaban inalcanzables. El sync seguía en verde: sólo se veía en el
    navegador.
    """
    position = sync._layout_tabs(tabs_sinteticos)
    assert position["ROOT_ID"]["type"] == "ROOT"
    assert position["ROOT_ID"]["children"] == [sync.TABS_NODE_ID]

    tabs_node = position[sync.TABS_NODE_ID]
    assert tabs_node["type"] == "TABS"
    assert tabs_node["parentId"] == "ROOT_ID"
    assert tabs_node["children"] == ["TAB-D1", "TAB-D2"]


def test_layout_tabs_cada_tab_cuelga_del_contenedor_y_no_de_root(sync, tabs_sinteticos) -> None:
    position = sync._layout_tabs(tabs_sinteticos)
    for tab_id in ("D1", "D2"):
        tab_node = position[f"TAB-{tab_id}"]
        assert tab_node["type"] == "TAB"
        assert tab_node["parentId"] == sync.TABS_NODE_ID
        assert tab_node["meta"]["text"]  # etiqueta visible del tab
        # Las filas cuelgan DIRECTO del tab: sin GRID intermedio (BUG-038, defecto 2).
        assert all(position[hijo]["type"] == "ROW" for hijo in tab_node["children"])


def test_layout_tabs_sin_grid_intermedio_entre_tab_y_filas(sync, tabs_sinteticos) -> None:
    """Guarda de regresión del defecto 2 de BUG-038.

    Con un `GRID-<id>` entre el TAB y sus ROW, Superset dibujaba la barra de tabs
    pero dejaba el contenido de todos ellos en blanco. Ningún nodo GRID debe
    existir en el árbol con tabs — el GRID sólo vive en el camino plano.
    """
    position = sync._layout_tabs(tabs_sinteticos)
    grids = [k for k, v in position.items() if isinstance(v, dict) and v.get("type") == "GRID"]
    assert grids == [], f"el árbol con tabs no debe tener nodos GRID, encontrados: {grids}"


def test_layout_tabs_cada_chart_cuelga_de_una_fila_dentro_de_su_tab(sync, tabs_sinteticos) -> None:
    position = sync._layout_tabs(tabs_sinteticos)
    tipos_encontrados: list[str] = []
    for row_id in position["TAB-D1"]["children"]:
        row_node = position[row_id]
        assert row_node["type"] == "ROW"
        assert row_node["parentId"] == "TAB-D1"
        for comp_id in row_node["children"]:
            comp_node = position[comp_id]
            assert comp_node["parentId"] == row_id
            tipos_encontrados.append(comp_node["type"])
    # D1 en tabs_sinteticos trae nota (1 MARKDOWN) + 2 charts.
    assert tipos_encontrados.count("CHART") == 2
    assert tipos_encontrados.count("MARKDOWN") == 1


def test_layout_tabs_nota_es_markdown_estatico_en_la_primera_fila(sync, tabs_sinteticos) -> None:
    """Aprobado por Manuel junto con los tabs: id estable MD-{tab}-0, colgado
    del ROW, primera fila del TAB (antes que los charts)."""
    position = sync._layout_tabs(tabs_sinteticos)
    primer_row_id = position["TAB-D1"]["children"][0]
    primer_row = position[primer_row_id]
    assert primer_row["children"] == ["MD-D1-0"]

    md_node = position["MD-D1-0"]
    assert md_node["type"] == "MARKDOWN"
    assert md_node["parentId"] == primer_row_id
    assert md_node["meta"]["code"] == "CONEVAL/CONAPO (DS-07/DS-08) · medido a nivel municipio"


def test_layout_tabs_sin_nota_no_genera_nodo_markdown(sync, tabs_sinteticos) -> None:
    """D2 en tabs_sinteticos no trae nota: su TAB no debe tener ningún MARKDOWN."""
    position = sync._layout_tabs(tabs_sinteticos)
    assert "MD-D2-0" not in position
    for row_id in position["TAB-D2"]["children"]:
        for comp_id in position[row_id]["children"]:
            assert position[comp_id]["type"] != "MARKDOWN"


def test_layout_tabs_conserva_metadata_del_chart(sync, tabs_sinteticos) -> None:
    """chartId/sliceName/width/height deben sobrevivir intactos (el importador
    v1 los lee de aquí para asociar cada chart real)."""
    position = sync._layout_tabs(tabs_sinteticos)
    metas = [
        n["meta"] for n in position.values()
        if isinstance(n, dict) and n.get("type") == "CHART"
    ]
    metas_por_chart_id = {m["chartId"]: m for m in metas}
    assert metas_por_chart_id[101] == {"chartId": 101, "sliceName": "D1 · KPI-19", "width": 3, "height": 38}
    assert metas_por_chart_id[201] == {"chartId": 201, "sliceName": "D2 · KPI-19", "width": 3, "height": 38}


def test_layout_tabs_no_afecta_el_camino_plano_existente(sync) -> None:
    """Guarda de regresión: _layout_grilla() (los 4 tableros ya sincronizados)
    debe seguir generando ROOT_ID de tipo GRID, sin ningún tab."""
    layout_plano = [(1, "Chart A", 6, 40), (2, "Chart B", 6, 40)]
    position = sync._layout_grilla(layout_plano)
    assert position["ROOT_ID"]["type"] == "GRID"
    assert position["ROOT_ID"]["children"] == ["GRID_ID"]
    assert "TAB-D1" not in position


# --------------------------------------------------------------------------- tablero declarativo DB-05 (US-213)
#
# WIP: solo el tab D1 está completo (validación previa a replicar D2-D6, según
# lo acordado con Manuel Serranía). Estas pruebas deben seguir pasando según se
# agreguen los tabs restantes -- no asumen que hay exactamente uno.

YAML_DB05_DASHBOARD = RAIZ / "superset" / "dashboards" / "db05_analisis_driver.yaml"

# El chart declara `dataset: db05_cubo_driver` (nombre del dataset de Superset,
# el stem del .sql -- ver ensure_datasets() en sync_semantic_layer.py), pero
# metrics_db05_db08.yaml nombra el dataset "cubo_driver" (nombre semántico).
# Mismo mapeo que ya resuelve sync_metrics() por sql_match.
DATASET_SQL_A_SEMANTICO = {"db05_cubo_driver": "cubo_driver", "db08_cubo_pivot": "cubo_pivot"}


@pytest.fixture(scope="module")
def dashboard_db05() -> dict:
    yaml = pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")
    data = yaml.safe_load(leer(YAML_DB05_DASHBOARD))
    return data["dashboards"][0]


def _charts_de_todos_los_tabs(dashboard: dict) -> list[dict]:
    return [ch for tab in dashboard.get("tabs", []) for ch in tab.get("charts", [])]


def test_el_dashboard_db05_tiene_el_slug_correcto(dashboard_db05: dict) -> None:
    assert dashboard_db05["slug"] == "db05-analisis-driver"


def test_el_dashboard_db05_declara_tabs_no_charts_planos(dashboard_db05: dict) -> None:
    """US-213 pide un tab por driver: la clave raíz debe ser `tabs`, no `charts`."""
    assert "tabs" in dashboard_db05
    assert "charts" not in dashboard_db05


def test_el_dashboard_db05_tiene_los_seis_tabs(dashboard_db05: dict) -> None:
    assert {t["id"] for t in dashboard_db05["tabs"]} == {"D1", "D2", "D3", "D4", "D5", "D6"}


def test_todos_los_tabs_de_db05_traen_nota_de_fuente(dashboard_db05: dict) -> None:
    """Cube_Specs §3.3: cada driver documenta su fuente -- ningún tab se queda sin nota,
    ni siquiera D5 (SIN_DATO 100%, donde la nota explica por qué)."""
    for tab in dashboard_db05["tabs"]:
        assert tab.get("nota"), f"Tab {tab['id']}: falta la nota de fuente."


def test_todo_chart_de_db05_apunta_a_dataset_y_metrica_declarados(
    dashboard_db05: dict, metricas: dict
) -> None:
    """Un chart huérfano (dataset o métrica inexistente) rompe en runtime, no en CI."""
    metricas_por_dataset = {
        ds["nombre"]: {m["nombre"] for m in ds.get("metricas", [])}
        for ds in metricas["datasets"]
    }
    for ch in _charts_de_todos_los_tabs(dashboard_db05):
        ds_sql = ch["dataset"]
        ds_semantico = DATASET_SQL_A_SEMANTICO.get(ds_sql, ds_sql)
        assert ds_semantico in metricas_por_dataset, (
            f"{ch['nombre']}: dataset '{ds_sql}' no declarado en metrics_db05_db08.yaml"
        )
        assert ch["metrica"] in metricas_por_dataset[ds_semantico], (
            f"{ch['nombre']}: métrica '{ch['metrica']}' no declarada en '{ds_semantico}'"
        )


def test_cada_tab_de_db05_filtra_por_su_propio_id_driver(dashboard_db05: dict) -> None:
    """Blindaje contra el riesgo de doble conteo (Cube_Specs §2.2/§3.6): cada
    chart de un tab debe traer un adhoc_filter fijando id_driver al driver de
    ESE tab -- sin esto, sumar entre tabs infla las métricas x6."""
    for tab in dashboard_db05.get("tabs", []):
        tab_id = tab["id"]
        for ch in tab.get("charts", []):
            filtros = ch.get("params_extra", {}).get("adhoc_filters", [])
            assert filtros, f"{ch['nombre']}: sin adhoc_filters -- se inflaría x6 sin filtrar por driver."
            filtro_driver = next((f for f in filtros if f.get("subject") == "id_driver"), None)
            assert filtro_driver is not None, f"{ch['nombre']}: sin filtro de id_driver."
            assert filtro_driver["comparator"] == tab_id, (
                f"{ch['nombre']}: filtra por '{filtro_driver['comparator']}', "
                f"debería ser '{tab_id}' (el tab al que pertenece)."
            )
            assert filtro_driver["clause"] == "WHERE"


def test_nombres_de_chart_de_db05_son_unicos_entre_tabs(dashboard_db05: dict) -> None:
    """BUG-011: dos tabs sobre el mismo dataset con nombres de chart iguales
    harían que el sync actualice el chart equivocado -- el prefijo del driver
    en cada `nombre` existe precisamente para evitar esto."""
    nombres = [ch["nombre"] for ch in _charts_de_todos_los_tabs(dashboard_db05)]
    assert len(nombres) == len(set(nombres)), "Hay nombres de chart repetidos entre tabs."


def test_la_nota_del_tab_d1_coincide_con_la_fuente_del_contrato(dashboard_db05: dict) -> None:
    """Cube_Specs §3.3: D1 = CONEVAL (DS-07), medido a nivel municipio."""
    tab_d1 = next(t for t in dashboard_db05["tabs"] if t["id"] == "D1")
    assert tab_d1["nota"] == "CONEVAL (DS-07) · medido a nivel municipio"


def test_el_dashboard_db05_se_traduce_a_un_arbol_valido_via_layout_tabs(sync, dashboard_db05: dict) -> None:
    """Simula lo que hace ensure_dashboard(): arma tabs_layout a partir del YAML
    real (con ids de chart ficticios, sin red) y confirma que _layout_tabs() no
    truena y produce un TAB por cada tab del YAML, con su nota como MARKDOWN."""
    tabs_layout = []
    for tab in dashboard_db05["tabs"]:
        layout_tab = [
            (i, ch["nombre"], int(ch.get("ancho", 12)), int(ch.get("alto", 60)))
            for i, ch in enumerate(tab.get("charts", []))
        ]
        tabs_layout.append((tab["id"], tab.get("etiqueta", tab["id"]), layout_tab, tab.get("nota")))

    position = sync._layout_tabs(tabs_layout)
    assert position["ROOT_ID"]["children"] == [sync.TABS_NODE_ID]
    assert position[sync.TABS_NODE_ID]["children"] == [
        f"TAB-{t['id']}" for t in dashboard_db05["tabs"]
    ]
    for tab in dashboard_db05["tabs"]:
        if tab.get("nota"):
            assert f"MD-{tab['id']}-0" in position


def test_cada_tab_de_db05_se_lee_en_horizontal_como_los_demas_tableros(
    sync, dashboard_db05: dict
) -> None:
    """Lectura horizontal de DB-05 (US-213), contra el YAML real.

    DB-05 se veía como una tira vertical de un chart por pantalla mientras los otros
    nueve tableros agrupaban: `_layout_tabs()` ignoraba el `ancho` declarado. Con los
    anchos reales (3,3,3,3 | 6,6 — el mismo patrón de DB-03) cada tab debe caber en
    una fila de tarjetas más una de charts anchos.

    Se valida contra el YAML para que también cace la deriva al revés: si alguien
    cambia un `ancho` y rompe la lectura horizontal, esta guarda lo dice.
    """
    tabs_layout = []
    for tab in dashboard_db05["tabs"]:
        layout_tab = [
            (i, ch["nombre"], int(ch.get("ancho", 12)), int(ch.get("alto", 60)))
            for i, ch in enumerate(tab.get("charts", []))
        ]
        tabs_layout.append((tab["id"], tab.get("etiqueta", tab["id"]), layout_tab, tab.get("nota")))

    position = sync._layout_tabs(tabs_layout)

    for tab in dashboard_db05["tabs"]:
        filas = position[f"TAB-{tab['id']}"]["children"]
        anchos_por_fila = [
            [position[h]["meta"]["width"] for h in position[f]["children"]] for f in filas
        ]
        # Ninguna fila puede desbordar la grilla de 12.
        for fila, anchos in zip(filas, anchos_por_fila):
            assert sum(anchos) <= sync.ANCHO_GRILLA, f"{fila} suma {sum(anchos)}"
        # Y ninguna fila puede llevar un solo chart estrecho: eso es la tira vertical.
        estrechas = [
            (f, a) for f, a in zip(filas, anchos_por_fila)
            if len(a) == 1 and a[0] < sync.ANCHO_GRILLA
        ]
        assert not estrechas, (
            f"TAB-{tab['id']} tiene filas de un solo chart angosto {estrechas}: "
            "es el defecto de lectura vertical que US-213 corrigió"
        )


# --------------------------------------------------------------------------- uuid por chartId (US-213)
#
# `_position_con_uuid()` emparejaba uuid con nodos CHART **por posición**: los uuid
# ordenados por id contra los nodos en orden de declaración. Sólo acierta si los ids
# ascienden en el mismo orden en que los charts aparecen en el YAML.


def _pos_de(sync, ids: list[int]) -> dict:
    """position_json plano con un chart por id, en orden de declaración."""
    return sync._layout_grilla([(cid, f"chart {cid}", 3, 38) for cid in ids])


def _uuid_por_chart(position: dict) -> dict:
    return {
        n["meta"]["chartId"]: n["meta"].get("uuid")
        for n in position.values()
        if isinstance(n, dict) and n.get("type") == "CHART"
    }


def test_el_uuid_sigue_al_chart_aunque_su_id_no_sea_el_menor(sync) -> None:
    """El defecto que rompió DB-05 el 2026-09-05.

    `ensure_chart()` identifica por `slice_name`, así que **renombrar** un chart crea
    uno nuevo con un id alto. Si ese chart va primero en el YAML —como el de KPI-07 en
    cada tab de DB-05— su id es el mayor de todos y el emparejamiento por posición le
    daba el uuid de otro chart. El sync terminaba en verde y el tablero salía con las
    tarjetas vacías o intercambiadas al abrirlo.
    """
    # 104 se declara primero (chart recién renombrado), 42..44 después.
    ids = [104, 42, 43, 44]
    uuids = {cid: f"uuid-{cid}" for cid in ids}
    position = sync._position_con_uuid(_pos_de(sync, ids), [(c, uuids[c]) for c in ids])

    assert _uuid_por_chart(position) == uuids, (
        "cada nodo CHART debe llevar el uuid de SU chartId; emparejar por posición "
        "se los cruza en cuanto un id no sigue el orden de declaración"
    )


def test_con_ids_ascendentes_el_resultado_no_cambia(sync) -> None:
    """Guarda de no-regresión para los 10 tableros: en el caso normal —ids que
    ascienden con el orden del YAML— el emparejamiento por chartId da exactamente lo
    mismo que daba el de por posición."""
    ids = [41, 42, 43, 44, 45, 46]
    uuids = {cid: f"uuid-{cid}" for cid in ids}
    position = sync._position_con_uuid(_pos_de(sync, ids), [(c, uuids[c]) for c in ids])
    assert _uuid_por_chart(position) == uuids


def test_un_chart_sin_uuid_no_borra_el_de_los_demas(sync) -> None:
    """`ensure_chart()` devuelve uuid vacío cuando no lo pudo resolver; eso no puede
    arrastrar a los otros nodos ni escribir un uuid vacío."""
    position = sync._position_con_uuid(
        _pos_de(sync, [41, 42, 43]), [(41, "uuid-41"), (42, ""), (43, "uuid-43")]
    )
    por_chart = _uuid_por_chart(position)
    assert por_chart[41] == "uuid-41"
    assert por_chart[43] == "uuid-43"
    assert not por_chart[42]


def test_el_camino_con_tabs_tambien_empareja_por_chartid(sync) -> None:
    """DB-05 es el tablero donde el defecto se manifestó, y va por `_layout_tabs()`."""
    tabs = [
        ("D1", "D1", [(104, "D1 · KPI-07", 3, 38), (42, "D1 · escuelas", 3, 38)], None),
        ("D2", "D2", [(105, "D2 · KPI-07", 3, 38), (48, "D2 · escuelas", 3, 38)], None),
    ]
    uuids = {104: "u-104", 42: "u-42", 105: "u-105", 48: "u-48"}
    position = sync._position_con_uuid(sync._layout_tabs(tabs), list(uuids.items()))
    assert _uuid_por_chart(position) == uuids


# --------------------------------------------------------------------------- tablero declarativo DB-08 (US-213)
#
# DB-08 usa el camino plano (`charts:`), no `tabs:` -- es un solo explorador
# libre, no un tab por driver.

YAML_DB08_DASHBOARD = RAIZ / "superset" / "dashboards" / "db08_explorador_cubo.yaml"


@pytest.fixture(scope="module")
def dashboard_db08() -> dict:
    yaml = pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")
    data = yaml.safe_load(leer(YAML_DB08_DASHBOARD))
    return data["dashboards"][0]


def test_el_dashboard_db08_tiene_el_slug_correcto(dashboard_db08: dict) -> None:
    assert dashboard_db08["slug"] == "db08-explorador-cubo"


def test_el_dashboard_db08_declara_charts_planos_no_tabs(dashboard_db08: dict) -> None:
    """DB-08 es un solo explorador, no un tab por driver: usa `charts`, no `tabs`."""
    assert "charts" in dashboard_db08
    assert "tabs" not in dashboard_db08


def test_todo_chart_de_db08_apunta_a_dataset_y_metrica_declarados(
    dashboard_db08: dict, metricas: dict
) -> None:
    metricas_por_dataset = {
        ds["nombre"]: {m["nombre"] for m in ds.get("metricas", [])}
        for ds in metricas["datasets"]
    }
    for ch in dashboard_db08["charts"]:
        ds_sql = ch["dataset"]
        ds_semantico = DATASET_SQL_A_SEMANTICO.get(ds_sql, ds_sql)
        assert ds_semantico in metricas_por_dataset, (
            f"{ch['nombre']}: dataset '{ds_sql}' no declarado en metrics_db05_db08.yaml"
        )
        assert ch["metrica"] in metricas_por_dataset[ds_semantico], (
            f"{ch['nombre']}: métrica '{ch['metrica']}' no declarada en '{ds_semantico}'"
        )


def test_pivote_no_incluye_matricula_total_sin_id_driver_agrupado(dashboard_db08: dict) -> None:
    """Cube_Specs §2.2/§4.3: 'matricula_total' se repite x6 por escuela x ciclo (una
    vez por id_driver). Si un pivote lo suma sin agrupar/filtrar por id_driver, el
    total se infla x6 en silencio. Blindaje: si 'matricula_total' aparece en las
    métricas de un pivot_table_v2, 'id_driver' debe estar en groupbyRows o
    groupbyColumns de ESE MISMO chart."""
    for ch in dashboard_db08["charts"]:
        if ch["viz"] != "pivot_table_v2":
            continue
        extra = ch.get("params_extra", {})
        metricas_pivote = extra.get("metrics", [])
        if "matricula_total" not in metricas_pivote:
            continue
        agrupado_por_driver = "id_driver" in extra.get("groupbyRows", []) or "id_driver" in extra.get("groupbyColumns", [])
        assert agrupado_por_driver, (
            f"{ch['nombre']}: incluye 'matricula_total' pero no agrupa por 'id_driver' "
            "-- se inflaría x6 (Cube_Specs §2.2/§4.3)."
        )


def test_pivote_de_db08_agrupa_por_id_driver_en_columnas(dashboard_db08: dict) -> None:
    """El pivote por defecto SÍ debe traer id_driver en groupbyColumns (aunque
    'matricula_total' no esté preseleccionado): es lo que hace que cada celda
    ya esté separada por driver, evitando el doble conteo por diseño."""
    pivotes = [ch for ch in dashboard_db08["charts"] if ch["viz"] == "pivot_table_v2"]
    assert pivotes, "DB-08 debe traer al menos un pivot_table_v2 (US-213: tabla dinámica libre)."
    for ch in pivotes:
        extra = ch.get("params_extra", {})
        assert "id_driver" in extra.get("groupbyColumns", []) + extra.get("groupbyRows", []), (
            f"{ch['nombre']}: el pivote debe agrupar por id_driver (filas o columnas) por defecto."
        )

# --------------------------------------------------------- contraste del link (DEC-016)


def _bloque_del_link(sql: str, columna_link: str) -> str:
    """Devuelve solo el fragmento de SQL que construye `columna_link`.

    Mismo helper que `tests/test_drill_down_db03_db04.py:72` (Marina García): un
    `.sql` puede definir varios links, y validar contra el archivo completo
    mezclaría el bloque de uno con el de otro.
    """
    fin = sql.index(f"AS {columna_link}")
    ini = sql.rindex("<a href=", 0, fin)
    return sql[ini:fin]


def test_el_link_db08_no_depende_del_color_del_tema(db05: str) -> None:
    """El `<a>` de DB-05 lo escribe FARO, así que FARO responde por su contraste (DEC-016).

    Reportado por Marina García el 2026-09-05 tras encontrar el mismo defecto en
    sus cuatro links de DB-03/DB-04: sin estilo propio el ancla hereda el azul de
    acento de Superset, que **pasa en tema oscuro y reprueba en claro** sobre el
    fondo de la celda de tabla. El barrido de contraste del 4-sep (§3.1 del plan
    de usabilidad) no lo cazó por dos razones que conviene dejar escritas: se
    midió el tema oscuro primero, y la tabla que contiene el link queda **debajo
    del pliegue**, fuera del viewport que se recorrió.

    **No se arregla eligiendo otro azul**, y es aritmética: para pasar 4.5:1
    contra el gris claro de la celda hace falta luminancia baja, y contra el
    fondo oscuro hace falta alta; los dos rangos no se cruzan, así que ningún
    color único sirve para ambos temas. La salida es heredar el color del texto
    de la celda —que ya pasa en los dos— y marcar el link con subrayado en vez
    de con tono, lo que además cumple WCAG 1.4.1.

    Gemela de `test_drill_down_db03_db04.py::test_el_link_no_depende_del_color_del_tema`.
    """
    bloque = _bloque_del_link(db05, "link_db08")

    assert "color:inherit" in bloque, (
        "link_db08 deja que el ancla tome el color de acento del tema; en claro reprueba AA"
    )
    assert "text-decoration:underline" in bloque, (
        "link_db08 se reconocería sólo por color: falta el subrayado (WCAG 1.4.1)"
    )
