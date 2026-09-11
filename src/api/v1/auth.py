"""Autenticación `/auth/*` (§3.2) — OAuth2 con Google + JWT propio (US-402).

- `GET  /auth/login`    → 302 a la pantalla de consentimiento de Google, con `state` anti-CSRF.
- `GET  /auth/callback` → valida el `state`, canjea el `code` por la identidad (vía verificador) y
  emite el par de JWT.
- `POST /auth/refresh`  → valida el refresh token y emite un par nuevo (re-resolviendo el rol).
- `GET  /auth/me`       → devuelve el usuario del access token (protegido por `get_current_user`).

Nota: el enforcement por rol de los endpoints de datos/admin es **US-403** (RBAC), aquí solo se
autentica.

**Protección CSRF del callback (US-402).** El `state` es un JWT propio de vida corta
(`create_state_token`) que viaja por dos canales independientes: el parámetro `state` de la URL de
Google y una cookie `HttpOnly` de primera parte. El callback exige que ambos existan, coincidan y
que el token sea válido. Un tercero puede inducir al navegador a llamar al callback, pero no puede
leer ni fabricar la cookie, así que el ataque muere ahí. Se eligió un `state` **firmado** en vez de
uno guardado en memoria porque Cloud Run corre varias instancias sin estado compartido: un `state`
en RAM se perdería entre la ida y la vuelta.
"""
from __future__ import annotations

import secrets
from urllib.parse import quote

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse

from src.api.config import get_settings
from src.api.schemas import ExchangeIn, RefreshIn, SesionOut, TokenPair, UserOut
from src.api.security.codigos_login import (
    AlmacenCodigos,
    IdentidadSesion,
    get_almacen_codigos,
)
from src.api.security.cookies import COOKIE_REFRESCO, borrar_sesion, sembrar_sesion
from src.api.security.deps import get_current_user, get_google_verifier
from src.api.security.google import (
    GoogleNotConfigured,
    GoogleVerifier,
    build_authorization_url,
)
from src.api.security.jwt import (
    AuthError,
    create_state_token,
    create_token_pair,
    verify_refresh_token,
    verify_state_token,
)
from src.api.security.roles import resolve_role

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Cookie de primera parte que sostiene la mitad "secreta" del `state`. `SameSite=Lax` es lo correcto
# aquí: la vuelta de Google es una navegación GET de nivel superior, así que la cookie SÍ se envía,
# pero no acompaña a peticiones cross-site incrustadas.
COOKIE_STATE = "faro_oauth_state"


@router.get("/login", status_code=status.HTTP_302_FOUND)
def login(redirect: str | None = None) -> RedirectResponse:
    """Inicia OAuth2 con Google redirigiendo a la pantalla de consentimiento.

    Genera el `state` anti-CSRF, lo manda a Google en la URL y guarda el mismo valor en una cookie
    `HttpOnly` para poder compararlos al volver.

    `redirect` (opcional, US-405) es la URL de FARO Web a la que volver con el codigo de un solo
    uso. **Se valida contra una allowlist**: sin eso tendriamos un open redirect, y uno dentro del
    flujo de login es el vehiculo clasico para desviar el codigo de autorizacion a un tercero.
    Sin `redirect`, el callback responde el `TokenPair` como JSON (clientes que no son navegador).
    """
    s = get_settings()
    destino = _validar_redirect(redirect)
    state = create_state_token(redirect=destino)
    respuesta = RedirectResponse(
        url=build_authorization_url(state),
        status_code=status.HTTP_302_FOUND,
    )
    respuesta.set_cookie(
        key=COOKIE_STATE,
        value=state,
        max_age=s.oauth_state_expire_minutes * 60,
        httponly=True,  # inaccesible a JavaScript: ni XSS ni un tercero pueden leerla
        secure=s.cookies_seguras,  # en local es http://, donde `Secure` impediría guardarla
        samesite="lax",  # se envía en la navegación de vuelta de Google, no en peticiones incrustadas
        path="/",
    )
    return respuesta


def _validar_redirect(redirect: str | None) -> str:
    """Devuelve el destino si esta en la allowlist; 400 si no. Cadena vacia si no se pidio.

    Comparacion **exacta** contra `FRONTEND_REDIRECT_URIS`, no por prefijo: un `startswith` deja
    pasar `https://faro.example.com.evil.tld` cuando la allowlist dice `https://faro.example.com`.
    """
    if not redirect:
        return ""
    if redirect not in get_settings().frontend_redirect_list:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Destino de redireccion no permitido."
        )
    return redirect


def _validar_state(request: Request, state: str | None) -> dict:
    """Verifica el `state` del callback: presente, firmado, vigente y **igual** al de la cookie.

    Cualquier fallo se traduce a un 401 uniforme, sin decir cuál de las tres condiciones falló: el
    mensaje detallado solo ayudaría a quien esté probando el ataque.
    """
    cookie = request.cookies.get(COOKIE_STATE)
    if not state or not cookie or not secrets.compare_digest(state, cookie):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="No se pudo verificar el origen de la petición."
        )
    try:
        return verify_state_token(state)
    except AuthError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="No se pudo verificar el origen de la petición."
        ) from exc


@router.get("/callback", response_model=TokenPair)
def callback(
    request: Request,
    response: Response,
    code: str,
    state: str | None = None,
    verifier: GoogleVerifier = Depends(get_google_verifier),
    almacen: AlmacenCodigos = Depends(get_almacen_codigos),
):
    """Callback de Google: valida el `state`, canjea el `code`, resuelve el rol y entrega la sesion.

    Dos salidas, segun si `/auth/login` llevaba `redirect` (el `state` firmado lo recuerda):

    - **Con `redirect`** (FARO Web): **302** al front con `?code_faro=<codigo de un solo uso>`. Los
      tokens NO viajan por la URL -- ver ADR-010 y `security/codigos_login.py`.
    - **Sin `redirect`**: el `TokenPair` como JSON, igual que antes (clientes no-navegador y pruebas).
    """
    claims_state = _validar_state(request, state)
    # El `state` es de un solo uso: se borra la cookie apenas se valida, pase lo que pase después.
    response.delete_cookie(COOKIE_STATE, path="/")

    try:
        identity = verifier.verify(code)
    except GoogleNotConfigured as exc:
        # Config del servidor incompleta: error interno, sin filtrar detalle al cliente.
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Auth no configurada."
        ) from exc
    except (ValueError, RuntimeError) as exc:
        # `code` inválido / no verificable => 401.
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="No se pudo verificar la identidad."
        ) from exc
    role = resolve_role(identity.email)

    destino = claims_state.get("redirect", "")
    if destino:
        codigo = almacen.guardar(
            IdentidadSesion(
                sub=identity.sub, email=identity.email, name=identity.name, role=role
            )
        )
        separador = "&" if "?" in destino else "?"
        redireccion = RedirectResponse(
            url=f"{destino}{separador}code_faro={quote(codigo)}",
            status_code=status.HTTP_302_FOUND,
        )
        # La cookie del `state` se borro en `response`, que aqui NO se devuelve: hay que repetirlo.
        redireccion.delete_cookie(COOKIE_STATE, path="/")
        return redireccion

    return create_token_pair(
        sub=identity.sub, role=role, email=identity.email, name=identity.name
    )


@router.post("/refresh", response_model=TokenPair | SesionOut)
def refresh(
    request: Request,
    respuesta: Response,
    body: RefreshIn | None = None,
) -> TokenPair | SesionOut:
    """Canjea un refresh token válido por un par nuevo, re-resolviendo el rol con la política vigente.

    **Dos modos que nunca se mezclan** (ADR-012). El modo lo determina *de dónde vino el token*, que
    es un dato inequívoco y no una bandera que el cliente pueda equivocarse en mandar:

    | Token en | Modo | Cookies | Cuerpo de la respuesta |
    |---|---|---|---|
    | `body.refresh_token` | **legacy** | no las toca | `TokenPair` |
    | cookie `faro_refresco` | **cookie** | las renueva | `SesionOut` — **sin JWT** |

    **Por qué el modo cookie no devuelve los tokens.** La cookie de refresco está acotada a esta
    ruta, así que el navegador la adjunta aquí y solo aquí. Si la respuesta trajera el `TokenPair`,
    un XSS podría hacer `fetch()` contra este endpoint y **leer los dos tokens del JSON**, anulando
    el beneficio de `HttpOnly`: la credencial volvería a ser alcanzable desde JavaScript. Por eso el
    modo cookie responde solo con `expira_en`, que es una duración y no un secreto.

    El modo legacy **no siembra cookies**: quien administra el token él mismo (el shell de Streamlit,
    las pruebas, cualquier cliente que no sea navegador) recibe exactamente lo de siempre.
    """
    desde_cookie = body is None
    token = request.cookies.get(COOKIE_REFRESCO) if desde_cookie else body.refresh_token
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Falta el refresh token.")
    try:
        claims = verify_refresh_token(token)
    except AuthError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido o expirado."
        ) from exc
    email = claims.get("email", "")
    role = resolve_role(email)
    # El `name` viaja tambien en el refresh: al renovar no hay id_token de Google que reconsultar.
    par = create_token_pair(
        sub=claims["sub"], role=role, email=email, name=claims.get("name", "")
    )
    if not desde_cookie:
        return par
    sembrar_sesion(respuesta, par, request)
    return SesionOut(expira_en=par.expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, respuesta: Response) -> None:
    """Cierra la sesión borrando **las dos** cookies (ADR-012).

    No exige token: cerrar sesión con una credencial ya vencida tiene que funcionar igual, o la
    persona se queda con cookies muertas y sin forma de deshacerse de ellas. Y borra la de refresco
    además de la de acceso — olvidarla dejaría la sesión viva 7 días.

    Los clientes que administran el token ellos mismos (Streamlit, pruebas) no necesitan llamarlo:
    para ellos cerrar sesión sigue siendo descartar el par que tienen guardado.
    """
    # Se mutan las cabeceras de la respuesta inyectada en vez de construir una nueva: `dict()` sobre
    # las cabeceras **colapsa los `Set-Cookie` repetidos en uno solo**, y así se borraba la cookie de
    # sesión pero no la de refresco -- dejando la sesión reconstruible 7 días.
    borrar_sesion(respuesta, request)


@router.post("/exchange", response_model=TokenPair | SesionOut)
def exchange(
    request: Request,
    respuesta: Response,
    body: ExchangeIn,
    sesion: Literal["cookie", "token"] = Query(
        default="token",
        description=(
            "`token` (por defecto): devuelve el `TokenPair` y no toca cookies — el comportamiento "
            "de siempre. `cookie`: siembra la sesión `httpOnly` y responde **sin JWT** (ADR-012)."
        ),
    ),
    almacen: AlmacenCodigos = Depends(get_almacen_codigos),
) -> TokenPair | SesionOut:
    """Canjea el codigo de un solo uso de `?code_faro=` por el par de JWT (US-405, ADR-010).

    Quién lo llama depende del modo: en **legacy** lo llama el **servidor** de Streamlit, y por eso
    los tokens viajan en el cuerpo y nunca por la URL; en **cookie** lo llama el **navegador** del
    frontend de React, a través del proxy same-origin de nginx, y los tokens no salen de las cookies
    `httpOnly`. El codigo se consume en el primer canje; un segundo intento
    con el mismo codigo (o uno expirado, inventado o ya usado) responde **401**, sin distinguir
    entre los casos.

    El rol se **re-resuelve** aqui con la politica vigente, no se confia en el que quedo guardado:
    si `ANALISTA_EMAILS` cambio entre el callback y el canje, manda la politica actual.

    **Dos modos que nunca se mezclan** (`ADR-012`), elegidos con `?sesion=`:

    | `?sesion=` | Cookies | Cuerpo de la respuesta |
    |---|---|---|
    | `token` *(por defecto)* | no las toca | `TokenPair` — **el comportamiento de siempre** |
    | `cookie` | siembra la sesion | `SesionOut` — **sin JWT** |

    Aqui el modo tiene que ser explicito porque el cuerpo es identico en los dos casos: no hay nada
    en la peticion que distinga al servidor de Streamlit del navegador. El **default es el legacy**,
    asi que ningun cliente existente cambia de comportamiento al desplegar esto.

    **Por que el modo cookie no devuelve los tokens:** si lo hiciera, el JWT volveria a ser
    alcanzable desde JavaScript y `HttpOnly` dejaria de servir para nada. Ver `SesionOut`.
    """
    identidad = almacen.canjear(body.code)
    if identidad is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Codigo de sesion invalido o expirado."
        )
    par = create_token_pair(
        sub=identidad.sub,
        role=resolve_role(identidad.email),
        email=identidad.email,
        name=identidad.name,
    )
    if sesion == "token":
        return par
    sembrar_sesion(respuesta, par, request)
    return SesionOut(expira_en=par.expires_in)


@router.get("/me", response_model=UserOut)
def me(user: UserOut = Depends(get_current_user)) -> UserOut:
    """Devuelve el usuario autenticado (requiere access token válido; 401 en caso contrario)."""
    return user
