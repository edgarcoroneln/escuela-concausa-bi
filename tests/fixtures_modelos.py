"""Fake de `RepositorioModelos` para la suite rápida del contrato (US-412, cierra BUG-010).

Implementa `src.api.repositorio_modelos.RepositorioModelos` en memoria, 100% datos sintéticos. Se
inyecta en `tests/test_api_contract.py` vía `app.dependency_overrides[get_repositorio_modelos]`,
mismo patrón que `RepositorioGoldFake` (`tests/fixtures_gold.py`, US-411) -- sin Postgres, sin
SQLite (no modela `gold` igual que Postgres).

Mismos CCT que `ESCUELAS_FAKE` (`tests/fixtures_gold.py`) para que las pruebas de `/escuelas` y de
`/predicciones` sean consistentes entre sí sobre la misma escuela sintética.
"""

from __future__ import annotations

from copy import deepcopy

from src.api.repositorio_modelos import RepositorioModelosNoDisponible

PREDICCIONES_FAKE: list[dict] = [
    {
        "cct": "09DPR0001A",
        "id_ciclo": "2024-2025",
        "indice_riesgo": 0.72,
        "driver_dominante": "D2",
        "recomendacion": "Coordinar con seguridad pública rutas escolares seguras y entornos protegidos.",
        "mlflow_run_id": "fake-run-ml01-0001",
        "cluster": None,  # ML-03 sin productor (BUG-010, US-321)
        # Contribuciones SHAP de ML-02 (BUG-053). Esta escuela las tiene las seis.
        "shap_d1": 0.11,
        "shap_d2": 0.47,
        "shap_d3": -0.05,
        "shap_d4": 0.09,
        "shap_d5": 0.0,
        "shap_d6": -0.12,
    },
    {
        "cct": "19DES0007C",
        "id_ciclo": "2024-2025",
        "indice_riesgo": 0.31,
        "driver_dominante": "D4",
        "recomendacion": "Ampliar conectividad y dotación de equipo de cómputo.",
        "mlflow_run_id": "fake-run-ml01-0002",
        "cluster": None,
        # D5 y D6 en `None` a proposito: son los dos drivers de cobertura parcial del proyecto
        # (agua regional, aire ~80 zonas urbanas), donde SIN_DATO es el caso NORMAL. Que el
        # fixture lo modele es lo que impide que alguien "arregle" un null colapsandolo a 0.0
        # y reintroduzca BUG-055 con datos reales.
        "shap_d1": 0.30,
        "shap_d2": 0.02,
        "shap_d3": 0.14,
        "shap_d4": 0.51,
        "shap_d5": None,
        "shap_d6": None,
    },
]


class RepositorioModelosFake:
    """Mismo contrato que `RepositorioModelosPostgres`, resuelto en memoria."""

    def __init__(self) -> None:
        self._predicciones = deepcopy(PREDICCIONES_FAKE)

    def obtener_prediccion(self, cct: str, id_ciclo: str) -> dict | None:
        for p in self._predicciones:
            if p["cct"] == cct and p["id_ciclo"] == id_ciclo:
                return dict(p)
        return None

    def listar_predicciones(self, ccts: list[str], id_ciclo: str) -> list[dict]:
        return [
            dict(p) for p in self._predicciones if p["cct"] in ccts and p["id_ciclo"] == id_ciclo
        ]


class RepositorioModelosNoDisponibleFake:
    """Simula un Postgres que nunca responde a tiempo (US-416).

    Usado para probar el mapeo a 503 `service_unavailable` en `test_api_contract.py` sin tocar
    Postgres real -- mismo espíritu que `RepositorioModelosFake`, pero para el camino de error.
    """

    def obtener_prediccion(self, cct: str, id_ciclo: str) -> dict | None:
        raise RepositorioModelosNoDisponible("Postgres no respondió en 3000ms.")

    def listar_predicciones(self, ccts: list[str], id_ciclo: str) -> list[dict]:
        raise RepositorioModelosNoDisponible("Postgres no respondió en 3000ms.")
