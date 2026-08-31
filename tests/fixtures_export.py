"""Fake de `RepositorioExport` para la suite rápida del contrato (US-413)."""
from __future__ import annotations

from copy import deepcopy

DATOS_FAKE: dict[str, list[dict]] = {
    "dim_escuela": [
        {"cct": "09DPR0001A", "nombre": "Primaria Benito Juárez", "nivel": "PRIMARIA"},
        {"cct": "15DPR0100B", "nombre": "Primaria Sor Juana Inés", "nivel": "PRIMARIA"},
    ],
    "dim_municipio": [
        {"cve_mun": "09010", "nombre_municipio": "Álvaro Obregón"},
    ],
    "fact_escuela_ciclo": [
        {"cct": "09DPR0001A", "id_ciclo": "2024-2025", "matricula_total": 480},
        {"cct": "09DPR0001A", "id_ciclo": "2023-2024", "matricula_total": 505},
    ],
    "predicciones": [],
    "recomendaciones": [],
}


class RepositorioExportFake:
    def __init__(self) -> None:
        self._datos = deepcopy(DATOS_FAKE)

    def exportar(self, tabla: str, *, ciclo: str | None) -> list[dict]:
        filas = self._datos.get(tabla, [])
        if ciclo:
            filas = [f for f in filas if f.get("id_ciclo") == ciclo]
        return [dict(f) for f in filas]
