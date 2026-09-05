"""BUG-047 — mejora aditiva: resolución dinámica del ciclo por defecto.

Historia: US-222 / REQ-002 (Oscar Antonio Quiroz Lázaro, Célula 2).

`metrics_db01_db02.yaml`, `metrics_db03_db04.yaml`, `metrics_db05_db08.yaml`,
`metrics_db06_db09.yaml` y `metrics_db07.yaml` documentaban `default: ultimo_ciclo`
para el filtro de Ciclo escolar (AC-002.2). El fix original de BUG-047
(Manuel Serranía, `dev/manuel-serrania`) resolvió el mismo defecto con
`valor_por_defecto` **estático** ("2024-2025", hay que actualizarlo a mano
cada ciclo). Estas pruebas cubren la mejora aditiva: `_filtros_nativos()`
ahora también resuelve `default: ultimo_<algo>` **dinámicamente** contra los
datos reales (`ORDER BY <columna> DESC LIMIT 1` vía `/api/v1/chart/data`),
con prioridad sobre `valor_por_defecto`, que queda como respaldo. Confirmado
en vivo antes del fix: `total_escuelas` de DB-07 mostraba 25,578 (3 ciclos
sumados) en vez de 8,382 — el mismo patrón que BUG-044 en la API, pero a
nivel de visualización de Superset, que no pasa por la API.

Estas pruebas importan el módulo sin red (mismo patrón que
`tests/test_sync_resiliencia_bug029.py`) y sustituyen `_request` por un
doble que simula la respuesta real de `/api/v1/chart/data`. Ver también
`tests/test_filtro_ciclo_por_defecto.py` (Marina García, el mecanismo
estático original), que sigue pasando sin modificaciones.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def sync():
    """Importa superset/sync_semantic_layer.py como módulo (sin red en import)."""
    ruta = RAIZ / "superset" / "sync_semantic_layer.py"
    spec = importlib.util.spec_from_file_location("sync_semantic_layer_bug050", ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("sync_semantic_layer_bug050", modulo)
    spec.loader.exec_module(modulo)
    return modulo


def test_default_ultimo_ciclo_resuelve_defaultdatamask(sync, monkeypatch) -> None:
    """Un filtro con `default: ultimo_ciclo` debe traer defaultDataMask con el valor real."""

    def _request_falso(method, path, token=None, body=None, csrf_token=None, **kw):
        assert method == "POST" and path == "/api/v1/chart/data"
        assert body["queries"][0]["orderby"] == [["id_ciclo", False]]
        return {"result": [{"data": [{"id_ciclo": "2024-2025"}]}]}

    monkeypatch.setattr(sync, "_request", _request_falso)

    cfg = {
        "filtros_globales": [
            {"columna": "id_ciclo", "etiqueta": "Ciclo escolar",
             "datasets": ["db07_cubo_completitud"], "default": "ultimo_ciclo"},
        ],
    }
    filtros = sync._filtros_nativos(
        cfg, {"db07_cubo_completitud": "uuid-1"},
        token="t", datasets_by_name={"db07_cubo_completitud": 3},
    )

    assert len(filtros) == 1
    mask = filtros[0].get("defaultDataMask")
    assert mask is not None, "el filtro con default: ultimo_ciclo debe traer defaultDataMask"
    assert mask["filterState"]["value"] == ["2024-2025"]
    assert mask["extraFormData"]["filters"] == [{"col": "id_ciclo", "op": "IN", "val": ["2024-2025"]}]


def test_sin_default_declarado_no_hay_defaultdatamask(sync, monkeypatch) -> None:
    """Guardia de no-regresión: un filtro sin `default:` (ej. Entidad) sigue sin preselección."""

    def _request_falso(method, path, token=None, body=None, csrf_token=None, **kw):
        raise AssertionError("no debería consultarse ningún valor por defecto sin 'default:'")

    monkeypatch.setattr(sync, "_request", _request_falso)

    cfg = {
        "filtros_globales": [
            {"columna": "nombre_entidad", "etiqueta": "Entidad",
             "datasets": ["db07_cubo_completitud"]},
        ],
    }
    filtros = sync._filtros_nativos(
        cfg, {"db07_cubo_completitud": "uuid-1"},
        token="t", datasets_by_name={"db07_cubo_completitud": 3},
    )

    assert filtros[0].get("defaultDataMask") is None


def test_resolucion_no_hardcodea_el_valor(sync, monkeypatch) -> None:
    """El valor debe venir siempre de la consulta real, nunca de un literal en el código."""

    def _request_falso(method, path, token=None, body=None, csrf_token=None, **kw):
        # Simula que el próximo ciclo (2025-2026) ya cargó: el default debe seguirlo.
        return {"result": [{"data": [{"id_ciclo": "2025-2026"}]}]}

    monkeypatch.setattr(sync, "_request", _request_falso)

    cfg = {
        "filtros_globales": [
            {"columna": "id_ciclo", "etiqueta": "Ciclo escolar",
             "datasets": ["db07_cubo_completitud"], "default": "ultimo_ciclo"},
        ],
    }
    filtros = sync._filtros_nativos(
        cfg, {"db07_cubo_completitud": "uuid-1"},
        token="t", datasets_by_name={"db07_cubo_completitud": 3},
    )

    assert filtros[0]["defaultDataMask"]["filterState"]["value"] == ["2025-2026"], (
        "el default debe seguir a los datos reales, no quedarse fijo en un ciclo hardcodeado"
    )


def test_error_al_resolver_no_rompe_el_sync(sync, monkeypatch) -> None:
    """Si la consulta del valor por defecto falla, el filtro se crea igual, sin preselección."""

    def _request_falso(method, path, token=None, body=None, csrf_token=None, **kw):
        raise RuntimeError("HTTP 500: la tabla aún no existe en este ambiente")

    monkeypatch.setattr(sync, "_request", _request_falso)

    cfg = {
        "filtros_globales": [
            {"columna": "id_ciclo", "etiqueta": "Ciclo escolar",
             "datasets": ["db07_cubo_completitud"], "default": "ultimo_ciclo"},
        ],
    }
    filtros = sync._filtros_nativos(
        cfg, {"db07_cubo_completitud": "uuid-1"},
        token="t", datasets_by_name={"db07_cubo_completitud": 3},
    )

    assert len(filtros) == 1, "el filtro debe seguir creándose aunque falle la resolución del default"
    assert filtros[0].get("defaultDataMask") is None


def test_valor_por_defecto_es_respaldo_si_falla_lo_dinamico(sync, monkeypatch) -> None:
    """Si un filtro declara ambas claves y la red falla, cae al respaldo estático de Manuel/Marina."""

    def _request_falso(method, path, token=None, body=None, csrf_token=None, **kw):
        raise RuntimeError("HTTP 500: sin red en este ambiente")

    monkeypatch.setattr(sync, "_request", _request_falso)

    cfg = {
        "filtros_globales": [
            {"columna": "id_ciclo", "etiqueta": "Ciclo escolar",
             "datasets": ["db07_cubo_completitud"],
             "default": "ultimo_ciclo", "valor_por_defecto": "2024-2025"},
        ],
    }
    filtros = sync._filtros_nativos(
        cfg, {"db07_cubo_completitud": "uuid-1"},
        token="t", datasets_by_name={"db07_cubo_completitud": 3},
    )

    assert filtros[0]["defaultDataMask"]["filterState"]["value"] == ["2024-2025"], (
        "sin resolución dinámica disponible, debe respaldarse en valor_por_defecto, no quedar sin default"
    )


def test_lo_dinamico_gana_sobre_el_respaldo_estatico(sync, monkeypatch) -> None:
    """Si un filtro declara ambas claves y la red funciona, gana el valor dinámico, no el fijo."""

    def _request_falso(method, path, token=None, body=None, csrf_token=None, **kw):
        return {"result": [{"data": [{"id_ciclo": "2025-2026"}]}]}

    monkeypatch.setattr(sync, "_request", _request_falso)

    cfg = {
        "filtros_globales": [
            {"columna": "id_ciclo", "etiqueta": "Ciclo escolar",
             "datasets": ["db07_cubo_completitud"],
             "default": "ultimo_ciclo", "valor_por_defecto": "2024-2025"},
        ],
    }
    filtros = sync._filtros_nativos(
        cfg, {"db07_cubo_completitud": "uuid-1"},
        token="t", datasets_by_name={"db07_cubo_completitud": 3},
    )

    assert filtros[0]["defaultDataMask"]["filterState"]["value"] == ["2025-2026"], (
        "con resolución dinámica disponible, debe ganar sobre el valor_por_defecto fijo"
    )


def test_firma_compatible_con_las_pruebas_de_marina(sync, monkeypatch) -> None:
    """La firma (cfg, datasets_uuids) sigue funcionando sin token/datasets_by_name.

    Mismo patrón de llamada que `tests/test_filtro_ciclo_por_defecto.py` — no debe
    romperse por los parámetros nuevos, que son opcionales y van al final.
    """

    def _request_falso(method, path, token=None, body=None, csrf_token=None, **kw):
        raise AssertionError("sin token/datasets_by_name no debería intentarse resolución dinámica")

    monkeypatch.setattr(sync, "_request", _request_falso)

    cfg = {
        "filtros_globales": [
            {"columna": "id_ciclo", "datasets": ["ds"], "valor_por_defecto": "2024-2025"},
        ]
    }
    filtros = sync._filtros_nativos(cfg, {"ds": "uuid-1"})

    assert filtros[0]["defaultDataMask"]["filterState"]["value"] == ["2024-2025"]


@pytest.mark.parametrize("ruta_yaml", sorted((RAIZ / "superset" / "dashboards").glob("*.yaml")))
def test_todo_filtro_de_ciclo_declara_default_dinamico(ruta_yaml: Path) -> None:
    """Guardia de no-regresión: ningún filtro `id_ciclo` debe volver a nacer sin `default:`.

    DB-10 es la única excepción legítima (monitoreo de pipeline, sin dimensión de ciclo).
    """
    cfg = yaml.safe_load(ruta_yaml.read_text(encoding="utf-8"))
    filtros = cfg.get("filtros_globales", [])
    for f in filtros:
        if f.get("columna") == "id_ciclo":
            assert f.get("default") == "ultimo_ciclo", (
                f"{ruta_yaml.name}: el filtro de id_ciclo debe declarar "
                f"'default: ultimo_ciclo' (BUG-047) para no triplicar los totales"
            )
