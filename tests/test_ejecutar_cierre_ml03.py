"""Pruebas del ejecutor agregado para US-321, US-322 y US-325."""

from __future__ import annotations

import pandas as pd

from src.modelos.ejecutar_cierre_ml03 import generar_evidencia


def test_evidencia_no_expone_cct_y_conserva_agregados(features: pd.DataFrame) -> None:
    evidencia, _ = generar_evidencia(features)

    assert evidencia["metadatos"]["filas"] == len(features)
    assert evidencia["metadatos"]["duplicados_cct_ciclo"] == 0
    serializada = str(evidencia)
    assert not any(cct in serializada for cct in features["cct"].unique())
    assert len(evidencia["cobertura_driver"]) == 6


def test_d5_d6_sin_dato_no_bloquean_ml03(features: pd.DataFrame) -> None:
    sin_d5_d6 = features.copy()
    sin_d5_d6["d5_agua"] = None
    sin_d5_d6["d5_cobertura"] = "SIN_DATO"
    sin_d5_d6["d6_aire"] = None
    sin_d5_d6["d6_cobertura"] = "SIN_DATO"

    evidencia, resultado = generar_evidencia(sin_d5_d6)

    assert resultado is not None
    assert evidencia["ml03"]["estado"] == "ejecutado"
    assert "d5_agua" not in evidencia["ml03"]["features"]
    assert "d6_aire" not in evidencia["ml03"]["features"]
    agua = next(fila for fila in evidencia["cobertura_driver"] if fila["driver"] == "d5_agua")
    aire = next(fila for fila in evidencia["cobertura_driver"] if fila["driver"] == "d6_aire")
    assert agua["pct_sin_dato"] == 1.0
    assert aire["pct_sin_dato"] == 1.0


def test_reporta_bloqueo_si_falta_driver_operativo(features: pd.DataFrame) -> None:
    sin_d2 = features.copy()
    sin_d2["d2_inseguridad"] = None
    sin_d2["d2_cobertura"] = "SIN_DATO"

    evidencia, resultado = generar_evidencia(sin_d2)

    assert resultado is None
    assert evidencia["ml03"]["estado"] == "bloqueado"
    assert "No hay casos completos" in evidencia["ml03"]["motivo"]


def test_ejecuta_ml03_sin_registrar_si_hay_casos_completos(
    features: pd.DataFrame,
) -> None:
    completas = features.dropna().copy()

    evidencia, resultado = generar_evidencia(completas)

    assert resultado is not None
    assert evidencia["ml03"]["estado"] == "ejecutado"
    assert evidencia["ml03"]["k_seleccionado"] in {2, 3, 4, 5, 6}
    assert "mlflow" not in evidencia
