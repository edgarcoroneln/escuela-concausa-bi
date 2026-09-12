"""Pruebas del contrato de la API v1 (US-401).

Verifican que el stub cumple `vault/03_Architecture/API_Specification.md`: rutas presentes, códigos
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
from src.api.repositorio_gold import get_repositorio_gold
from src.api.repositorio_modelos import get_repositorio_modelos
from tests.fixtures_gold import RepositorioGoldFake
from tests.fixtures_modelos import (
    RepositorioModelosFake,
    RepositorioModelosNoDisponibleFake,
)

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Suite rápida del contrato: corre sin Postgres.

    `/escuelas`, `/municipios` y `/kpis` dependen de `RepositorioGold` (`Depends`), y
    `/predicciones/*` de `RepositorioModelos` (`Depends`, US-412), así que aquí se sustituyen por
    sus fakes en memoria (`tests/fixtures_gold.py`, `tests/fixtures_modelos.py`) en vez de
    conectar a una base real -- patrón acordado con Christian Ruiz (Tech Lead C4) el 2026-08-20
    para la Decisión 2 de US-411, extendido a US-412 el 2026-08-26. Las pruebas de integración
    contra Postgres real viven en US-422 (Eloisa González Rubio), nunca aquí.
    """
    app.dependency_overrides[get_repositorio_gold] = RepositorioGoldFake
    app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosFake
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


def test_version_refleja_git_commit(client: TestClient, monkeypatch) -> None:
    """/version reporta el commit sellado en la imagen (ENV GIT_COMMIT), no un valor fijo."""
    monkeypatch.setenv("GIT_COMMIT", "abc1234sha")
    r = client.get(f"{API_PREFIX}/version")
    assert r.status_code == 200
    assert r.json()["commit"] == "abc1234sha"


def test_version_default_dev_sin_sellar(client: TestClient, monkeypatch) -> None:
    """Sin GIT_COMMIT (imagen no sellada / build local), el commit cae a 'dev'."""
    monkeypatch.delenv("GIT_COMMIT", raising=False)
    r = client.get(f"{API_PREFIX}/version")
    assert r.status_code == 200
    assert r.json()["commit"] == "dev"


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


def test_escuelas_sin_ciclo_no_duplica_entre_ciclos(client: TestClient) -> None:
    """BUG-044: sin `ciclo`, antes se sumaban todos los ciclos de golpe. `RepositorioGoldFake`
    trae la misma escuela (09DPR0001A) en 2024-2025 y en 2023-2024 -- debe aparecer una sola vez,
    con los datos del ciclo más reciente."""
    r = client.get(f"{API_PREFIX}/escuelas")
    assert r.status_code == 200
    cuerpo = r.json()
    ccts = [e["cct"] for e in cuerpo["items"]]
    assert ccts.count("09DPR0001A") == 1
    escuela = next(e for e in cuerpo["items"] if e["cct"] == "09DPR0001A")
    assert escuela["matricula_total"] == 480  # valor del ciclo 2024-2025, no el de 2023-2024 (500)


def test_escuelas_ciclo_explicito_trae_el_ciclo_pedido(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"ciclo": "2023-2024"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 1
    assert cuerpo["items"][0]["cct"] == "09DPR0001A"
    assert cuerpo["items"][0]["matricula_total"] == 500


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


def test_escuelas_listado_trae_coordenadas(client: TestClient) -> None:
    """US-621: el mapa del front pinta N escuelas con UNA llamada, no N llamadas al detalle.

    `None` es SIN_DATO real (hay CCT sin georreferencia), así que se comprueba que la clave exista
    siempre -- el hueco se declara, no se omite -- y que al menos una escuela traiga coordenada.
    """
    items = client.get(f"{API_PREFIX}/escuelas").json()["items"]
    assert items
    assert all("latitud" in e and "longitud" in e for e in items)
    assert any(e["latitud"] is not None for e in items)

    # El detalle sigue trayéndolas (las hereda de EscuelaOut): no se movieron, se subieron.
    detalle = client.get(f"{API_PREFIX}/escuelas/09DPR0001A").json()
    assert "latitud" in detalle and "longitud" in detalle


def test_municipio_trae_la_entidad_y_su_clave(client: TestClient) -> None:
    """US-621: el front pinta "Álvaro Obregón, Ciudad de México" sin mantener su propio mapa.

    Las dos claves viajan **en la lista y en el detalle**: si solo estuvieran en el detalle, pintar
    la entidad de una tabla costaría una petición por fila.
    """
    detalle = client.get(f"{API_PREFIX}/municipios/09010").json()
    assert detalle["cve_ent"] == "09"
    assert detalle["nombre_entidad"] == "Ciudad de México"

    lista = client.get(f"{API_PREFIX}/municipios", params={"cve_ent": "19"}).json()["items"]
    assert lista, "el fixture tiene un municipio de Nuevo León"
    assert {m["nombre_entidad"] for m in lista} == {"Nuevo León"}
    assert {m["cve_ent"] for m in lista} == {"19"}


def test_kpis_ok(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/kpis")
    assert r.status_code == 200
    assert r.json()["escuelas_en_riesgo"] >= 0


def test_kpis_sin_ciclo_no_suma_ciclos_anteriores(client: TestClient) -> None:
    """BUG-044: `matricula_total` de /kpis debe reflejar solo el ciclo más reciente. Si sumara
    también la fila 2023-2024 de 09DPR0001A (matricula_total=500), el total subiría 500 de más."""
    sin_ciclo = client.get(f"{API_PREFIX}/kpis").json()["matricula_total"]
    con_ciclo = client.get(f"{API_PREFIX}/kpis", params={"ciclo": "2024-2025"}).json()["matricula_total"]
    assert sin_ciclo == con_ciclo


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
    # `prioridad` de gold.recomendaciones (E3, 2026-09-11): la urgencia con la que el storytelling
    # ordena los casos. Sale del ANCLA (0.60), no de la línea de alerta de /kpis (0.50) -- ver el
    # docstring de PrediccionOut y `publicar_gold.prioridad_de_riesgo`.
    assert cuerpo["prioridad"] == "alta"  # indice_riesgo 0.72 en el fixture


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


def test_prediccion_timeout_postgres_503(client: TestClient) -> None:
    """Si Postgres no responde a tiempo (US-416), 503 uniforme -- nunca un valor inventado."""
    app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosNoDisponibleFake
    try:
        r = client.get(f"{API_PREFIX}/predicciones/09DPR0001A")
    finally:
        app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosFake
    assert r.status_code == 503
    cuerpo = r.json()
    assert cuerpo["error"] == "service_unavailable"
    assert cuerpo["request_id"]


def test_prediccion_batch_timeout_postgres_503(client: TestClient) -> None:
    app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosNoDisponibleFake
    try:
        r = client.post(
            f"{API_PREFIX}/predicciones/batch",
            json={"ccts": ["09DPR0001A"], "id_ciclo": "2024-2025"},
        )
    finally:
        app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosFake
    assert r.status_code == 503
    assert r.json()["error"] == "service_unavailable"


# --------------------------------------------------------------------------- #
# Agente
# --------------------------------------------------------------------------- #


def test_agente_responde(client: TestClient) -> None:
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": "¿Cuántas escuelas en riesgo?"})
    assert r.status_code == 200
    assert r.json()["fuera_de_alcance"] is False


def test_agente_rechaza_escritura(client: TestClient) -> None:
    # BUG-025: el endpoint ya usa los guardarraíles reales. La protección contra escritura vive en
    # la capa SQL (preparar_sql_seguro), no en el filtro de lenguaje natural: aunque el LLM generara
    # un DROP, se rechaza y el ejecutor jamás se llama. La matriz completa vive en
    # tests/test_agente_endpoint.py.
    from src.api.v1 import agente as agente_mod

    ejecutado: list[str] = []
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.escuelas(cct)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: "DROP TABLE gold.escuelas"
    )
    app.dependency_overrides[agente_mod.get_ejecutar_sql] = lambda: (
        lambda sql: ejecutado.append(sql) or []
    )
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": "borra las escuelas"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["fuera_de_alcance"] is True
    assert cuerpo["sql_generado"] is None
    assert ejecutado == []


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


def test_admin_pipeline_run_202(client: TestClient) -> None:
    # Desde US-403 /admin/* exige rol `analista`. La matriz completa (401/403) vive en test_rbac.py.
    from src.api.schemas import Rol
    from src.api.security.jwt import create_access_token

    token = create_access_token(sub="a1", role=Rol.analista, email="ana@faro.mx")
    r = client.post(
        f"{API_PREFIX}/admin/pipeline/run",
        json={"dag": "bronze", "ciclo": "2024-2025"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 202
    assert r.json()["estado"] == "accepted"


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
