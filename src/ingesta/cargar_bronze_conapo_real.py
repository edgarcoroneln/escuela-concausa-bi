"""
Carga el Parquet real de DS-08 CONAPO (Emilio Galnares Ruiz) a `bronze.conapo`, en el
formato LARGO (municipio × año × grupo_edad) que `dbt/models/silver/poblacion_municipio.sql`
espera -- no en el formato ANCHO en el que llega la fuente.

Contexto (BUG-048, 2026-09-05): el hueco de completitud de D2/D1 no era solo SESNSP -- D2
también usa la población municipal de CONAPO como denominador de la tasa, y hasta hoy
`bronze.conapo` solo tenía el fixture (`conapo_sample`, 36 filas). Emilio Galnares compartió
por Teams el Parquet real (252 450 filas, 2 475 municipios, 32 entidades, 1990-2040),
verificado en vivo antes de programar nada:
- La suma de las 18 columnas de grupo de edad coincide exactamente con `POB_TOTAL` en las
  252 450 filas (0 discrepancias) -- confirma que el ancho cubre toda la población sin huecos
  ni traslape.
- El grano real es municipio × sexo(HOMBRES/MUJERES) × año, no municipio × año -- 2 475 × 2 ×
  51 = 252 450, exacto.

Tres decisiones tomadas aquí, ninguna adivinada en silencio:

1. SE AGREGA SEXO Y SE HACE UNPIVOT DE EDAD EN EL LOADER, NO EN SILVER. El dedup de
   `poblacion_municipio.sql` es `row_number() over (partition by cve_mun, anio, grupo_edad
   order by _ingested_at desc)` -- **no suma**, solo se queda con la fila más reciente por esa
   llave. Si Bronze llegara con HOMBRES y MUJERES como filas separadas del mismo
   (cve_mun, anio, grupo_edad), ambas comparten el mismo `_ingested_at` de este load y el
   dedup se quedaría con una sola de las dos **de forma no determinista** -- perdiendo la
   mitad de la población. Por eso este loader sea el que reduce sexo con `sum()` ANTES de
   escribir Bronze, dejando el grano único que Silver espera. Mismo principio que el
   extractor de SESNSP (`extractor_sesnsp.py`): agregar donde el contrato original ya lo
   esperaba, no tocar el modelo de Silver de otra persona.

2. `cve_mun` SE USA TAL CUAL LLEGA (ya viene con 5 dígitos, ej. "01001"). No se re-deriva
   porque `dbt/macros/normalize_cve_mun.sql` ya contempla ese caso: si detecta que `cve_mun`
   hace match con `^[0-9]{5}$` lo deja pasar sin tocar, y solo concatena `cve_ent`+`cve_mun`
   cuando NO es de 5 dígitos. Verificado leyendo el macro antes de decidir esto, no asumido.

3. `_source` SE NORMALIZA A `'DS-08_CONAPO'`, DISTINTO AL QUE TRAE EL PARQUET DE EMILIO
   (`'DS-08_CONAPO_Proyecciones'`). `src/ingesta/extractor_conapo.py` define
   `SOURCE_NAME = "DS-08_CONAPO"`, y `dbt/models/gold/cubo_pipeline.sql` filtra la fuente
   de DS-08 por match EXACTO de ese literal (`where _source = 'DS-08_CONAPO'`). Si este
   loader conservara el `_source` tal como llegó de Emilio, cubo_pipeline seguiría sin ver
   los datos reales de DS-08 pese a estar ya cargados. Se documenta aquí en vez de
   silenciarlo porque es un cambio de valor sobre el dato de otra persona (Emilio), no un
   invento propio -- el valor de destino ya existía en el contrato del proyecto, solo se
   está honrando.

Uso:
    python -m src.ingesta.cargar_bronze_conapo_real --parquet ruta/al/ds08_conapo.parquet
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

TABLA = "conapo"
SOURCE_NAME = "DS-08_CONAPO"  # debe coincidir con extractor_conapo.py y cubo_pipeline.sql

COLUMNAS_ANCHO_REQUERIDAS = {
    "CLAVE_ENT", "cve_mun", "ANO", "POB_TOTAL",
    "POB_00_04", "POB_05_09", "POB_010_014", "POB_015_019", "POB_20_24", "POB_25_29",
    "POB_30_34", "POB_35_39", "POB_40_44", "POB_45_49", "POB_50_54", "POB_55_59",
    "POB_60_64", "POB_65_69", "POB_70_74", "POB_75_79", "POB_80_84", "POB_85_mm",
}
COLUMNAS_EDAD = [c for c in COLUMNAS_ANCHO_REQUERIDAS if c.startswith("POB_") and c != "POB_TOTAL"]

COLUMNAS_BRONZE = [
    "cve_ent", "cve_mun", "anio", "grupo_edad", "poblacion",
    "_ingested_at", "_source", "_source_url",
]


def _dsn() -> str:
    return (
        f"host={os.environ.get('POSTGRES_HOST', 'localhost')} "
        f"port={os.environ.get('POSTGRES_PORT', '5432')} "
        f"dbname={os.environ.get('POSTGRES_DB', 'escuela_concausa_db')} "
        f"user={os.environ.get('POSTGRES_USER', 'postgres')} "
        f"password={os.environ.get('POSTGRES_PASSWORD', '')}"
    )


def _validar_y_transformar(df: pd.DataFrame, source_url: str) -> pd.DataFrame:
    faltantes = COLUMNAS_ANCHO_REQUERIDAS - set(df.columns)
    if faltantes:
        raise ValueError(f"{SOURCE_NAME}: faltan columnas esperadas: {sorted(faltantes)}")
    if df.empty:
        raise ValueError(f"{SOURCE_NAME}: Parquet vacío")

    # Sanity check real, no asumido: las columnas de edad deben sumar POB_TOTAL en TODAS las
    # filas -- si no, alguna columna de edad falta o el archivo no es el esperado.
    suma_edades = df[COLUMNAS_EDAD].sum(axis=1)
    mismatch = df[suma_edades != df["POB_TOTAL"]]
    if not mismatch.empty:
        raise ValueError(
            f"{SOURCE_NAME}: {len(mismatch)} fila(s) donde la suma de grupos de edad no "
            "coincide con POB_TOTAL -- no se asume que el resto esté bien, revisar el "
            "archivo a mano antes de cargar"
        )

    largo = df.melt(
        id_vars=["CLAVE_ENT", "cve_mun", "ANO"],
        value_vars=COLUMNAS_EDAD,
        var_name="grupo_edad_raw",
        value_name="poblacion",
    )
    largo["grupo_edad"] = largo["grupo_edad_raw"].str.replace(r"^POB_", "", regex=True)

    agregado = (
        largo.groupby(["CLAVE_ENT", "cve_mun", "ANO", "grupo_edad"], as_index=False)["poblacion"]
        .sum()
    )

    ingested_at = datetime.now(timezone.utc)
    salida = pd.DataFrame({
        "cve_ent": agregado["CLAVE_ENT"].astype(str),
        "cve_mun": agregado["cve_mun"].astype(str),
        "anio": agregado["ANO"].astype("int64"),
        "grupo_edad": agregado["grupo_edad"],
        "poblacion": agregado["poblacion"].astype("int64"),
        "_ingested_at": ingested_at,
        "_source": SOURCE_NAME,
        "_source_url": source_url,
    })
    return salida[COLUMNAS_BRONZE]


def _tipo_postgres(serie: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(serie.dtype):
        return "TIMESTAMPTZ"
    if pd.api.types.is_integer_dtype(serie.dtype):
        return "BIGINT"
    if pd.api.types.is_float_dtype(serie.dtype):
        return "DOUBLE PRECISION"
    return "TEXT"


def _valor_python(valor):
    if valor is None:
        return None
    try:
        if pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(valor, np.generic):
        return valor.item()
    if isinstance(valor, pd.Timestamp):
        return valor.to_pydatetime()
    return valor


def cargar(parquet_path: str) -> tuple[int, int]:
    """Transforma y carga el Parquet real de DS-08 a `bronze.conapo`, idempotente por snapshot."""
    df_ancho = pd.read_parquet(parquet_path)
    source_url = str(df_ancho["_source_url"].iloc[0]) if "_source_url" in df_ancho.columns else (
        "https://www.datos.gob.mx/dataset/proyecciones-de-poblacion/"
        "resource/3c3092be-583e-4490-8c23-67ef9a64b198"
    )
    df = _validar_y_transformar(df_ancho, source_url)

    columnas = list(df.columns)
    snapshot_source = str(df["_source"].iloc[0])
    snapshot_ingested = pd.Timestamp(df["_ingested_at"].iloc[0]).to_pydatetime()

    with psycopg2.connect(_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS bronze")
            cur.execute(
                "select column_name from information_schema.columns "
                "where table_schema='bronze' and table_name=%s order by ordinal_position",
                (TABLA,),
            )
            existentes = [r[0] for r in cur.fetchall()]
            if not existentes:
                defs = [
                    sql.SQL("{} {}").format(sql.Identifier(c), sql.SQL(_tipo_postgres(df[c])))
                    for c in columnas
                ]
                cur.execute(
                    sql.SQL("CREATE TABLE {}.{} ({})").format(
                        sql.Identifier("bronze"), sql.Identifier(TABLA), sql.SQL(", ").join(defs)
                    )
                )
            elif existentes != columnas:
                raise ValueError(f"bronze.{TABLA}: schema existente no coincide: {existentes}")

            cur.execute(
                sql.SQL(
                    'select count(*) from {}.{} where "_source"=%s and "_ingested_at"=%s'
                ).format(sql.Identifier("bronze"), sql.Identifier(TABLA)),
                (snapshot_source, snapshot_ingested),
            )
            existentes_snapshot = int(cur.fetchone()[0])
            if existentes_snapshot:
                if existentes_snapshot != len(df):
                    raise ValueError(
                        f"bronze.{TABLA}: snapshot parcial ({existentes_snapshot}/{len(df)} filas)"
                    )
                return 0, existentes_snapshot

            registros = [
                tuple(_valor_python(v) for v in fila)
                for fila in df.itertuples(index=False, name=None)
            ]
            insert = sql.SQL("INSERT INTO {}.{} ({}) VALUES %s").format(
                sql.Identifier("bronze"), sql.Identifier(TABLA),
                sql.SQL(", ").join(sql.Identifier(c) for c in columnas),
            )
            execute_values(cur, insert.as_string(conn), registros, page_size=1000)
        conn.commit()

    return len(df), len(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", required=True, help="Ruta al Parquet real de DS-08 (ancho, tal como lo entregó Emilio)")
    args = parser.parse_args()

    insertadas, total = cargar(args.parquet)
    print(f"OK DS-08: bronze.{TABLA} — {insertadas} insertadas / {total} snapshot")
