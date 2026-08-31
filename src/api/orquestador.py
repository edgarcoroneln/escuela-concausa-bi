"""Cliente del orquestador Airflow para `/admin/pipeline/run` (US-413).

Aísla la llamada HTTP a la API REST de Airflow detrás de un `Protocol` inyectado con
`Depends(get_orquestador)` -- mismo patrón que `RepositorioGold` (`repositorio_gold.py`, US-411):
la suite rápida del contrato sustituye `OrquestadorAirflow` por un fake en memoria, así que las
pruebas no dependen de que Airflow esté corriendo.

`DAGS_VALIDOS` es la whitelist real (los 6 `dag_id` que existen en `dags/`, ver `grep dag_id
dags/*.py`) -- un `dag` fuera de esta lista responde 422 antes de intentar tocar Airflow, nunca
texto libre hacia la API del orquestador.
"""
from __future__ import annotations

from typing import Protocol
from uuid import uuid4

import httpx

from src.api.config import get_settings

DAGS_VALIDOS = (
    "dag_anual",
    "dag_bienal",
    "dag_censal_estatico",
    "dag_diario",
    "dag_horario",
    "dag_mensual",
)


class OrquestadorError(RuntimeError):
    """Airflow rechazó la corrida o no respondió -- nunca se inventa un `run_id` si esto pasa."""


class Orquestador(Protocol):
    def disparar_dag(self, dag_id: str, *, ciclo: str) -> str:
        """Encola una corrida de `dag_id` y devuelve su `run_id`."""
        ...


class OrquestadorAirflow:
    """Implementación real: `POST` a la API REST estable de Airflow 2.x."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.airflow_base_url
        self._auth = (settings.airflow_www_user_username, settings.airflow_www_user_password)

    def disparar_dag(self, dag_id: str, *, ciclo: str) -> str:
        run_id = f"faro__{dag_id}__{ciclo}__{uuid4().hex[:8]}"
        try:
            respuesta = httpx.post(
                f"{self._base_url}/api/v1/dags/{dag_id}/dagRuns",
                json={"dag_run_id": run_id, "conf": {"ciclo": ciclo}},
                auth=self._auth,
                timeout=10.0,
            )
            respuesta.raise_for_status()
        except httpx.HTTPError as exc:
            raise OrquestadorError(f"Airflow no aceptó la corrida de {dag_id}.") from exc
        return run_id


def get_orquestador() -> Orquestador:
    return OrquestadorAirflow()
