"""Fake de `Orquestador` para la suite rápida del contrato (US-413).

Mismo patrón que `RepositorioGoldFake` (US-411) y `RepositorioModelosFake` (US-412): se inyecta en
`tests/test_api_contract.py` vía `app.dependency_overrides[get_orquestador]` para que
`/admin/pipeline/run` no dependa de que Airflow esté corriendo.
"""
from __future__ import annotations

from src.api.orquestador import OrquestadorError


class OrquestadorFake:
    """Registra las corridas "disparadas" en memoria, sin llamar a Airflow.

    `fallar=True` simula que Airflow rechazó/no respondió la corrida -- para probar que el
    endpoint responde 502 y nunca inventa un `run_id` (ver `test_admin_pipeline_run_airflow_caido_502`).
    """

    def __init__(self, *, fallar: bool = False) -> None:
        self.corridas: list[tuple[str, str]] = []
        self._fallar = fallar

    def disparar_dag(self, dag_id: str, *, ciclo: str) -> str:
        if self._fallar:
            raise OrquestadorError(f"Airflow no aceptó la corrida de {dag_id} (fake de prueba).")
        self.corridas.append((dag_id, ciclo))
        return f"fake__{dag_id}__{ciclo}"
