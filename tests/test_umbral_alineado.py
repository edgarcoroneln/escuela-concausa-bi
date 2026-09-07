"""La capa de presentación de Superset usa la misma línea de alerta que /kpis (`DEC-019`, BUG-060).

`test_linea_de_alerta.py` protege el corte en Python (`LINEA_DE_ALERTA`) y en los
cubos Gold de dbt. Este archivo cierra el flanco que quedaba: la **presentación C2**.
dbt ya cuenta `escuelas_en_riesgo` con `>= 0.5` desde el PR #273 de C1, pero los
YAML de métricas, los `subheader` de los tableros y los comentarios de cabecera de
los SQL seguían declarando el 0.60 de la época `DEC-006` — un tablero que solo se
sincroniza, nunca recalcula, por lo que mostraba la estimación correcta bajo un
cartel que mentía.

Doble guarda (respuesta al PM en PR #275):
1. **Barrido total de `superset/semantic/**` y `superset/dashboards/**`**: ninguna
   línea vuelve a imprimir un 0.6/0.60 antiguo asociado a riesgo (patrones
   `>= 0.6`, `≥ 0.6`, `umbral … 0.6`, `desde 0.60`), salvo cuando el contexto es
   explícitamente el **ancla de calibración** (`ANCLA_SIGMOIDE = 0.60`, DEC-006),
   que sí debe seguir viva en la documentación.
2. **Invariantes puntuales**: `umbral` de `escuelas_en_riesgo` en los YAML de
   métricas == `LINEA_DE_ALERTA`; los `subheader` de los tiles de riesgo imprimen
   0.5, nunca 0.6/0.60; la nota de KPI-04 referencia DEC-019.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.api.repositorio_gold import ANCLA_SIGMOIDE, LINEA_DE_ALERTA

RAIZ = Path(__file__).resolve().parents[1]
SEMANTIC = RAIZ / "superset" / "semantic"
DASHBOARDS = RAIZ / "superset" / "dashboards"
_DIRS_SCOPED = (SEMANTIC, DASHBOARDS)

_TILE_KPI04 = "KPI-04 · Escuelas en riesgo"
_VIEJOS = ("0.6", "0.60")

_ANCLA_RE = re.compile(r"ancla|calibra", re.IGNORECASE)
_VIEJO_RE = re.compile(
    r"""
    (?:>=\s*|≥\s*|desde\s*|de\s*)0\.60?               # >= 0.6, ≥ 0.6, desde 0.60, de 0.6
    |umbral[^\n]{0,30}?0\.60?                          # umbral: 0.6, umbral R3 (>= 0.6)…
    |0\.60?\s*\((?:DEC-006|R3)\)                       # 0.60 (DEC-006), 0.6 (R3)
    """,
    re.IGNORECASE | re.VERBOSE,
)


@pytest.fixture(scope="module")
def yaml():
    return pytest.importorskip("yaml", reason="pyyaml no está en requirements.txt")


def _charts_del_tablero(yaml, archivo: Path) -> list[dict]:
    data = yaml.safe_load(archivo.read_text(encoding="utf-8"))
    tablero = data["dashboards"][0]
    charts: list[dict] = tablero.get("charts", [])
    for tab in tablero.get("tabs", []):
        charts.extend(tab.get("charts", []))
    return charts


def _umbrales_escuelas_en_riesgo(yaml, archivos_metricas) -> list[tuple[str, object]]:
    encontrados: list[tuple[str, object]] = []
    for archivo in archivos_metricas:
        data = yaml.safe_load(archivo.read_text(encoding="utf-8"))
        for ds in data.get("datasets", []):
            for m in ds["metricas"]:
                if m["nombre"] == "escuelas_en_riesgo" and "umbral" in m:
                    encontrados.append((ds["nombre"], m["umbral"]))
    return encontrados


def test_el_umbral_de_escuelas_en_riesgo_es_la_linea_de_alerta(yaml) -> None:
    """`umbral:` declarado para `escuelas_en_riesgo` == `LINEA_DE_ALERTA`, en todos los YAML."""
    metricas = sorted(SEMANTIC.glob("metrics_*.yaml"))
    umbrales = _umbrales_escuelas_en_riesgo(yaml, metricas)
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
    data = yaml.safe_load((SEMANTIC / "metrics_kpis_base_us221.yaml").read_text(encoding="utf-8"))
    nota = next(k for k in data["tarjetas"] if k["kpi"] == "KPI-04")["nota"]
    assert "DEC-019" in nota and "0.5" in nota
    assert "DEC-006" not in nota and not any(v in nota for v in _VIEJOS), (
        "KPI-04 sigue citando el umbral viejo: caseta desincronizada del cubo."
    )


def test_los_subheaders_de_riesgo_imprimen_el_umbral_vigente(yaml) -> None:
    """Ningún tile de riesgo imprime el umbral viejo; si declara uno, es 0.5 (DEC-019)."""
    tiles_vistos = 0
    for archivo in sorted(DASHBOARDS.glob("*.yaml")):
        for tile in _charts_del_tablero(yaml, archivo):
            nombre = (tile.get("nombre") or "").lower()
            sub = tile.get("subheader", "")
            if not (("riesgo" in nombre or "ml-01" in nombre) and sub):
                continue
            tiles_vistos += 1
            assert not any(v in sub for v in _VIEJOS), (
                f"{archivo.name}: tile '{tile.get('nombre')}' imprime un umbral anterior: '{sub}'"
            )
            assert not _VIEJO_RE.search(sub), (
                f"{archivo.name}: tile '{tile.get('nombre')}' imprime un umbral anterior: '{sub}'"
            )
    assert tiles_vistos, "no encontró ningún tile de riesgo con subheader: se dejó de vigilar"


def test_barrido_no_deja_umbral_anterior_en_semantic_ni_en_dashboards() -> None:
    """Barrido total: ningún 0.6/0.60 antiguo en SEMANTIC/** ni DASHBOARDS/** salvo el ancla.

    La excepción única es el **ancla de calibración** (DEC-006): `ANCLA_SIGMOIDE`
    sigue siendo 0.60 en el contrato de ML-01 y su documentación puede citarlo
    cuando la línea menciona explícitamente 'ancla'/'calibra'. El bucket de
    distribución `rango_riesgo` de db06 (`indice_riesgo < 0.6`, rotulado
    "0.40 - 0.59") no es la línea de alerta y queda fuera de estos patrones.
    """
    ofensas: list[str] = []
    for carpeta in _DIRS_SCOPED:
        for archivo in sorted(carpeta.rglob("*")):
            if archivo.suffix not in (".yaml", ".yml", ".sql", ".md"):
                continue
            for num, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), 1):
                if not _VIEJO_RE.search(linea):
                    continue
                if _ANCLA_RE.search(linea):
                    continue  # ancla de calibración (0.60 ≈ perder 5%), permitida a propósito
                rel = archivo.relative_to(RAIZ)
                ofensas.append(f"{rel}:{num}: {linea.strip()}")
    assert not ofensas, (
        "quedan 0.6/0.60 antiguos (BUG-060, PR #275):\n- "
        + "\n- ".join(ofensas)
        + "\nLa línea de alerta es 0.5 (DEC-019). El único 0.60 legítimo es el ancla "
        f"ANCLA_SIGMOIDE ({ANCLA_SIGMOIDE}) y debe citarse junto a 'ancla'/'calibra'."
    )