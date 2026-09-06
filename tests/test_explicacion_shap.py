"""Pruebas de contrato de `GET /predicciones/{cct}/explicacion` (US-412 / REQ-004).

La ruta **no tenía ninguna prueba**: ni de forma, ni de acceso, ni de 404. Se descubrió al revisar
la petición de C3 de conectar las contribuciones SHAP reales (2026-09-05).

Dos cosas se fijan aquí, y las dos son afirmaciones sobre lo que el sistema hace **hoy**:

1. **La forma de la respuesta**, para que el día que C3 persista SHAP en Gold el cambio sea del
   cuerpo del endpoint y no del contrato que ya consumen el frontend y el agente.
2. **El acceso real: `require_lectura`, no `analista`.** El docstring del módulo prometía "solo
   analista" desde antes de que US-403 cerrara y nunca fue cierto -- el router se monta con
   `require_lectura` en `v1/__init__.py`. Estas pruebas dejan la promesa y el código atados: si
   alguien decide de verdad restringir la explicación a analista, `test_como_ciudadano_da_200`
   reprueba y obliga a actualizar el contrato en vez de que la diferencia se descubra en la demo.

Todo offline: `explicacion` corre sobre `mock_data`, sin base de datos.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.api import mock_data
from src.api.app import API_PREFIX, app
from src.api.config import Settings, get_settings
from src.api.schemas import Rol
from src.api.security import jwt as jwtmod

DRIVERS = ("D1", "D2", "D3", "D4", "D5", "D6")


def _ruta(cct: str) -> str:
    return f"{API_PREFIX}/predicciones/{cct}/explicacion"


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def escuela() -> dict:
    return mock_data.ESCUELAS[0]


@pytest.fixture
def lectura_protegida() -> Iterator[None]:
    """Apaga `AUTH_LECTURA_PUBLICA` por override, sin contaminar otras pruebas."""
    app.dependency_overrides[get_settings] = lambda: Settings(auth_lectura_publica=False)
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_settings, None)


# --------------------------------------------------------------------------- #
# Forma de la respuesta
# --------------------------------------------------------------------------- #


def test_responde_la_forma_del_contrato(client: TestClient, escuela: dict) -> None:
    r = client.get(_ruta(escuela["cct"]))
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"cct", "driver_dominante", "contribuciones"}
    assert cuerpo["cct"] == escuela["cct"]
    assert cuerpo["driver_dominante"] == escuela["driver_dominante"]


def test_contribuciones_trae_los_seis_drivers(client: TestClient, escuela: dict) -> None:
    """Los seis drivers del proyecto, siempre presentes. Nunca un subconjunto silencioso."""
    contribuciones = client.get(_ruta(escuela["cct"])).json()["contribuciones"]
    assert tuple(contribuciones) == DRIVERS
    assert all(isinstance(v, float) for v in contribuciones.values())


def test_cct_inexistente_da_404_estructurado(client: TestClient) -> None:
    r = client.get(_ruta("00XXXX0000Z"))
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


def test_cct_con_forma_rara_no_revienta(client: TestClient) -> None:
    """Un CCT inválido es 404, nunca un 500: `_buscar_escuela` no interpreta el texto."""
    for cct in ("../../etc/passwd", "'; DROP TABLE gold.predicciones; --", "x" * 300):
        assert client.get(_ruta(cct)).status_code in (404, 422)


# --------------------------------------------------------------------------- #
# Acceso real: `require_lectura`, NO `analista`
# --------------------------------------------------------------------------- #


def test_lectura_publica_no_exige_token(client: TestClient, escuela: dict) -> None:
    assert client.get(_ruta(escuela["cct"])).status_code == 200


def test_con_lectura_protegida_sin_token_da_401(
    client: TestClient, escuela: dict, lectura_protegida: None
) -> None:
    r = client.get(_ruta(escuela["cct"]))
    assert r.status_code == 401
    assert r.json()["error"] == "unauthorized"


def test_como_ciudadano_da_200(
    client: TestClient, escuela: dict, lectura_protegida: None
) -> None:
    """**La explicación NO es solo de analista.** Si algún día lo fuera, esta prueba reprueba."""
    token = jwtmod.create_access_token(sub="c1", role=Rol.ciudadano, email="ciu@faro.mx")
    r = client.get(_ruta(escuela["cct"]), headers=_auth(token))
    assert r.status_code == 200


def test_como_analista_da_200(
    client: TestClient, escuela: dict, lectura_protegida: None
) -> None:
    token = jwtmod.create_access_token(sub="a1", role=Rol.analista, email="ana@faro.mx")
    assert client.get(_ruta(escuela["cct"]), headers=_auth(token)).status_code == 200
