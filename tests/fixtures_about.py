"""Fake de `RepositorioAbout` para la suite rápida del contrato (US-601).

Mismo espíritu que `fixtures_gold.py`: en memoria, sin Postgres, para que
`tests/test_api_contract.py` corra en cualquier máquina vía
`app.dependency_overrides[get_repositorio_about]`.
"""
from __future__ import annotations


class RepositorioAboutFake:
    """Devuelve conteos fijos, con una tabla ausente a propósito para ejercitar `SIN_DATO`."""

    def conteos_capas(self) -> list[dict]:
        return [
            {"capa": "bronze", "tabla": "formato911_2024_2025", "filas": 45276, "nota": None},
            {
                "capa": "bronze",
                "tabla": "conapo_*",
                "filas": None,
                "nota": "Todavía sin tabla ingerida para esta fuente.",
            },
            {"capa": "silver", "tabla": "escuela", "filas": 45276, "nota": None},
            {"capa": "gold", "tabla": "fact_escuela_ciclo", "filas": 45276, "nota": None},
            {
                "capa": "gold",
                "tabla": "cubo_pipeline",
                "filas": None,
                "nota": "Tabla no materializada todavía.",
            },
        ]


class RepositorioAboutSinPostgresFake:
    """Postgres inalcanzable: todo vuelve `None`/nota, nunca una excepción."""

    def conteos_capas(self) -> list[dict]:
        return [
            {
                "capa": capa,
                "tabla": "sin_datos",
                "filas": None,
                "nota": "Tabla no materializada todavía.",
            }
            for capa in ("bronze", "silver", "gold")
        ]
