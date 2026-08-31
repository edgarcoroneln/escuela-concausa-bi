"""Repositorio de exportación de datos en bruto para `/admin/export` (US-413).

Whitelist explícita de tablas exportables -- nunca una relación arbitraria (pedido de seguridad
de Luis Téllez, Tech Lead C5, 2026-08-27): las mismas 5 tablas de Gold ya modeladas en `db.py`,
no las 9 `gold.cubo_*` (esas son para Superset, no para exportar en bruto).

El export completo a GCS (bucket + signed URLs) queda **fuera de alcance de US-413**: no existe
bucket `faro-exports` ni permisos de Cloud Storage en la service account del API (verificado por
Luis Téllez el 2026-08-27) -- provisionarlo es cambio de seguridad de C5, gated a cuando exista
contenido real que exportar (ver `API_Specification.md` §3.6). Mientras tanto, este repositorio
entrega las filas reales directo desde Postgres -- viable porque Gold en producción es chico
(~25 escuelas).
"""
from __future__ import annotations

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.engine import Engine

from src.api.db import get_engine, get_tablas

TABLAS_EXPORTABLES = (
    "dim_escuela",
    "dim_municipio",
    "fact_escuela_ciclo",
    "predicciones",
    "recomendaciones",
)

# Tablas con grano por ciclo escolar -- `ciclo` solo filtra estas (igual que /municipios ignora
# `ciclo` en US-411: se acepta en la firma por paridad y se ignora si no aplica).
_COLUMNA_CICLO = {
    "fact_escuela_ciclo": "id_ciclo",
    "predicciones": "id_ciclo",
    "recomendaciones": "id_ciclo",
}


class RepositorioExport(Protocol):
    def exportar(self, tabla: str, *, ciclo: str | None) -> list[dict]:
        """Filas de `gold.<tabla>`, filtradas por `ciclo` cuando la tabla tiene esa columna."""
        ...


class RepositorioExportPostgres:
    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine or get_engine()
        _, dim_escuela, dim_municipio, fact, predicciones, recomendaciones = get_tablas()
        self._tablas = {
            "dim_escuela": dim_escuela,
            "dim_municipio": dim_municipio,
            "fact_escuela_ciclo": fact,
            "predicciones": predicciones,
            "recomendaciones": recomendaciones,
        }

    def exportar(self, tabla: str, *, ciclo: str | None) -> list[dict]:
        tabla_sql = self._tablas[tabla]
        consulta = select(tabla_sql)
        columna_ciclo = _COLUMNA_CICLO.get(tabla)
        if ciclo and columna_ciclo:
            consulta = consulta.where(tabla_sql.c[columna_ciclo] == ciclo)
        with self._engine.connect() as conexion:
            return [dict(fila) for fila in conexion.execute(consulta).mappings().all()]


def get_repositorio_export() -> RepositorioExport:
    return RepositorioExportPostgres()
