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
    """Las seis claves siempre presentes. Nunca un subconjunto silencioso."""
    contribuciones = client.get(_ruta(escuela["cct"])).json()["contribuciones"]
    assert tuple(contribuciones) == DRIVERS
    assert all(v is None or isinstance(v, float) for v in contribuciones.values())


# --------------------------------------------------------------------------- #
# SIN_DATO: el hueco se dice, no se rellena
# --------------------------------------------------------------------------- #


def _cct_con_driver_vacio(driver: str) -> str:
    """CCT de `mock_data` cuyo driver `dN` viene sin dato, o `skip` si ya no existe ninguno."""
    clave = driver.lower()
    for e in mock_data.ESCUELAS:
        if e.get(clave) is None:
            return e["cct"]
    pytest.skip(f"mock_data ya no tiene ninguna escuela con {driver} vacio")


@pytest.mark.parametrize("driver", ["D5", "D6"])
def test_un_driver_sin_dato_viaja_como_none_no_como_cero(
    client: TestClient, driver: str
) -> None:
    """Regresión: la ruta devolvía `0.0` donde `mock_data` dice `None`.

    D5 (estrés hídrico) es regional y D6 (aire) cubre ~80 zonas urbanas: el hueco es el caso
    **normal**, no la excepción, y `mock_data` ya lo modelaba con `None`. El `or 0.0` que había en
    el endpoint lo borraba y afirmaba "este driver contribuyó cero" -- falso, y contradictorio con
    la regla de cobertura parcial del proyecto y con `indice_completitud_drivers`, que sí marcan
    `SIN_DATO`.

    Con SHAP real la distinción pesa más todavía: "no influyó" y "no lo sabemos" son respuestas
    distintas a la pregunta de por qué una escuela está en riesgo.
    """
    cct = _cct_con_driver_vacio(driver)
    contribuciones = client.get(_ruta(cct)).json()["contribuciones"]

    assert driver in contribuciones  # la clave está: el hueco se declara, no se omite
    assert contribuciones[driver] is None


def test_un_cero_legitimo_no_se_confunde_con_un_hueco(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`0.0` y `None` son valores distintos y deben llegar distintos.

    El `or 0.0` anterior los colapsaba en el mismo número: una contribución medida como cero y una
    no medida salían idénticas. Con SHAP real eso hace indistinguible un driver irrelevante de uno
    que nunca se evaluó.
    """
    escuela = {**mock_data.ESCUELAS[0], "cct": "09DPR9999Z", "d1": 0.0, "d2": None}
    monkeypatch.setattr(mock_data, "ESCUELAS", [escuela])

    contribuciones = client.get(_ruta("09DPR9999Z")).json()["contribuciones"]
    assert contribuciones["D1"] == 0.0
    assert contribuciones["D2"] is None


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
