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


def test_reporta_bloqueo_si_no_hay_casos_completos(features: pd.DataFrame) -> None:
    sin_d5 = features.copy()
    sin_d5["d5_agua"] = None
    sin_d5["d5_cobertura"] = "SIN_DATO"

    evidencia, resultado = generar_evidencia(sin_d5)

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
