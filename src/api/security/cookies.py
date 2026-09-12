"""Sesión por cookie `httpOnly` para el frontend de React.

> **Dónde vive la decisión.** El mecanismo se acordó en el gate de E5 del 10-sep (Luis Téllez +
> Christian Ruiz) y está asentado en **`ADR-012` §Auth** (*Retiro del embebido de Superset/Streamlit*,
> de Diana Álvarez, `accepted` 11-sep, PR #302). Este módulo lo **implementa**; no lo decide. Los
> residuales (CSRF, XSS) están en `vault/07_Security/Threat_Model.md §Sesión del frontend de React`.
> No se escribe un ADR aparte a propósito: partiría una sola decisión en dos documentos.
>
> **El frontend de React usa el modo cookie** (`?sesion=cookie`); el shell de Streamlit, el legacy.


**Por qué existe.** Hasta `ADR-010`, el servidor de Streamlit canjeaba el `code_faro` y guardaba
los tokens de su lado: el navegador nunca los veía. El frontend nuevo es estático —Vite compilado,
servido por nginx— y no tiene servidor propio, así que la ruta obvia era que el navegador guardara
el par de JWT. Se descartó: el `refresh_token` vive **7 días**, y en `localStorage` un XSS lo
convierte en una semana de acceso a la cuenta.

**Cómo se resuelve sin construir un servicio nuevo.** nginx sirve los estáticos **y** hace
`proxy_pass` de `/api` a esta API, así que el navegador ve **un solo origen**. Entonces basta con
que la API emita la cookie:

1. `/auth/exchange` responde con `Set-Cookie` **sin atributo `Domain`** → el navegador la guarda
   **host-only para el origen del frontend**, porque la respuesta llega por el proxy.
2. Las llamadas siguientes a `/api/*` la mandan solas.
3. `get_current_user` la lee cuando no viene `Authorization`.

Resultado: **el token nunca toca JavaScript**, `ADR-010` se conserva intacto y el frontend no
maneja tokens en absoluto.

> **Esto no contradice `BUG-059`.** Ahí el hallazgo fue que `.run.app` está en la Public Suffix
> List, así que la API **no puede** poner una cookie compartida entre dos subdominios distintos.
> Aquí la cookie es **host-only del propio origen del front**, puesta a través del proxy: es un
> caso distinto, no una excepción al anterior.

**Residual aceptado — CSRF.** Con sesión por cookie, un sitio de terceros puede provocar
peticiones que el navegador acompaña con la credencial. Lo contiene `SameSite=Lax`, que **no envía
la cookie en un POST cross-site**; nuestros POST son `/agente/consulta`, `/auth/*` y `/admin/*`.
Para la ventana del proyecto alcanza, y queda registrado como residual —no como resuelto— en
`vault/07_Security/Threat_Model.md`.

El encabezado `Authorization: Bearer` **sigue funcionando** y tiene precedencia: los clientes que no
son navegador, las pruebas y el shell de Streamlit no se enteran de este cambio.
"""
from __future__ import annotations

from fastapi import Request, Response

from src.api.config import get_settings
from src.api.schemas import TokenPair

#: Access token. `path=/` porque acompaña a toda llamada de la API.
COOKIE_SESION = "faro_sesion"

#: Refresh token. **Acotado a la ruta que lo canjea**: el navegador no lo manda en ninguna otra
#: petición, así que un fallo en cualquier otro endpoint no puede filtrarlo. Es la diferencia entre
#: exponer la credencial de 7 días en cada llamada o solo en una.
COOKIE_REFRESCO = "faro_refresco"

#: Vida de la cookie de refresco, en segundos (7 días, igual que el token que transporta).
_MAX_AGE_REFRESCO = 7 * 24 * 60 * 60


def ruta_de_refresco(request: Request) -> str:
    """Ruta exacta en la que el navegador debe mandar la cookie de refresco.

    Se deriva del montaje real de la app (`url_path_for`) en vez de escribir `/api/v1/...` a mano:
    si algun dia cambia el prefijo, la cookie lo sigue sola en vez de dejar de enviarse en silencio
    --que es la clase de fallo que nadie nota hasta que la sesion se cae sin motivo aparente.
    """
    return request.scope["app"].url_path_for("refresh")


def sembrar_sesion(respuesta: Response, par: TokenPair, request: Request) -> None:
    """Escribe las dos cookies de sesión sobre `respuesta`.

    Solo se llama en el **modo cookie**, cuyo cuerpo es `SesionOut` —**sin JWT**—: si el cuerpo
    trajera el par, un XSS lo leería y `HttpOnly` no serviría de nada. El modo legacy (default) no
    pasa por aquí, así que el shell de Streamlit no recibe cookies que no pidió.

    Nunca se fija `Domain`: la cookie queda **host-only** del origen que respondió.
    """
    s = get_settings()
    respuesta.set_cookie(
        key=COOKIE_SESION,
        value=par.access_token,
        max_age=par.expires_in,
        httponly=True,  # inaccesible a JavaScript: un XSS no puede leerla
        secure=s.cookies_seguras,  # en local es http://, donde `Secure` impediría guardarla
        samesite="lax",  # contiene CSRF: no viaja en un POST cross-site
        path="/",
    )
    respuesta.set_cookie(
        key=COOKIE_REFRESCO,
        value=par.refresh_token,
        max_age=_MAX_AGE_REFRESCO,
        httponly=True,
        secure=s.cookies_seguras,
        samesite="lax",
        path=ruta_de_refresco(request),
    )


def borrar_sesion(respuesta: Response, request: Request) -> None:
    """Borra **las dos** cookies. Olvidar la de refresco dejaría la sesión viva 7 días."""
    respuesta.delete_cookie(COOKIE_SESION, path="/")
    respuesta.delete_cookie(COOKIE_REFRESCO, path=ruta_de_refresco(request))
