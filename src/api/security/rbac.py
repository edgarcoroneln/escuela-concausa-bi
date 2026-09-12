"""Control de acceso por rol — RBAC (US-403).

Construye sobre `get_current_user` (US-402) dos dependencias reutilizables de FastAPI:

- `require_role(*roles)` — fábrica que devuelve una dependencia que exige que el usuario
  autenticado tenga **alguno** de los roles indicados; si no, responde **403** con la forma
  uniforme `ErrorOut` (§5, manejador en `app.py`). Se usa para proteger `/admin/*` (analista).
- `require_lectura` — dependencia para los endpoints de **lectura** (gold, predicciones, agente).
  Aplica el interruptor híbrido `AUTH_LECTURA_PUBLICA` (ver `config.py` y ADR-004 §RBAC):
    * `True`  → lectura pública (no exige token), para no bloquear la demo mientras el login
      Google no está operativo (credenciales pendientes de Célula 5).
    * `False` → exige sesión válida de **cualquier** rol (mínimo `ciudadano`); `analista` también
      pasa por ser un superconjunto de privilegios.

Los dos roles del PRD son `ciudadano` (dashboards + agente) y `analista` (pipelines, export en
bruto, ML avanzado). La política de **quién** es analista vive en `security/roles.py` (mínimo
privilegio); aquí solo se decide **qué** puede hacer cada rol.
"""
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from src.api.config import Settings, get_settings
from src.api.schemas import Rol, UserOut
from src.api.security.deps import bearer_scheme, get_current_user


def require_role(*roles: Rol) -> Callable[..., UserOut]:
    """Devuelve una dependencia que exige que el usuario tenga alguno de `roles` (si no, 403).

    Ejemplo::

        @router.get("/export", dependencies=[Depends(require_role(Rol.analista))])
    """
    permitidos = frozenset(roles)

    def _verificar_rol(user: UserOut = Depends(get_current_user)) -> UserOut:
        # get_current_user ya emitió 401 si no hay sesión válida; aquí solo decidimos el 403.
        if user.role not in permitidos:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="El rol del usuario no tiene permiso para esta operación.",
            )
        return user

    return _verificar_rol


def require_lectura(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> UserOut | None:
    """Protege la lectura de datos según el interruptor híbrido `AUTH_LECTURA_PUBLICA`.

    Devuelve `None` cuando la lectura es pública (nadie autenticado), o el `UserOut` cuando se
    exige sesión. No distingue rol: cualquier usuario autenticado (ciudadano o analista) puede leer.
    """
    if settings.auth_lectura_publica:
        return None
    # Reutiliza exactamente la validación de US-402 (401 uniforme si el token falta o es inválido).
    # El `request` viaja porque desde ADR-012 el token puede venir en la cookie `faro_sesion` y no
    # solo en el encabezado: si no se pasara, el frontend de React nunca autenticaría aquí.
    return get_current_user(request, credentials)
