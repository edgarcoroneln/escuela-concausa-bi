"""Entrenamiento y backtesting de ML-02 — clasificacion de driver dominante (US-302).

El contrato vigente de `gold.features_escuela` todavia no incluye una etiqueta supervisada de
`driver_dominante`. Para no bloquear US-302, este modulo permite avanzar con un target proxy
deterministico (`driver_dominante_proxy`) derivado de los seis drivers normalizados. Cuando C1 publique
la etiqueta real en Gold, `cargar_features_ml02()` la consumira sin cambiar el resto del pipeline.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score

from src.modelos.contrato import DRIVERS
from src.modelos.entrenar_ml01 import FEATURES_POR_DEFECTO
from src.modelos.mlflow_utils import RegistroModelo, registrar_sklearn
from src.modelos.particion_temporal import (
    ParticionTemporal,
    generar_backtesting,
    verificar_sin_fuga,
)
from src.modelos.recomendaciones import CODIGOS_DRIVER as CLASES_DRIVER
from src.modelos.recomendaciones import recomendacion_para_driver

COLUMNA_TARGET_REAL = "driver_dominante"
COLUMNA_TARGET_PROXY = "driver_dominante_proxy"
COLUMNA_TARGET = COLUMNA_TARGET_REAL
NOMBRE_MODELO = "ML02_DriverClasificador"

DRIVER_A_CLASE: dict[str, str] = {
    "d1_pobreza": "D1",
    "d2_inseguridad": "D2",
    "d3_infraestructura": "D3",
    "d4_conectividad": "D4",
    "d5_agua": "D5",
    "d6_aire": "D6",
}

#: Drivers que miden SERVICIOS PRESENTES (alto = escuela mejor). Entran al argmax de
#: `driver_dominante` invertidos como (1 - valor), para que el dominante sea el driver que MÁS
#: presiona y no el mejor servicio. Debe coincidir con la regla 4 del CTE `con_driver_dominante`
#: en dbt/models/gold/features_escuela.sql y con el perfilado de entrenar_ml03.py (P-05, 2026-08-31).
DRIVERS_INVERTIDOS: tuple[str, ...] = ("d3_infraestructura", "d4_conectividad")

HIPERPARAMETROS: dict[str, object] = {
    "max_iter": 150,
    "learning_rate": 0.06,
    "max_leaf_nodes": 15,
    "l2_regularization": 0.01,
    "random_state": 0,
}


@dataclass(frozen=True)
class MetricasClasificacionVentana:
    """Metricas de una ventana temporal de ML-02."""

    particion: ParticionTemporal
    f1_macro: float
    accuracy: float
    precision_macro: float
    f1_macro_baseline: float
    n_entrena: int
    n_prueba: int

    @property
    def mejora_sobre_baseline(self) -> float:
        if self.f1_macro_baseline == 0:
            return 0.0
        return (self.f1_macro - self.f1_macro_baseline) / self.f1_macro_baseline


@dataclass(frozen=True)
class ResultadoML02:
    """Resultado de backtesting mas modelo de produccion."""

    ventanas: tuple[MetricasClasificacionVentana, ...]
    modelo: HistGradientBoostingClassifier
    columna_target_usada: str
    drivers_usados: tuple[str, ...] = DRIVERS
    drivers_excluidos: tuple[str, ...] = ()
    excluidos_por_ventana: dict[str, tuple[str, ...]] | None = None

    @property
    def f1_macro_promedio(self) -> float:
        return float(np.mean([v.f1_macro for v in self.ventanas]))

    @property
    def f1_macro_desviacion(self) -> float:
        return float(np.std([v.f1_macro for v in self.ventanas]))

    @property
    def accuracy_promedio(self) -> float:
        return float(np.mean([v.accuracy for v in self.ventanas]))

    @property
    def ventana_produccion(self) -> MetricasClasificacionVentana:
        return self.ventanas[-1]


def generar_driver_dominante_proxy(df: pd.DataFrame) -> pd.Series:
    """Deriva una etiqueta provisional `D1`..`D6` desde el driver que MÁS presiona.

    D3/D4 miden servicios presentes (suben cuando la escuela está mejor), así que se invierten
    (`1 - valor`) antes del argmax: sin eso, la escuela mejor equipada quedaría coronada como
    "dominante en infraestructura" (P-05). Es la misma regla del CTE `con_driver_dominante` de
    features_escuela.sql y del perfilado de entrenar_ml03.py.

    Los `SIN_DATO` llegan como `NaN`; aqui se tratan como no elegibles para dominar. No se imputan a
    cero porque cero puede ser un valor valido de un driver.
    """
    faltantes = set(DRIVERS) - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan drivers para derivar target proxy: {sorted(faltantes)}")

    puntajes = df[list(DRIVERS)].astype(float)
    for driver in DRIVERS_INVERTIDOS:
        puntajes[driver] = 1 - puntajes[driver]
    puntajes = puntajes.fillna(-np.inf)
    dominante = puntajes.idxmax(axis=1)
    sin_observaciones = np.isneginf(puntajes.max(axis=1))
    if bool(sin_observaciones.any()):
        raise ValueError("No se puede derivar driver_dominante_proxy para filas sin ningun driver.")
    return dominante.map(DRIVER_A_CLASE)


def cargar_features_ml02(ruta: Path = FEATURES_POR_DEFECTO) -> pd.DataFrame:
    """Carga features y agrega target proxy si Gold aun no trae `driver_dominante`."""
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta}.")
    df = pd.read_parquet(ruta) if ruta.suffix == ".parquet" else pd.read_csv(ruta)
    faltantes = ({"cct", "id_ciclo"} | set(DRIVERS)) - set(df.columns)
    if faltantes:
        raise ValueError(f"La tabla de features no cumple el contrato; faltan: {sorted(faltantes)}")

    if COLUMNA_TARGET_REAL not in df.columns:
        df[COLUMNA_TARGET_PROXY] = generar_driver_dominante_proxy(df)
    return df


def columna_target_disponible(df: pd.DataFrame) -> str:
    """Prefiere la etiqueta real; si no existe, usa el proxy documentado."""
    if COLUMNA_TARGET_REAL in df.columns:
        return COLUMNA_TARGET_REAL
    if COLUMNA_TARGET_PROXY in df.columns:
        return COLUMNA_TARGET_PROXY
    raise ValueError("Falta driver_dominante o driver_dominante_proxy para entrenar ML-02.")


def validar_target_ml02(df: pd.DataFrame, columna_target: str) -> None:
    """Valida que el target esté completo y use exclusivamente las clases D1..D6."""
    if bool(df[columna_target].isna().any()):
        raise ValueError(f"{columna_target} contiene etiquetas nulas.")
    clases = set(df[columna_target].astype(str))
    invalidas = clases - set(CLASES_DRIVER)
    if invalidas:
        raise ValueError(f"{columna_target} contiene clases inválidas: {sorted(invalidas)}")
    if len(clases) < 2:
        raise ValueError(f"{columna_target} necesita al menos dos clases para entrenar ML-02.")


def drivers_utilizables(df: pd.DataFrame) -> list[str]:
    """Devuelve los drivers con al menos un valor observado en este conjunto."""
    return [driver for driver in DRIVERS if df[driver].notna().any()]


def _matriz(df: pd.DataFrame, columnas: list[str] | None = None) -> pd.DataFrame:
    """Extrae drivers para el clasificador; los ausentes quedan como NaN."""
    return df[list(columnas if columnas is not None else DRIVERS)]


def entrenar_y_evaluar(
    df: pd.DataFrame,
    n_ventanas: int = 3,
    hiperparametros: dict[str, object] | None = None,
) -> ResultadoML02:
    """Ejecuta backtesting temporal de ML-02."""
    target = columna_target_disponible(df)
    validar_target_ml02(df, target)
    params = {**HIPERPARAMETROS, **(hiperparametros or {})}
    ventanas: list[MetricasClasificacionVentana] = []
    usables: list[str] = []
    excluidos_por_ventana: dict[str, tuple[str, ...]] = {}
    modelo: HistGradientBoostingClassifier | None = None

    for particion in generar_backtesting(df, n_ventanas=n_ventanas):
        entrena, prueba = particion.aplicar(df)
        verificar_sin_fuga(entrena, prueba)

        usables = drivers_utilizables(entrena)
        if not usables:
            raise ValueError(
                f"Ningún driver tiene datos en la ventana de entrenamiento {particion}. "
                "Revisa la cobertura por ciclo de `gold.features_escuela`."
            )
        fuera = [driver for driver in DRIVERS if driver not in usables]
        if fuera:
            excluidos_por_ventana[str(particion)] = tuple(fuera)

        x_entrena, y_entrena = _matriz(entrena, usables), entrena[target]
        x_prueba, y_prueba = _matriz(prueba, usables), prueba[target]

        modelo = HistGradientBoostingClassifier(**params).fit(x_entrena, y_entrena)
        predicho = modelo.predict(x_prueba)
        baseline = DummyClassifier(strategy="most_frequent").fit(x_entrena, y_entrena).predict(x_prueba)

        ventanas.append(
            MetricasClasificacionVentana(
                particion=particion,
                f1_macro=float(f1_score(y_prueba, predicho, labels=CLASES_DRIVER, average="macro", zero_division=0)),
                accuracy=float(accuracy_score(y_prueba, predicho)),
                precision_macro=float(
                    precision_score(y_prueba, predicho, labels=CLASES_DRIVER, average="macro", zero_division=0)
                ),
                f1_macro_baseline=float(
                    f1_score(y_prueba, baseline, labels=CLASES_DRIVER, average="macro", zero_division=0)
                ),
                n_entrena=len(entrena),
                n_prueba=len(prueba),
            )
        )

    if modelo is None:  # pragma: no cover
        raise RuntimeError("El backtesting no produjo ninguna ventana.")
    return ResultadoML02(
        ventanas=tuple(ventanas),
        modelo=modelo,
        columna_target_usada=target,
        drivers_usados=tuple(usables),
        drivers_excluidos=tuple(driver for driver in DRIVERS if driver not in usables),
        excluidos_por_ventana=excluidos_por_ventana,
    )


def predecir_driver(modelo: HistGradientBoostingClassifier, features: pd.DataFrame) -> pd.DataFrame:
    """Predice driver dominante y recomendacion en la forma que consumira la API."""
    columnas = list(getattr(modelo, "feature_names_in_", DRIVERS))
    drivers = modelo.predict(_matriz(features, columnas))
    return pd.DataFrame(
        {
            "cct": features["cct"].to_numpy(),
            "id_ciclo": features["id_ciclo"].to_numpy(),
            "driver_dominante": drivers,
            "recomendacion": [recomendacion_para_driver(driver) for driver in drivers],
        }
    )


def registrar_en_mlflow(
    resultado: ResultadoML02,
    tracking_uri: str,
    experimento: str = "ML-02-clasificacion-driver",
    registrar_modelo: bool = False,
) -> str:
    """Registra el modelo de produccion de ML-02 en MLflow (US-303)."""
    config = RegistroModelo(
        nombre_modelo=NOMBRE_MODELO,
        experimento=experimento,
        tracking_uri=tracking_uri,
        registrar_modelo=registrar_modelo,
        parametros={
            "target": resultado.columna_target_usada,
            "particion": "temporal walk-forward (nunca aleatoria)",
            "n_ventanas": len(resultado.ventanas),
            **{f"modelo__{k}": v for k, v in HIPERPARAMETROS.items()},
        },
        metricas={
            "f1_macro_promedio": resultado.f1_macro_promedio,
            "f1_macro_desviacion": resultado.f1_macro_desviacion,
            "accuracy_promedio": resultado.accuracy_promedio,
            "f1_macro_produccion": resultado.ventana_produccion.f1_macro,
            "accuracy_produccion": resultado.ventana_produccion.accuracy,
        },
    )
    return registrar_sklearn(resultado.modelo, config)


def calcular_shap_batch(
    modelo: HistGradientBoostingClassifier,
    filas: pd.DataFrame,
) -> list[dict[str, float]]:
    """Calcula contribuciones SHAP en batch para ML-02 si `shap` esta instalado.

    Se mantiene fuera del camino critico de pruebas porque SHAP vive en `requirements/celula-3.txt`,
    no en el requirements base del CI.
    """
    try:
        import shap
    except ImportError as exc:  # pragma: no cover - depende del ambiente de C3
        raise RuntimeError("Instala shap para calcular explicabilidad de ML-02.") from exc

    columnas = list(getattr(modelo, "feature_names_in_", DRIVERS))
    x_filas = _matriz(filas, columnas)
    explainer = shap.TreeExplainer(modelo)
    valores = explainer.shap_values(x_filas)
    probabilidades = modelo.predict_proba(x_filas)

    resultados: list[dict[str, float]] = []
    for indice_fila, indice_clase in enumerate(np.argmax(probabilidades, axis=1)):
        if isinstance(valores, list):
            contribuciones = np.asarray(valores[indice_clase][indice_fila], dtype=float)
        else:
            arr = np.asarray(valores, dtype=float)
            contribuciones = arr[indice_fila, :, indice_clase] if arr.ndim == 3 else arr[indice_fila]
        resultados.append(dict(zip(columnas, contribuciones, strict=True)))
    return resultados


def explicar_driver(
    modelo: HistGradientBoostingClassifier,
    referencia: pd.DataFrame,
    filas: pd.DataFrame,
    max_referencia: int = 50,
) -> list[dict[str, object]]:
    """Devuelve la explicación por escuela según `ExplicacionSHAPOut` de la API."""
    predicciones = predecir_driver(modelo, filas)
    valores_shap = calcular_shap_batch(modelo, filas)

    explicaciones: list[dict[str, object]] = []
    for prediccion, contribuciones in zip(
        predicciones.to_dict(orient="records"),
        valores_shap,
        strict=True,
    ):
        explicaciones.append(
            {
                "cct": prediccion["cct"],
                "driver_dominante": prediccion["driver_dominante"],
                "contribuciones": {
                    DRIVER_A_CLASE[driver]: (
                        float(contribuciones[driver]) if driver in contribuciones else None
                    )
                    for driver in DRIVERS
                },
            }
        )
    return explicaciones


def _imprimir_reporte(resultado: ResultadoML02) -> None:
    print(f"Target usado: {resultado.columna_target_usada}")
    print(f"\n{'ventana':52} {'F1 macro':>9} {'accuracy':>9} {'baseline':>9} {'mejora':>8}")
    print("-" * 92)
    for ventana in resultado.ventanas:
        print(
            f"{ventana.particion!s:52} {ventana.f1_macro:9.4f} {ventana.accuracy:9.4f} "
            f"{ventana.f1_macro_baseline:9.4f} {ventana.mejora_sobre_baseline:7.1%}"
        )
    print("-" * 92)
    print(
        f"F1 macro {resultado.f1_macro_promedio:.4f} +/- {resultado.f1_macro_desviacion:.4f}    "
        f"Accuracy {resultado.accuracy_promedio:.4f}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Entrena y evalua ML-02 (US-302).")
    parser.add_argument("--features", type=Path, default=FEATURES_POR_DEFECTO)
    parser.add_argument("--ventanas", type=int, default=3)
    parser.add_argument(
        "--tracking-uri",
        default=os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"),
        help="URI de MLflow para registrar el modelo",
    )
    parser.add_argument("--sin-mlflow", action="store_true", help="solo entrena y reporta")
    parser.add_argument(
        "--registrar-modelo", action="store_true", help=f"publica en registry como {NOMBRE_MODELO}"
    )
    args = parser.parse_args()

    df = cargar_features_ml02(args.features)
    resultado = entrenar_y_evaluar(df, n_ventanas=args.ventanas)
    _imprimir_reporte(resultado)
    if not args.sin_mlflow:
        run_id = registrar_en_mlflow(
            resultado, tracking_uri=args.tracking_uri, registrar_modelo=args.registrar_modelo
        )
        print(f"\nMLflow run_id: {run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
