"""Repositorio de métricas internas para `/admin/metrics` (US-413).

`frescura_por_fuente` lee `gold.cubo_pipeline` (DB-10, US-113, Deni Garrido): ese cubo ya
materializa fuente × fecha de ingesta con `SIN_DATO` explícito para las fuentes que nunca se han
ingerido. Aquí solo se toma el último `_ingested_at` real por fuente -- una fuente sin ingerir
simplemente **no aparece** en el dict (no se inventa una fecha ni se pone `null` como valor).

`RepositorioMetricas` sigue el mismo patrón `Protocol` + `Depends` inyectable que
`RepositorioGold` (US-411) y `RepositorioModelos` (US-412), para que la suite rápida del contrato
no dependa de Postgres.
"""
from __future__ import annotations

from datetime import datetime
from typing import Protocol

from sqlalchemy import Column, Date, DateTime, Integer, MetaData, String, Table, func, select
from sqlalchemy.engine import Engine

from src.api.db import get_engine

ESQUEMA_GOLD = "gold"


def _tabla_cubo_pipeline() -> Table:
    """`gold.cubo_pipeline` (Data_Model.md / DB-10) -- grano fuente × fecha_ingesta."""
    metadata = MetaData(schema=ESQUEMA_GOLD)
    return Table(
        "cubo_pipeline",
        metadata,
        Column("id_fuente", String, primary_key=True),
        Column("fuente", String, primary_key=True),
        Column("fecha_ingesta", Date, primary_key=True),
        Column("filas", Integer, nullable=True),
        Column("_ingested_at", DateTime(timezone=True), nullable=True),
        Column("source_url", String, nullable=True),
        Column("cobertura_pipeline", String),
    )


class RepositorioMetricas(Protocol):
    def obtener_frescura_por_fuente(self) -> dict[str, datetime]:
        """`{fuente: último _ingested_at real}` -- una fuente sin ingerir no aparece."""
        ...


class RepositorioMetricasPostgres:
    """Implementación real sobre `gold.cubo_pipeline`."""

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine or get_engine()
        self._cubo_pipeline = _tabla_cubo_pipeline()

    def obtener_frescura_por_fuente(self) -> dict[str, datetime]:
        cubo = self._cubo_pipeline
        ultima_ingesta = cubo.c["_ingested_at"]
        consulta = (
            select(cubo.c.fuente, func.max(ultima_ingesta).label("ultima_ingesta"))
            .where(ultima_ingesta.is_not(None))
            .group_by(cubo.c.fuente)
        )
        with self._engine.connect() as conexion:
            filas = conexion.execute(consulta).all()
        return {fuente: ultima for fuente, ultima in filas}


def get_repositorio_metricas() -> RepositorioMetricas:
    return RepositorioMetricasPostgres()
