"""Pruebas del contrato semántico de DB-06 y DB-09 (US-204, repunteo US-205).

Mismas reglas que `test_semantic_db01_db02.py` y `test_semantic_db03_db04.py`,
ahora para el par prescriptivo: el tablero de **Predicciones** (DB-06) y el de
**Recomendaciones prescriptivas** (DB-09):

* **`SIN_DATO` nunca es cero.** La escuela sin predicción ML-01 viaja con
  `cobertura_prediccion = 'SIN_DATO'` y `en_riesgo` nulo; el driver aún no
  explicado por ML-02 se etiqueta `'SIN_DATO'` como categoría (etiquetar el
  vacío, jamás rellenar una métrica).
* **El SQL semántico lee `gold.cubo_*`** (repunteo US-205/US-113): db06 consume
  los cubos pre-agregados y **no** re-une salidas de ML; db09 es el único que
  conserva el LEFT JOIN a `gold.predicciones` con la llave completa, el modelo
  y el grano `escuela` (DEC-010), porque el cubo de recomendaciones no trae
  riesgo.
* **Grano dual (DEC-010): solo se lee el grano `escuela`** de
  `gold.predicciones` (`(p.grano IS NULL OR p.grano = 'escuela')`); la
  proyección de `municipio × nivel` jamás se reparte entre escuelas.
* **El umbral de riesgo es >= 0.6** (R3, ratificado 2026-08-13): en db09 vive
  en el SQL y en db06 en el YAML de métricas (`umbral: 0.6`).
* **Componentes aditivos** (DEC-008/DEC-009): la razón vive en
  `metrics_db06_db09.yaml`, nunca es un promedio precalculado en el SQL.
* **El mock es aditivo**: declara `grano` con ADD COLUMN IF NOT EXISTS, sin
  tocar ni borrar filas del esquema existente.

Validación estática: no necesita base de datos. La validación contra datos
corre en local vía `superset/sync_semantic_layer.py --validar-datos`.

Contratos: `04_UX_Design/Cube_Specs_DB06_DB09.md` (§2-§5) y `Screen_Specs.md` §4.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SEMANTIC = RAIZ / "superset" / "semantic"
DASHBOARDS = RAIZ / "superset" / "dashboards"
MOCK = RAIZ / "superset" / "mock" / "gold_ml_outputs_mock.sql"

SQL_CUBO = SEMANTIC / "db06_cubo_predicciones.sql"
SQL_PUNTOS = SEMANTIC / "db06_predicciones_escuela.sql"
SQL_REC = SEMANTIC / "db09_cubo_recomendaciones.sql"
SQLS_ML = (SQL_CUBO, SQL_PUNTOS, SQL_REC)
YAML_METRICAS = SEMANTIC / "metrics_db06_db09.yaml"
YAML_DB06 = DASHBOARDS / "db06_predicciones.yaml"
YAML_DB09 = DASHBOARDS / "db09_recomendaciones.yaml"

UMBRAL_RIESGO = "0.6"

# Salidas de ML: viven en gold.predicciones / gold.recomendaciones, jamás en el hecho.
SALIDAS_ML = ("indice_riesgo", "driver_dominante", "recomendacion", "prioridad")


# --------------------------------------------------------------------------- utilidades


def leer(ruta: Path) -> str:
    """Lee un artefacto; falla con un mensaje útil si no está."""
    assert ruta.exists(), f"Falta el artefacto: {ruta}"
    texto = ruta.read_text(encoding="utf-8")
    assert texto.strip(), f"{ruta.name} está vacío"
    return texto


def sin_comentarios(sql: str) -> str:
    """Quita los comentarios `--` para que las reglas no se cumplan 'de mentiras'."""
    return "\n".join(linea.split("--")[0] for linea in sql.splitlines())


@pytest.fixture(scope="module")
def db06_cubo() -> str:
    return sin_comentarios(leer(SQL_CUBO))


@pytest.fixture(scope="module")
def db06_puntos() -> str:
    return sin_comentarios(leer(SQL_PUNTOS))


@pytest.fixture(scope="module")
def db09_rec() -> str:
    return sin_comentarios(leer(SQL_REC))


# --------------------------------------------------------------------------- R2: SIN_DATO nunca es cero


@pytest.mark.parametrize("fixture_name", ["db06_cubo", "db06_puntos", "db09_rec"])
def test_el_riesgo_no_se_rellena_con_cero(fixture_name: str, request: pytest.FixtureRequest) -> None:
    """Una escuela sin predicción no tiene riesgo 0: tiene SIN_DATO."""
    sql = request.getfixturevalue(fixture_name)
    patron = r"coalesce\s*\(\s*\w*\.?indice_riesgo\b[^)]*,\s*0"
    assert not re.search(patron, sql, re.IGNORECASE), (
        f"{fixture_name}: `indice_riesgo` se rellena con cero. Debe quedar nulo "
        "y la cobertura declararse 'SIN_DATO' (regla R2)."
    )


def test_la_etiqueta_sin_dato_es_categoria_no_metrica(db09_rec: str) -> None:
    """El vacío viaja como literal 'SIN_DATO', jamás como cero (R2)."""
    assert re.search(r"coalesce\s*\([^)]*,\s*'SIN_DATO'\s*\)", db09_rec, re.IGNORECASE), (
        "db09: el driver sin explicar se etiqueta 'SIN_DATO' (categoría, no métrica)."
    )
    assert "cobertura_recomendacion" in db09_rec, (
        "db09: falta cobertura_recomendacion para gobernar el SIN_DATO de ML-02."
    )
    # Prohibido: rellenar conteos o métricas con cero.
    assert not re.search(r"coalesce\s*\(\s*(sum|count)\s*\(", db09_rec, re.IGNORECASE), (
        "db09: no se rellenan agregaciones con COALESCE."
    )


def test_el_driver_vacio_agrupa_como_categoria(db09_rec: str) -> None:
    """La cobertura de predicción marca 'SIN_DATO' de forma explícita (R2)."""
    assert re.search(r"when\s+p\.cct\s+is\s+null\s+then\s+'SIN_DATO'", db09_rec, re.IGNORECASE), (
        "db09: cobertura_prediccion debe etiquetar la ausencia de predicción como SIN_DATO."
    )


# --------------------------------------------------------------------------- R1: las salidas de ML van por JOIN


@pytest.mark.parametrize("fixture_name", ["db06_cubo", "db06_puntos", "db09_rec"])
def test_las_salidas_de_ml_no_se_leen_del_hecho(fixture_name: str, request: pytest.FixtureRequest) -> None:
    """`fact_escuela_ciclo` solo tiene hechos observados (Data_Model §4.1)."""
    sql = request.getfixturevalue(fixture_name)
    for salida in SALIDAS_ML:
        assert not re.search(rf"\bf\.{salida}\b", sql), (
            f"{fixture_name}: `f.{salida}` se lee del hecho. Las salidas de ML se "
            "consultan por JOIN a gold.predicciones / gold.recomendaciones."
        )


@pytest.mark.parametrize("fixture_name", ["db06_cubo", "db06_puntos", "db09_rec"])
def test_lee_el_cubo_fisico_del_c1(fixture_name: str, request: pytest.FixtureRequest) -> None:
    """Repunteo US-205: el riesgo ya viene pre-agregado por C1, no se re-une a ML."""
    sql = request.getfixturevalue(fixture_name)
    fuentes = {
        "db06_cubo": (r"from\s+gold\.cubo_matricula\b", r"join\s+gold\.cubo_riesgo_territorial\b"),
        "db06_puntos": (r"from\s+gold\.cubo_escuela_360\b",),
        "db09_rec": (r"from\s+gold\.cubo_recomendaciones\b",),
    }[fixture_name]
    for patron in fuentes:
        assert re.search(patron, sql, re.IGNORECASE), (
            f"{fixture_name}: falta {patron} (repunteo a cubos C1)."
        )


@pytest.mark.parametrize("fixture_name", ["db06_cubo", "db06_puntos"])
def test_db06_no_reune_predicciones(fixture_name: str, request: pytest.FixtureRequest) -> None:
    """db06 consume los cubos pre-agregados de C1: no re-une gold.predicciones."""
    sql = request.getfixturevalue(fixture_name)
    assert not re.search(r"gold\.predicciones\b", sql, re.IGNORECASE), (
        f"{fixture_name}: ML-01 ya lo resolvió el cubo C1; no se re-une aquí."
    )


def test_db09_une_predicciones_con_left_join_y_llave_completa(db09_rec: str) -> None:
    """El cubo de recomendaciones no trae riesgo: db09 lo une por LEFT JOIN con la
    llave completa (cct, id_ciclo), el modelo y el grano escuela (R1 + DEC-010)."""
    assert re.search(r"left\s+join\s+gold\.predicciones\b", db09_rec, re.IGNORECASE)
    assert re.search(r"cr\.cct\s*=\s*p\.cct", db09_rec)
    assert re.search(r"cr\.id_ciclo\s*=\s*p\.id_ciclo", db09_rec)
    assert re.search(r"modelo\s*=\s*'ML-01'", db09_rec)
    assert re.search(r"p\.grano\s+is\s+null\s+or\s+p\.grano\s*=\s*'escuela'", db09_rec, re.IGNORECASE)


def test_el_grano_dual_ya_lo_acoto_el_cubo(db06_cubo: str, db06_puntos: str) -> None:
    """DEC-010: C1 ya acotó gold.predicciones al grano escuela dentro de los cubos
    de db06; la capa semántica no necesita (ni debe) volver a filtrar p.grano."""
    for nombre, sql in (("db06_cubo", db06_cubo), ("db06_puntos", db06_puntos)):
        assert not re.search(r"\bp\.grano\b", sql), (
            f"{nombre}: el acote al grano escuela vive en C1, no en la capa semántica."
        )


def test_db09_expone_el_driver_etiquetado_desde_el_cubo(db09_rec: str) -> None:
    """KPI-07/11 vienen resueltos en gold.cubo_recomendaciones (C1): la capa solo
    etiqueta el vacío del catálogo y expone la cobertura de ML-02."""
    assert re.search(r"nombre_driver,\s*'SIN_DATO'", db09_rec, re.IGNORECASE)
    assert re.search(r"\bcobertura_recomendacion\b", db09_rec)
    assert not re.search(r"gold\.recomendaciones\b", db09_rec, re.IGNORECASE), (
        "db09: ML-02 ya lo resolvió el cubo C1; no se re-une gold.recomendaciones."
    )


def test_db09_expone_la_prioridad_de_ml02(db09_rec: str, datasets_por_nombre: dict[str, dict]) -> None:
    """La métrica 'recomendaciones_prioridad_alta' (KPI-11) y el chart por [prioridad]
    del dashboard DB-09 necesitan la columna cruda; el cubo C1 la trae y la capa la expone."""
    assert re.search(r"\bprioridad\b", db09_rec), (
        "db09: falta la columna `prioridad` que consume recomendaciones_prioridad_alta "
        "y el chart por prioridad del dashboard DB-09."
    )
    cubo = datasets_por_nombre["db09_cubo_recomendaciones"]
    metrica = {m["nombre"]: m for m in cubo["metricas"]}["recomendaciones_prioridad_alta"]
    assert "prioridad" in metrica["expresion"]


def test_las_filas_municipio_nivel_no_se_reparten(db06_cubo: str) -> None:
    """El denominador real escuelas_con_prediccion viene pre-agregado de C1 (grano
    escuela ya acotado): es físicamente imposible nutrir un municipio con
    predicción ajena."""
    assert re.search(r"escuelas_con_prediccion", db06_cubo), (
        "db06_cubo: falta el denominador real escuelas_con_prediccion."
    )
    assert not re.search(r"\bp\.cve_mun\b", db06_cubo), (
        "db06_cubo: no debe agruparse por cve_mun traído de predicciones (grano dual)."
    )


# --------------------------------------------------------------------------- R3: umbral de negocio


def test_el_umbral_de_riesgo_es_el_ratificado_donde_dice_umbral(
    db09_rec: str, datasets_por_nombre: dict[str, dict]
) -> None:
    """0.6 = perder ~5% de matrícula, ratificado el 2026-08-13 (Indice_Riesgo_ML01).
    En db09 (el único que une gold.predicciones) vive en el SQL; en db06 vive en el
    YAML de métricas (`umbral: 0.6`), porque C1 ya lo aplicó dentro de los cubos."""
    assert re.search(rf"p\.indice_riesgo\s*>=\s*{UMBRAL_RIESGO}", db09_rec), (
        "db09: el umbral de 'escuela en riesgo' debe ser >= 0.6 (R3)."
    )
    for nombre in ("db06_cubo_predicciones", "db06_predicciones_escuela"):
        ds = datasets_por_nombre[nombre]
        metricas = {m["nombre"]: m for m in ds["metricas"]}
        assert metricas["escuelas_en_riesgo"].get("umbral") == float(UMBRAL_RIESGO), (
            f"{nombre}: debe ratificar el umbral 0.6 como R3 en el YAML."
        )


@pytest.mark.parametrize("fixture_name", ["db06_puntos", "db09_rec"])
def test_sin_prediccion_no_es_en_riesgo(fixture_name: str, request: pytest.FixtureRequest) -> None:
    """La escuela sin predicción viaja con en_riesgo nulo, jamás FALSE ni TRUE."""
    sql = request.getfixturevalue(fixture_name)
    if fixture_name == "db09_rec":
        patron = r"when\s+p\.indice_riesgo\s+is\s+null\s+then\s+null"
        assert re.search(patron, sql, re.IGNORECASE), (
            "db09: `en_riesgo` debe ser NULL cuando no hay predicción."
        )
    else:
        # db06_puntos sirve en_riesgo del cubo C1 (ya nullable): no se fabrica.
        assert not re.search(r"coalesce\s*\(\s*\w*\.?en_riesgo\b", sql, re.IGNORECASE), (
            "db06_puntos: `en_riesgo` no se fabrica con COALESCE (R2)."
        )
    assert "cobertura_prediccion" in sql, f"{fixture_name}: falta la bandera cobertura_prediccion."


# --------------------------------------------------------------------------- grano, componentes y filtros globales


def test_los_componentes_son_aditivos_no_promedios(db06_cubo: str) -> None:
    """Numerador y denominador por separado (patron DEC-008/DEC-009): la razón
    vive en el YAML, nunca es un promedio precalculado en el SQL."""
    assert not re.search(r"\bavg\s*\(", db06_cubo, re.IGNORECASE), (
        "db06_cubo guarda un promedio precalculado; al quitar filtros Superset "
        "promediaría promedios (Cube_Specs §2.2)."
    )


def _metrica_db(dataset: str, nombre: str, metricas: dict) -> dict:
    """Busca una métrica por nombre dentro de un dataset del YAML."""
    ds = next(d for d in metricas["datasets"] if d["nombre"] == dataset)
    return next(m for m in ds["metricas"] if m["nombre"] == nombre)


def test_variacion_exige_numerador_y_denominador_separados(
    db06_cubo: str, metricas: dict
) -> None:
    """KPI-02 (R-3 DEC-012): numerador `variacion_ponderada` y denominador
    `matricula_total` por separado, en el cubo y en el detalle por escuela."""
    assert re.search(r"\bvariacion_ponderada\b", db06_cubo), (
        "db06_cubo: falta el numerador variacion_ponderada."
    )
    assert re.search(r"\bmatricula_total\b", db06_cubo), (
        "db06_cubo: falta el denominador matricula_total."
    )
    assert not re.search(r"\bvariacion_x_matricula\b(?!\s+as\b)", db06_cubo, re.IGNORECASE), (
        "db06_cubo: expone el producto ponderado como columna; "
        "separar numerador/denominador (R-3 DEC-012)."
    )
    for dataset in ("db06_cubo_predicciones", "db06_predicciones_escuela"):
        metrica = _metrica_db(dataset, "variacion_ponderada_pct", metricas)
        assert metrica["expresion"] == (
            "SUM(variacion_ponderada) / NULLIF(SUM(matricula_total), 0)"
        ), f"{dataset}: la razon debe ser SUM(numerador)/SUM(denominador) (R-3 DEC-012)."
        assert "fraccion" in metrica.get("unidad", ""), (
            f"{dataset}: falta declarar la unidad fraccion del numerador (R-3 DEC-012)."
        )


def test_completitud_se_reagrega_como_razon(db06_cubo: str) -> None:
    """KPI-05 = SUM(suma_completitud)/SUM(escuelas), componible con cualquier filtro."""
    assert "suma_completitud" in db06_cubo, "db06_cubo: falta el numerador suma_completitud."


def test_cubo_agrupa_en_c1_al_grano_municipio_nivel_ciclo(
    db06_cubo: str, datasets_por_nombre: dict[str, dict]
) -> None:
    """Grano cve_mun × nivel × ciclo (Cube_Specs §3.1), servido por los cubos C1."""
    assert datasets_por_nombre["db06_cubo_predicciones"]["grano"] == ["cve_mun", "nivel", "id_ciclo"]
    assert re.search(r"from\s+gold\.cubo_matricula\b", db06_cubo, re.IGNORECASE)
    assert re.search(r"join\s+gold\.cubo_riesgo_territorial\b", db06_cubo, re.IGNORECASE)
    assert not re.search(r"\bgroup\s+by\b", db06_cubo, re.IGNORECASE), (
        "db06_cubo: los cubos C1 ya vienen al grano; no se reagrega en la capa semántica."
    )


def test_detalle_y_recomendaciones_estan_al_grano_de_la_escuela(
    db06_puntos: str, db09_rec: str
) -> None:
    """Ni la capa de detalle ni las recomendaciones agregan: cada CCT es una fila."""
    for nombre, sql in (("db06_puntos", db06_puntos), ("db09_rec", db09_rec)):
        assert re.search(r"\bcct\b", sql)
        assert not re.search(r"\bgroup\s+by\b", sql, re.IGNORECASE), f"{nombre} no debe agrupar."


@pytest.mark.parametrize("fixture_name", ["db06_cubo", "db06_puntos", "db09_rec"])
def test_los_filtros_globales_tienen_columna(fixture_name: str, request: pytest.FixtureRequest) -> None:
    """AC-002.2: ciclo, entidad y nivel deben existir donde el tablero los filtra."""
    sql = request.getfixturevalue(fixture_name)
    for columna in ("id_ciclo", "cve_ent", "nivel"):
        assert columna in sql, f"{fixture_name}: falta la columna del filtro global `{columna}`."
    assert "nombre_entidad" in sql, f"{fixture_name}: el filtro nativo de entidad filtra por nombre."


# --------------------------------------------------------------------------- capa semántica (YAML)


@pytest.fixture(scope="module")
def metricas() -> dict:
    yaml = pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")
    return yaml.safe_load(leer(YAML_METRICAS))


@pytest.fixture(scope="module")
def datasets_por_nombre(metricas: dict) -> dict[str, dict]:
    return {d["nombre"]: d for d in metricas["datasets"]}


def test_el_yaml_declara_los_tres_datasets(metricas: dict) -> None:
    nombres = {d["nombre"] for d in metricas["datasets"]}
    assert nombres == {
        "db06_cubo_predicciones",
        "db06_predicciones_escuela",
        "db09_cubo_recomendaciones",
    }


def test_el_yaml_declara_los_tres_filtros_globales(metricas: dict) -> None:
    nombres = {f["nombre"] for f in metricas["filtros_globales"]}
    assert nombres == {"ciclo", "entidad", "nivel"}


def test_el_grano_del_yaml_coincide_con_el_sql(datasets_por_nombre: dict[str, dict]) -> None:
    assert datasets_por_nombre["db06_cubo_predicciones"]["grano"] == ["cve_mun", "nivel", "id_ciclo"]
    assert datasets_por_nombre["db06_predicciones_escuela"]["grano"] == ["cct", "id_ciclo"]
    assert datasets_por_nombre["db09_cubo_recomendaciones"]["grano"] == ["cct", "id_ciclo"]


def test_toda_razon_protege_la_division(metricas: dict) -> None:
    """Una división sin NULLIF revienta o miente cuando el denominador es cero."""
    for dataset in metricas["datasets"]:
        for metrica in dataset["metricas"]:
            expresion = metrica.get("expresion", "")
            if "/" in expresion:
                assert "NULLIF" in expresion.upper(), (
                    f"{dataset['nombre']}.{metrica['nombre']}: división sin NULLIF."
                )


def test_ninguna_metrica_rellena_con_cero(metricas: dict) -> None:
    """La regla del SQL se repite en la capa semántica: SIN_DATO nunca es 0."""
    for dataset in metricas["datasets"]:
        for metrica in dataset["metricas"]:
            assert "COALESCE" not in metrica.get("expresion", "").upper(), (
                f"{dataset['nombre']}.{metrica['nombre']}: no se rellenan huecos con COALESCE."
            )


def test_las_proyecciones_usan_cobertura_real(datasets_por_nombre: dict[str, dict]) -> None:
    """Los promedios de ML-01 dividen entre escuelas puntuadas; el % de escuelas
    con predicción declara ese denominador como visible (misma convención que
    DB-02, KPI-03/04)."""
    cubo = datasets_por_nombre["db06_cubo_predicciones"]
    variacion = next(m for m in cubo["metricas"] if m["nombre"] == "variacion_proyectada_promedio")
    assert "escuelas_con_prediccion" in variacion["expresion"]
    assert variacion.get("denominador_visible") == "escuelas_con_prediccion"
    riesgo = next(m for m in cubo["metricas"] if m["nombre"] == "indice_riesgo_promedio")
    assert "escuelas_con_prediccion" in riesgo["expresion"]
    assert riesgo.get("cobertura") == "cobertura_prediccion"
    pct = next(m for m in cubo["metricas"] if m["nombre"] == "pct_escuelas_con_prediccion")
    assert "escuelas" in pct["expresion"], "el % de cobertura divide entre el total, no entre puntuadas"


def test_el_porcentaje_de_recomendadas_usa_el_total_de_escuelas(datasets_por_nombre: dict[str, dict]) -> None:
    """Cobertura del plan = recomendadas / total; aquí sí el denominador es el total."""
    db09 = datasets_por_nombre["db09_cubo_recomendaciones"]
    metrica = next(m for m in db09["metricas"] if m["nombre"] == "pct_escuelas_recomendadas")
    assert "recomendacion_emitida" in metrica["expresion"]
    assert metrica.get("denominador_visible") == "escuelas"


def test_los_kpis_ratificados_estan_trazados(datasets_por_nombre: dict[str, dict]) -> None:
    """Cada KPI del Screen_Specs que vive aquí declara su ID (trazabilidad REQ→US)."""
    kpis: set[str] = set()
    for dataset in datasets_por_nombre.values():
        for metrica in dataset["metricas"]:
            if metrica.get("kpi"):
                kpis.add(metrica["kpi"])
    esperados = {"KPI-01", "KPI-02", "KPI-03", "KPI-04", "KPI-05", "KPI-07", "KPI-11", "KPI-12"}
    faltantes = esperados - kpis
    assert not faltantes, f"KPIs sin trazabilidad en el YAML: {sorted(faltantes)}"


def test_cada_dataset_declara_su_sql_real() -> None:
    """El campo `sql:` del YAML apunta a un archivo que existe en superset/semantic/."""
    yaml = pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")
    data = yaml.safe_load(leer(YAML_METRICAS))
    for dataset in data["datasets"]:
        ruta = SEMANTIC / dataset["sql"]
        assert ruta.exists(), f"{dataset['nombre']}: su SQL declarado no existe ({ruta})."


def test_toda_metrica_de_ml_declara_su_cobertura(datasets_por_nombre: dict[str, dict]) -> None:
    """Las métricas alimentadas por LEFT JOIN deben exponer la bandera de cobertura."""
    por_dataset = {
        "db06_cubo_predicciones": ("variacion_proyectada_promedio", "indice_riesgo_promedio", "escuelas_en_riesgo"),
        "db06_predicciones_escuela": ("indice_riesgo", "variacion_proyectada"),
        "db09_cubo_recomendaciones": ("recomendaciones_prioridad_alta", "indice_riesgo", "escuelas_en_riesgo"),
    }
    for dataset, nombres in por_dataset.items():
        metricas = {m["nombre"]: m for m in datasets_por_nombre[dataset]["metricas"]}
        for nombre in nombres:
            assert metricas[nombre].get("cobertura"), f"{dataset}.{nombre}: sin bandera de cobertura."


# --------------------------------------------------------------------------- tableros declarativos (YAML)


@pytest.fixture(scope="module")
def dashboards() -> dict[str, dict]:
    yaml = pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")
    resultado: dict[str, dict] = {}
    for archivo in (YAML_DB06, YAML_DB09):
        data = yaml.safe_load(leer(archivo))
        for dash in data["dashboards"]:
            resultado[dash["slug"]] = dash
    return resultado


def test_existen_los_dos_tableros(dashboards: dict[str, dict]) -> None:
    assert set(dashboards) == {"db06-predicciones", "db09-recomendaciones"}


def test_todo_chart_apunta_a_dataset_y_metrica_declarados(
    dashboards: dict[str, dict], datasets_por_nombre: dict[str, dict]
) -> None:
    """Un chart huérfano (dataset o métrica inexistente) rompe en runtime, no en CI."""
    metricas_por_dataset = {
        nombre: {m["nombre"] for m in ds.get("metricas", [])}
        for nombre, ds in datasets_por_nombre.items()
    }
    for slug, dash in dashboards.items():
        charts = dash.get("charts", [])
        assert charts, f"{slug}: sin charts"
        for chart in charts:
            ds = chart["dataset"]
            assert ds in datasets_por_nombre, f"{slug}/{chart['nombre']}: dataset '{ds}' no declarado"
            assert chart["metrica"] in metricas_por_dataset[ds], (
                f"{slug}/{chart['nombre']}: métrica '{chart['metrica']}' no declarada en '{ds}'"
            )


def test_los_tiles_kpi_son_big_number(dashboards: dict[str, dict]) -> None:
    """Contrato visual §4: la fila superior son tiles KPI (big_number_total)."""
    for slug, dash in dashboards.items():
        primeros = dash["charts"][:4]
        for chart in primeros:
            assert chart["viz"] == "big_number_total", (
                f"{slug}: '{chart['nombre']}' debería ser un tile KPI (big_number_total)"
            )
            assert int(chart.get("ancho", 12)) <= 3, (
                f"{slug}: '{chart['nombre']}' excede el ancho de un tile KPI"
            )


def test_los_filtros_nativos_cubren_columnas_reales(
    dashboards: dict[str, dict], datasets_por_nombre: dict[str, dict]
) -> None:
    """Cada filtro nativo apunta a columnas que existen en sus datasets objetivo."""
    for slug, dash in dashboards.items():
        for filtro in dash.get("filtros_globales", []):
            assert filtro.get("columna"), f"{slug}: filtro sin columna"
            assert filtro.get("datasets"), f"{slug}: filtro '{filtro['columna']}' sin datasets"
            for ds in filtro["datasets"]:
                assert ds in datasets_por_nombre, f"{slug}: filtro apunta a dataset inexistente '{ds}'"


# --------------------------------------------------------------------------- mock local de ML (guardarrailes)


@pytest.fixture(scope="module")
def mock_sql() -> str:
    return sin_comentarios(leer(MOCK))


def test_el_mock_declara_el_grano_dual_de_forma_aditiva(mock_sql: str) -> None:
    """El cubo nuevo necesita `grano` (DEC-010); el mock lo añade sin borrar nada."""
    assert mock_sql.count("grano TEXT DEFAULT 'escuela'") >= 2 or len(
        re.findall(r"grano\s+TEXT DEFAULT 'escuela'", mock_sql, re.IGNORECASE)
    ) >= 2, (
        "El mock debe declarar `grano TEXT DEFAULT 'escuela'` en el CREATE TABLE y "
        "en un ALTER ADD COLUMN IF NOT EXISTS (aditivo, legacy-safe)."
    )
    assert re.search(
        r"add\s+column\s+if\s+not\s+exists\s+grano", mock_sql, re.IGNORECASE
    ), "El mock debe completar `grano` con ADD COLUMN IF NOT EXISTS."


def test_el_mock_sigue_siendo_idempotente_y_no_destructivo(mock_sql: str) -> None:
    """La adición de `grano` no rompe las garantías originales del mock (US-203)."""
    assert re.search(r"create\s+table\s+if\s+not\s+exists", mock_sql, re.IGNORECASE)
    assert mock_sql.upper().count("ON CONFLICT") >= 2
    assert "DO NOTHING" in mock_sql.upper()
    sin_aditivos = "\n".join(
        linea for linea in mock_sql.splitlines()
        if not re.search(r"add\s+column\s+if\s+not\s+exists", linea, re.IGNORECASE)
    )
    for prohibido in ("delete", "drop table", "truncate", "update ", "alter ", "drop column"):
        assert not re.search(re.escape(prohibido), sin_aditivos, re.IGNORECASE), (
            f"El mock contiene '{prohibido.strip()}': solo CREATE/ALTER aditivo + INSERT."
        )


def test_el_mock_sigue_siendo_identificable(mock_sql: str) -> None:
    assert "MOCK-US203" in mock_sql


# --------------------------------------------------------------------------- script de sincronización


@pytest.fixture(scope="module")
def sync():
    """Importa superset/sync_semantic_layer.py como módulo (sin red en import)."""
    ruta = RAIZ / "superset" / "sync_semantic_layer.py"
    spec = importlib.util.spec_from_file_location("sync_semantic_layer", ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("sync_semantic_layer", modulo)
    spec.loader.exec_module(modulo)
    return modulo


def test_los_formatos_d3_cubren_los_formatos_del_yaml(sync, metricas: dict) -> None:
    """Todo `formato:` usado en metrics_db06_db09.yaml tiene formato d3 para charts."""
    formatos_yaml = {
        m.get("formato")
        for ds in metricas["datasets"]
        for m in ds["metricas"]
        if m.get("formato")
    }
    faltantes = formatos_yaml - set(sync.FORMATO_D3)
    assert not faltantes, f"Formatos sin mapeo d3 en FORMATO_D3: {sorted(faltantes)}"


def test_los_porcentajes_se_formatean_como_porcentaje(sync) -> None:
    """'porcentaje_1' debe renderizar 0.123 como '12.3%', no como '0.1'."""
    assert sync.FORMATO_D3["porcentaje_1"].endswith("%")
    assert sync.FORMATO_D3["porcentaje_0"].endswith("%")