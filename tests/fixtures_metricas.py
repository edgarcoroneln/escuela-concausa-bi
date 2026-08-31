"""Fake de `RepositorioMetricas` para la suite rápida del contrato (US-413).

Mismo patrón que `RepositorioGoldFake` (US-411): datos sintéticos en memoria, sin Postgres.
"""
from __future__ import annotations

from datetime import datetime, timezone

FRESCURA_FAKE: dict[str, datetime] = {
    "DS-04_SESNSP": datetime(2026, 8, 20, 6, 0, tzinfo=timezone.utc),
    "DS-05_SINAICA": datetime(2026, 8, 27, 5, 0, tzinfo=timezone.utc),
    # DS-06_CONAGUA_SINA no aparece a propósito: sin ingerir todavía (SIN_DATO), no se inventa.
}


class RepositorioMetricasFake:
    def obtener_frescura_por_fuente(self) -> dict[str, datetime]:
        return dict(FRESCURA_FAKE)
