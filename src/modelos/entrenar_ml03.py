"""Entrenamiento temporal de ML-03 — clustering de escuelas (US-321, US-631).

La variante candidata de S7 usa D1--D4. ``indice_completitud_drivers`` y
D5/D6 se conservan únicamente para auditar cobertura: no entran al vector ni
se imputan como cero. El módulo aplica ``casos_completos`` sólo al vector
operativo, con exclusiones auditables y validación temporal sin fuga.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import version
from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.modelos.contrato import DRIVERS, columna_cobertura
from src.modelos.mlflow_utils import RegistroModelo, registrar_sklearn
from src.modelos.particion_temporal import (
    generar_backtesting,
    ventanas_posibles,
    verificar_sin_fuga,
)

COLUMNA_COMPLETITUD = "indice_completitud_drivers"
COLUMNA_TARGET = "target_variacion_matricula"
DRIVERS_OPERATIVOS_ML03: tuple[str, ...] = tuple(
    driver for driver in DRIVERS if driver not in {"d5_agua", "d6_aire"}
)
FEATURES_ML03: tuple[str, ...] = DRIVERS_OPERATIVOS_ML03
COLUMNAS_PROHIBIDAS: frozenset[str] = frozenset(
    {"cct", "cve_mun", "id_ciclo", COLUMNA_TARGET}
)
POLITICA_AUSENCIA_VIGENTE = "casos_completos"
NOMBRE_MODELO = "ML03_ClusteringEscuelas"

NOMBRES_NEGOCIO = {
    "d1_pobreza": "pobreza y rezago",
    "d2_inseguridad": "inseguridad",
    "d3_infraestructura": "carencias de infraestructura",
    "d4_conectividad": "brecha de conectividad",
    "d5_agua": "estrés hídrico",
    "d6_aire": "calidad del aire",
}
NOMBRES_PISTAS = {
    "d1_pobreza": "Pobreza y rezago",
    "d2_inseguridad": "Inseguridad",
    "d3_infraestructura": "Infraestructura",
    "d4_conectividad": "Conectividad",
    "d5_agua": "Estrés hídrico",
    "d6_aire": "Calidad del aire",
}

#: D3/D4 miden servicios presentes (alto = escuela mejor); su "presión" es el complemento, igual
#: que la inversión del argmax de `driver_dominante` (P-05, 2026-08-31). Ver el CTE
#: `con_driver_dominante` en features_escuela.sql y generar_driver_dominante_proxy en
#: entrenar_ml02.py. Por eso NOMBRES_NEGOCIO ya nombra D3/D4 como "carencias"/"brecha".
DRIVERS_INVERTIDOS: tuple[str, ...] = ("d3_infraestructura", "d4_conectividad")


def _presion_driver(driver: str, valor: float) -> float:
    """Convierte el valor medio de un driver en 'presión' (mayor = peor situación).

    D3/D4 suben cuando la escuela está mejor, así que su presión es `1 - valor`; el resto ya viene
    en escala de presión (mayor = peor situación).
    """
    return 1 - valor if driver in DRIVERS_INVERTIDOS else valor


@dataclass(frozen=True)
class ResultadoML03:
    """Modelo final, validación temporal y perfiles auditables de ML-03."""

    modelo: Pipeline
    k_seleccionado: int
    metricas: pd.DataFrame
    asignaciones: pd.DataFrame
    perfiles: pd.DataFrame
    evidencia: pd.DataFrame
    filas_totales: int
    filas_entrenadas: int
    filas_excluidas: int
    politica_ausencia: str = POLITICA_AUSENCIA_VIGENTE

    @property
    def silhouette_promedio(self) -> float:
        """Promedio temporal para el ``k`` seleccionado."""
        elegidas = self.metricas[self.metricas["k"] == self.k_seleccionado]
        return float(elegidas["silhouette"].dropna().mean())


def _validar_contrato(df: pd.DataFrame) -> None:
    requeridas = {
        "cct",
        "id_ciclo",
        *FEATURES_ML03,
        COLUMNA_COMPLETITUD,
        *(columna_cobertura(driver) for driver in DRIVERS),
    }
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas para ML-03: {sorted(faltantes)}")
    if bool(df.duplicated(["cct", "id_ciclo"]).any()):
        raise ValueError("Hay filas duplicadas para la llave cct × id_ciclo.")

    for driver in DRIVERS:
        sin_dato = df[columna_cobertura(driver)].eq("SIN_DATO")
        if not sin_dato.equals(df[driver].isna()):
            raise ValueError(f"Cobertura inconsistente en {driver}.")


def preparar_casos_completos(
    df: pd.DataFrame,
    politica_ausencia: str = POLITICA_AUSENCIA_VIGENTE,
) -> tuple[pd.DataFrame, int]:
    """Retiene filas completas sin ejecutar una imputación no aprobada.

    Returns:
        DataFrame completo y cantidad de filas excluidas.
    """
    if politica_ausencia != POLITICA_AUSENCIA_VIGENTE:
        raise ValueError(
            "La única política aprobada provisionalmente es 'casos_completos'; "
            "la imputación municipal/estatal requiere ratificación humana."
        )

    _validar_contrato(df)
    numericas = df.loc[:, FEATURES_ML03].apply(pd.to_numeric, errors="raise")
    mascara = numericas.notna().all(axis=1)
    completas = df.loc[mascara].copy()
    completas.loc[:, FEATURES_ML03] = numericas.loc[mascara]
    completas = completas.sort_values(["id_ciclo", "cct"], kind="stable").reset_index(
        drop=True
    )
    excluidas = int((~mascara).sum())
    if completas.empty:
        raise ValueError(
            "No hay casos completos para ML-03; no se imputará hasta aprobar la política."
        )
    return completas, excluidas


def _pipeline(k: int, semilla: int) -> Pipeline:
    return Pipeline(
        steps=[
            ("escala", StandardScaler()),
            (
                "kmeans",
                KMeans(n_clusters=k, random_state=semilla, n_init=20),
            ),
        ]
    )


def _silhouette_prueba(modelo: Pipeline, prueba: pd.DataFrame) -> float | None:
    matriz = prueba.loc[:, FEATURES_ML03]
    etiquetas = modelo.predict(matriz)
    distintas = np.unique(etiquetas)
    if len(distintas) < 2 or len(distintas) >= len(prueba):
        return None
    escalada = modelo.named_steps["escala"].transform(matriz)
    return float(silhouette_score(escalada, etiquetas))


def evaluar_k_temporal(
    df: pd.DataFrame,
    valores_k: tuple[int, ...] = (2, 3, 4, 5, 6),
    n_ventanas: int | None = None,
    semilla: int = 42,
) -> pd.DataFrame:
    """Evalúa cada ``k`` con walk-forward; cada scaler se ajusta sólo en train."""
    completas, _ = preparar_casos_completos(df)
    ventanas = ventanas_posibles(completas) if n_ventanas is None else n_ventanas
    filas: list[dict[str, object]] = []

    for particion in generar_backtesting(completas, n_ventanas=ventanas):
        entrena, prueba = particion.aplicar(completas)
        verificar_sin_fuga(entrena, prueba)
        for k in valores_k:
            if k < 2:
                raise ValueError("KMeans requiere k >= 2 para calcular Silhouette.")
            if len(entrena) <= k:
                silhouette = None
            else:
                modelo = _pipeline(k, semilla)
                modelo.fit(entrena.loc[:, FEATURES_ML03])
                silhouette = _silhouette_prueba(modelo, prueba)
            filas.append(
                {
                    "ciclos_entrenamiento": ",".join(
                        particion.ciclos_entrenamiento
                    ),
                    "ciclo_prueba": particion.ciclos_prueba[0],
                    "k": k,
                    "silhouette": silhouette,
                    "n_entrenamiento": len(entrena),
                    "n_prueba": len(prueba),
                }
            )
    return pd.DataFrame(filas)


def _seleccionar_k(metricas: pd.DataFrame) -> int:
    promedios = metricas.groupby("k", sort=True)["silhouette"].mean().dropna()
    if promedios.empty:
        raise ValueError(
            "Ningún valor de k produjo Silhouette válido en las ventanas temporales."
        )
    mejor = promedios.max()
    return int(promedios[promedios.eq(mejor)].index.min())


def _perfilar(asignaciones: pd.DataFrame) -> pd.DataFrame:
    perfiles = (
        asignaciones.groupby("cluster", sort=True)
        .agg(
            observaciones=("cct", "size"),
            escuelas=("cct", "nunique"),
            **{driver: (driver, "mean") for driver in DRIVERS_OPERATIVOS_ML03},
            completitud_promedio=(COLUMNA_COMPLETITUD, "mean"),
        )
        .reset_index()
    )

    nombres: list[str] = []
    descripciones: list[str] = []
    for _, fila in perfiles.iterrows():
        # D3/D4 miden servicios presentes (alto = mejor); su PRESIÓN es el complemento (1 - media),
        # igual que la inversión del argmax en features_escuela.sql y entrenar_ml02.py (P-05).
        orden = sorted(
            DRIVERS_OPERATIVOS_ML03,
            key=lambda driver: (-_presion_driver(driver, fila[driver]), driver),
        )
        principal, secundaria = orden[:2]
        if principal == "d4_conectividad" and secundaria == "d3_infraestructura":
            nombres.append("Presión por conectividad e infraestructura")
        else:
            nombres.append(f"Presión por {NOMBRES_PISTAS[principal].lower()}")
        descripciones.append(
            f"Presión principal: {NOMBRES_NEGOCIO[principal]}; "
            f"secundaria: {NOMBRES_NEGOCIO[secundaria]}; "
            f"completitud media: {fila['completitud_promedio']:.0%}."
        )
    perfiles["perfil"] = nombres
    perfiles["perfil_negocio"] = descripciones
    return perfiles


def _resumir_evidencia(
    df: pd.DataFrame,
    asignaciones: pd.DataFrame,
    perfiles: pd.DataFrame,
) -> pd.DataFrame:
    """Explica la cobertura sin convertirla en una entrada del agrupamiento."""
    identidad = ["cct", "id_ciclo"]
    evidencia = df.loc[:, identidad].copy()
    disponibles = df.loc[:, FEATURES_ML03].notna()
    evidencia["pistas_disponibles"] = disponibles.sum(axis=1).astype(int)
    evidencia["pistas_totales"] = len(DRIVERS)

    def _nombres_disponibles(fila: pd.Series) -> tuple[str, ...]:
        return tuple(NOMBRES_PISTAS[driver] for driver in FEATURES_ML03 if fila[driver])

    def _nombres_pendientes(fila: pd.Series) -> tuple[str, ...]:
        faltantes = [driver for driver in FEATURES_ML03 if not fila[driver]]
        return tuple(
            NOMBRES_PISTAS[driver]
            for driver in [*faltantes, "d5_agua", "d6_aire"]
        )

    evidencia["pistas_comparables"] = disponibles.apply(_nombres_disponibles, axis=1)
    evidencia["pistas_pendientes"] = disponibles.apply(_nombres_pendientes, axis=1)

    asignadas = asignaciones.loc[:, [*identidad, "cluster"]].merge(
        perfiles.loc[:, ["cluster", "perfil"]], on="cluster", validate="many_to_one"
    )
    evidencia = evidencia.merge(asignadas, on=identidad, how="left", validate="one_to_one")
    evidencia["cluster"] = evidencia["cluster"].astype("Int64")
    con_perfil = evidencia["cluster"].notna()
    evidencia["estado_evidencia"] = np.where(con_perfil, "PARCIAL", "INSUFICIENTE")

    evidencia["descripcion"] = evidencia.apply(
        lambda fila: (
            f"Esta escuela comparte características con otros planteles donde destaca "
            f"{str(fila['perfil']).removeprefix('Presión por ').lower()}. Contamos con "
            f"evidencia comparable en {fila['pistas_disponibles']} de las 6 pistas. "
            "Estrés hídrico y calidad del aire permanecen pendientes."
            if pd.notna(fila["cluster"])
            else "Aún no tenemos evidencia suficiente para comparar esta escuela de manera "
            f"responsable. Encontramos información comparable en "
            f"{fila['pistas_disponibles']} de las 6 pistas."
        ),
        axis=1,
    )
    return evidencia


def entrenar_y_evaluar(
    df: pd.DataFrame,
    valores_k: tuple[int, ...] = (2, 3, 4, 5, 6),
    n_ventanas: int | None = None,
    semilla: int = 42,
) -> ResultadoML03:
    """Selecciona ``k`` temporalmente, entrena KMeans y perfila los clusters."""
    completas, excluidas = preparar_casos_completos(df)
    metricas = evaluar_k_temporal(
        completas,
        valores_k=valores_k,
        n_ventanas=n_ventanas,
        semilla=semilla,
    )
    k = _seleccionar_k(metricas)
    modelo = _pipeline(k, semilla)
    modelo.fit(completas.loc[:, FEATURES_ML03])

    columnas_identidad = ["cct", "id_ciclo"]
    if "cve_mun" in completas.columns:
        columnas_identidad.append("cve_mun")
    asignaciones = completas.loc[
        :, [*columnas_identidad, *FEATURES_ML03, COLUMNA_COMPLETITUD]
    ].copy()
    asignaciones["cluster"] = modelo.predict(completas.loc[:, FEATURES_ML03])
    perfiles = _perfilar(asignaciones)
    evidencia = _resumir_evidencia(df, asignaciones, perfiles)

    return ResultadoML03(
        modelo=modelo,
        k_seleccionado=k,
        metricas=metricas,
        asignaciones=asignaciones,
        perfiles=perfiles,
        evidencia=evidencia,
        filas_totales=len(df),
        filas_entrenadas=len(completas),
        filas_excluidas=excluidas,
    )


SEMILLAS_ESTABILIDAD_DEFAULT: tuple[int, ...] = (7, 21, 42, 84, 2026)


def evaluar_estabilidad_semillas(
    df: pd.DataFrame,
    k: int,
    semillas: tuple[int, ...] = SEMILLAS_ESTABILIDAD_DEFAULT,
) -> dict[str, object]:
    """Mide la estabilidad de las asignaciones de KMeans ante el cambio de semilla,
    vía el Índice de Rand Ajustado (ARI) por cada par de semillas.

    ARI = 1.0 entre dos semillas significa que ambas particiones asignan las mismas
    escuelas a los mismos clusters (salvo el número de etiqueta, que KMeans no fija);
    valores menores indican que el resultado depende de dónde arrancó el algoritmo, no
    solo de los datos. Es la evidencia detrás de `estabilidad.ari_minimo/ari_promedio`
    en `ML03_Comparacion_RISK011_20260910.json` -- ver `Propuesta_Cierre_ML03_D1_D4.md`
    §1 para el resultado ya publicado (ARI mínimo y promedio 1.0 en cinco semillas).

    Se comparan TODOS los pares de semillas (`C(n, 2)`), no cada una contra una sola
    semilla de referencia: así el resultado no depende de qué semilla se eligió como
    ancla.

    Args:
        df: mismo contrato de entrada que `entrenar_y_evaluar` (Gold `features_escuela`
            o equivalente). Se filtra a casos completos con `preparar_casos_completos`.
        k: número de clusters ya seleccionado (p. ej. `ResultadoML03.k_seleccionado`);
            esta función no vuelve a elegir `k`, solo mide su estabilidad.
        semillas: semillas de `KMeans` a comparar entre sí. Requiere al menos 2.

    Returns:
        Diccionario con `semillas`, `k`, `ari_por_par` (clave `"semilla_a-semilla_b"`)
        y los agregados `ari_minimo`/`ari_promedio` -- mismos nombres que ya consume
        `registrar_en_mlflow`.

    Raises:
        ValueError: si `semillas` trae menos de 2 elementos.
    """
    if len(semillas) < 2:
        raise ValueError("Se requieren al menos 2 semillas para medir estabilidad (ARI).")

    completas, _ = preparar_casos_completos(df)
    matriz = completas.loc[:, FEATURES_ML03]

    etiquetas_por_semilla = {
        semilla: _pipeline(k, semilla).fit_predict(matriz) for semilla in semillas
    }

    ari_por_par = {
        f"{a}-{b}": float(
            adjusted_rand_score(etiquetas_por_semilla[a], etiquetas_por_semilla[b])
        )
        for a, b in combinations(semillas, 2)
    }
    valores = list(ari_por_par.values())

    return {
        "semillas": list(semillas),
        "k": k,
        "ari_por_par": ari_por_par,
        "ari_minimo": min(valores),
        "ari_promedio": sum(valores) / len(valores),
    }


def registrar_en_mlflow(
    resultado: ResultadoML03,
    tracking_uri: str,
    experimento: str = "ML-03-clustering-escuelas",
    ari_minimo: float | None = None,
    ari_promedio: float | None = None,
    semillas_estabilidad: tuple[int, ...] = (),
) -> str:
    """Registra la corrida y crea una versión canónica de ML-03 en el Registry."""
    kmeans = resultado.modelo.named_steps["kmeans"]
    parametros: dict[str, object] = {
        "k": resultado.k_seleccionado,
        "semilla": kmeans.random_state,
        "n_init": kmeans.n_init,
        "politica_ausencia": resultado.politica_ausencia,
        "features": ",".join(FEATURES_ML03),
        "version_numpy": version("numpy"),
        "version_pandas": version("pandas"),
        "version_scikit_learn": version("scikit-learn"),
    }
    metricas: dict[str, float] = {
        "silhouette_temporal_promedio": resultado.silhouette_promedio,
        "filas_entrenadas": resultado.filas_entrenadas,
        "filas_excluidas": resultado.filas_excluidas,
    }
    if semillas_estabilidad:
        parametros["semillas_estabilidad"] = ",".join(map(str, semillas_estabilidad))
    if ari_minimo is not None:
        metricas["ari_minimo"] = ari_minimo
    if ari_promedio is not None:
        metricas["ari_promedio"] = ari_promedio
    for perfil in resultado.perfiles.itertuples(index=False):
        cluster = int(perfil.cluster)
        parametros[f"perfil_cluster_{cluster}"] = perfil.perfil
        metricas[f"observaciones_cluster_{cluster}"] = float(perfil.observaciones)
        metricas[f"escuelas_cluster_{cluster}"] = float(perfil.escuelas)

    config = RegistroModelo(
        nombre_modelo=NOMBRE_MODELO,
        experimento=experimento,
        tracking_uri=tracking_uri,
        registrar_modelo=True,
        parametros=parametros,
        metricas=metricas,
    )
    return registrar_sklearn(resultado.modelo, config)
