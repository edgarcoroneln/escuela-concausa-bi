"""Router agregado de la v1 del contrato FARO.

Reúne todos los subrouters de §3 bajo un único `api_v1_router` que la app monta en `/api/v1`.

**RBAC (US-403)** se aplica aquí, a nivel de `include_router`, para no invadir los routers de
otras células (gold/predicciones son de US-411/US-412). Política:

- `health`, `auth` → **públicos** (probes de Cloud Run y flujo de login).
- `gold`, `predicciones`, `agente` → **lectura** vía `require_lectura` (pública u obligatoria según
  el flag híbrido `AUTH_LECTURA_PUBLICA`, ver ADR-004 §RBAC).
- `admin` → **solo `analista`** vía `require_role`, siempre (independiente del flag).
- `about` (US-601) → **público siempre**, independiente de `AUTH_LECTURA_PUBLICA`: es metadata del
  sistema (arquitectura, modelo de datos, stack), no dato de escuela, así que no tiene sentido que
  se oculte cuando C4 endurezca la lectura de Gold.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.schemas import Rol
from src.api.security.rbac import require_lectura, require_role
from src.api.v1 import about, admin, agente, auth, gold, health, predicciones

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(about.router)
api_v1_router.include_router(gold.router, dependencies=[Depends(require_lectura)])
api_v1_router.include_router(predicciones.router, dependencies=[Depends(require_lectura)])
api_v1_router.include_router(agente.router, dependencies=[Depends(require_lectura)])
api_v1_router.include_router(admin.router, dependencies=[Depends(require_role(Rol.analista))])

__all__ = ["api_v1_router"]
