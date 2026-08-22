"""Extractor de DS-01 Formato 911 -- distribucion HISTORICA multi-ciclo (repodatos.atdt.gob.mx),
para la serie municipio x nivel x ciclo que consume unir_target() en src/modelos/target_hibrido.py
(PR #56, Hector Morales) -- mitigacion de RISK-007 / DEC-007 (el target hibrido se registro
primero como DEC-005, pero ese numero ya designaba otra decision -- colision de ID resuelta por
Edgar el 2026-08-19, el target hibrido se movio formalmente a DEC-007, ver Decision_Log.md).

NO reemplaza ni modifica src/ingesta/extractor_formato911.py (ciclo unico 2024-2025, ya usado
por bronze.formato911 / silver.matricula / el LAG de gold.features_escuela) -- esta es una
distribucion NUEVA y AISLADA de DS-01, con su propia tabla bronze.formato911_historico. Cero
impacto sobre el pipeline existente (ver DevLog 2026-08-21).

URLs verificadas UNA POR UNA a mano por Diana Alvarez Varela (clic derecho -> copiar direccion
del enlace, boton "Descargar" en datos.gob.mx), NO por formula: confirmamos que ciclos
consecutivos usan estructuras de URL distintas entre si (2023-2024 y 2024-2025 rompen el patron
de 2019-2020..2022-2023 cada una a su manera), asi que no existe una formula derivable.

Columnas: del CSV real (~190 columnas) solo se extraen las que hacen falta para la agregacion
municipio x nivel x ciclo: entidad, municipio, nivel, periodo, insc_t (matricula total), mas cct
(llave de escuela) y turno (para la UNIQUE de bronze -- un cct puede reportar mas de un turno en
el mismo ciclo). El resto de las columnas no se necesita para este target.

La columna llave de escuela cambia de nombre entre ciclos (`clavecct` en 2019-2020/2021-2022,
`clave_cct` en 2024-2025). Verificado real contra los 6 CSV descargados por Diana (2019-2020 a
2024-2025, ver DevLog 2026-08-22): los 6 parsean con `_parsear_ciclo` sin adivinar nada, 0 filas
con `matricula_total` no numerico en ninguno. Aun asi el detector no asume la variante -- si un
archivo futuro no trae ninguna de las dos, FALLA con un error explicito en vez de adivinar. Lo
mismo aplica a las columnas fijas (entidad/municipio/nivel/periodo/insc_t/turno): se valida su
presencia antes de procesar.

Bronze es nacional (Data_Model.md Section7): el filtro a SCOPE_ENTIDADES se aplica en Gold, no aqui
-- mismo principio que ya sigue el resto del proyecto (ver comentarios en fact_escuela_ciclo.sql).

Uso:
    python -m src.ingesta.extractor_formato911_historico
    python -m src.ingesta.extractor_formato911_historico --ciclos 2023-2024 2024-2025
"""
import argparse
import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

SOURCE_NAME = "DS-01_FORMATO911_HISTORICO"
BRONZE_PATH = "data/bronze/formato911_historico"

# Verificadas a mano, una por una -- ver docstring del modulo y DevLog 2026-08-21.
# NO derivar por formula: 2023-2024 y 2024-2025 ya demostraron que no hay patron unico.
SOURCE_URL_POR_CICLO = {
    "2019-2020": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/BASICA_2019-2020.csv",
    "2020-2021": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/BASICA_2020-2021.csv",
    "2021-2022": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/BASICA_2021-2022.csv",
    "2022-2023": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/BASICA_2022-2023.csv",
    "2023-2024": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/ESTANDAR_BASICA_I2324.csv",
    "2024-2025": (
        "https://repodatos.atdt.gob.mx/api_update/secretaria_educacion/"
        "registro_alumnado_personal_docente_educacion_basica_media_superior_formato_911/"
        "educacion_basica_2024_2025.csv"
    ),
}

# Verificado real con `head -1` contra los CSV descargados de 2019-2020 y 2021-2022 (formato
# legacy) y 2024-2025 (formato nuevo) -- ver DevLog. Para 2020-2021/2022-2023/2023-2024 se
# detecta en tiempo de ejecucion cual de las dos aplica; si no aplica ninguna, se falla.
VARIANTES_COLUMNA_CCT = ["clave_cct", "clavecct"]

# Verificadas identicas (mismo nombre, sin variante) en los 3 encabezados reales que sí
# comparamos columna por columna (2019-2020, 2021-2022, 2024-2025).
COLUMNAS_FIJAS_REQUERIDAS = ["entidad", "municipio", "nivel", "periodo", "insc_t", "turno"]

COLUMNAS_BRONZE = [
    "cct", "ciclo", "turno", "entidad", "municipio", "nivel", "matricula_total",
    "_ingested_at", "_source", "_source_url",
]


def _detectar_columna_cct(columnas_csv: list) -> str:
    """Devuelve el nombre real de la columna llave de escuela en este archivo. Falla explicito
    si el archivo no trae ninguna de las variantes ya verificadas -- no asume, no adivina."""
    for variante in VARIANTES_COLUMNA_CCT:
        if variante in columnas_csv:
            return variante
    raise ValueError(
        f"{SOURCE_NAME}: no se encontro ninguna variante conocida de la columna llave de "
        f"escuela ({VARIANTES_COLUMNA_CCT}) en las columnas del archivo. Esto significa que "
        f"este ciclo usa un tercer formato no verificado todavia -- hay que revisarlo a mano "
        f"antes de seguir, no adivinar el nombre."
    )


def _validar_columnas_fijas(columnas_csv: list) -> None:
    faltantes = [c for c in COLUMNAS_FIJAS_REQUERIDAS if c not in columnas_csv]
    if faltantes:
        raise ValueError(
            f"{SOURCE_NAME}: faltan columnas esperadas en el archivo: {faltantes}. "
            f"No se asume su ausencia como dato vacio -- hay que revisar el archivo a mano."
        )


def _parsear_ciclo(ruta_csv: str, ciclo: str, url: str) -> pd.DataFrame:
    """Lee el CSV real de un ciclo (ruta local a un archivo ya descargado) y devuelve un
    DataFrame con el esquema canonico de bronze.formato911_historico. No filtra por entidad
    (Bronze es nacional, Data_Model.md Section7)."""
    encabezado = pd.read_csv(ruta_csv, dtype=str, keep_default_na=False, nrows=0)
    columnas_csv = list(encabezado.columns)

    columna_cct = _detectar_columna_cct(columnas_csv)
    _validar_columnas_fijas(columnas_csv)

    columnas_a_leer = [columna_cct] + COLUMNAS_FIJAS_REQUERIDAS
    df = pd.read_csv(ruta_csv, dtype=str, keep_default_na=False, usecols=columnas_a_leer)

    ingested_at = datetime.now(timezone.utc)
    resultado = pd.DataFrame({
        "cct": df[columna_cct],
        "ciclo": ciclo,
        "turno": df["turno"],
        "entidad": df["entidad"],
        "municipio": df["municipio"],
        "nivel": df["nivel"],
        "matricula_total": pd.to_numeric(df["insc_t"], errors="coerce").astype("Int64"),
        "_ingested_at": ingested_at,
        "_source": SOURCE_NAME,
        "_source_url": url,
    })
    return resultado


def extraer_formato911_historico(ciclos: list = None) -> list:
    """Descarga y parsea los ciclos indicados (todos por default) de la distribucion historica
    de DS-01, y guarda un Parquet por ciclo en Bronze. Devuelve la lista de rutas generadas.

    Raises:
        ValueError: si se pide un ciclo sin URL verificada, o si el archivo descargado no trae
            las columnas esperadas (ver _detectar_columna_cct / _validar_columnas_fijas).
        requests.RequestException: si falla la descarga.
    """
    ciclos_a_procesar = ciclos or list(SOURCE_URL_POR_CICLO.keys())
    desconocidos = [c for c in ciclos_a_procesar if c not in SOURCE_URL_POR_CICLO]
    if desconocidos:
        raise ValueError(
            f"{SOURCE_NAME}: ciclo(s) sin URL verificada: {desconocidos}. "
            f"Ciclos disponibles: {list(SOURCE_URL_POR_CICLO.keys())}"
        )

    Path(BRONZE_PATH).mkdir(parents=True, exist_ok=True)
    rutas_generadas = []

    for ciclo in ciclos_a_procesar:
        url = SOURCE_URL_POR_CICLO[ciclo]
        logger.info("Descargando %s (%s)", SOURCE_NAME, ciclo)

        with requests.get(url, stream=True, timeout=120) as response:
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    tmp.write(chunk)
                tmp_path = tmp.name

        try:
            df = _parsear_ciclo(tmp_path, ciclo, url)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        ciclo_archivo = ciclo.replace("-", "_")
        output_path = f"{BRONZE_PATH}/formato911_historico_{ciclo_archivo}_{timestamp}.parquet"
        df.to_parquet(output_path, index=False)
        logger.info("Guardado %s (%d filas)", output_path, len(df))
        rutas_generadas.append(output_path)

    return rutas_generadas


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ciclos", nargs="*", default=None,
        help="Ciclos a extraer (ej. 2023-2024 2024-2025). Por default, los 6.",
    )
    args = parser.parse_args()

    rutas = extraer_formato911_historico(args.ciclos)
    print(f"OK: {len(rutas)} archivo(s) generado(s):")
    for r in rutas:
        print(f"  {r}")