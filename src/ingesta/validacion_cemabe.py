"""Validaciones Great Expectations de DS-03 CEMABE sobre Silver."""

from __future__ import annotations

import logging
import os

import pandas as pd
import psycopg2

import great_expectations as gx

logger = logging.getLogger(__name__)

GE_CONTEXT_DIR = "great_expectations"
SUITE_NAME = "suite_ds03_cemabe"
DRIVERS = (
    "agua",
    "drenaje",
    "electricidad",
    "sanitarios",
    "internet",
    "computadoras",
)
VALORES_DRIVER = ["0", "1", "SIN_DATO"]


def _dsn() -> str:
    return (
        f"host={os.environ.get('POSTGRES_HOST', 'localhost')} "
        f"port={os.environ.get('POSTGRES_PORT', '5432')} "
        f"dbname={os.environ.get('POSTGRES_DB', 'escuela_concausa_db')} "
        f"user={os.environ.get('POSTGRES_USER', 'postgres')} "
        f"password={os.environ.get('POSTGRES_PASSWORD', '')}"
    )


def cargar_silver() -> pd.DataFrame:
    """Lee el contrato conformado de DS-03 sin modificar la base de datos."""
    query = """
        select
            cct,
            agua,
            drenaje,
            electricidad,
            sanitarios,
            internet,
            computadoras
        from silver.cemabe
    """
    with psycopg2.connect(_dsn()) as conn, conn.cursor() as cur:
        cur.execute(query)
        columnas = [descripcion.name for descripcion in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columnas)


def construir_suite(context: gx.data_context.AbstractDataContext) -> gx.ExpectationSuite:
    """Define las reglas de calidad del contrato Silver de DS-03."""
    suite = context.suites.add_or_update(gx.ExpectationSuite(name=SUITE_NAME))

    # Llave conformada y grano de una fila por escuela.
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="cct"))
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="cct"))
    suite.add_expectation(
        gx.expectations.ExpectColumnValueLengthsToEqual(column="cct", value=10)
    )

    # Los drivers binarios representan ausencia explícitamente como SIN_DATO.
    for columna in DRIVERS:
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(column=columna)
        )
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeInSet(
                column=columna, value_set=VALORES_DRIVER
            )
        )

    return suite


def validar(
    df: pd.DataFrame,
    context: gx.data_context.AbstractDataContext,
) -> gx.core.expectation_validation_result.ExpectationSuiteValidationResult:
    """Valida un DataFrame con el contrato de `silver.cemabe`."""
    data_source = context.data_sources.add_or_update_pandas(name="pandas_ds03")
    if "ds03_cemabe" in data_source.get_asset_names():
        data_asset = data_source.get_asset("ds03_cemabe")
    else:
        data_asset = data_source.add_dataframe_asset(name="ds03_cemabe")

    try:
        batch_definition = data_asset.get_batch_definition("batch_ds03")
    except KeyError:
        batch_definition = data_asset.add_batch_definition_whole_dataframe("batch_ds03")

    suite = construir_suite(context)
    batch = batch_definition.get_batch(batch_parameters={"dataframe": df})
    return batch.validate(suite)


def main() -> None:
    """Valida `silver.cemabe` y actualiza Data Docs locales."""
    context = gx.get_context(mode="file", context_root_dir=GE_CONTEXT_DIR)
    resultado = validar(cargar_silver(), context)

    for validacion in resultado.results:
        configuracion = validacion.expectation_config
        objetivo = configuracion.kwargs.get("column")
        print(
            f"{'PASS' if validacion.success else 'FAIL'} "
            f"{configuracion.type} {objetivo}"
        )

    context.build_data_docs()
    logger.info(
        "DS-03: success=%s (%d/%d expectativas)",
        resultado.success,
        resultado.statistics["successful_expectations"],
        resultado.statistics["evaluated_expectations"],
    )
    if not resultado.success:
        raise SystemExit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
