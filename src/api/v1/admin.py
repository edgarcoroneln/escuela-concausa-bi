"""Administración `/admin/*` — solo `analista` (§3.6).

RBAC ya se aplica a nivel de router (`src/api/v1/__init__.py`, US-403): todo `/admin/*` exige
`Depends(require_role(Rol.analista))`, así que aquí no hay que repetirlo. El agente y los
endpoints de datos **nunca** ejecutan escritura/borrado.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.orquestador import DAGS_VALIDOS, Orquestador, OrquestadorError, get_orquestador
from src.api.repositorio_metricas import RepositorioMetricas, get_repositorio_metricas
from src.api.schemas import MetricsOut, PipelineRunIn, PipelineRunOut

router = APIRouter(prefix="/admin", tags=["Administración"])


@router.post("/pipeline/run", response_model=PipelineRunOut, status_code=status.HTTP_202_ACCEPTED)
def pipeline_run(
    body: PipelineRunIn, orquestador: Orquestador = Depends(get_orquestador)
) -> PipelineRunOut:
    """Encola una corrida real de `body.dag` en Airflow (rol: **analista**).

    `dag` se valida contra `DAGS_VALIDOS` (los DAG reales de `dags/`) -- 422 si no está en la
    lista, nunca se le pasa texto libre a Airflow.
    """
    if body.dag not in DAGS_VALIDOS:
        # 422 literal, no status.HTTP_422_UNPROCESSABLE_ENTITY (deprecado en Starlette reciente,
        # ver _ERROR_POR_STATUS en app.py que ya usa el literal por portabilidad de versión).
        raise HTTPException(
            422, detail=f"'{body.dag}' no es un DAG válido. Usa uno de: {', '.join(DAGS_VALIDOS)}."
        )
    try:
        run_id = orquestador.disparar_dag(body.dag, ciclo=body.ciclo)
    except OrquestadorError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail="Airflow no aceptó la corrida.") from exc
    return PipelineRunOut(run_id=run_id, estado="accepted")


@router.get("/export")
def export(
    tabla: str = Query(...),
    ciclo: str | None = Query(None),
    formato: str = Query("csv"),
) -> dict:
    """Exporta datos en bruto (rol: **analista**). En el stub devuelve una referencia, no el stream."""
    return {
        "tabla": tabla,
        "ciclo": ciclo,
        "formato": formato,
        "url": f"gs://faro-exports/{tabla}.{formato}",
    }


@router.get("/metrics", response_model=MetricsOut)
def metrics(repo: RepositorioMetricas = Depends(get_repositorio_metricas)) -> MetricsOut:
    """Métricas internas (rol: **analista**): frescura real por fuente (`gold.cubo_pipeline`,
    US-113) y estado de las suites de Great Expectations.

    `suites_ge_en_verde` es `None` (SIN_DATO explícito): no hay checkpoints de GE persistidos
    todavía de dónde leer un resultado real -- avisado a Luis García (dueño de las suites) y a
    C2/C3 (cambio de forma del contrato, ver `API_Specification.md` §4).
    """
    return MetricsOut(
        frescura_por_fuente=repo.obtener_frescura_por_fuente(),
        suites_ge_en_verde=None,
    )
