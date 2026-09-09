"""Conexión a Postgres para las lecturas reales sobre Gold (US-411).

Define el motor SQLAlchemy y las tablas de `gold.*` que consultan los endpoints de
`src/api/v1/gold.py`, como reemplazo de `mock_data` (US-401). Mismo estilo **SQLAlchemy Core**
(`Table`/`MetaData` explícitos, no ORM declarativo) que ya usa `src/modelos/publicar_gold.py`,
para no introducir un segundo patrón de acceso a datos en el proyecto.

Las columnas y tipos replican exactamente lo que materializa `dbt/models/gold/` (verificado
contra Postgres local, no inventado): `SIN_DATO` se modela como texto libre en las columnas
`d#_cobertura` (no como enum de Postgres), igual que lo define `dbt/models/gold/*.sql`.
"""
from __future__ import annotations

from functools import lru_cache

from sqlalchemy import (
    Column,
    Float,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    create_engine,
)
from sqlalchemy.engine import Engine

from src.api.config import get_settings

ESQUEMA_GOLD = "gold"


@lru_cache
def get_engine() -> Engine:
    """Motor de conexión cacheado (una sola vez por proceso), igual que `get_settings()`."""
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def _metadatos() -> tuple[MetaData, Table, Table, Table, Table]:
    """Define las tablas de Gold que consulta esta API (Data_Model.md §6)."""
    metadata = MetaData(schema=ESQUEMA_GOLD)

    dim_escuela = Table(
        "dim_escuela",
        metadata,
        Column("cct", String(10), primary_key=True),
        Column("nombre", String),
        Column("nivel", String),
        Column("sostenimiento", String),
        Column("latitud", Float, nullable=True),
        Column("longitud", Float, nullable=True),
        Column("cve_ent", String(2)),
        Column("cve_mun", String(5)),
        Column("agua", String, nullable=True),
        Column("drenaje", String, nullable=True),
        Column("electricidad", String, nullable=True),
        Column("sanitarios", String, nullable=True),
        Column("internet", String, nullable=True),
        Column("computadoras", String, nullable=True),
    )

    dim_municipio = Table(
        "dim_municipio",
        metadata,
        Column("cve_mun", String(5), primary_key=True),
        Column("cve_ent", String(2)),
        Column("nombre_municipio", String),
        Column("nombre_entidad", String),
        Column("poblacion", Numeric, nullable=True),
        Column("indice_rezago_social", Float, nullable=True),
        Column("grado_rezago", String, nullable=True),
        Column("pobreza_pct", Float, nullable=True),
    )

    fact_escuela_ciclo = Table(
        "fact_escuela_ciclo",
        metadata,
        Column("cct", String(10), primary_key=True),
        Column("id_ciclo", String, primary_key=True),
        Column("cve_mun", String(5)),
        Column("matricula_total", Integer),
        Column("matricula_ciclo_anterior", Integer),
        Column("variacion_matricula", Float),
        Column("indice_completitud_drivers", Numeric),
        Column("d1", Float, nullable=True),
        Column("d2", Float, nullable=True),
        Column("d3", Numeric, nullable=True),
        Column("d4", Numeric, nullable=True),
        Column("d5", Float, nullable=True),
        Column("d6", Float, nullable=True),
        Column("d1_cobertura", String),
        Column("d2_cobertura", String),
        Column("d3_cobertura", String),
        Column("d4_cobertura", String),
        Column("d5_cobertura", String),
        Column("d6_cobertura", String),
    )

    # gold.predicciones (Data_Model.md §4.5) — salida de ML-01. Se consulta por JOIN, nunca
    # se duplica en fact_escuela_ciclo (regla ratificada, ver Screen_Specs.md KPI-03/04).
    # `grano` (DEC-010, 2026-08-23): discriminador `escuela` | `municipio_nivel` -- las lecturas
    # a nivel escuela (US-412) siempre filtran `grano == "escuela"`, ver BUG-010 §Nota.
    predicciones = Table(
        "predicciones",
        metadata,
        Column("cct", String(10), primary_key=True),
        Column("id_ciclo", String, primary_key=True),
        Column("modelo", String, primary_key=True),
        Column("grano", String),
        Column("valor", Float),
        Column("indice_riesgo", Float),
        Column("probabilidad", Float, nullable=True),
        Column("mlflow_run_id", String),
    )

    # gold.recomendaciones (Data_Model.md §4.5) — salida de ML-02.
    #
    # `shap_d*` son la contribución de cada driver al riesgo, que alimenta
    # `/predicciones/{cct}/explicacion` (BUG-053). Las escribe `publicar_gold.py` desde
    # `entrenar_ml02.explicar_driver` (C3, commit 924c8b4).
    #
    # **Nullable a propósito**: `NULL` significa SIN_DATO ("no se pudo calcular"), que NO es lo
    # mismo que `0.0` ("este driver no contribuyó"). Confundirlos fue BUG-055, y con datos reales
    # es peor: la explicación responde *por qué* una escuela está en riesgo, así que un cero
    # inventado ahí es una afirmación falsa sobre la causa. C3 escribe `NULL` (su validador
    # convierte NaN/infinito), la API lo transporta como `null` y nadie lo colapsa por el camino.
    recomendaciones = Table(
        "recomendaciones",
        metadata,
        Column("cct", String(10), primary_key=True),
        Column("id_ciclo", String, primary_key=True),
        Column("driver_dominante", String),
        Column("recomendacion", String),
        Column("prioridad", String),
        Column("shap_d1", Float, nullable=True),
        Column("shap_d2", Float, nullable=True),
        Column("shap_d3", Float, nullable=True),
        Column("shap_d4", Float, nullable=True),
        Column("shap_d5", Float, nullable=True),
        Column("shap_d6", Float, nullable=True),
    )

    return metadata, dim_escuela, dim_municipio, fact_escuela_ciclo, predicciones, recomendaciones


@lru_cache
def get_tablas() -> tuple[MetaData, Table, Table, Table, Table, Table]:
    """`(metadata, dim_escuela, dim_municipio, fact_escuela_ciclo, predicciones,
    recomendaciones)`, cacheado."""
    return _metadatos()
