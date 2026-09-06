"""Pruebas de la sesión de FARO Web: canje del código, guardas por rol y logout (US-405).

Sin red y sin Streamlit real: se sustituye `httpx.Client` por un transporte falso y se usa un doble
mínimo de `st.session_state` / `st.query_params`. Lo que se verifica es el contrato acordado con la
Célula 2 — el dict de sesión con `sub`/`email`/`name`/`role`, y que `access_token` quede donde
`pages/3_Chat.py` ya lo busca.
"""
from __future__ import annotations

import httpx
import pytest

pytest.importorskip("streamlit")

from src.frontend import auth as authmod

USUARIO = {
    "sub": "google-1",
    "email": "persona@faro.mx",
    "name": "Persona de Prueba",
    "role": "ciudadano",
}


class _EstadoFalso(dict):
    """`st.session_state` es un dict con acceso por atributo; para esto basta el dict."""


class _QueryParamsFalso(dict):
    pass


@pytest.fixture
def st_falso(monkeypatch: pytest.MonkeyPatch):
    """Sustituye el `st` del módulo por un doble con lo mínimo que usa `auth.py`."""
    errores: list[str] = []

    class _St:
        session_state = _EstadoFalso()
        query_params = _QueryParamsFalso()

        @staticmethod
        def error(mensaje: str) -> None:
            errores.append(mensaje)

    st = _St()
    st.errores = errores  # type: ignore[attr-defined]
    monkeypatch.setattr(authmod, "st", st)
    return st


# Se guarda la clase real ANTES de que ninguna prueba parchee `httpx.Client`: la fabrica de abajo
# tiene que construir un cliente de verdad, no volver a entrar en el parche (recursion infinita).
_CLIENTE_REAL = httpx.Client


def _transporte(handler):
    """Devuelve una fábrica de `httpx.Client` con transporte falso, para monkeypatch."""

    def fabrica(*args, **kwargs):
        kwargs.pop("transport", None)
        return _CLIENTE_REAL(
            base_url=kwargs.get("base_url", authmod.API_BASE_URL),
            transport=httpx.MockTransport(handler),
        )

    return fabrica


def _api_ok(peticiones: list[str] | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        if peticiones is not None:
            peticiones.append(request.url.path)
        if request.url.path == "/api/v1/auth/exchange":
            return httpx.Response(
                200,
                json={
                    "access_token": "access-abc",
                    "refresh_token": "refresh-xyz",
                    "token_type": "bearer",
                    "expires_in": 900,
                },
            )
        if request.url.path == "/api/v1/auth/me":
            assert request.headers["authorization"] == "Bearer access-abc"
            return httpx.Response(200, json=USUARIO)
        return httpx.Response(404)

    return handler


# --------------------------------------------------------------------------- #
# URL de login
# --------------------------------------------------------------------------- #


def test_la_url_de_login_lleva_el_redirect_del_front() -> None:
    url = authmod.url_de_login()
    assert url.startswith(f"{authmod.API_BASE_URL}/api/v1/auth/login")
    assert f"redirect={authmod.FRONTEND_URL}" in url


# --------------------------------------------------------------------------- #
# Canje del código
# --------------------------------------------------------------------------- #


def test_current_user_canjea_el_codigo_de_la_url(
    st_falso, monkeypatch: pytest.MonkeyPatch
) -> None:
    peticiones: list[str] = []
    monkeypatch.setattr(authmod.httpx, "Client", _transporte(_api_ok(peticiones)))
    st_falso.query_params["code_faro"] = "codigo-de-un-solo-uso"

    usuario = authmod.current_user()

    assert usuario == USUARIO
    assert peticiones == ["/api/v1/auth/exchange", "/api/v1/auth/me"]


def test_el_access_token_queda_donde_lo_busca_el_chat(
    st_falso, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`pages/3_Chat.py` lee `st.session_state["access_token"]` (US-305). No se puede mover."""
    monkeypatch.setattr(authmod.httpx, "Client", _transporte(_api_ok()))
    st_falso.query_params["code_faro"] = "c"
    authmod.current_user()
    assert st_falso.session_state["access_token"] == "access-abc"
    assert st_falso.session_state["refresh_token"] == "refresh-xyz"


def test_el_codigo_se_borra_de_la_url(st_falso, monkeypatch: pytest.MonkeyPatch) -> None:
    """Si el código se queda en la URL, recargar la página falla: es de un solo uso."""
    monkeypatch.setattr(authmod.httpx, "Client", _transporte(_api_ok()))
    st_falso.query_params["code_faro"] = "c"
    authmod.current_user()
    assert "code_faro" not in st_falso.query_params


def test_el_codigo_se_borra_tambien_si_el_canje_falla(
    st_falso, monkeypatch: pytest.MonkeyPatch
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "unauthorized"})

    monkeypatch.setattr(authmod.httpx, "Client", _transporte(handler))
    st_falso.query_params["code_faro"] = "ya-usado"

    assert authmod.current_user() is None
    assert "code_faro" not in st_falso.query_params
    assert st_falso.errores  # se le dice a la persona, no se falla en silencio


def test_api_caida_no_revienta_la_pagina(st_falso, monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sin ruta al host")

    monkeypatch.setattr(authmod.httpx, "Client", _transporte(handler))
    st_falso.query_params["code_faro"] = "c"

    assert authmod.current_user() is None
    assert "API" in st_falso.errores[0]


def test_sin_codigo_y_sin_sesion_no_hay_usuario(st_falso) -> None:
    assert authmod.current_user() is None


def test_la_sesion_existente_no_se_recanjea(st_falso, monkeypatch: pytest.MonkeyPatch) -> None:
    """Con sesión en curso no se toca la API: `current_user()` se llama en cada rerun de Streamlit."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no debio llamarse a la API")

    monkeypatch.setattr(authmod.httpx, "Client", _transporte(handler))
    st_falso.session_state["user"] = USUARIO
    assert authmod.current_user() == USUARIO


# --------------------------------------------------------------------------- #
# Guardas por rol
# --------------------------------------------------------------------------- #


def test_sin_sesion_ningun_rol_alcanza(st_falso) -> None:
    assert authmod.require_role("ciudadano") is False
    assert authmod.require_role("analista") is False


def test_ciudadano_no_alcanza_analista(st_falso) -> None:
    st_falso.session_state["user"] = USUARIO
    assert authmod.require_role("ciudadano") is True
    assert authmod.require_role("analista") is False


def test_analista_pasa_cualquier_guarda(st_falso) -> None:
    st_falso.session_state["user"] = {**USUARIO, "role": "analista"}
    assert authmod.require_role("ciudadano") is True
    assert authmod.require_role("analista") is True


def test_rol_inventado_es_error_de_programacion(st_falso) -> None:
    with pytest.raises(AssertionError):
        authmod.require_role("superadmin")


# --------------------------------------------------------------------------- #
# Refresco del access token (P0 de Edgar, 2026-09-06)
# --------------------------------------------------------------------------- #
#
# El access token dura 15 min (`src/api/config.py::access_token_expire_minutes`), menos que una
# demo. `auth.py` guardaba el `refresh_token` y **nunca lo usaba**: no habia una sola llamada a
# `/auth/refresh` en todo el front, asi que iniciar sesion en la preparacion significaba llegar
# con el token muerto a la sala.


def _api_refresco(peticiones: list[str] | None = None, estado: int = 200):
    """Google falso que responde `/auth/refresh` con un par nuevo."""

    def handler(request: httpx.Request) -> httpx.Response:
        if peticiones is not None:
            peticiones.append(request.url.path)
        if request.url.path == "/api/v1/auth/refresh":
            if estado != 200:
                return httpx.Response(estado, json={"error": "unauthorized"})
            return httpx.Response(
                200,
                json={
                    "access_token": "access-nuevo",
                    "refresh_token": "refresh-nuevo",
                    "token_type": "bearer",
                    "expires_in": 900,
                },
            )
        return httpx.Response(404)

    return handler


def _sesion_viva(st_falso, vence_en: float) -> None:
    """Deja una sesion en curso cuyo access token vence dentro de `vence_en` segundos."""
    import time

    st_falso.session_state["user"] = USUARIO
    st_falso.session_state["access_token"] = "access-viejo"
    st_falso.session_state["refresh_token"] = "refresh-viejo"
    st_falso.session_state["access_token_vence"] = time.monotonic() + vence_en


def test_el_canje_guarda_el_vencimiento(st_falso, monkeypatch: pytest.MonkeyPatch) -> None:
    """`expires_in` viene en la respuesta y antes se tiraba: sin el no se puede saber cuando refrescar."""
    monkeypatch.setattr(authmod.httpx, "Client", _transporte(_api_ok()))
    st_falso.query_params["code_faro"] = "c"
    authmod.current_user()
    assert st_falso.session_state["access_token_vence"] > 0


def test_token_vigente_no_llama_a_la_api(st_falso, monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no debio refrescar: el token sigue vigente")

    monkeypatch.setattr(authmod.httpx, "Client", _transporte(handler))
    _sesion_viva(st_falso, vence_en=600)
    assert authmod.token_de_acceso() == "access-viejo"


def test_token_por_expirar_se_refresca(st_falso, monkeypatch: pytest.MonkeyPatch) -> None:
    """Dentro del margen se pide uno nuevo ANTES de que expire, no despues del 401."""
    peticiones: list[str] = []
    monkeypatch.setattr(authmod.httpx, "Client", _transporte(_api_refresco(peticiones)))
    _sesion_viva(st_falso, vence_en=30)  # margen es 120 s

    assert authmod.token_de_acceso() == "access-nuevo"
    assert peticiones == ["/api/v1/auth/refresh"]
    # El refresh token tambien rota: el viejo no se reutiliza.
    assert st_falso.session_state["refresh_token"] == "refresh-nuevo"


def test_token_ya_expirado_se_refresca(st_falso, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(authmod.httpx, "Client", _transporte(_api_refresco()))
    _sesion_viva(st_falso, vence_en=-60)
    assert authmod.token_de_acceso() == "access-nuevo"


def test_refresh_rechazado_cierra_la_sesion(st_falso, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mejor mostrar "Iniciar sesion" que dejar un token muerto dando 401 en cada pagina."""
    monkeypatch.setattr(authmod.httpx, "Client", _transporte(_api_refresco(estado=401)))
    _sesion_viva(st_falso, vence_en=0)

    assert authmod.token_de_acceso() is None
    assert "user" not in st_falso.session_state
    assert "access_token" not in st_falso.session_state


def test_api_caida_no_borra_la_sesion(st_falso, monkeypatch: pytest.MonkeyPatch) -> None:
    """Un corte de red pasajero no debe tirar la sesion: el token actual quiza siga sirviendo."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sin ruta al host")

    monkeypatch.setattr(authmod.httpx, "Client", _transporte(handler))
    _sesion_viva(st_falso, vence_en=10)

    assert authmod.token_de_acceso() == "access-viejo"
    assert st_falso.session_state["user"] == USUARIO


def test_sin_sesion_no_hay_token(st_falso) -> None:
    assert authmod.token_de_acceso() is None


def test_cerrar_sesion_limpia_las_cuatro_claves(st_falso) -> None:
    _sesion_viva(st_falso, vence_en=600)
    authmod.cerrar_sesion()
    for clave in ("user", "access_token", "refresh_token", "access_token_vence"):
        assert clave not in st_falso.session_state
