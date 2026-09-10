"""
Extractor de SINAICA (DS-05) — Calidad del aire, periodicidad horaria.

SINAICA/INECC no publica una API REST/JSON documentada. Los endpoints usados aquí son
los mismos que usa internamente el sitio `sinaica.inecc.gob.mx`; se identificaron por
ingeniería inversa del paquete open-source `rsinaica`
(https://github.com/diegovalle/rsinaica) y se verificaron en vivo el 2026-08-14 (ver
`vault/14_Data_Sources/DS-05_SINAICA_Calidad_Aire.md`, sección 9).

Produce dos tablas Bronze independientes (así las espera
`dbt/models/silver/aire_estacion.sql`):
  - `sinaica_estaciones`: catálogo de estaciones (identidad + georreferencia).
  - `sinaica_observaciones`: lecturas horarias por estación y parámetro.

Backfill histórico (D6, resuelve la cobertura temporal corta de la ingesta horaria):
`extraer_sinaica_observaciones_historico()` recorre, por estación, desde su
`fechaIniDatos` real (catálogo de estaciones) hasta hoy, en ventanas de `rango=6`
(~21 meses reales por llamada, confirmado empírico el 2026-09-10 contra
`datGrafs.php` -- NO son exactamente 2 años calendario pese a lo que dice la
ficha DS-05 §2). `fechaIni` es el INICIO de la ventana: la API avanza hacia
adelante desde ahí y la recorta sola en "hoy" si la ventana cruzaría al futuro
(verificado: `fechaIni=2026-01-01, rango=6` no devolvió fechas futuras). Antes
de este hallazgo, `_extraer_dato_horario` tenía `rango=1` fijo en el código --
por eso la ingesta horaria nunca traía más que el día en curso.
"""
import json
import logging
import os
import random
import re
import time
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import requests

logger = logging.getLogger(__name__)

SOURCE_NAME = "DS-05_SINAICA"
BASE_URL = "https://sinaica.inecc.gob.mx"
ESTACIONES_URL = f"{BASE_URL}/lib/j/php/getData.php"
ULTIMOS_ENVIOS_URL = f"{BASE_URL}/lib/libd/cnxn.php"
DATOS_URL = f"{BASE_URL}/pags/datGrafs.php"

BRONZE_PATH_ESTACIONES = "data/bronze/sinaica/estaciones"
BRONZE_PATH_OBSERVACIONES = "data/bronze/sinaica/observaciones"

# Parámetros de calidad del aire por defecto (contaminantes criterio). Cada estación
# reporta solo un subconjunto; los que no aplican se descartan por estación sin
# tumbar la corrida (ver _extraer_dato_horario).
PARAMETROS_DEFAULT = ("PM2.5", "PM10", "O3", "CO", "NO2", "SO2")

# La respuesta de datGrafs.php es HTML+JS, no JSON puro: los datos vienen embebidos
# en una línea `var dat = [...];` que hay que extraer antes de poder parsearlos.
_DAT_PATTERN = re.compile(r"var\s+dat\s*=\s*(\[[\s\S]*?\])\s*;")


def _guardar_parquet(df: pd.DataFrame, bronze_path: str, prefix: str) -> str:
    """Escribe `df` como Parquet en Bronze con timestamp único (idempotente por corrida)."""
    os.makedirs(bronze_path, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = f"{bronze_path}/{prefix}_{timestamp}.parquet"
    df.to_parquet(output_path, index=False)
    return output_path


def _parsear_estaciones_activas(data: list[dict]) -> list[int]:
    """Extrae y deduplica los IDs de estación de la respuesta de `getUltimosEnvios`."""
    return sorted({int(item["idEstacion"]) for item in data})


def _estaciones_activas() -> list[int]:
    """IDs de estaciones con envío reciente (`getUltimosEnvios`)."""
    response = requests.post(
        ULTIMOS_ENVIOS_URL, data={"metodo": "getUltimosEnvios"}, timeout=30
    )
    response.raise_for_status()
    return _parsear_estaciones_activas(response.json())


def _catalogo_estaciones() -> list[dict]:
    """Catálogo completo de estaciones (identidad, red, lat/lon, municipioId,
    fechaIniDatos) tal cual lo entrega `getData.php`. Factorizado de
    `extraer_sinaica_estaciones` para que el backfill histórico pueda leer
    `fechaIniDatos` por estación sin repetir la llamada HTTP."""
    fields = (
        "e.id, e.nombre, e.codigo, e.redesId, r.nombre as nombre_red, "
        "r.codigo as codigo_red, e.municipioId, e.estadoId, e.latitud, e.longitud, "
        "e.fechaIniDatos"
    )
    response = requests.post(
        ESTACIONES_URL,
        data={
            "tabla": "Estaciones e INNER JOIN Redes r ON e.redesid = r.id",
            "fields": fields,
            "where": "1=1 ORDER BY r.nombre, e.codigo",
        },
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    if not data:
        raise ValueError(f"{SOURCE_NAME}: catálogo de estaciones vacío, no se guarda nada")
    return data


def extraer_sinaica_estaciones() -> str:
    """
    Descarga el catálogo de estaciones de SINAICA (nombre, red, lat/lon, municipioId)
    y lo guarda en Bronze.

    Returns:
        Ruta del archivo Parquet generado.

    Raises:
        requests.RequestException: si falla la descarga.
        ValueError: si la respuesta viene vacía.
    """
    logger.info("Iniciando extracción de catálogo de estaciones de %s", SOURCE_NAME)

    data = _catalogo_estaciones()

    df = pd.DataFrame(data)
    df["_ingested_at"] = datetime.now(timezone.utc)
    df["_source"] = SOURCE_NAME
    df["_source_url"] = ESTACIONES_URL

    output_path = _guardar_parquet(df, BRONZE_PATH_ESTACIONES, "sinaica_estaciones")
    logger.info("Guardado %s (%d estaciones)", output_path, len(df))

    return output_path


def _parsear_respuesta_datos(texto: str, estacion_id: int, parametro: str) -> pd.DataFrame:
    """
    Extrae el arreglo `var dat = [...]` embebido en la respuesta HTML+JS de
    `datGrafs.php` (no es JSON puro, ver módulo).

    Devuelve un DataFrame vacío (no lanza error) si la estación no reporta ese
    parámetro — es un caso esperado, no una falla.
    """
    match = _DAT_PATTERN.search(texto)
    if not match:
        raise ValueError(
            f"{SOURCE_NAME}: no se encontró 'var dat = [...]' en la respuesta "
            f"(estación={estacion_id}, parametro={parametro})"
        )

    registros = json.loads(match.group(1))
    columnas = ["id_estacion", "parametro", "fecha", "hora", "valor", "val"]
    if not registros:
        return pd.DataFrame(columns=columnas)

    df = pd.DataFrame(registros)
    df["id_estacion"] = int(estacion_id)
    df["parametro"] = parametro
    return df[["fecha", "hora", "valor", "val", "id_estacion", "parametro"]]


def _extraer_dato_horario(
    estacion_id: int, parametro: str, fecha_ini: str, rango: int = 1
) -> pd.DataFrame:
    """Descarga los datos horarios de un parámetro/estación desde `datGrafs.php`.

    `rango` (1-6, ver DS-05 doc) define el tamaño de la ventana hacia ADELANTE desde
    `fecha_ini` -- confirmado empírico el 2026-09-10: `fechaIni` es el inicio, no el
    fin, de la ventana, y la API la recorta sola en "hoy" si cruzaría al futuro. Antes
    este valor estaba fijo en 1 (un día); por eso la ingesta horaria nunca acumulaba
    historia. El backfill (`extraer_sinaica_observaciones_historico`) usa `rango=6`.
    """
    response = requests.post(
        DATOS_URL,
        data={
            "estacionId": estacion_id,
            "param": parametro,
            "fechaIni": fecha_ini,
            "rango": rango,
            "tipoDatos": "",  # "" = Cruda, "V" = Validada, "M" = Manual
            "datoBase": 1,
        },
        timeout=60,
    )
    response.raise_for_status()
    return _parsear_respuesta_datos(response.text, estacion_id, parametro)


def extraer_sinaica_observaciones(
    estacion_ids: list[int] | None = None,
    parametros: tuple[str, ...] = PARAMETROS_DEFAULT,
    dias_atras: int = 0,
) -> str:
    """
    Descarga las observaciones horarias de SINAICA para una lista de estaciones y
    parámetros, y las guarda en Bronze.

    Args:
        estacion_ids: estaciones a consultar. Si es None, usa todas las estaciones
            con envío reciente (`getUltimosEnvios`).
        parametros: parámetros a descargar por estación.
        dias_atras: desplazamiento en días respecto a hoy para `fechaIni` (0 = hoy).

    Returns:
        Ruta del archivo Parquet generado.

    Raises:
        ValueError: si no se obtuvo ningún registro en toda la corrida.
    """
    logger.info("Iniciando extracción de observaciones horarias de %s", SOURCE_NAME)

    if estacion_ids is None:
        estacion_ids = _estaciones_activas()

    fecha_ini = (datetime.now(timezone.utc) - timedelta(days=dias_atras)).strftime("%Y-%m-%d")

    frames = []
    for estacion_id in estacion_ids:
        for parametro in parametros:
            try:
                frames.append(_extraer_dato_horario(estacion_id, parametro, fecha_ini))
            except (requests.RequestException, ValueError) as exc:
                # Una estación sin ese parámetro, o una falla puntual, no debe tumbar
                # la corrida completa: se registra y se continúa con las demás.
                logger.warning(
                    "Fallo estación=%s parametro=%s: %s", estacion_id, parametro, exc
                )
            # No saturar el servidor -- mismo criterio que usa rsinaica entre llamadas.
            time.sleep(random.uniform(0, 0.5))

    frames = [f for f in frames if not f.empty]
    if not frames:
        raise ValueError(f"{SOURCE_NAME}: no se descargó ningún registro, no se guarda nada")

    df = pd.concat(frames, ignore_index=True)
    df["_ingested_at"] = datetime.now(timezone.utc)
    df["_source"] = SOURCE_NAME
    df["_source_url"] = DATOS_URL

    output_path = _guardar_parquet(df, BRONZE_PATH_OBSERVACIONES, "sinaica_observaciones")
    logger.info("Guardado %s (%d registros)", output_path, len(df))

    return output_path


FECHA_PISO_BACKFILL = "2013-01-01"  # arranque de red SINAICA razonable si fechaIniDatos falta
PASO_DIAS_BACKFILL = 700  # menor al máximo observado (~21 meses) para no dejar huecos


def _fechas_backfill(fecha_inicio: date, fecha_fin: date, paso_dias: int = PASO_DIAS_BACKFILL):
    """`fechaIni` de cada ventana de backfill, de `fecha_inicio` a `fecha_fin` inclusive."""
    actual = fecha_inicio
    while actual <= fecha_fin:
        yield actual.strftime("%Y-%m-%d")
        actual += timedelta(days=paso_dias)


def extraer_sinaica_observaciones_historico(
    estacion_ids: list[int] | None = None,
    parametro: str = "PM2.5",
    rango: int = 6,
    paso_dias: int = PASO_DIAS_BACKFILL,
) -> str:
    """
    Backfill histórico de un parámetro (PM2.5 por defecto, D6) para todas las
    estaciones del catálogo: por cada una, descarga desde su `fechaIniDatos` real
    hasta hoy, en ventanas de `rango` (ver `_extraer_dato_horario` para la dirección
    de la ventana). A diferencia de `extraer_sinaica_observaciones` (incremental, un
    día), esta función cubre toda la serie disponible por estación.

    Si una estación no trae `fechaIniDatos` válida, se omite con una advertencia --
    no se inventa una fecha de arranque (regla SIN_DATO del proyecto).

    Args:
        estacion_ids: estaciones a recorrer. Si es None, usa TODAS las del catálogo
            completo (no solo las "activas recientes" de `_estaciones_activas`) --
            una estación hoy inactiva puede tener años de historia real útil para D6.
        parametro: parámetro a descargar (PM2.5 por defecto).
        rango: tamaño de ventana por llamada hacia adelante desde `fechaIni`.
        paso_dias: avance entre ventanas. Se solapa a propósito con la ventana real
            observada (~21 meses) para no dejar huecos; el solape se deduplica antes
            de guardar.

    Returns:
        Ruta del archivo Parquet generado.

    Raises:
        ValueError: si no se obtuvo ningún registro en toda la corrida.
    """
    logger.info(
        "Iniciando backfill histórico de %s para %s (rango=%d, paso=%d días)",
        parametro, SOURCE_NAME, rango, paso_dias,
    )

    catalogo = _catalogo_estaciones()
    if estacion_ids is not None:
        ids_pedidos = set(estacion_ids)
        catalogo = [e for e in catalogo if int(e["id"]) in ids_pedidos]

    hoy = datetime.now(timezone.utc).date()
    frames = []
    estaciones_con_datos = 0

    for estacion in catalogo:
        estacion_id = int(estacion["id"])
        fecha_ini_raw = estacion.get("fechaIniDatos")
        try:
            fecha_inicio = date.fromisoformat(str(fecha_ini_raw))
        except (TypeError, ValueError):
            logger.warning(
                "Estación %s sin fechaIniDatos válida (%r) -- se omite del backfill, "
                "no se inventa fecha de arranque",
                estacion_id, fecha_ini_raw,
            )
            continue

        estaciones_con_datos += 1
        for fecha_ini in _fechas_backfill(fecha_inicio, hoy, paso_dias):
            try:
                frames.append(
                    _extraer_dato_horario(estacion_id, parametro, fecha_ini, rango=rango)
                )
            except (requests.RequestException, ValueError) as exc:
                logger.warning(
                    "Fallo backfill estación=%s parametro=%s fechaIni=%s: %s",
                    estacion_id, parametro, fecha_ini, exc,
                )
            time.sleep(random.uniform(0, 0.5))

    frames = [f for f in frames if not f.empty]
    if not frames:
        raise ValueError(f"{SOURCE_NAME}: backfill no descargó ningún registro, no se guarda nada")

    df = pd.concat(frames, ignore_index=True)
    # Las ventanas se solapan a propósito (ver paso_dias) -- el mismo dato puede venir
    # en dos llamadas consecutivas; se conserva una sola copia por llave natural.
    df = df.drop_duplicates(subset=["id_estacion", "parametro", "fecha", "hora"])

    df["_ingested_at"] = datetime.now(timezone.utc)
    df["_source"] = SOURCE_NAME
    df["_source_url"] = DATOS_URL

    output_path = _guardar_parquet(df, BRONZE_PATH_OBSERVACIONES, "sinaica_observaciones")
    logger.info(
        "Guardado %s (%d registros históricos, %d/%d estaciones con fechaIniDatos válida)",
        output_path, len(df), estaciones_con_datos, len(catalogo),
    )

    return output_path


def extraer_sinaica() -> dict[str, str]:
    """
    Punto de entrada usado por `dags/dag_horario.py`: corre ambas extracciones
    (catálogo de estaciones + observaciones horarias) en una sola llamada.

    Returns:
        Diccionario con las rutas de los dos Parquet generados.
    """
    return {
        "estaciones": extraer_sinaica_estaciones(),
        "observaciones": extraer_sinaica_observaciones(),
    }
