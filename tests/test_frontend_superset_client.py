"""Pruebas del cliente del guest token de Superset para el embebido (US-206).

Contrato nuevo (embebido REAL con Embedded SDK): login (+CSRF) → resolver id por slug →
habilitar embed (``POST /dashboard/{id}/embedded``) para obtener el ``embedded_uuid`` →
un guest token acotado a esos uuids. El recurso del guest token es el ``embedded_uuid``
(NO el uuid regular), que es lo que exige el SDK; el token NO viaja en la URL del iframe.
"""

from __future__ import annotations

import json

import httpx
import pytest

from src.frontend.superset_client import (
    SUPERSET_PUBLIC_URL,
    SUPERSET_URL,
    PanelSuperset,
    SupersetDeshabilitado,
    TableroEmbebido,
    tableros_embebidos,
)


def _cliente_fake(handler) -> httpx.Client:
    transporte = httpx.MockTransport(handler)
    return httpx.Client(base_url=SUPERSET_URL, transport=transporte)


@pytest.fixture(autouse=True)
def _password_admin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fija credenciales para las pruebas (el .env no se carga en el CI/test)."""
    monkeypatch.setattr("src.frontend.superset_client.ADMIN_PASS", "test-password")


def test_devuelve_el_panel_con_embedded_uuid_y_guest_token() -> None:
    peticiones: list[str] = []
    contador = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        peticiones.append(path)
        if path == "/api/v1/security/login":
            return httpx.Response(200, json={"access_token": "admin-token"})
        if path == "/api/v1/security/csrf_token/":
            return httpx.Response(200, json={"result": "csrf-abc"})
        if path == "/api/v1/dashboard/":
            # un id distinto por slug (simula 10 dashboards resueltos)
            contador["n"] += 1
            return httpx.Response(200, json={"result": [{"id": contador["n"]}]})
        if path.startswith("/api/v1/dashboard/") and path.endswith("/embedded"):
            did = path.split("/")[-2]
            # El embed exige CSRF: la cabecera debe llegar (regresión del contrato nuevo).
            assert request.headers.get("X-CSRFToken") == "csrf-abc"
            return httpx.Response(200, json={"result": {"uuid": f"uuid-{did}"}})
        if path == "/api/v1/security/guest_token/":
            body = json.loads(request.read().decode())
            # El recurso del token es el embedded_uuid, no el id regular del dashboard.
            assert body["resources"], "el guest token debe pedir recursos"
            assert all(r["id"].startswith("uuid-") for r in body["resources"])
            return httpx.Response(200, json={"token": "guest-token"})
        return httpx.Response(404, json={})

    cliente = _cliente_fake(handler)
    panel = tableros_embebidos(rol="ciudadano", cliente=cliente)

    assert isinstance(panel, PanelSuperset)
    assert panel.guest_token == "guest-token"
    assert panel.superset_domain == SUPERSET_PUBLIC_URL
    assert len(panel.tableros) == 10  # los 10 dashboards DB-01…DB-10
    assert len({t.uuid for t in panel.tableros}) == 10  # uuids distintos por dashboard
    for t in panel.tableros:
        assert isinstance(t, TableroEmbebido)
        assert t.slug and t.uuid.startswith("uuid-")
    # Se habilitó el embed de cada dashboard y se pidió el guest token.
    assert sum(1 for p in peticiones if p.endswith("/embedded")) == 10
    assert "/api/v1/security/guest_token/" in peticiones


def test_rechaza_guest_token_deshabilitado_en_config() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/api/v1/security/login":
            return httpx.Response(200, json={"access_token": "admin-token"})
        if path == "/api/v1/security/csrf_token/":
            return httpx.Response(200, json={"result": "csrf-abc"})
        if path == "/api/v1/dashboard/":
            return httpx.Response(200, json={"result": [{"id": 1}]})
        if path.endswith("/embedded"):
            return httpx.Response(200, json={"result": {"uuid": "uuid-1"}})
        if path == "/api/v1/security/guest_token/":
            return httpx.Response(401, json={"msg": "No guest token"})
        return httpx.Response(404, json={})

    cliente = _cliente_fake(handler)
    with pytest.raises(SupersetDeshabilitado, match="SUPERSET_EMBEDDED"):
        tableros_embebidos(rol="ciudadano", cliente=cliente)


def test_rechaza_si_no_puede_habilitar_el_embed() -> None:
    """Si Superset no tiene el flag, ``POST /embedded`` responde 401/403 ⇒ deshabilitado."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/api/v1/security/login":
            return httpx.Response(200, json={"access_token": "admin-token"})
        if path == "/api/v1/security/csrf_token/":
            return httpx.Response(200, json={"result": "csrf-abc"})
        if path == "/api/v1/dashboard/":
            return httpx.Response(200, json={"result": [{"id": 1}]})
        if path.endswith("/embedded"):
            return httpx.Response(403, json={"msg": "embedding disabled"})
        return httpx.Response(404, json={})

    cliente = _cliente_fake(handler)
    with pytest.raises(SupersetDeshabilitado, match="SUPERSET_EMBEDDED"):
        tableros_embebidos(rol="ciudadano", cliente=cliente)


def test_no_renderiza_tablero_si_no_hay_slug_resuelto() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/api/v1/security/login":
            return httpx.Response(200, json={"access_token": "admin-token"})
        if path == "/api/v1/security/csrf_token/":
            return httpx.Response(200, json={"result": "csrf-abc"})
        if path == "/api/v1/dashboard/":
            return httpx.Response(200, json={"result": []})  # ningún id resuelto
        return httpx.Response(404, json={})

    cliente = _cliente_fake(handler)
    with pytest.raises(Exception, match="dashboards embebibles"):
        tableros_embebidos(rol="analista", cliente=cliente)


def test_falla_claramente_si_no_hay_password_de_admin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.frontend.superset_client.ADMIN_PASS", "")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access_token": "x"})

    cliente = _cliente_fake(handler)
    with pytest.raises(Exception, match="SUPERSET_ADMIN_PASSWORD no está definido"):
        tableros_embebidos(rol="ciudadano", cliente=cliente)
