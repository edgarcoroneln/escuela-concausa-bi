"""
Validaciones de calidad (Great Expectations) para DS-05 SINAICA — capa Bronze.

Valida las dos tablas Bronze que produce `extractor_sinaica.py`:
  - `sinaica_estaciones`: catálogo de estaciones.
  - `sinaica_observaciones`: lecturas horarias por estación y parámetro.

Corre sobre el Parquet más reciente de cada tabla en `data/bronze/sinaica/` y publica
Data Docs (HTML) en `great_expectations/uncommitted/data_docs/` (excluido de git).

Nota de diseño: Bronze es crudo por definición (medallón bronze→silver→gold), así que
`latitud`/`longitud`/`municipioId` siguen siendo texto aquí -- el tipado real
(`cast(... as double precision)`) ya vive en `dbt/models/silver/aire_estacion.sql`.
Esta suite valida lo que Bronze *debe* garantizar: nulos, llave, duplicados y las
anomalías de calidad que SINAICA expone tal cual (ver `_expect_estaciones`).
"""
import glob
import logging

import pandas as pd

import great_expectations as gx

logger = logging.getLogger(__name__)

GE_CONTEXT_DIR = "great_expectations"
BRONZE_ESTACIONES_GLOB = "data/bronze/sinaica/estaciones/*.parquet"
BRONZE_OBSERVACIONES_GLOB = "data/bronze/sinaica/observaciones/*.parquet"

# Rangos físicos plausibles por parámetro (unidades ver `.recode_sinaica_units` en
# extractor_sinaica / DS-05 doc sección 5). Generosos a propósito: el objetivo es
# atrapar errores de captura/transmisión, no imponer el límite normativo (NOM) de
# exposición, que es mucho más estricto.
RANGOS_FISICOS = {
    "O3": (0, 0.5),      # ppm
    "CO": (0, 50),       # ppm
    "NO2": (0, 1),       # ppm
    "SO2": (0, 1),       # ppm
    "PM2.5": (0, 1000),  # µg/m³
    "PM10": (0, 1200),   # µg/m³
}

# Valores literales que SINAICA usa como placeholder de "sin georreferencia" en vez
# de omitir el campo. Ver hallazgo en el DevLog de esta historia: ~5% de las
# estaciones del catálogo traen "0.0"/"0" en vez de lat/lon real o un nulo explícito
# -- exactamente el caso que la regla SIN_DATO del proyecto busca atrapar.
PLACEHOLDER_SIN_GEORREFERENCIA = ["0.0", "0", "", "0.0000000000"]


def _archivo_mas_reciente(patron: str) -> str:
    archivos = sorted(glob.glob(patron))
    if not archivos:
        raise FileNotFoundError(
            f"No hay archivos Bronze en '{patron}'. Corre extractor_sinaica primero."
        )
    return archivos[-1]


def _contexto():
    """Data Context de Great Expectations, persistido en `great_expectations/`."""
    return gx.get_context(mode="file", context_root_dir=GE_CONTEXT_DIR)


def _obtener_o_crear_asset(context, nombre_datasource: str, nombre_asset: str):
    data_source = context.data_sources.add_or_update_pandas(name=nombre_datasource)
    if nombre_asset in data_source.get_asset_names():
        return data_source.get_asset(nombre_asset)
    return data_source.add_dataframe_asset(name=nombre_asset)


def _obtener_o_crear_batch_definition(data_asset, nombre_batch_def: str):
    try:
        return data_asset.get_batch_definition(nombre_batch_def)
    except KeyError:
        return data_asset.add_batch_definition_whole_dataframe(nombre_batch_def)


def _validar(context, df: pd.DataFrame, nombre: str, expectativas: list):
    """Registra `df` como asset efímero, define/actualiza la suite y valida."""
    data_asset = _obtener_o_crear_asset(context, f"{nombre}_datasource", f"{nombre}_asset")
    batch_def = _obtener_o_crear_batch_definition(data_asset, f"{nombre}_batch")
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})

    suite = gx.ExpectationSuite(name=f"suite_{nombre}", expectations=expectativas)
    suite = context.suites.add_or_update(suite)

    return batch.validate(suite)


def _expectativas_estaciones() -> list:
    return [
        # Llave
        gx.expectations.ExpectColumnValuesToNotBeNull(column="id"),
        gx.expectations.ExpectColumnValuesToBeUnique(column="id"),
        # Tipos (Bronze crudo: numérico solo donde SINAICA ya lo entrega numérico)
        gx.expectations.ExpectColumnValuesToBeOfType(column="id", type_="int64"),
        # Nulos en columnas críticas
        gx.expectations.ExpectColumnValuesToNotBeNull(column="nombre"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="latitud"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="longitud"),
        # Rango físico / calidad: coordenadas dentro de México, EXCLUYENDO el
        # placeholder "0.0" que SINAICA usa para "sin georreferencia". Se espera que
        # esta expectativa FALLE para ~5% de las estaciones -- es un hallazgo real,
        # no un bug de la suite (ver DS-05_SINAICA_Calidad_Aire.md, sección 10).
        gx.expectations.ExpectColumnValuesToNotBeInSet(
            column="latitud", value_set=PLACEHOLDER_SIN_GEORREFERENCIA
        ),
        gx.expectations.ExpectColumnValuesToNotBeInSet(
            column="longitud", value_set=PLACEHOLDER_SIN_GEORREFERENCIA
        ),
    ]


def _expectativas_observaciones() -> list:
    expectativas = [
        # Nulos en columnas críticas
        gx.expectations.ExpectColumnValuesToNotBeNull(column="id_estacion"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="parametro"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="fecha"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="hora"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="valor"),
        # Tipos
        gx.expectations.ExpectColumnValuesToBeOfType(column="hora", type_="int64"),
        gx.expectations.ExpectColumnValuesToBeOfType(column="valor", type_="float64"),
        # Rangos físicos genéricos
        gx.expectations.ExpectColumnValuesToBeBetween(column="hora", min_value=0, max_value=23),
        gx.expectations.ExpectColumnValuesToBeBetween(column="valor", min_value=0),
        gx.expectations.ExpectColumnValuesToBeInSet(column="val", value_set=[0, 1]),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="parametro", value_set=list(RANGOS_FISICOS.keys())
        ),
        # Llave / duplicados: una estación no debe reportar dos veces la misma
        # hora del mismo parámetro dentro de un mismo archivo Bronze.
        gx.expectations.ExpectCompoundColumnsToBeUnique(
            column_list=["id_estacion", "parametro", "fecha", "hora"]
        ),
    ]

    # Rango físico específico por parámetro (unidades distintas por contaminante,
    # así que un solo rango para toda la columna `valor` no tendría sentido).
    for parametro, (minimo, maximo) in RANGOS_FISICOS.items():
        expectativas.append(
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="valor",
                min_value=minimo,
                max_value=maximo,
                row_condition=f'parametro == "{parametro}"',
                condition_parser="pandas",
            )
        )

    return expectativas


def validar_sinaica_estaciones() -> "gx.core.expectation_validation_result.ExpectationSuiteValidationResult":
    """Valida el catálogo de estaciones (`sinaica_estaciones`) contra el Bronze más reciente."""
    archivo = _archivo_mas_reciente(BRONZE_ESTACIONES_GLOB)
    logger.info("Validando sinaica_estaciones desde %s", archivo)
    df = pd.read_parquet(archivo)

    context = _contexto()
    resultado = _validar(context, df, "sinaica_estaciones", _expectativas_estaciones())
    logger.info(
        "sinaica_estaciones: success=%s (%d/%d expectativas)",
        resultado.success,
        resultado.statistics["successful_expectations"],
        resultado.statistics["evaluated_expectations"],
    )
    return resultado


def validar_sinaica_observaciones() -> "gx.core.expectation_validation_result.ExpectationSuiteValidationResult":
    """Valida las lecturas horarias (`sinaica_observaciones`) contra el Bronze más reciente."""
    archivo = _archivo_mas_reciente(BRONZE_OBSERVACIONES_GLOB)
    logger.info("Validando sinaica_observaciones desde %s", archivo)
    df = pd.read_parquet(archivo)

    context = _contexto()
    resultado = _validar(context, df, "sinaica_observaciones", _expectativas_observaciones())
    logger.info(
        "sinaica_observaciones: success=%s (%d/%d expectativas)",
        resultado.success,
        resultado.statistics["successful_expectations"],
        resultado.statistics["evaluated_expectations"],
    )
    return resultado


def validar_sinaica() -> dict:
    """Corre ambas validaciones y publica Data Docs. No lanza excepción si fallan
    expectativas individuales -- el caller decide qué hacer con `resultado.success`
    (los fallos esperados, como el de georreferencia, son hallazgos, no errores)."""
    resultados = {
        "estaciones": validar_sinaica_estaciones(),
        "observaciones": validar_sinaica_observaciones(),
    }
    _contexto().build_data_docs()
    logger.info("Data Docs actualizados en great_expectations/uncommitted/data_docs/")
    return resultados


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    validar_sinaica()
