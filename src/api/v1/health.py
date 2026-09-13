"""Salud y versión (endpoints públicos, §3.1 del contrato)."""
from __future__ import annotations

import os

from fastapi import APIRouter

from src.api.repositorio_gold import ANCLA_SIGMOIDE, CORTE_ATENCION_MEDIA, LINEA_DE_ALERTA
from src.api.schemas import CortesAtencionOut, HealthOut, VersionOut

router = APIRouter(tags=["Salud"])


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    """Liveness del contrato v1 (público, sin token)."""
    return HealthOut(status="ok")


@router.get("/version", response_model=VersionOut)
def version() -> VersionOut:
    """Versión de la API, commit desplegado y cortes del nivel de atención (público, sin token).

    Los cortes viajan aquí, y no en una ruta nueva, porque son **metadatos del contrato**: cambian
    con una decisión (`DEC-019`, `DEC-023`), no con los datos, y el front los necesita **antes** de
    iniciar sesión para poder etiquetar lo que ya tenga en pantalla.
    """
    return VersionOut(
        api="v1",
        commit=os.getenv("GIT_COMMIT", "dev"),
        cortes_atencion=CortesAtencionOut(
            alta=LINEA_DE_ALERTA,
            media=CORTE_ATENCION_MEDIA,
            ancla_calibracion=ANCLA_SIGMOIDE,
        ),
    )
