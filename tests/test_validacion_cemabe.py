"""Pruebas offline de la suite Great Expectations de DS-03 CEMABE."""

from __future__ import annotations

import pandas as pd

import great_expectations as gx
from src.ingesta.validacion_cemabe import SUITE_NAME, construir_suite, validar


def _df_limpio() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "cct": "09DPR0001A",
                "agua": "1",
                "drenaje": "1",
                "electricidad": "1",
                "sanitarios": "1",
                "internet": "0",
                "computadoras": "1",
            },
            {
                "cct": "15DPR0002B",
                "agua": "SIN_DATO",
                "drenaje": "0",
                "electricidad": "1",
                "sanitarios": "SIN_DATO",
                "internet": "0",
                "computadoras": "SIN_DATO",
            },
        ]
    )


def test_suite_ds03_declara_las_quince_expectativas() -> None:
    context = gx.get_context(mode="ephemeral")
    suite = construir_suite(context)

    assert suite.name == SUITE_NAME
    assert len(suite.expectations) == 15
    assert any(
        expectativa.expectation_type == "expect_column_values_to_be_unique"
        and expectativa.column == "cct"
        for expectativa in suite.expectations
    )


def test_datos_limpios_pasan_todas_las_expectativas() -> None:
    context = gx.get_context(mode="ephemeral")

    resultado = validar(_df_limpio(), context)

    assert resultado.success is True
    assert resultado.statistics["successful_expectations"] == 15


def test_detecta_brechas_de_llave_y_catalogos() -> None:
    df = pd.DataFrame(
        [
            {
                "cct": "09DPR0001A",
                "agua": "2",
                "drenaje": None,
                "electricidad": "1",
                "sanitarios": "1",
                "internet": "0",
                "computadoras": "1",
            },
            {
                "cct": "09DPR0001A",
                "agua": "1",
                "drenaje": "1",
                "electricidad": "1",
                "sanitarios": "1",
                "internet": "0",
                "computadoras": "1",
            },
            {
                "cct": "CORTA",
                "agua": "1",
                "drenaje": "1",
                "electricidad": "1",
                "sanitarios": "1",
                "internet": "0",
                "computadoras": "1",
            },
        ]
    )
    context = gx.get_context(mode="ephemeral")

    resultado = validar(df, context)

    assert resultado.success is False
    fallos = {
        (
            validacion.expectation_config.type,
            validacion.expectation_config.kwargs.get("column"),
        )
        for validacion in resultado.results
        if not validacion.success
    }
    assert ("expect_column_values_to_be_unique", "cct") in fallos
    assert ("expect_column_value_lengths_to_equal", "cct") in fallos
    assert ("expect_column_values_to_be_in_set", "agua") in fallos
    assert ("expect_column_values_to_not_be_null", "drenaje") in fallos
