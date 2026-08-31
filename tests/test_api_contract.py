"""Pruebas del contrato de la API v1 (US-401).

Verifican que el stub cumple `03_Architecture/API_Specification.md`: rutas presentes, códigos
correctos (200/302/404/422), formas de respuesta (`Page`, `ErrorOut`) y que el OpenAPI publicado
en `api/openapi.v1.json` está sincronizado con el código.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scripts.export_openapi import SALIDA
from src.api.app import API_PREFIX, app
from src.api.orquestador import get_orquestador
from src.api.repositorio_gold import get_repositorio_gold
from src.api.repositorio_metricas import get_repositorio_metricas
from src.api.repositorio_modelos import get_repositorio_modelos
from tests.fixtures_admin import OrquestadorFake
from tests.fixtures_gold import RepositorioGoldFake
from tests.fixtures_metricas import RepositorioMetricasFake
from tests.fixtures_modelos import RepositorioModelosFake

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Suite rápida del contrato: corre sin Postgres ni Airflow.

    `/escuelas`, `/municipios` y `/kpis` dependen de `RepositorioGold` (`Depends`), y
    `/predicciones/*` de `RepositorioModelos` (`Depends`, US-412), así que aquí se sustituyen por
    sus fakes en memoria (`tests/fixtures_gold.py`, `tests/fixtures_modelos.py`) en vez de
    conectar a una base real -- patrón acordado con Christian Ruiz (Tech Lead C4) el 2026-08-20
    para la Decisión 2 de US-411, extendido a US-412 el 2026-08-26 y a `/admin/pipeline/run`
    (`Orquestador`, US-413) el 2026-08-27. Las pruebas de integración contra Postgres/Airflow
    reales viven en US-422 (Eloisa González Rubio), nunca aquí.
    """
    app.dependency_overrides[get_repositorio_gold] = RepositorioGoldFake
    app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosFake
    app.dependency_overrides[get_orquestador] = OrquestadorFake
    app.dependency_overrides[get_repositorio_metricas] = RepositorioMetricasFake
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


# --------------------------------------------------------------------------- #
# Salud / versión
# --------------------------------------------------------------------------- #


def test_health_ok(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version_ok(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/version")
    assert r.status_code == 200
    assert r.json()["api"] == "v1"


# --------------------------------------------------------------------------- #
# Lectura sobre Gold
# --------------------------------------------------------------------------- #


def test_escuelas_devuelve_page(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas")
    assert r.status_code == 200
    cuerpo = r.json()
    assert {"items", "total", "page", "size"} <= cuerpo.keys()
    assert cuerpo["total"] == len(cuerpo["items"]) >= 1
    escuela = cuerpo["items"][0]
    assert len(escuela["cct"]) == 10
    assert len(escuela["cve_mun"]) == 5
    assert 0 <= escuela["indice_riesgo"] <= 1


def test_escuelas_filtro_por_entidad(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"cve_ent": "09"})
    assert r.status_code == 200
    assert all(e["cve_mun"].startswith("09") for e in r.json()["items"])


def test_escuela_detalle_incluye_drivers(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas/09DPR0001A")
    assert r.status_code == 200
    cuerpo = r.json()
    assert {"d1", "d2", "d3", "d4", "d5", "d6"} <= cuerpo.keys()
    assert 0 <= cuerpo["indice_completitud_drivers"] <= 1


def test_escuela_inexistente_404_con_forma_error(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas/00XXXX0000Z")
    assert r.status_code == 404
    cuerpo = r.json()
    assert cuerpo["error"] == "not_found"
    assert {"error", "message", "request_id"} == cuerpo.keys()
    # No se filtra detalle interno ni el CCT crudo.
    assert "Traceback" not in cuerpo["message"]


def test_municipio_ok_y_404(client: TestClient) -> None:
    # 09010 existe en tests/fixtures_gold.py::MUNICIPIOS_FAKE (no es una coincidencia con datos
    # reales de Postgres -- el override del repositorio hace que esta prueba no dependa de la BD).
    assert client.get(f"{API_PREFIX}/municipios/09010").status_code == 200
    assert client.get(f"{API_PREFIX}/municipios/00000").status_code == 404


def test_kpis_ok(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/kpis")
    assert r.status_code == 200
    assert r.json()["escuelas_en_riesgo"] >= 0


# --------------------------------------------------------------------------- #
# Ordenamiento (Decisión 3 de US-411)
# --------------------------------------------------------------------------- #


def test_escuelas_order_by_matricula_desc(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"order_by": "matricula_total", "order": "desc"})
    assert r.status_code == 200
    matriculas = [e["matricula_total"] for e in r.json()["items"]]
    assert matriculas == sorted(matriculas, reverse=True)


def test_escuelas_order_by_indice_riesgo_sin_dato_al_final(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"order_by": "indice_riesgo", "order": "asc"})
    assert r.status_code == 200
    riesgos = [e["indice_riesgo"] for e in r.json()["items"]]
    con_valor = [v for v in riesgos if v is not None]
    assert con_valor == sorted(con_valor)
    assert all(v is None for v in riesgos[len(con_valor) :])


def test_escuelas_order_by_invalido_422(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"order_by": "no_existe"})
    assert r.status_code == 422


def test_municipios_order_by_poblacion_desc(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/municipios", params={"order_by": "poblacion", "order": "desc"})
    assert r.status_code == 200
    poblaciones = [m["poblacion"] for m in r.json()["items"]]
    assert poblaciones == sorted(poblaciones, reverse=True)


def test_municipios_order_by_invalido_422(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/municipios", params={"order_by": "no_existe"})
    assert r.status_code == 422


# --------------------------------------------------------------------------- #
# Predicciones
# --------------------------------------------------------------------------- #


def test_prediccion_combina_ml(client: TestClient) -> None:
    """Lee `RepositorioModelosFake` (US-412, cierra BUG-010) -- ya no `mock_data`."""
    r = client.get(f"{API_PREFIX}/predicciones/09DPR0001A")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["driver_dominante"].startswith("D")
    assert cuerpo["recomendacion"]  # ML-02 prescriptivo, no vacío
    # ML-03 sin productor todavía (BUG-010, US-321): None, nunca un entero inventado.
    assert cuerpo["cluster"] is None


def test_prediccion_cct_sin_fila_404(client: TestClient) -> None:
    """Un CCT sin fila en `gold.predicciones` es 404, no un valor fabricado."""
    r = client.get(f"{API_PREFIX}/predicciones/00XXXX0000Z")
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


def test_prediccion_batch(client: TestClient) -> None:
    r = client.post(
        f"{API_PREFIX}/predicciones/batch",
        json={"ccts": ["09DPR0001A", "19DES0007C"], "id_ciclo": "2024-2025"},
    )
    assert r.status_code == 200
    assert r.json()["total"] == 2


def test_prediccion_batch_omite_ccts_sin_fila(client: TestClient) -> None:
    """Un CCT sin predicción se omite del resultado -- nunca se inventa una fila para él."""
    r = client.post(
        f"{API_PREFIX}/predicciones/batch",
        json={"ccts": ["09DPR0001A", "00XXXX0000Z"], "id_ciclo": "2024-2025"},
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 1
    assert cuerpo["items"][0]["cct"] == "09DPR0001A"


def test_prediccion_batch_valida_entrada_422(client: TestClient) -> None:
    r = client.post(f"{API_PREFIX}/predicciones/batch", json={"ccts": [], "id_ciclo": "x"})
    assert r.status_code == 422
    assert r.json()["error"] == "validation_error"


# --------------------------------------------------------------------------- #
# Agente
# --------------------------------------------------------------------------- #


def test_agente_responde(client: TestClient) -> None:
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": "¿Cuántas escuelas en riesgo?"})
    assert r.status_code == 200
    assert r.json()["fuera_de_alcance"] is False


def test_agente_rechaza_escritura(client: TestClient) -> None:
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": "DROP table escuelas"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["fuera_de_alcance"] is True
    assert cuerpo["sql_generado"] is None


# --------------------------------------------------------------------------- #
# Auth (stub) y admin
# --------------------------------------------------------------------------- #


def test_auth_login_redirige(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/auth/login", follow_redirects=False)
    assert r.status_code == 302


def test_auth_me_requiere_token(client: TestClient) -> None:
    # Desde US-402 /auth/me exige access token: sin él responde 401 (no 200).
    assert client.get(f"{API_PREFIX}/auth/me").status_code == 401
    from src.api.schemas import Rol
    from src.api.security.jwt import create_access_token

    token = create_access_token(sub="u1", role=Rol.ciudadano, email="a@b.mx")
    r = client.get(f"{API_PREFIX}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["role"] in ("ciudadano", "analista")


def _token_analista() -> str:
    from src.api.schemas import Rol
    from src.api.security.jwt import create_access_token

    return create_access_token(sub="a1", role=Rol.analista, email="ana@faro.mx")


def test_admin_pipeline_run_202(client: TestClient) -> None:
    # Desde US-403 /admin/* exige rol `analista`. La matriz completa (401/403) vive en test_rbac.py.
    r = client.post(
        f"{API_PREFIX}/admin/pipeline/run",
        json={"dag": "dag_diario", "ciclo": "2024-2025"},
        headers={"Authorization": f"Bearer {_token_analista()}"},
    )
    assert r.status_code == 202
    assert r.json()["estado"] == "accepted"
    assert r.json()["run_id"]  # viene de Orquestador, no un string fabricado en el endpoint


def test_admin_metrics_frescura_real_y_sin_dato_explicito(client: TestClient) -> None:
    """`/admin/metrics` lee `RepositorioMetricas` (US-413): frescura real por fuente, y
    `suites_ge_en_verde` en `None` (SIN_DATO, no hay checkpoints de GE persistidos)."""
    r = client.get(f"{API_PREFIX}/admin/metrics", headers={"Authorization": f"Bearer {_token_analista()}"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert "DS-05_SINAICA" in cuerpo["frescura_por_fuente"]
    # DS-06 nunca se ingirió en el fake -- no aparece, no se inventa una fecha.
    assert "DS-06_CONAGUA_SINA" not in cuerpo["frescura_por_fuente"]
    assert cuerpo["suites_ge_en_verde"] is None


def test_admin_pipeline_run_dag_invalido_422(client: TestClient) -> None:
    """Un `dag` que no existe en `dags/` se rechaza antes de tocar el orquestador (US-413)."""
    r = client.post(
        f"{API_PREFIX}/admin/pipeline/run",
        json={"dag": "no_existe", "ciclo": "2024-2025"},
        headers={"Authorization": f"Bearer {_token_analista()}"},
    )
    assert r.status_code == 422


# --------------------------------------------------------------------------- #
# OpenAPI publicado sincronizado con el código
# --------------------------------------------------------------------------- #


def test_openapi_publicado_existe_y_sincronizado(client: TestClient) -> None:
    """El JSON publicado debe estar estructuralmente sincronizado con el código.

    Se compara la **estructura** (rutas + métodos + nombres de modelos), no el JSON completo:
    así el test detecta "olvidé regenerar tras cambiar el contrato" sin volverse frágil ante
    diferencias menores del OpenAPI entre versiones de FastAPI (requirements usa pisos, no pines).
    """
    assert SALIDA.exists(), "Falta api/openapi.v1.json. Corre: python scripts/export_openapi.py"
    en_disco = json.loads(SALIDA.read_text(encoding="utf-8"))
    en_vivo = app.openapi()

    def rutas_y_metodos(spec: dict) -> set[str]:
        return {
            f"{metodo.upper()} {ruta}"
            for ruta, ops in spec.get("paths", {}).items()
            for metodo in ops
        }

    def modelos(spec: dict) -> set[str]:
        return set(spec.get("components", {}).get("schemas", {}).keys())

    assert rutas_y_metodos(en_disco) == rutas_y_metodos(en_vivo), (
        "Rutas del OpenAPI publicado desincronizadas. Regenéralo: python scripts/export_openapi.py"
    )
    assert modelos(en_disco) == modelos(en_vivo), (
        "Modelos del OpenAPI publicado desincronizados. Regenéralo: python scripts/export_openapi.py"
    )


def test_openapi_declara_todas_las_rutas(client: TestClient) -> None:
    paths = app.openapi()["paths"].keys()
    esperadas = [
        f"{API_PREFIX}/health",
        f"{API_PREFIX}/version",
        f"{API_PREFIX}/auth/login",
        f"{API_PREFIX}/escuelas",
        f"{API_PREFIX}/escuelas/{{cct}}",
        f"{API_PREFIX}/municipios",
        f"{API_PREFIX}/kpis",
        f"{API_PREFIX}/predicciones/{{cct}}",
        f"{API_PREFIX}/predicciones/batch",
        f"{API_PREFIX}/agente/consulta",
        f"{API_PREFIX}/admin/pipeline/run",
        f"{API_PREFIX}/admin/metrics",
    ]
    for ruta in esperadas:
        assert ruta in paths, f"Falta la ruta {ruta} en el OpenAPI"
