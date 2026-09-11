"""Dependencias FastAPI de seguridad (US-402).

- `get_current_user` — extrae y valida el Bearer token; devuelve el `UserOut` autenticado o **401**
  uniforme. Es la base sobre la que US-403 construirá `require_role(...)`.
- `get_google_verifier` — proveedor del verificador de Google (los tests lo sobreescriben con un
  doble para no depender de credenciales).
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.schemas import Rol, UserOut
from src.api.security.cookies import COOKIE_SESION
from src.api.security.google import GoogleVerifier, RealGoogleVerifier
from src.api.security.jwt import AuthError, verify_access_token

# auto_error=False => nosotros emitimos el 401 con el formato ErrorOut del contrato (§5).
bearer_scheme = HTTPBearer(auto_error=False, scheme_name="bearerAuth")


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserOut:
    """Valida el access token y devuelve el usuario.

    Acepta **dos** portadores, en este orden:

    1. `Authorization: Bearer <token>` — clientes que administran el token ellos mismos (Streamlit,
       pruebas, cualquier consumidor que no sea navegador). **Tiene precedencia.**
    2. La cookie `faro_sesion` (`httpOnly`) — el frontend de React, que es estático y no debe tocar
       el token. Ver `src/api/security/cookies.py` y `ADR-012`.

    La precedencia importa: un `Authorization` explícito describe la intención del cliente, mientras
    que la cookie la manda el navegador sola. Si llegaran los dos, gana el explícito.

    Lanza 401 (sin filtrar la causa) si falta el token, está malformado, expiró o fue manipulado.
    """
    token = credentials.credentials if credentials else None
    if not token:
        token = request.cookies.get(COOKIE_SESION)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Falta el token de acceso.")
    try:
        claims = verify_access_token(token)
    except AuthError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado."
        ) from exc
    return UserOut(
        sub=claims["sub"],
        email=claims.get("email", ""),
        role=Rol(claims["role"]),
        name=claims.get("name", ""),
    )


def get_google_verifier() -> GoogleVerifier:
    """Proveedor del verificador de Google. Sobrescribible en tests vía dependency_overrides."""
    return RealGoogleVerifier()
