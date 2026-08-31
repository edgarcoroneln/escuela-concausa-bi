"""Pruebas de control de acceso por rol — RBAC (US-403).

Verifican la matriz de acceso de §3 del contrato con las dos dependencias de `security/rbac.py`:

- `/admin/*` exige **analista**: sin token → 401, `ciudadano` → 403, `analista` → 200.
- La **lectura** (gold, predicciones, agente) obedece el flag híbrido `AUTH_LECTURA_PUBLICA`:
  pública por defecto (200 sin token) y, al apagar el flag, exige sesión (401 sin token, 200 con
  cualquier rol).

Todo offline: tokens firmados con el secreto de desarrollo; no se toca la base de datos (los 401/403
se emiten en la dependencia de router, antes del cuerpo del endpoint; los 200 usan `/admin/metrics`
-- con `RepositorioMetricas` sustituido por un fake, US-413 -- y `/agente/consulta`, sobre stub).
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.api.app import API_PREFIX, app
from src.api.config import Settings, get_settings
from src.api.repositorio_export import get_repositorio_export
from src.api.repositorio_metricas import get_repositorio_metricas
from src.api.schemas import Rol, UserOut
from src.api.security import jwt as jwtmod
from src.api.security.rbac import require_role
from tests.fixtures_export import RepositorioExportFake
from tests.fixtures_metricas import RepositorioMetricasFake


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_repositorio_metricas] = RepositorioMetricasFake
    app.dependency_overrides[get_repositorio_export] = RepositorioExportFake
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_repositorio_metricas, None)
        app.dependency_overrides.pop(get_repositorio_export, None)


@pytest.fixture
def lectura_protegida() -> Iterator[None]:
    """Fuerza AUTH_LECTURA_PUBLICA=False vía dependency override (no contamina otras pruebas)."""
    app.dependency_overrides[get_settings] = lambda: Settings(auth_lectura_publica=False)
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_settings, None)


# --------------------------------------------------------------------------- #
# /admin/* — exige analista
# --------------------------------------------------------------------------- #


def test_admin_sin_token_da_401(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/admin/metrics")
    assert r.status_code == 401
    assert r.json()["error"] == "unauthorized"


def test_admin_como_ciudadano_da_403(client: TestClient) -> None:
    token = jwtmod.create_access_token(sub="c1", role=Rol.ciudadano, email="ciu@faro.mx")
    r = client.get(f"{API_PREFIX}/admin/metrics", headers=_auth(token))
    assert r.status_code == 403
    assert r.json()["error"] == "forbidden"


def test_admin_como_analista_ok(client: TestClient) -> None:
    token = jwtmod.create_access_token(sub="a1", role=Rol.analista, email="ana@faro.mx")
    r = client.get(f"{API_PREFIX}/admin/metrics", headers=_auth(token))
    assert r.status_code == 200


def test_admin_export_ciudadano_da_403(client: TestClient) -> None:
    """El export en bruto es la ruta sensible: un ciudadano nunca debe alcanzarlo."""
    token = jwtmod.create_access_token(sub="c1", role=Rol.ciudadano)
    r = client.get(f"{API_PREFIX}/admin/export", params={"tabla": "fact_escuela_ciclo"},
                   headers=_auth(token))
    assert r.status_code == 403


def test_admin_export_como_analista_ok(client: TestClient) -> None:
    """Antes de US-413 nadie probaba el 200 real de /admin/export (era puro stub)."""
    token = jwtmod.create_access_token(sub="a1", role=Rol.analista, email="ana@faro.mx")
    r = client.get(f"{API_PREFIX}/admin/export", params={"tabla": "dim_escuela"}, headers=_auth(token))
    assert r.status_code == 200


# --------------------------------------------------------------------------- #
# Lectura — flag híbrido AUTH_LECTURA_PUBLICA
# --------------------------------------------------------------------------- #


def test_lectura_publica_por_defecto_sin_token(client: TestClient) -> None:
    """Con el flag por defecto (True), el agente responde sin credenciales."""
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": "¿cuántas escuelas hay?"})
    assert r.status_code == 200


def test_lectura_protegida_sin_token_da_401(client: TestClient, lectura_protegida: None) -> None:
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": "hola"})
    assert r.status_code == 401
    assert r.json()["error"] == "unauthorized"


def test_lectura_protegida_ciudadano_ok(client: TestClient, lectura_protegida: None) -> None:
    """Con el flag apagado, cualquier sesión válida (mínimo ciudadano) puede leer."""
    token = jwtmod.create_access_token(sub="c1", role=Rol.ciudadano)
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": "hola"}, headers=_auth(token))
    assert r.status_code == 200


def test_lectura_protegida_gold_sin_token_da_401(client: TestClient, lectura_protegida: None) -> None:
    """El 401 se emite en la dependencia de router, antes de tocar el repositorio de Gold."""
    r = client.get(f"{API_PREFIX}/escuelas")
    assert r.status_code == 401


# --------------------------------------------------------------------------- #
# require_role — unidad
# --------------------------------------------------------------------------- #


def test_require_role_admite_varios_roles() -> None:
    dep = require_role(Rol.ciudadano, Rol.analista)
    user = UserOut(sub="u1", email="a@b.mx", role=Rol.ciudadano)
    assert dep(user=user) is user  # ciudadano permitido cuando está en la lista


def test_require_role_rechaza_rol_no_incluido() -> None:
    from fastapi import HTTPException

    dep = require_role(Rol.analista)
    user = UserOut(sub="u1", email="a@b.mx", role=Rol.ciudadano)
    with pytest.raises(HTTPException) as exc:
        dep(user=user)
    assert exc.value.status_code == 403
