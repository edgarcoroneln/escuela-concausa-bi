"""Administración `/admin/*` — solo `analista` (§3.6).

RBAC ya se aplica a nivel de router (`src/api/v1/__init__.py`, US-403): todo `/admin/*` exige
`Depends(require_role(Rol.analista))`, así que aquí no hay que repetirlo. El agente y los
endpoints de datos **nunca** ejecutan escritura/borrado.
"""
from __future__ import annotations

import csv
import io
import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from src.api.orquestador import DAGS_VALIDOS, Orquestador, OrquestadorError, get_orquestador
from src.api.repositorio_export import RepositorioExport, get_repositorio_export
from src.api.repositorio_metricas import RepositorioMetricas, get_repositorio_metricas
from src.api.schemas import MetricsOut, PipelineRunIn, PipelineRunOut

router = APIRouter(prefix="/admin", tags=["Administración"])

# Mismos nombres que TABLAS_EXPORTABLES de repositorio_export.py, como Literal para que una
# tabla fuera de la whitelist responda 422 por validación de Pydantic -- nunca una relación
# arbitraria (pedido de seguridad de Luis Téllez, Tech Lead C5, 2026-08-27).
TablaExportable = Literal[
    "dim_escuela", "dim_municipio", "fact_escuela_ciclo", "predicciones", "recomendaciones"
]
FormatoExportable = Literal["csv", "json"]


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
    tabla: TablaExportable = Query(...),
    ciclo: str | None = Query(None),
    formato: FormatoExportable = Query("csv"),
    repo: RepositorioExport = Depends(get_repositorio_export),
) -> StreamingResponse:
    """Exporta `gold.<tabla>` real en CSV o JSON (rol: **analista**).

    `tabla` y `formato` se validan contra una whitelist (`Literal` -> 422 fuera de lista, nunca
    una relación arbitraria). El export completo a GCS queda **fuera de alcance de US-413**: no
    existe bucket ni permisos de Cloud Storage en la service account del API (confirmado por Luis
    Téllez, Tech Lead C5, 2026-08-27) -- mientras tanto se regresa el *stream* real desde Postgres,
    viable porque Gold en producción son ~25 escuelas.
    """
    filas = repo.exportar(tabla, ciclo=ciclo)
    nombre_archivo = f"{tabla}.{formato}"

    if formato == "json":
        return StreamingResponse(
            iter([json.dumps(filas, default=str)]),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
        )

    buffer = io.StringIO()
    if filas:
        escritor = csv.DictWriter(buffer, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )


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
