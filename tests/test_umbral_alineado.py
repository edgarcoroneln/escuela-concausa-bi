"""La capa de presentación de Superset usa la misma línea de alerta que /kpis (`DEC-019`, BUG-060).

`test_linea_de_alerta.py` protege el corte en Python (`LINEA_DE_ALERTA`) y en los
cubos Gold de dbt. Este archivo cierra el flanco que quedaba: la **presentación C2**.
dbt ya cuenta `escuelas_en_riesgo` con `>= 0.5` desde el PR #273 de C1, pero los
YAML de métricas y los `subheader` de los tableros seguían declarando el 0.60 de la
época `DEC-006` — un tablero que solo se sincroniza, nunca recalcula, por lo que
mostraba la estimación correcta bajo un cartel que mentía.

Regla que protege: **`umbral` de `escuelas_en_riesgo` es igual a `LINEA_DE_ALERTA`**
y ningún comparable del tablero vuelve a imprimir 0.6/0.60. DB-03 360 es un caso
distinto a propósito: su KPI-17 describe el ancla de calibración `ANCLA_SIGMOIDE`
(0.60, DEC-006), que **no** es la línea de alerta.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.api.repositorio_gold import ANCLA_SIGMOIDE, LINEA_DE_ALERTA

RAIZ = Path(__file__).resolve().parents[1]
SEMANTIC = RAIZ / "superset" / "semantic"
DASHBOARDS = RAIZ / "superset" / "dashboards"

METRICAS = SEMANTIC / "metrics_db01_db02.yaml"
KPIS_BASE = SEMANTIC / "metrics_kpis_base_us221.yaml"
_DASHBOARDS_RIESGO = (DASHBOARDS / "db02_mapa_riesgo.yaml", DASHBOARDS / "db09_recomendaciones.yaml")
_TILE_KPI04 = "KPI-04 · Escuelas en riesgo"

_VIEJOS = ("0.6", "0.60")


@pytest.fixture(scope="module")
def yaml():
    return pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")


def _charts_del_tablero(yaml, archivo: Path) -> list[dict]:
    data = yaml.safe_load(archivo.read_text(encoding="utf-8"))
    return data["dashboards"][0]["charts"]


def test_el_umbral_de_escuelas_en_riesgo_es_la_linea_de_alerta(yaml) -> None:
    """`umbral:` declarado para `escuelas_en_riesgo` == `LINEA_DE_ALERTA`, nunca el ancla."""
    data = yaml.safe_load(METRICAS.read_text(encoding="utf-8"))
    umbrales = [
        (ds["nombre"], m["umbral"])
        for ds in data["datasets"]
        for m in ds["metricas"]
        if m["nombre"] == "escuelas_en_riesgo" and "umbral" in m
    ]
    assert umbrales, (
        "ninguna métrica escuelas_en_riesgo declara umbral: el alineamiento ya no se vigila"
    )

    for nombre_ds, umbral in umbrales:
        assert umbral == LINEA_DE_ALERTA, (
            f"{nombre_ds} declara umbral {umbral} y la API {LINEA_DE_ALERTA}. "
            "BUG-060: dbt ya cuenta con 0.5 (PR #273); la presentación debe declarar lo mismo."
        )
        assert umbral != ANCLA_SIGMOIDE, (
            f"{nombre_ds}: volviste a fundir ANCLA_SIGMOIDE ({ANCLA_SIGMOIDE}) con LINEA_DE_ALERTA."
        )


def test_la_base_de_kpis_cita_dec019_y_no_dec006(yaml) -> None:
    """La nota de KPI-04 referencia el ADR correcto y el número correcto."""
    data = yaml.safe_load(KPIS_BASE.read_text(encoding="utf-8"))
    nota = next(k for k in data["tarjetas"] if k["kpi"] == "KPI-04")["nota"]
    assert "DEC-019" in nota and "0.5" in nota
    assert "DEC-006" not in nota and not any(v in nota for v in _VIEJOS), (
        "KPI-04 sigue citando el umbral viejo: caseta desincronizada del cubo."
    )


def test_los_subheaders_de_riesgo_imprimen_el_umbral_vigente(yaml) -> None:
    """Los carteles big_number de DB-02 y DB-09 describen la línea real, no la vieja."""
    for archivo in _DASHBOARDS_RIESGO:
        charts = _charts_del_tablero(yaml, archivo)
        tiles_kpi04 = [t for t in charts if t.get("nombre") == _TILE_KPI04]
        assert tiles_kpi04, f"{archivo.name}: no encontró el tile {_TILE_KPI04}"

        for tile in tiles_kpi04:
            sub = tile.get("subheader", "")
            assert any(v in sub for v in ("0.5", "0,5")), (
                f"{archivo.name}: KPI-04 subheader '{sub}' no declara umbral 0.5 (DEC-019)"
            )
            assert not any(v in sub for v in _VIEJOS), (
                f"{archivo.name}: KPI-04 subheader '{sub}' aún imprime el umbral anterior"
            )