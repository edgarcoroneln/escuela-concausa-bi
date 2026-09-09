"""Guarda del repunteo US-205: los datasets semánticos leen cubos físicos, no hechos.

La capa semántica de Superset pasó de agregar `gold.fact_escuela_ciclo` (y unir salidas de
ML) a consumir los cubos físicos C1 (`gold.cubo_*`) del grano DEC-009/010. Este guardarraíl
estático hace cumplir dos invariantes sobre los 15 SQL de `superset/semantic/` (13 del
repunteo US-205 + 2 de DB-07, US-222, que ya siguen el mismo patrón):

1. **Nada lee `gold.fact_*`.** Un `FROM gold.fact_escuela_ciclo` reintroduciría en la capa
   semántica la agregación que US-205 eliminó.
2. **Solo se tocan las fuentes del repunteo** (allowlist): los 8 cubos C1 + las dimensiones
   de enrich (`geo_municipio`, `dim_driver`) + `gold.predicciones` (db09, el único LEFT JOIN
   que el cubo de recomendaciones no resuelve).

Además, si un YAML declara `cubo_canonico_futuro: gold.<cubo>`, el SQL de ese dataset debe
leer ese mismo cubo.

Validación **estática**: no necesita base de datos. La validación contra datos corre con
`superset/sync_semantic_layer.py --validar-datos`.

Contratos: `vault/04_UX_Design/Cube_Specs_DB*.md` (US-113/205).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SEMANTIC = RAIZ / "superset" / "semantic"

# Los 13 datasets virtuales que US-205 repuntó a gold.cubo_* (mismo contra lo
# que declaran los YAML de métricas en `sql:`).
SQLS_US205 = (
    "db01_cubo_matricula.sql",
    "db01_distribucion_escuelas.sql",
    "db01_driver_dominante.sql",
    "db02_cubo_riesgo_territorial.sql",
    "db02_coropletico.sql",
    "db02_puntos_escuela.sql",
    "db03_cubo_escuela_360.sql",
    "db04_cubo_comparador_municipio.sql",
    "db05_cubo_driver.sql",
    "db06_cubo_predicciones.sql",
    "db06_predicciones_escuela.sql",
    "db08_cubo_pivot.sql",
    "db09_cubo_recomendaciones.sql",
)

# DB-07 (US-222, Oscar Quiroz) consume gold.cubo_completitud y geo_municipio:
# entra al guardarraíl para que el inventario completo del directorio sea exacto.
SQLS_DB07 = (
    "db07_cubo_completitud.sql",
    "db07_mapa_vacios.sql",
)

# Inventario completo de datasets virtuales del directorio semantic/.
SQLS_SEMANTIC = SQLS_US205 + SQLS_DB07

# Únicas tablas Gold que la capa semántica puede tocar en v1 del repunteo.
GOLD_SOURCES = {
    "gold.cubo_matricula",
    "gold.cubo_riesgo_territorial",
    "gold.cubo_escuela_360",
    "gold.cubo_comparador_municipio",
    "gold.cubo_driver",
    "gold.cubo_pivot",
    "gold.cubo_recomendaciones",
    "gold.cubo_completitud",    # DB-07 (US-222)
    "gold.geo_municipio",   # enrich: nombre oficial INEGI del municipio
    "gold.dim_driver",      # enrich: catalogo de drivers (db08)
    "gold.predicciones",    # solo db09 (el cubo de recomendaciones no trae riesgo)
}


def _sin_comentarios(sql: str) -> str:
    """Quita los comentarios `--` para no validar 'de mentiras' la prosa."""
    return "\n".join(linea.split("--")[0] for linea in sql.splitlines())


def _leer(nombre: str) -> str:
    ruta = SEMANTIC / nombre
    assert ruta.exists(), f"Falta el SQL del repunteo: {ruta}"
    return _sin_comentarios(ruta.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def textos() -> dict[str, str]:
    return {nombre: _leer(nombre) for nombre in SQLS_SEMANTIC}


# --------------------------------------------------------------------------- el set es exacto


def test_son_exactamente_los_15_datasets_virtuales(textos: dict[str, str]) -> None:
    """Si alguien agrega o elimina un dataset virtual, el inventario se queda corto."""
    existentes = {p.name for p in sorted(SEMANTIC.glob("db0*.sql"))}
    assert set(textos) == existentes == set(SQLS_SEMANTIC)


# --------------------------------------------------------------------------- invariante 1: sin hechos


@pytest.mark.parametrize("nombre", SQLS_SEMANTIC)
def test_ningun_sql_lee_el_hecho(nombre: str, textos: dict[str, str]) -> None:
    """US-205: la agregación vive en C1, no en la capa semántica."""
    assert not re.search(r"gold\.fact_[a-z_0-9]+", textos[nombre], re.IGNORECASE), (
        f"{nombre}: lee un hecho (gold.fact_*). Repuntar a gold.cubo_* (US-205)."
    )


# --------------------------------------------------------------------------- invariante 2: allowlist


@pytest.mark.parametrize("nombre", SQLS_SEMANTIC)
def test_las_fuentes_estan_en_la_allowlist(nombre: str, textos: dict[str, str]) -> None:
    """Un FORASTERO aquí (gold.dim_*, gold_ml_runtime.*, etc.) rompe el contrato del repunteo."""
    fuentes = set(re.findall(r"gold\.[a-z_0-9]+", textos[nombre]))
    forasteras = fuentes - GOLD_SOURCES
    assert not forasteras, (
        f"{nombre}: fuentes fuera de la allowlist US-205: {sorted(forasteras)}"
    )
    assert fuentes, f"{nombre}: no referencia ninguna tabla gold."


# --------------------------------------------------------------------------- consistencia con el YAML


@pytest.fixture(scope="module")
def datasets_con_cubo_futuro() -> list[dict]:
    """Los datasets que declaran `cubo_canonico_futuro` en su YAML de métricas."""
    yaml = pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")
    resultado: list[dict] = []
    for ruta in sorted(SEMANTIC.glob("metrics_db*.yaml")):
        data = yaml.safe_load(ruta.read_text(encoding="utf-8"))
        for dataset in data.get("datasets", []):
            cubo = dataset.get("cubo_canonico_futuro")
            if cubo:
                resultado.append({"nombre": dataset["nombre"], "sql": dataset["sql"], "cubo": cubo})
    return resultado


def test_cada_dataset_declara_su_sql_y_cubo_futuro(datasets_con_cubo_futuro: list[dict]) -> None:
    """El YAML apunta a un SQL existente y todos los que declaraban un cubo futuro
    deberían haberlo consumido ya (US-113 materializó gold.cubo_*)."""
    assert datasets_con_cubo_futuro, "Ningún dataset declara cubo_canonico_futuro."
    for dataset in datasets_con_cubo_futuro:
        ruta = SEMANTIC / dataset["sql"]
        assert ruta.exists(), f"{dataset['nombre']}: SQL declarado no existe ({ruta})."


def test_el_sql_lee_el_cubo_que_declara(datasets_con_cubo_futuro: list[dict]) -> None:
    """`cubo_canonico_futuro: gold.X` debe leerse en el SQL del dataset (o en un cubo
    que lo derive, ver db06_cubo_predicciones)."""
    for dataset in datasets_con_cubo_futuro:
        sql = _sin_comentarios(_leer(dataset["sql"]))
        assert re.search(re.escape(dataset["cubo"]), sql), (
            f"{dataset['nombre']}: declara {dataset['cubo']} pero su SQL no lo lee."
        )


# --------------------------------------------------------------------------- columnas del YAML vivas en el SQL


SQL_KEYWORDS = {
    "sum", "count", "avg", "nullif", "coalesce", "case", "when", "then", "else",
    "upper", "numeric",
    "end", "distinct", "filter", "where", "true", "false", "if", "and", "or",
    "not", "in", "is", "null", "as",
}


@pytest.fixture(scope="module")
def metricas_por_dataset() -> dict[str, dict]:
    yaml = pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")
    resultado: dict[str, dict] = {}
    for ruta in sorted(SEMANTIC.glob("metrics_db*.yaml")):
        for dataset in yaml.safe_load(ruta.read_text(encoding="utf-8")).get("datasets", []):
            resultado[dataset["nombre"]] = dataset
    return resultado


def test_toda_metrica_referencia_solo_columnas_del_dataset(metricas_por_dataset: dict[str, dict]) -> None:
    """Cada identificador de una expresion de metrica debe vivir en el SQL del dataset.
    Con el passthrough de C1 es facil que una columna del cubo no se re-exporte y la
    metrica truene en Superset (regresion real encontrada en db09.prioridad, US-205)."""
    for nombre, dataset in metricas_por_dataset.items():
        sql = _sin_comentarios(_leer(dataset["sql"]))
        for metrica in dataset["metricas"]:
            identificadores = {
                t.lower()
                for t in re.findall(r"[a-z_][a-z0-9_]*", metrica.get("expresion", ""))
                if t.lower() not in SQL_KEYWORDS
            }
            ausentes = [
                ident
                for ident in sorted(identificadores)
                if not re.search(rf"\b{re.escape(ident)}\b", sql)
            ]
            assert not ausentes, (
                f"{nombre}.{metrica['nombre']}: la expresion usa columnas ausentes del SQL "
                f"(passthrough de C1): {ausentes}"
            )