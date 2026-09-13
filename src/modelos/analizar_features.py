"""Diagnóstico reproducible de features y cobertura para US-322 y US-325.

No transforma ni imputa datos para entrenamiento. Su objetivo es convertir en
validaciones y tablas auditables las decisiones que preceden al clustering de
ML-03: exclusión de llaves y targets, coherencia de ``SIN_DATO`` y cobertura
por driver, entidad y municipio.
"""

from __future__ import annotations

import pandas as pd

from src.modelos.contrato import DRIVERS, columna_cobertura, entidad_de_cct

COLUMNA_COMPLETITUD = "indice_completitud_drivers"
COLUMNA_TARGET = "target_variacion_matricula"
COLUMNA_MUNICIPIO = "cve_mun"
COLUMNAS_NO_ENTRENABLES = frozenset(
    {"cct", COLUMNA_MUNICIPIO, "id_ciclo", COLUMNA_TARGET}
)


def _correlacion_pearson_segura(
    izquierda: pd.Series, derecha: pd.Series
) -> float | None:
    """Calcula Pearson sólo cuando el par tiene variación suficiente.

    Una correlación no está definida si una de las dos series no cambia tras
    retirar sus nulos. Devolver ``None`` conserva ese hecho en la evidencia
    agregada y evita que NumPy emita un ``RuntimeWarning`` por dividir entre
    una desviación estándar igual a cero.
    """
    pares = pd.concat([izquierda, derecha], axis=1).dropna()
    if len(pares) < 2 or any(pares.iloc[:, indice].nunique() < 2 for indice in (0, 1)):
        return None
    return float(pares.iloc[:, 0].corr(pares.iloc[:, 1]))


def validar_features_para_analisis(df: pd.DataFrame) -> None:
    """Verifica el mínimo contrato antes de generar un diagnóstico.

    Cada valor ausente debe declararse con ``SIN_DATO`` y cada ``SIN_DATO``
    debe conservar el valor ausente. Así se evita ocultar cobertura parcial
    antes de seleccionar variables o entrenar un modelo.
    """
    requeridas = {
        "cct",
        "id_ciclo",
        COLUMNA_COMPLETITUD,
        COLUMNA_TARGET,
        *DRIVERS,
        *(columna_cobertura(driver) for driver in DRIVERS),
    }
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")

    duplicadas = df.duplicated(["cct", "id_ciclo"])
    if bool(duplicadas.any()):
        raise ValueError("Hay filas duplicadas para la llave cct × id_ciclo.")

    for driver in DRIVERS:
        cobertura = columna_cobertura(driver)
        valores_cobertura = set(df[cobertura].dropna().unique())
        invalidos = valores_cobertura - {"OK", "SIN_DATO"}
        if invalidos:
            raise ValueError(f"{cobertura} tiene valores inválidos: {sorted(invalidos)}")

        sin_dato = df[cobertura].eq("SIN_DATO")
        valor_ausente = df[driver].isna()
        if not sin_dato.equals(valor_ausente):
            raise ValueError(
                f"Cobertura inconsistente en {driver}: SIN_DATO y valor ausente deben coincidir."
            )


def columnas_excluidas_por_fuga() -> frozenset[str]:
    """Devuelve llaves y target que no pueden entrar a una matriz de clustering."""
    return COLUMNAS_NO_ENTRENABLES


def variables_candidatas_ml03() -> tuple[str, ...]:
    """Declara las variables candidatas para ML-03, sin construir aún la matriz.

    D5 y D6 incluyen indicadores de disponibilidad conforme a ADR-003. La
    imputación solo se incorporará al entrenar, ajustada exclusivamente sobre
    cada partición de entrenamiento.
    """
    return (*DRIVERS, COLUMNA_COMPLETITUD, "d5_dato_disponible", "d6_dato_disponible")


def resumen_eda(df: pd.DataFrame) -> pd.DataFrame:
    """Resume nulos, cardinalidad y correlación lineal de variables numéricas."""
    validar_features_para_analisis(df)
    columnas = [*DRIVERS, COLUMNA_COMPLETITUD, COLUMNA_TARGET]
    filas: list[dict[str, object]] = []
    for columna in columnas:
        serie = pd.to_numeric(df[columna], errors="raise")
        filas.append(
            {
                "feature": columna,
                "observaciones": len(serie),
                "nulos": int(serie.isna().sum()),
                "pct_nulos": float(serie.isna().mean()),
                "valores_unicos": int(serie.nunique(dropna=True)),
                "correlacion_target": (
                    None
                    if columna == COLUMNA_TARGET
                    else _correlacion_pearson_segura(serie, df[COLUMNA_TARGET])
                ),
            }
        )
    return pd.DataFrame(filas)


def correlaciones_drivers(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula correlaciones definidas entre drivers y completitud.

    Las celdas sin variación suficiente quedan como nulas: no representan una
    correlación de cero ni se usan como input del clustering.
    """
    validar_features_para_analisis(df)
    columnas = [*DRIVERS, COLUMNA_COMPLETITUD]
    numericas = df[columnas].astype(float)
    matriz = pd.DataFrame(index=columnas, columns=columnas, dtype=float)
    for izquierda in columnas:
        for derecha in columnas:
            matriz.loc[izquierda, derecha] = _correlacion_pearson_segura(
                numericas[izquierda], numericas[derecha]
            )
    return matriz


def cobertura_por_driver(df: pd.DataFrame) -> pd.DataFrame:
    """Mide la cobertura por driver a grano CCT × ciclo y escuelas afectadas."""
    validar_features_para_analisis(df)
    filas: list[dict[str, object]] = []
    for driver in DRIVERS:
        sin_dato = df[columna_cobertura(driver)].eq("SIN_DATO")
        filas.append(
            {
                "driver": driver,
                "observaciones": len(df),
                "con_dato": int((~sin_dato).sum()),
                "sin_dato": int(sin_dato.sum()),
                "pct_sin_dato": float(sin_dato.mean()),
                "escuelas_afectadas": int(df.loc[sin_dato, "cct"].nunique()),
            }
        )
    return pd.DataFrame(filas)


def cobertura_por_entidad(df: pd.DataFrame) -> pd.DataFrame:
    """Desglosa la cobertura por entidad derivada del CCT, sin inventar municipio."""
    validar_features_para_analisis(df)
    filas: list[dict[str, object]] = []
    entidades = df["cct"].map(entidad_de_cct)
    for driver in DRIVERS:
        sin_dato = df[columna_cobertura(driver)].eq("SIN_DATO")
        detalle = pd.DataFrame({"entidad": entidades, "sin_dato": sin_dato, "cct": df["cct"]})
        for entidad, grupo in detalle.groupby("entidad", sort=True):
            filas.append(
                {
                    "entidad": entidad,
                    "driver": driver,
                    "observaciones": len(grupo),
                    "sin_dato": int(grupo["sin_dato"].sum()),
                    "pct_sin_dato": float(grupo["sin_dato"].mean()),
                    "escuelas_afectadas": int(
                        grupo.loc[grupo["sin_dato"], "cct"].nunique()
                    ),
                }
            )
    return pd.DataFrame(filas)


def completitud_por_entidad(df: pd.DataFrame) -> pd.DataFrame:
    """Resume el índice de completitud por entidad para detectar sesgo territorial."""
    validar_features_para_analisis(df)
    detalle = df.assign(entidad=df["cct"].map(entidad_de_cct))
    return (
        detalle.groupby("entidad", sort=True)
        .agg(
            observaciones=("cct", "size"),
            escuelas=("cct", "nunique"),
            completitud_promedio=(COLUMNA_COMPLETITUD, "mean"),
            completitud_minima=(COLUMNA_COMPLETITUD, "min"),
            completitud_maxima=(COLUMNA_COMPLETITUD, "max"),
        )
        .reset_index()
    )


def requerir_clave_municipio(df: pd.DataFrame) -> None:
    """Valida la llave municipal antes de cualquier agregado territorial.

    No se infiere el municipio desde el CCT. La coincidencia de los primeros
    dos caracteres sólo comprueba que la clave recibida pertenece a la misma
    entidad que la escuela.
    """
    if COLUMNA_MUNICIPIO not in df.columns:
        raise ValueError(
            "El análisis municipal requiere cve_mun de gold.features_escuela; "
            "coordina este campo con Célula 1 antes de concluir US-325."
        )

    municipios = df[COLUMNA_MUNICIPIO]
    if bool(municipios.isna().any()):
        raise ValueError("cve_mun no puede ser nulo para el análisis municipal.")

    municipios_texto = municipios.astype("string")
    formato_invalido = ~municipios_texto.str.fullmatch(r"\d{5}")
    if bool(formato_invalido.any()):
        ejemplos = sorted(municipios_texto[formato_invalido].unique().tolist())
        raise ValueError(
            "cve_mun debe tener exactamente 5 dígitos; "
            f"valores inválidos: {ejemplos[:5]}"
        )

    entidades_cct = df["cct"].map(entidad_de_cct)
    entidad_inconsistente = municipios_texto.str[:2].ne(entidades_cct)
    if bool(entidad_inconsistente.any()):
        raise ValueError("cve_mun y CCT deben pertenecer a la misma entidad.")


def cobertura_por_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """Mide ``SIN_DATO`` por municipio y driver sin convertir ausencias en cero."""
    validar_features_para_analisis(df)
    requerir_clave_municipio(df)

    filas: list[dict[str, object]] = []
    for driver in DRIVERS:
        detalle = df.assign(
            _sin_dato=df[columna_cobertura(driver)].eq("SIN_DATO")
        )
        for municipio, grupo in detalle.groupby(COLUMNA_MUNICIPIO, sort=True):
            sin_dato = grupo["_sin_dato"]
            filas.append(
                {
                    COLUMNA_MUNICIPIO: municipio,
                    "entidad": str(municipio)[:2],
                    "driver": driver,
                    "observaciones": len(grupo),
                    "escuelas": int(grupo["cct"].nunique()),
                    "con_dato": int((~sin_dato).sum()),
                    "sin_dato": int(sin_dato.sum()),
                    "pct_sin_dato": float(sin_dato.mean()),
                    "escuelas_afectadas": int(
                        grupo.loc[sin_dato, "cct"].nunique()
                    ),
                }
            )
    return pd.DataFrame(filas)


def completitud_por_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """Resume la completitud de drivers por municipio para US-325 y DB-07."""
    validar_features_para_analisis(df)
    requerir_clave_municipio(df)

    detalle = df.assign(entidad=df[COLUMNA_MUNICIPIO].astype("string").str[:2])
    return (
        detalle.groupby(["entidad", COLUMNA_MUNICIPIO], sort=True)
        .agg(
            observaciones=("cct", "size"),
            escuelas=("cct", "nunique"),
            ciclos=("id_ciclo", "nunique"),
            completitud_promedio=(COLUMNA_COMPLETITUD, "mean"),
            completitud_minima=(COLUMNA_COMPLETITUD, "min"),
            completitud_maxima=(COLUMNA_COMPLETITUD, "max"),
        )
        .reset_index()
    )


def dispersion_cobertura_municipal(df: pd.DataFrame) -> pd.DataFrame:
    """Cuantifica la brecha municipal de cobertura sin inventar un umbral de sesgo.

    Devuelve, por entidad y driver, los municipios con menor y mayor porcentaje
    de ``SIN_DATO`` y la brecha entre ambos. La interpretación sustantiva se
    conserva fuera del código porque todavía no existe un umbral aprobado.
    """
    cobertura = cobertura_por_municipio(df)
    filas: list[dict[str, object]] = []
    for (entidad, driver), grupo in cobertura.groupby(
        ["entidad", "driver"], sort=True
    ):
        menor = grupo.sort_values(
            ["pct_sin_dato", COLUMNA_MUNICIPIO]
        ).iloc[0]
        mayor = grupo.sort_values(
            ["pct_sin_dato", COLUMNA_MUNICIPIO], ascending=[False, True]
        ).iloc[0]
        filas.append(
            {
                "entidad": entidad,
                "driver": driver,
                "municipios": int(grupo[COLUMNA_MUNICIPIO].nunique()),
                "municipio_menor_sin_dato": menor[COLUMNA_MUNICIPIO],
                "pct_min_sin_dato": float(menor["pct_sin_dato"]),
                "municipio_mayor_sin_dato": mayor[COLUMNA_MUNICIPIO],
                "pct_max_sin_dato": float(mayor["pct_sin_dato"]),
                "brecha_pct_sin_dato": float(
                    mayor["pct_sin_dato"] - menor["pct_sin_dato"]
                ),
            }
        )
    return pd.DataFrame(filas)
