"""Pruebas del contrato semántico de los cubos de DB-03 y DB-04 (US-211a, repunteo US-205).

Convierten en algo que el CI puede hacer cumplir las reglas que este proyecto no puede
permitirse romper en la capa de BI:

* **`SIN_DATO` nunca es cero.** Si alguien —persona o IA— "arregla" un hueco con
  `COALESCE(d1, 0)`, el tablero afirmaría "aquí no hay problema" justo donde el Estado no
  está midiendo. Estas pruebas fallan si eso aparece.
* **El SQL semántico lee `gold.cubo_*`** (repunteo US-205/US-113): ya no agrega el hecho
  ni une salidas de ML — los LEFT JOIN con llave completa, el modelo `ML-01` y el umbral
  `0.5` (DEC-019, antes 0.6/ancla DEC-006) ya los resolvió el cubo C1. La capa hace
  passthrough explícito del contrato.
* **Las razones se guardan como numerador y denominador**, para que se puedan reagregar con
  cualquier combinación de los filtros globales (AC-002.2).

Validación **estática**: no necesita base de datos ni dependencias fuera de `requirements.txt`.
La validación contra datos reales queda pendiente de `gold.*` (US-112 / US-113, Célula 1).

Contrato: `vault/04_UX_Design/Cube_Specs_DB03_DB04.md` (DOC-CUBESPEC-DB0304).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SEMANTIC = RAIZ / "superset" / "semantic"

SQL_DB03 = SEMANTIC / "db03_cubo_escuela_360.sql"
SQL_DB04 = SEMANTIC / "db04_cubo_comparador_municipio.sql"
YAML_METRICAS = SEMANTIC / "metrics_db03_db04.yaml"

DRIVERS = ("d1", "d2", "d3", "d4", "d5", "d6")
UMBRAL_RIESGO = "0.5"

# Salidas de ML: viven en gold.predicciones / gold.recomendaciones, jamás en el hecho.
SALIDAS_ML = ("indice_riesgo", "driver_dominante", "recomendacion", "prioridad")


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
def db03() -> str:
    return sin_comentarios(leer(SQL_DB03))


@pytest.fixture(scope="module")
def db04() -> str:
    return sin_comentarios(leer(SQL_DB04))


# --------------------------------------------------------------------------- R2: SIN_DATO nunca es cero


@pytest.mark.parametrize("cubo", ["db03", "db04"])
def test_ningun_driver_se_rellena_con_cero(cubo: str, request: pytest.FixtureRequest) -> None:
    """Prohibido `COALESCE(d#, 0)`: la ausencia de dato no es un cero (Data_Model §1)."""
    sql = request.getfixturevalue(cubo)
    for driver in DRIVERS:
        patron = rf"coalesce\s*\(\s*\w*\.?{driver}\b[^)]*,\s*0"
        assert not re.search(patron, sql, re.IGNORECASE), (
            f"{cubo}: `{driver}` se rellena con cero. SIN_DATO nunca es cero (regla R2)."
        )


@pytest.mark.parametrize("cubo", ["db03", "db04"])
def test_el_riesgo_no_se_rellena_con_cero(cubo: str, request: pytest.FixtureRequest) -> None:
    """Una escuela sin predicción no es una escuela con riesgo 0."""
    sql = request.getfixturevalue(cubo)
    patron = r"coalesce\s*\(\s*\w*\.?indice_riesgo\b[^)]*,\s*0"
    assert not re.search(patron, sql, re.IGNORECASE), (
        f"{cubo}: `indice_riesgo` se rellena con cero. Debe quedar nulo y declararse SIN_DATO."
    )


def test_db03_expone_las_banderas_de_cobertura(db03: str) -> None:
    """Cada driver viaja con su bandera, y hay bandera para predicción y recomendación."""
    for driver in DRIVERS:
        assert f"{driver}_cobertura" in db03, f"Falta la bandera {driver}_cobertura en DB-03"
    assert "cobertura_prediccion" in db03
    assert "cobertura_recomendacion" in db03


def test_db04_publica_el_denominador_real_de_cada_driver(db04: str) -> None:
    """El promedio de un driver se calcula sobre las escuelas con cobertura OK, no sobre el total."""
    for driver in DRIVERS:
        assert f"escuelas_con_{driver}" in db04, (
            f"Falta el denominador `escuelas_con_{driver}`: sin él, el promedio de {driver} "
            "se calcularía sobre escuelas que nunca se midieron."
        )
        assert f"cobertura_{driver}" in db04, (
            f"Falta la bandera `cobertura_{driver}` (R2: SIN_DATO nunca cero)."
        )


def test_db04_no_guarda_promedios_ya_calculados(db04: str) -> None:
    """Un promedio no se puede reagregar: el cubo guarda componentes, la razón vive en la capa semántica."""
    assert not re.search(r"\bavg\s*\(", db04, re.IGNORECASE), (
        "DB-04 guarda un promedio precalculado. Al quitar el filtro de nivel, Superset "
        "promediaría promedios y daría un número incorrecto (Cube_Specs §4.3)."
    )


# --------------------------------------------------------------------------- R1: las salidas de ML van por JOIN


@pytest.mark.parametrize("cubo", ["db03", "db04"])
def test_las_salidas_de_ml_no_se_leen_del_hecho(cubo: str, request: pytest.FixtureRequest) -> None:
    """`fact_escuela_ciclo` solo tiene hechos observados (Data_Model §4.1)."""
    sql = request.getfixturevalue(cubo)
    for salida in SALIDAS_ML:
        assert not re.search(rf"\bf\.{salida}\b", sql), (
            f"{cubo}: `f.{salida}` se lee del hecho. Las salidas de ML se consultan por JOIN "
            "a gold.predicciones / gold.recomendaciones."
        )


def test_db03_lee_el_cubo_fisico(db03: str) -> None:
    """Repunteo US-205: la ficha 360 se sirve de gold.cubo_escuela_360 (C1)."""
    assert re.search(r"from\s+gold\.cubo_escuela_360\b", db03, re.IGNORECASE), (
        "db03: debe leer gold.cubo_escuela_360."
    )


def test_db04_lee_el_cubo_fisico(db04: str) -> None:
    """Repunteo US-205: el comparador se sirve de gold.cubo_comparador_municipio (C1)."""
    assert re.search(r"from\s+gold\.cubo_comparador_municipio\b", db04, re.IGNORECASE), (
        "db04: debe leer gold.cubo_comparador_municipio."
    )


def test_db04_publica_la_cobertura_de_riesgo(db04: str) -> None:
    """R2: el riesgo viaja con cobertura_riesgo (SIN_DATO nunca cero) desde el cubo."""
    assert re.search(r"\bcobertura_riesgo\b", db04), (
        "db04: falta cobertura_riesgo para gobernar el área de predicción."
    )


@pytest.mark.parametrize("cubo", ["db03", "db04"])
def test_la_capa_semantica_no_reune_salidas_de_ml(cubo: str, request: pytest.FixtureRequest) -> None:
    """R1 ya lo resolvió el cubo C1; la capa semántica no re-une gold.predicciones ni
    gold.recomendaciones."""
    sql = request.getfixturevalue(cubo)
    for tabla in ("gold.predicciones", "gold.recomendaciones"):
        assert not re.search(rf"\b{re.escape(tabla)}\b", sql, re.IGNORECASE), (
            f"{cubo}: {tabla} ya fue resuelta por C1; no se re-une en la capa semántica."
        )


# --------------------------------------------------------------------------- DEC-019: linea de alerta


def test_el_umbral_de_riesgo_es_la_linea_de_alerta(datasets_por_nombre: dict[str, dict]) -> None:
    """0.5 = línea de alerta DEC-019 (antes 0.6, ancla de calibración DEC-006).
    Con el repunteo el umbral ya no vive en el SQL (lo aplicó C1): queda declarado
    en el YAML de métricas (`umbral: 0.5`) para mantener el contrato KPI-04 (BUG-060)."""
    for nombre in ("cubo_escuela_360", "cubo_comparador_municipio"):
        ds = datasets_por_nombre[nombre]
        metricas = {m["nombre"]: m for m in ds["metricas"]}
        assert metricas["escuelas_en_riesgo"].get("umbral") == float(UMBRAL_RIESGO), (
            f"{nombre}: debe ratificar el umbral 0.5 (DEC-019) en el YAML."
        )


# --------------------------------------------------------------------------- grano y filtros globales


def test_db03_tiene_grano_de_escuela_por_ciclo(db03: str) -> None:
    """Grano cct × ciclo (Data_Model §4.3), servido por el cubo C1 a detalle."""
    assert re.search(r"\bcct\b", db03)
    assert re.search(r"\bid_ciclo\b", db03)
    assert not re.search(r"\bgroup\s+by\b", db03, re.IGNORECASE), (
        "DB-03 está al grano del detalle: no debe agregar."
    )


def test_db04_agrupa_al_grano_declaro_en_el_cubo(db04: str, datasets_por_nombre: dict[str, dict]) -> None:
    """Repunteo US-205: db04 ya viene al grano cve_mun × nivel × ciclo desde C1 — el
    YAML lo declara y el SQL no reagrega (sin nivel no se cumpliría AC-002.2)."""
    assert datasets_por_nombre["cubo_comparador_municipio"]["grano"] == ["cve_mun", "nivel", "id_ciclo"]
    assert not re.search(r"\bgroup\s+by\b", db04, re.IGNORECASE), (
        "db04: el cubo C1 ya viene al grano; no se reagrega en la capa semántica."
    )


@pytest.mark.parametrize("cubo", ["db03", "db04"])
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


@pytest.fixture(scope="module")
def datasets_por_nombre(metricas: dict) -> dict[str, dict]:
    return {d["nombre"]: d for d in metricas["datasets"]}


def test_el_yaml_declara_los_dos_cubos(metricas: dict) -> None:
    nombres = {d["nombre"] for d in metricas["datasets"]}
    assert nombres == {"cubo_escuela_360", "cubo_comparador_municipio"}


def test_el_yaml_declara_los_tres_filtros_globales(metricas: dict) -> None:
    """AC-002.2: ciclo, entidad y nivel aplican al conjunto de tableros."""
    nombres = {f["nombre"] for f in metricas["filtros_globales"]}
    assert nombres == {"ciclo", "entidad", "nivel"}


def test_el_grano_del_yaml_coincide_con_el_sql(metricas: dict) -> None:
    granos = {d["nombre"]: d["grano"] for d in metricas["datasets"]}
    assert granos["cubo_escuela_360"] == ["cct", "id_ciclo"]
    assert granos["cubo_comparador_municipio"] == ["cve_mun", "nivel", "id_ciclo"]


def test_toda_razon_protege_la_division(metricas: dict) -> None:
    """Una división sin `NULLIF` revienta o miente cuando el denominador es cero."""
    for dataset in metricas["datasets"]:
        for metrica in dataset["metricas"]:
            expresion = metrica.get("expresion", "")
            if "/" in expresion:
                assert "NULLIF" in expresion.upper(), (
                    f"{dataset['nombre']}.{metrica['nombre']}: división sin NULLIF."
                )


def test_los_porcentajes_no_se_multiplican_dos_veces(metricas: dict) -> None:
    """Una razón con formato de porcentaje NO lleva `* 100`: el d3 ya multiplica.

    `formato: porcentaje_0|1` se mapea a los formatos d3 `,.0%` / `,.1%`, que multiplican
    por 100 al renderizar. Si además la expresión multiplica, el tablero pinta el número
    cien veces más grande — `0.318` se vería como `3,180.0%`. El error ya apareció tres
    veces en el proyecto (US-203, US-211b y US-212), así que aquí se hace cumplir.
    """
    for dataset in metricas["datasets"]:
        for metrica in dataset["metricas"]:
            if not str(metrica.get("formato", "")).startswith("porcentaje"):
                continue
            expresion = metrica.get("expresion", "")
            assert "100" not in expresion, (
                f"{dataset['nombre']}.{metrica['nombre']}: expresión con `* 100` y "
                f"formato '{metrica['formato']}'. El formato d3 ya multiplica por 100; "
                "guarda la razón como fracción."
            )



def test_una_metrica_de_porcentaje_no_multiplica_dos_medidas(metricas: dict) -> None:
    """Una razón se calcula como razón de sumas, no como promedio ponderado de razones.

    Regresión de BUG-031. `variacion_ponderada_pct` era
    `SUM(variacion_matricula * matricula_total) / NULLIF(SUM(matricula_total), 0)`: un promedio
    de `variacion_matricula` ponderado por matrícula, que solo tendría sentido si esa columna
    fuera una razón. Son alumnos absolutos, así que el tablero pintó **-54.5%** durante dos
    semanas donde el valor real era **-0.19%**.

    La firma del defecto es el **producto de dos columnas dentro de un agregado**: delata que se
    está promediando una razón que no es razón, y que el numerador y el denominador reales no
    existen por separado. La prueba hermana —la del `* 100`— no lo detectaba porque esta
    expresión nunca tuvo `* 100`: cubría la *forma* del error de US-203/US-211b/US-212, no su
    *clase*. Esa confianza falsa es lo que esta prueba viene a cerrar.

    Nota deliberada sobre el alcance: esto es verificable sin base de datos, así que corre en
    CI. Lo que NO sustituye es mirar el número — "devuelve datos" no es "devuelve el dato
    correcto".
    """
    producto_de_columnas = re.compile(
        r"(?:SUM|AVG)\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*\*\s*[A-Za-z_][A-Za-z0-9_]*",
        re.IGNORECASE,
    )
    for dataset in metricas["datasets"]:
        for metrica in dataset["metricas"]:
            if not str(metrica.get("formato", "")).startswith("porcentaje"):
                continue
            expresion = metrica.get("expresion", "")
            assert not producto_de_columnas.search(expresion), (
                f"{dataset['nombre']}.{metrica['nombre']}: la expresión multiplica dos medidas "
                f"dentro de un agregado ({expresion!r}) y se renderiza como porcentaje. "
                "Guarda numerador y denominador por separado y divide sumas de una sola "
                "columna (Cube_Specs_DB03_DB04 §4.4, BUG-031)."
            )

def test_ninguna_metrica_rellena_con_cero(metricas: dict) -> None:
    for dataset in metricas["datasets"]:
        for metrica in dataset["metricas"]:
            assert "COALESCE" not in metrica.get("expresion", "").upper(), (
                f"{dataset['nombre']}.{metrica['nombre']}: no se rellenan huecos con COALESCE."
            )


def test_el_porcentaje_en_riesgo_usa_las_escuelas_puntuadas(metricas: dict) -> None:
    """Decir '10% en riesgo' cuando solo se puntuó al 30% inventaría una cobertura inexistente."""
    db04 = next(d for d in metricas["datasets"] if d["nombre"] == "cubo_comparador_municipio")
    metrica = next(m for m in db04["metricas"] if m["nombre"] == "pct_escuelas_en_riesgo")
    assert "escuelas_con_prediccion" in metrica["expresion"]
    assert metrica.get("denominador_visible") == "escuelas_con_prediccion"


def test_cada_metrica_de_driver_declara_su_cobertura(metricas: dict) -> None:
    db04 = next(d for d in metricas["datasets"] if d["nombre"] == "cubo_comparador_municipio")
    por_nombre = {m["nombre"]: m for m in db04["metricas"]}
    for driver in DRIVERS:
        metrica = por_nombre[f"{driver}_promedio"]
        assert metrica["cobertura"] == f"escuelas_con_{driver}"
