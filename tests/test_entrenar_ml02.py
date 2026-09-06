"""Pruebas del scaffold de ML-02 (US-302)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.modelos.contrato import DRIVERS
from src.modelos.entrenar_ml02 import (
    CLASES_DRIVER,
    COLUMNA_TARGET_PROXY,
    NOMBRE_MODELO,
    cargar_features_ml02,
    columna_target_disponible,
    entrenar_y_evaluar,
    explicar_driver,
    generar_driver_dominante_proxy,
    predecir_driver,
    recomendacion_para_driver,
    validar_target_ml02,
)
from src.modelos.particion_temporal import _anio_inicial


def test_deriva_driver_dominante_proxy_sin_imputar_cero(features: pd.DataFrame) -> None:
    proxy = generar_driver_dominante_proxy(features)
    assert set(proxy) <= set(CLASES_DRIVER)

    fila = pd.DataFrame([{driver: np.nan for driver in DRIVERS} | {"d2_inseguridad": 0.7}])
    assert generar_driver_dominante_proxy(fila).iloc[0] == "D2"


def test_falla_si_no_hay_ningun_driver_observado() -> None:
    fila = pd.DataFrame([{driver: np.nan for driver in DRIVERS}])
    with pytest.raises(ValueError, match="sin ningun driver"):
        generar_driver_dominante_proxy(fila)


def test_carga_fixture_y_agrega_target_proxy(tmp_path, features: pd.DataFrame) -> None:
    """Cuando la tabla NO trae `driver_dominante` real, se agrega el proxy (comportamiento
    histórico de esta función). El fixture por defecto (`features_escuela_mock.csv`) ya trae
    `driver_dominante` real desde que Gold lo publica (US-302, 2026-08-28, ver
    `dbt/models/gold/features_escuela.sql`) -- por eso aquí se prueba contra una copia sin esa
    columna, para seguir cubriendo la rama de "todavía no hay etiqueta real"."""
    sin_columna_real = features.drop(columns=["driver_dominante"])
    ruta = tmp_path / "features_sin_driver_dominante_real.csv"
    sin_columna_real.to_csv(ruta, index=False)

    df = cargar_features_ml02(ruta=ruta)
    assert COLUMNA_TARGET_PROXY in df.columns
    assert columna_target_disponible(df) == COLUMNA_TARGET_PROXY


def test_paridad_driver_dominante_real_contra_proxy(features: pd.DataFrame) -> None:
    """Prueba de paridad pedida por Andrés González Habib/C3 (2026-08-28, US-302): la etiqueta
    REAL que ahora publica Gold (`dbt/models/gold/features_escuela.sql`, CTE
    `con_driver_dominante`) debe coincidir con `generar_driver_dominante_proxy()` en las filas
    donde el proxy sí puede calcularse (al menos un driver observado). Ambas implementan la
    misma regla de argmax con el mismo desempate (primer driver en orden D1..D6) y con D3/D4
    invertidos como (1 - valor), porque miden servicios presentes y suben cuando la escuela está
    mejor (P-05, 2026-08-31) -- una en SQL, otra en Python. El fixture
    tests/fixtures/features_escuela_mock.csv ya trae la columna driver_dominante con esa misma
    regla. Si llegaran a divergir, Gold y ML-02 estarían entrenando/reportando sobre etiquetas
    distintas sin que nadie se diera cuenta."""
    con_al_menos_un_driver = features[features[list(DRIVERS)].notna().any(axis=1)]
    proxy = generar_driver_dominante_proxy(con_al_menos_un_driver).reset_index(drop=True)
    real = con_al_menos_un_driver["driver_dominante"].reset_index(drop=True)

    assert (real == proxy).all(), (
        "driver_dominante (Gold) diverge de generar_driver_dominante_proxy() (Python) en al "
        f"menos una fila: {int((real != proxy).sum())} de {len(real)} no coinciden."
    )


def test_prefiere_target_real_cuando_esta_disponible(features: pd.DataFrame) -> None:
    df = features.copy()
    df["driver_dominante"] = generar_driver_dominante_proxy(df)
    df[COLUMNA_TARGET_PROXY] = "D6"

    assert columna_target_disponible(df) == "driver_dominante"


@pytest.mark.parametrize(
    ("valores", "mensaje"),
    [
        (["D1", None], "etiquetas nulas"),
        (["D1", "D9"], "clases inválidas"),
        (["D1", "D1"], "al menos dos clases"),
    ],
)
def test_rechaza_target_que_no_cumple_contrato(valores, mensaje) -> None:
    df = pd.DataFrame({"driver_dominante": valores})

    with pytest.raises(ValueError, match=mensaje):
        validar_target_ml02(df, "driver_dominante")


@pytest.fixture(scope="module")
def resultado_ml02(features: pd.DataFrame):
    df = features.copy()
    df[COLUMNA_TARGET_PROXY] = generar_driver_dominante_proxy(df)
    return entrenar_y_evaluar(df, n_ventanas=3)


def test_ml02_genera_backtesting_temporal(resultado_ml02) -> None:
    assert len(resultado_ml02.ventanas) == 3
    for ventana in resultado_ml02.ventanas:
        ultimo_train = max(_anio_inicial(c) for c in ventana.particion.ciclos_entrenamiento)
        primero_test = min(_anio_inicial(c) for c in ventana.particion.ciclos_prueba)
        assert ultimo_train < primero_test


def test_metricas_de_clasificacion_son_acotadas(resultado_ml02) -> None:
    for ventana in resultado_ml02.ventanas:
        assert 0 <= ventana.f1_macro <= 1
        assert 0 <= ventana.accuracy <= 1
        assert 0 <= ventana.precision_macro <= 1


def test_driver_vacio_en_entrenamiento_no_rompe_ml02(features: pd.DataFrame) -> None:
    """Reproduce BUG-018: D6 solo tiene cobertura en el ciclo más reciente."""
    df = features.copy()
    ciclos = sorted(df["id_ciclo"].unique())
    df.loc[df["id_ciclo"] != ciclos[-1], "d6_aire"] = np.nan

    resultado = entrenar_y_evaluar(df, n_ventanas=2)

    assert resultado.excluidos_por_ventana
    assert any(
        "d6_aire" in excluidos for excluidos in resultado.excluidos_por_ventana.values()
    )
    predicciones = predecir_driver(resultado.modelo, df[df["id_ciclo"] == ciclos[-1]])
    assert len(predicciones) > 0


def test_falla_claro_si_ningun_driver_tiene_datos(features: pd.DataFrame) -> None:
    df = features.copy()
    df[list(DRIVERS)] = np.nan

    with pytest.raises(ValueError, match="Ningún driver tiene datos"):
        entrenar_y_evaluar(df, n_ventanas=2)


def test_prediccion_incluye_driver_y_recomendacion(resultado_ml02, features: pd.DataFrame) -> None:
    predicciones = predecir_driver(resultado_ml02.modelo, features.head(5))
    assert set(predicciones.columns) == {"cct", "id_ciclo", "driver_dominante", "recomendacion"}
    assert set(predicciones["driver_dominante"]) <= set(CLASES_DRIVER)
    assert predicciones["recomendacion"].str.len().min() > 0


def test_recomendacion_falla_con_driver_desconocido() -> None:
    with pytest.raises(ValueError, match="Driver desconocido"):
        recomendacion_para_driver("D9")


def test_nombre_mlflow_es_canonico() -> None:
    assert NOMBRE_MODELO == "ML02_DriverClasificador"


def test_explicacion_shap_cumple_contrato_api(
    resultado_ml02,
    features: pd.DataFrame,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    filas = features.head(2)
    contribuciones = [
        {driver: float(indice) for indice, driver in enumerate(DRIVERS)}
        for _ in range(len(filas))
    ]
    monkeypatch.setattr(
        "src.modelos.entrenar_ml02.calcular_shap_batch",
        lambda *args, **kwargs: contribuciones,
    )

    explicaciones = explicar_driver(resultado_ml02.modelo, features, filas)

    assert len(explicaciones) == len(filas)
    assert set(explicaciones[0]) == {"cct", "driver_dominante", "contribuciones"}
    assert set(explicaciones[0]["contribuciones"]) == set(CLASES_DRIVER)
    assert explicaciones[0]["cct"] == filas.iloc[0]["cct"]


def test_explicacion_shap_marca_driver_excluido_como_sin_dato(
    resultado_ml02,
    features: pd.DataFrame,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    filas = features.head(1)
    contribuciones = [{driver: 0.1 for driver in DRIVERS if driver != "d5_agua"}]
    monkeypatch.setattr(
        "src.modelos.entrenar_ml02.calcular_shap_batch",
        lambda *args, **kwargs: contribuciones,
    )

    explicacion = explicar_driver(resultado_ml02.modelo, features, filas)[0]

    assert set(explicacion["contribuciones"]) == set(CLASES_DRIVER)
    assert explicacion["contribuciones"]["D5"] is None
