"""Fake de `Orquestador` para la suite rápida del contrato (US-413).

Mismo patrón que `RepositorioGoldFake` (US-411) y `RepositorioModelosFake` (US-412): se inyecta en
`tests/test_api_contract.py` vía `app.dependency_overrides[get_orquestador]` para que
`/admin/pipeline/run` no dependa de que Airflow esté corriendo.
"""
from __future__ import annotations


class OrquestadorFake:
    """Registra las corridas "disparadas" en memoria, sin llamar a Airflow."""

    def __init__(self) -> None:
        self.corridas: list[tuple[str, str]] = []

    def disparar_dag(self, dag_id: str, *, ciclo: str) -> str:
        self.corridas.append((dag_id, ciclo))
        return f"fake__{dag_id}__{ciclo}"
