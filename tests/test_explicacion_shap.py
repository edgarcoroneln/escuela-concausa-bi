"""Contrato de `GET /predicciones/{cct}/explicacion` — contribuciones SHAP reales (BUG-053).

La ruta **no tenía ninguna prueba** hasta el 2026-09-05, y arrastraba dos defectos distintos que se
descubrieron uno detrás del otro:

- **BUG-055** (`fixed`): el contrato era `dict[str, float]` y el código hacía `or 0.0`, así que un
  hueco salía como cero — una afirmación falsa sobre la causa del riesgo.
- **BUG-053** (este archivo): las contribuciones venían de `mock_data`, no de ningún modelo. Desde
  que ML-02 persiste `shap_d1..shap_d6` en `gold.recomendaciones` (`publicar_gold.py`, C3) hay
  fuente real, y el endpoint la lee vía `RepositorioModelos`.

Lo que se fija aquí:

1. **Las contribuciones vienen del repositorio**, no de datos fabricados en el router.
2. **`null` sobrevive el viaje entero.** Es la regresión que más importa: es barato "arreglar" un
   `None` colapsándolo a `0.0` y reintroducir BUG-055 con datos reales, que es peor que con el mock.
3. **`0.0` medido y `null` se distinguen** — si se confunden, un driver irrelevante y uno que nunca
   se evaluó se vuelven indistinguibles.
4. **El acceso real es `require_lectura`, no `analista`** (ver el docstring de `v1/predicciones.py`).

Todo offline: `RepositorioModelosFake` en memoria, sin Postgres.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.api.app import API_PREFIX, app
from src.api.config import Settings, get_settings
from src.api.repositorio_modelos import get_repositorio_modelos
from src.api.schemas import Rol
from src.api.security import jwt as jwtmod
from tests.fixtures_modelos import (
    PREDICCIONES_FAKE,
    RepositorioModelosFake,
    RepositorioModelosNoDisponibleFake,
)

DRIVERS = ("D1", "D2", "D3", "D4", "D5", "D6")
# Escuela con las seis contribuciones calculadas.
COMPLETA = PREDICCIONES_FAKE[0]
# Escuela con D5/D6 en SIN_DATO — los dos drivers de cobertura parcial del proyecto.
CON_HUECOS = PREDICCIONES_FAKE[1]

CCT_INVENTADO = "00XXXX0000Z"
INYECCION_SQL = "'; DROP TABLE gold.recomendaciones; --"


def _ruta(cct: str) -> str:
    return f"{API_PREFIX}/predicciones/{cct}/explicacion"


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosFake
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def lectura_protegida() -> Iterator[None]:
    app.dependency_overrides[get_settings] = lambda: Settings(auth_lectura_publica=False)
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_settings, None)


# --------------------------------------------------------------------------- #
# Las contribuciones salen de Gold, no de mock_data (BUG-053)
# --------------------------------------------------------------------------- #


def test_las_contribuciones_vienen_del_repositorio(client: TestClient) -> None:
    cuerpo = client.get(_ruta(COMPLETA["cct"])).json()
    assert cuerpo["cct"] == COMPLETA["cct"]
    assert cuerpo["driver_dominante"] == COMPLETA["driver_dominante"]
    assert cuerpo["contribuciones"] == {f"D{i}": COMPLETA[f"shap_d{i}"] for i in range(1, 7)}


def test_las_seis_claves_siempre_presentes(client: TestClient) -> None:
    """El hueco se declara, no se omite: seis claves aunque algunas sean `null`."""
    for cct in (COMPLETA["cct"], CON_HUECOS["cct"]):
        assert tuple(client.get(_ruta(cct)).json()["contribuciones"]) == DRIVERS


def test_el_driver_dominante_es_el_de_la_misma_fila(client: TestClient) -> None:
    """Explicación y predicción salen de la MISMA fila: no se pueden desincronizar."""
    expl = client.get(_ruta(CON_HUECOS["cct"])).json()
    pred = client.get(f"{API_PREFIX}/predicciones/{CON_HUECOS['cct']}").json()
    assert expl["driver_dominante"] == pred["driver_dominante"]


# --------------------------------------------------------------------------- #
# SIN_DATO sobrevive el viaje (regresión de BUG-055 con datos reales)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("driver", ["D5", "D6"])
def test_una_contribucion_sin_dato_viaja_como_null(client: TestClient, driver: str) -> None:
    """`null`, nunca `0.0`. Un cero ahí afirmaría que ese driver no contribuyó al riesgo."""
    contribuciones = client.get(_ruta(CON_HUECOS["cct"])).json()["contribuciones"]
    assert contribuciones[driver] is None


def test_un_cero_medido_no_se_confunde_con_un_hueco(client: TestClient) -> None:
    """`D5` vale `0.0` en una escuela y `null` en la otra: tienen que llegar distintos."""
    con_cero = client.get(_ruta(COMPLETA["cct"])).json()["contribuciones"]["D5"]
    con_hueco = client.get(_ruta(CON_HUECOS["cct"])).json()["contribuciones"]["D5"]
    assert con_cero == 0.0
    assert con_hueco is None


def test_las_contribuciones_negativas_no_se_pierden(client: TestClient) -> None:
    """SHAP tiene signo: un driver puede empujar el riesgo hacia abajo."""
    contribuciones = client.get(_ruta(COMPLETA["cct"])).json()["contribuciones"]
    assert contribuciones["D3"] < 0


# --------------------------------------------------------------------------- #
# Errores: nunca una explicación inventada
# --------------------------------------------------------------------------- #


def test_cct_sin_fila_da_404_estructurado(client: TestClient) -> None:
    r = client.get(_ruta(CCT_INVENTADO))
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


def test_ciclo_sin_fila_da_404(client: TestClient) -> None:
    """El `ciclo` es un parámetro real: pedir uno que no existe es 404, no la fila de otro ciclo."""
    r = client.get(_ruta(COMPLETA["cct"]), params={"ciclo": "1999-2000"})
    assert r.status_code == 404


def test_gold_caido_da_503_no_500(client: TestClient) -> None:
    """Mismo trato que `/predicciones/{cct}` (US-416): 503, nunca un 500 ni un valor inventado."""
    app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosNoDisponibleFake
    r = client.get(_ruta(COMPLETA["cct"]))
    assert r.status_code == 503
    assert r.json()["error"] == "service_unavailable"


def test_cct_con_forma_rara_no_revienta(client: TestClient) -> None:
    for cct in ("../../etc/passwd", INYECCION_SQL, "x" * 300):
        assert client.get(_ruta(cct)).status_code in (404, 422)


# --------------------------------------------------------------------------- #
# Acceso real: `require_lectura`, NO `analista`
# --------------------------------------------------------------------------- #


def test_lectura_publica_no_exige_token(client: TestClient) -> None:
    assert client.get(_ruta(COMPLETA["cct"])).status_code == 200


def test_con_lectura_protegida_sin_token_da_401(
    client: TestClient, lectura_protegida: None
) -> None:
    r = client.get(_ruta(COMPLETA["cct"]))
    assert r.status_code == 401
    assert r.json()["error"] == "unauthorized"


def test_como_ciudadano_da_200(client: TestClient, lectura_protegida: None) -> None:
    """**La explicación NO es solo de analista.** Si algún día lo fuera, esta prueba reprueba."""
    token = jwtmod.create_access_token(sub="c1", role=Rol.ciudadano, email="ciu@faro.mx")
    assert client.get(_ruta(COMPLETA["cct"]), headers=_auth(token)).status_code == 200


def test_como_analista_da_200(client: TestClient, lectura_protegida: None) -> None:
    token = jwtmod.create_access_token(sub="a1", role=Rol.analista, email="ana@faro.mx")
    assert client.get(_ruta(COMPLETA["cct"]), headers=_auth(token)).status_code == 200
