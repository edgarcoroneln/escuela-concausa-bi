"""Sesión por cookie `httpOnly` para el frontend de React (ADR-012).

El frontend nuevo es estático —Vite compilado, servido por nginx— y no tiene servidor donde guardar
el token. La alternativa era que el navegador guardara el par de JWT, pero el `refresh_token` vive
**7 días**: en `localStorage`, un XSS lo convierte en una semana de acceso a la cuenta.

La salida no fue construir un BFF, sino aprovechar que nginx ya hace `proxy_pass` de `/api`: con un
solo origen, basta con que la API emita la cookie. Lo que este archivo fija:

1. **`/auth/exchange` siembra la sesión** — y `/auth/refresh` la renueva.
2. **`get_current_user` acepta la cookie** cuando no hay `Authorization`, y el encabezado **tiene
   precedencia** cuando llegan los dos.
3. **El cambio es aditivo**: el cuerpo sigue trayendo el par, así que el shell de Streamlit y las
   pruebas existentes no se enteran. Es lo que permite que los dos frontends convivan.
4. **Los atributos de la cookie son la protección, no un detalle**: `httpOnly` contra XSS,
   `SameSite=Lax` contra CSRF, y la de refresco **acotada a la ruta que la canjea**.
5. **El logout borra las dos.** Olvidar la de refresco dejaría la sesión viva 7 días.

Todo offline: sin Google, sin Postgres.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.api.app import API_PREFIX, app
from src.api.config import Settings, get_settings
from src.api.schemas import Rol
from src.api.security.codigos_login import (
    AlmacenMemoria,
    IdentidadSesion,
    get_almacen_codigos,
)
from src.api.security.cookies import COOKIE_REFRESCO, COOKIE_SESION
from src.api.security.jwt import create_access_token, create_token_pair

RUTA_EXCHANGE = f"{API_PREFIX}/auth/exchange"
RUTA_REFRESH = f"{API_PREFIX}/auth/refresh"
RUTA_LOGOUT = f"{API_PREFIX}/auth/logout"
RUTA_ME = f"{API_PREFIX}/auth/me"
#: Ruta bajo `require_lectura` que **no toca Postgres**: el agente degrada seguro sin LLM ni
#: base, asi que sirve para ejercitar la autenticacion sin depender del entorno.
RUTA_AGENTE = f"{API_PREFIX}/agente/consulta"

EMAIL = "ciudadano@faro.mx"


@pytest.fixture
def almacen() -> Iterator[AlmacenMemoria]:
    """Almacén real de códigos en memoria: el canje de un solo uso se ejercita de verdad."""
    a = AlmacenMemoria()
    app.dependency_overrides[get_almacen_codigos] = lambda: a
    try:
        yield a
    finally:
        app.dependency_overrides.pop(get_almacen_codigos, None)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def lectura_protegida() -> Iterator[None]:
    """`AUTH_LECTURA_PUBLICA=false`, que es como corre producción desde SEC-006."""
    app.dependency_overrides[get_settings] = lambda: Settings(auth_lectura_publica=False)
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_settings, None)


def _codigo(almacen: AlmacenMemoria) -> str:
    return almacen.guardar(
        IdentidadSesion(sub="u-1", email=EMAIL, name="Ciudadana", role=Rol.ciudadano)
    )


def _canjear(client: TestClient, almacen: AlmacenMemoria):
    """Canje en **modo cookie**: siembra la sesion y NO devuelve JWT."""
    return client.post(
        RUTA_EXCHANGE, params={"sesion": "cookie"}, json={"code": _codigo(almacen)}
    )


def _canjear_legacy(client: TestClient, almacen: AlmacenMemoria):
    """Canje en **modo legacy** (el default): devuelve el `TokenPair` y no toca cookies."""
    return client.post(RUTA_EXCHANGE, json={"code": _codigo(almacen)})


# --------------------------------------------------------------------------- #
# 1. El canje siembra la sesión, y el cuerpo NO cambia
# --------------------------------------------------------------------------- #


def test_el_canje_siembra_las_dos_cookies(client: TestClient, almacen: AlmacenMemoria) -> None:
    r = _canjear(client, almacen)
    assert r.status_code == 200, r.text
    assert COOKIE_SESION in r.cookies
    assert COOKIE_REFRESCO in r.cookies


def test_el_modo_legacy_sigue_trayendo_el_par(
    client: TestClient, almacen: AlmacenMemoria
) -> None:
    """El default no cambia: el shell de Streamlit consume el cuerpo y no debe romperse."""
    cuerpo = _canjear_legacy(client, almacen).json()
    assert cuerpo["access_token"]
    assert cuerpo["refresh_token"]
    assert cuerpo["token_type"] == "bearer"


def test_el_modo_legacy_no_siembra_cookies(
    client: TestClient, almacen: AlmacenMemoria
) -> None:
    """Los modos no se mezclan: quien administra el token el mismo no recibe sesion por cookie."""
    r = _canjear_legacy(client, almacen)
    assert COOKIE_SESION not in r.cookies
    assert COOKIE_REFRESCO not in r.cookies


def test_un_codigo_invalido_no_siembra_nada(client: TestClient, almacen: AlmacenMemoria) -> None:
    """Un 401 no puede dejar cookies a medias."""
    r = client.post(RUTA_EXCHANGE, json={"code": "x" * 32})
    assert r.status_code == 401
    assert COOKIE_SESION not in r.cookies


# --------------------------------------------------------------------------- #
# 2. Atributos de la cookie: aquí vive la protección
# --------------------------------------------------------------------------- #


def _set_cookie_de(respuesta, nombre: str) -> str:
    for cabecera in respuesta.headers.get_list("set-cookie"):
        if cabecera.startswith(f"{nombre}="):
            return cabecera
    raise AssertionError(f"no se emitió la cookie {nombre}")


@pytest.mark.parametrize("nombre", [COOKIE_SESION, COOKIE_REFRESCO])
def test_las_cookies_son_httponly(
    client: TestClient, almacen: AlmacenMemoria, nombre: str
) -> None:
    """Sin `HttpOnly` todo el diseño se cae: un XSS volvería a poder leer el token."""
    assert "httponly" in _set_cookie_de(_canjear(client, almacen), nombre).lower()


@pytest.mark.parametrize("nombre", [COOKIE_SESION, COOKIE_REFRESCO])
def test_las_cookies_son_samesite_lax(
    client: TestClient, almacen: AlmacenMemoria, nombre: str
) -> None:
    """Es lo que contiene el residual de CSRF: no viajan en un POST cross-site."""
    assert "samesite=lax" in _set_cookie_de(_canjear(client, almacen), nombre).lower()


def test_la_cookie_de_refresco_esta_acotada_a_su_ruta(
    client: TestClient, almacen: AlmacenMemoria
) -> None:
    """El navegador no debe mandar la credencial de 7 días en toda petición, solo donde se canjea."""
    cabecera = _set_cookie_de(_canjear(client, almacen), COOKIE_REFRESCO)
    assert f"Path={RUTA_REFRESH}" in cabecera


def test_la_cookie_de_sesion_vale_para_toda_la_api(
    client: TestClient, almacen: AlmacenMemoria
) -> None:
    assert "Path=/" in _set_cookie_de(_canjear(client, almacen), COOKIE_SESION)


@pytest.mark.parametrize("nombre", [COOKIE_SESION, COOKIE_REFRESCO])
def test_ninguna_cookie_fija_domain(
    client: TestClient, almacen: AlmacenMemoria, nombre: str
) -> None:
    """Sin `Domain` la cookie es **host-only**: por eso esto no choca con BUG-059 (Public Suffix
    List). Fijar un `Domain` sería exactamente el error que aquel bug documentó."""
    assert "domain=" not in _set_cookie_de(_canjear(client, almacen), nombre).lower()


# --------------------------------------------------------------------------- #
# 3. La cookie autentica de verdad
# --------------------------------------------------------------------------- #


def test_la_cookie_autentica_sin_encabezado(
    client: TestClient, almacen: AlmacenMemoria, lectura_protegida: None
) -> None:
    """El caso completo del frontend de React: canjea y luego navega sin tocar el token."""
    _canjear(client, almacen)  # TestClient conserva las cookies
    r = client.get(RUTA_ME)
    assert r.status_code == 200
    assert r.json()["email"] == EMAIL


def test_una_ruta_de_lectura_protegida_acepta_la_cookie(
    client: TestClient, almacen: AlmacenMemoria, lectura_protegida: None
) -> None:
    """Con SEC-006 activo, sin esto el sitio cargaría y todo devolvería 401."""
    _canjear(client, almacen)
    r = client.post(RUTA_AGENTE, json={"pregunta": "¿cuántas escuelas hay en riesgo?"})
    assert r.status_code == 200


def test_sin_cookie_ni_encabezado_sigue_dando_401(
    client: TestClient, lectura_protegida: None
) -> None:
    r = client.get(RUTA_ME)
    assert r.status_code == 401
    assert r.json()["error"] == "unauthorized"


def test_una_cookie_manipulada_da_401(client: TestClient, lectura_protegida: None) -> None:
    """La cookie se valida como cualquier token: no basta con que exista."""
    client.cookies.set(COOKIE_SESION, "no.es.un.jwt")
    r = client.get(RUTA_ME)
    assert r.status_code == 401


def test_el_encabezado_tiene_precedencia_sobre_la_cookie(
    client: TestClient, almacen: AlmacenMemoria, lectura_protegida: None
) -> None:
    """Un `Authorization` explícito describe la intención del cliente; la cookie la manda el
    navegador solo. Si llegan los dos, gana el explícito."""
    _canjear(client, almacen)  # deja la cookie de `ciudadano@faro.mx`
    otro = create_access_token(sub="u-2", role=Rol.analista, email="analista@faro.mx")
    r = client.get(RUTA_ME, headers={"Authorization": f"Bearer {otro}"})
    assert r.json()["email"] == "analista@faro.mx"


# --------------------------------------------------------------------------- #
# 4. Refresco por cookie
# --------------------------------------------------------------------------- #


def test_el_refresco_funciona_solo_con_la_cookie(
    client: TestClient, almacen: AlmacenMemoria
) -> None:
    """El frontend de React no tiene el refresh token: solo puede llamar sin cuerpo."""
    _canjear(client, almacen)
    r = client.post(RUTA_REFRESH)
    assert r.status_code == 200, r.text
    assert r.json()["expira_en"] > 0


def test_el_refresco_renueva_la_cookie(client: TestClient, almacen: AlmacenMemoria) -> None:
    _canjear(client, almacen)
    r = client.post(RUTA_REFRESH)
    assert COOKIE_SESION in r.cookies


def test_el_refresco_por_cuerpo_sigue_funcionando(client: TestClient) -> None:
    """Retrocompatibilidad: es como refresca el shell de Streamlit hoy."""
    par = create_token_pair(sub="u-1", role=Rol.ciudadano, email=EMAIL, name="")
    r = client.post(RUTA_REFRESH, json={"refresh_token": par.refresh_token})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_refrescar_sin_cuerpo_ni_cookie_da_401(client: TestClient) -> None:
    assert client.post(RUTA_REFRESH).status_code == 401


def test_un_access_token_no_sirve_para_refrescar(
    client: TestClient, almacen: AlmacenMemoria
) -> None:
    """Los dos tokens son distintos: confundirlos sería aceptar el de vida corta como el de 7 días."""
    acceso = _canjear_legacy(client, almacen).json()["access_token"]
    assert client.post(RUTA_REFRESH, json={"refresh_token": acceso}).status_code == 401


# --------------------------------------------------------------------------- #
# 5. Logout
# --------------------------------------------------------------------------- #


def test_el_logout_borra_las_dos_cookies(client: TestClient, almacen: AlmacenMemoria) -> None:
    """Borrar solo la de acceso dejaría la sesión reconstruible durante 7 días."""
    _canjear(client, almacen)
    r = client.post(RUTA_LOGOUT)
    assert r.status_code == 204
    borradas = " ".join(r.headers.get_list("set-cookie"))
    assert COOKIE_SESION in borradas
    assert COOKIE_REFRESCO in borradas


def test_despues_del_logout_la_sesion_no_sirve(
    client: TestClient, almacen: AlmacenMemoria, lectura_protegida: None
) -> None:
    _canjear(client, almacen)
    client.post(RUTA_LOGOUT)
    assert client.get(RUTA_ME).status_code == 401


def test_el_logout_sin_sesion_no_falla(client: TestClient) -> None:
    """Cerrar sesión con una credencial ya vencida tiene que funcionar, o quedan cookies muertas
    sin forma de deshacerse de ellas."""
    assert client.post(RUTA_LOGOUT).status_code == 204


# --------------------------------------------------------------------------- #
# 6. Cabeceras de seguridad (la otra mitad de ADR-012)
# --------------------------------------------------------------------------- #


def test_nosniff_en_toda_respuesta(client: TestClient) -> None:
    """Un JSON que el navegador interprete como HTML es XSS."""
    r = client.get(f"{API_PREFIX}/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"


def test_referrer_policy_no_referrer(client: TestClient) -> None:
    """El `code_faro` viaja en la URL del redirect (ADR-010); sin esto se filtra en el `Referer`."""
    assert client.get(f"{API_PREFIX}/health").headers["Referrer-Policy"] == "no-referrer"


def test_las_cabeceras_acompanan_tambien_a_un_error(client: TestClient) -> None:
    """Una respuesta de error es tan interpretable por el navegador como una buena."""
    r = client.post(RUTA_EXCHANGE, json={"code": "x" * 32})
    assert r.status_code == 401
    assert r.headers["X-Content-Type-Options"] == "nosniff"


# --------------------------------------------------------------------------- #
# 7. El modo cookie NUNCA devuelve un JWT en el cuerpo
#
# Es el núcleo de la corrección que pidió el PO al revisar el PR #304, y es la razón de ser del
# modo: la cookie de refresco está acotada a `/auth/refresh`, así que el navegador la adjunta ahí.
# Si la respuesta trajera el par, un XSS podría hacer `fetch()` contra ese endpoint y **leer los dos
# tokens del JSON**, dejando `HttpOnly` sin ningún efecto. Estas pruebas existen para que nadie
# "mejore" la respuesta devolviendo el token por comodidad del frontend.
# --------------------------------------------------------------------------- #

_CLAVES_PROHIBIDAS = ("access_token", "refresh_token", "token", "jwt")


def _sin_jwt(cuerpo: dict) -> None:
    for clave in _CLAVES_PROHIBIDAS:
        assert clave not in cuerpo, f"el modo cookie filtró `{clave}` en el cuerpo"


def test_el_canje_en_modo_cookie_no_devuelve_jwt(
    client: TestClient, almacen: AlmacenMemoria
) -> None:
    _sin_jwt(_canjear(client, almacen).json())


def test_el_refresco_en_modo_cookie_no_devuelve_jwt(
    client: TestClient, almacen: AlmacenMemoria
) -> None:
    """El caso que un XSS explotaría: llamar al refresh y leer la respuesta."""
    _canjear(client, almacen)
    _sin_jwt(client.post(RUTA_REFRESH).json())


@pytest.mark.parametrize("ruta", [RUTA_EXCHANGE, RUTA_REFRESH])
def test_ningun_jwt_aparece_como_texto_en_la_respuesta_del_modo_cookie(
    client: TestClient, almacen: AlmacenMemoria, ruta: str
) -> None:
    """Más fuerte que mirar claves: un JWT tiene forma reconocible (`eyJ...`), así que se busca en
    el texto crudo. Cubre el caso de que alguien lo anide bajo otro nombre."""
    if ruta == RUTA_EXCHANGE:
        texto = _canjear(client, almacen).text
    else:
        _canjear(client, almacen)
        texto = client.post(RUTA_REFRESH).text
    assert "eyJ" not in texto, "hay algo con forma de JWT en el cuerpo del modo cookie"


def test_el_modo_cookie_solo_informa_la_vigencia(
    client: TestClient, almacen: AlmacenMemoria
) -> None:
    """Lo único que viaja es una duración, que no es un secreto: permite al frontend refrescar
    **antes** del vencimiento en vez de descubrirlo con un 401 a media pantalla."""
    cuerpo = _canjear(client, almacen).json()
    assert cuerpo["expira_en"] > 0
    assert cuerpo["modo"] == "cookie"


def test_los_dos_modos_no_se_mezclan_en_el_refresco(client: TestClient) -> None:
    """Refrescar por cuerpo devuelve el par **y no siembra cookies**; son caminos separados."""
    par = create_token_pair(sub="u-1", role=Rol.ciudadano, email=EMAIL, name="")
    r = client.post(RUTA_REFRESH, json={"refresh_token": par.refresh_token})
    assert r.json()["access_token"]
    assert COOKIE_SESION not in r.cookies
