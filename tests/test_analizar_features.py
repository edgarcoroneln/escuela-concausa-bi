"""Pruebas del diagnóstico de features y cobertura (US-322, US-325)."""

from __future__ import annotations

import warnings

import pandas as pd
import pytest

from src.modelos.analizar_features import (
    COLUMNA_TARGET,
    cobertura_por_driver,
    cobertura_por_entidad,
    cobertura_por_municipio,
    columnas_excluidas_por_fuga,
    completitud_por_entidad,
    completitud_por_municipio,
    correlaciones_drivers,
    dispersion_cobertura_municipal,
    requerir_clave_municipio,
    resumen_eda,
    validar_features_para_analisis,
    variables_candidatas_ml03,
)
from src.modelos.contrato import DRIVERS


@pytest.fixture
def features_municipales(features: pd.DataFrame) -> pd.DataFrame:
    """Agrega una asignación municipal sintética explícita; no la infiere del CCT."""
    salida = features.copy()
    ccts = sorted(salida["cct"].unique())
    asignacion = {
        cct: f"{cct[:2]}{(indice % 3) + 1:03d}"
        for indice, cct in enumerate(ccts)
    }
    salida["cve_mun"] = salida["cct"].map(asignacion).astype("string")
    return salida


def test_fixture_cumple_contrato_para_diagnostico(features: pd.DataFrame) -> None:
    validar_features_para_analisis(features)


def test_detecta_cobertura_inconsistente(features: pd.DataFrame) -> None:
    inconsistente = features.copy()
    inconsistente.loc[0, "d5_agua"] = None
    inconsistente.loc[0, "d5_cobertura"] = "OK"

    with pytest.raises(ValueError, match="Cobertura inconsistente"):
        validar_features_para_analisis(inconsistente)


def test_detecta_llave_duplicada(features: pd.DataFrame) -> None:
    duplicado = pd.concat([features, features.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="filas duplicadas"):
        validar_features_para_analisis(duplicado)


def test_eda_reporta_nulos_y_correlacion(features: pd.DataFrame) -> None:
    reporte = resumen_eda(features)

    assert set(reporte["feature"]) == {*DRIVERS, "indice_completitud_drivers", COLUMNA_TARGET}
    assert pd.isna(reporte.loc[reporte["feature"] == COLUMNA_TARGET, "correlacion_target"].item())
    assert reporte["nulos"].sum() > 0


def test_correlaciones_excluyen_target(features: pd.DataFrame) -> None:
    matriz = correlaciones_drivers(features)

    assert set(matriz.columns) == {*DRIVERS, "indice_completitud_drivers"}
    assert COLUMNA_TARGET not in matriz.columns


def test_correlaciones_constantes_quedan_nulas_sin_runtime_warning(
    features: pd.DataFrame,
) -> None:
    """Una variable constante no tiene Pearson definido y no debe ensuciar la corrida."""
    constantes = features.copy()
    disponibles = constantes["d1_cobertura"].eq("OK")
    constantes.loc[disponibles, "d1_pobreza"] = 1.0

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        eda = resumen_eda(constantes)
        matriz = correlaciones_drivers(constantes)

    fila_d1 = eda.loc[eda["feature"] == "d1_pobreza"].iloc[0]
    assert pd.isna(fila_d1["correlacion_target"])
    assert pd.isna(matriz.loc["d1_pobreza", "d2_inseguridad"])
    assert pd.isna(matriz.loc["d1_pobreza", "d1_pobreza"])


def test_variables_ml03_excluyen_llaves_y_target() -> None:
    candidatas = variables_candidatas_ml03()

    assert set(candidatas).isdisjoint(columnas_excluidas_por_fuga())
    assert {"d5_dato_disponible", "d6_dato_disponible"} <= set(candidatas)
    assert {"cct", "cve_mun", "id_ciclo", COLUMNA_TARGET} <= set(
        columnas_excluidas_por_fuga()
    )


def test_cobertura_por_driver_cuadra_con_observaciones(features: pd.DataFrame) -> None:
    reporte = cobertura_por_driver(features)

    assert set(reporte["driver"]) == set(DRIVERS)
    assert (reporte["con_dato"] + reporte["sin_dato"] == len(features)).all()
    assert reporte["pct_sin_dato"].between(0, 1).all()


def test_cobertura_y_completitud_por_entidad(features: pd.DataFrame) -> None:
    cobertura = cobertura_por_entidad(features)
    completitud = completitud_por_entidad(features)

    assert set(cobertura["driver"]) == set(DRIVERS)
    assert set(cobertura["entidad"]) == set(completitud["entidad"])
    assert completitud["completitud_promedio"].between(0, 1).all()


def test_analisis_municipal_no_infiere_clave_desde_cct(features: pd.DataFrame) -> None:
    """Sin `cve_mun`, el análisis municipal se detiene en vez de inferirla del CCT.

    La ausencia se construye aquí a propósito. Antes el test la heredaba del fixture
    compartido, que no traía la columna; cuando US-325 la incorporó al contrato el
    escenario dejó de existir y la prueba pasó a no comprobar nada.
    """
    sin_clave = features.drop(columns=["cve_mun"], errors="ignore")

    with pytest.raises(ValueError, match="requiere cve_mun"):
        requerir_clave_municipio(sin_clave)


def test_clave_municipal_conserva_cero_inicial(
    features_municipales: pd.DataFrame,
) -> None:
    requerir_clave_municipio(features_municipales)

    municipios_cdmx = features_municipales.loc[
        features_municipales["cct"].str.startswith("09"), "cve_mun"
    ]
    assert municipios_cdmx.str.fullmatch(r"09\d{3}").all()


@pytest.mark.parametrize("cve_mun", ["9001", "09A01", "090001", None])
def test_rechaza_clave_municipal_invalida(
    features_municipales: pd.DataFrame, cve_mun: str | None
) -> None:
    invalido = features_municipales.copy()
    invalido.loc[invalido.index[0], "cve_mun"] = cve_mun

    with pytest.raises(ValueError, match="cve_mun"):
        requerir_clave_municipio(invalido)


def test_rechaza_municipio_de_otra_entidad(
    features_municipales: pd.DataFrame,
) -> None:
    invalido = features_municipales.copy()
    invalido.loc[invalido.index[0], "cve_mun"] = "99001"

    with pytest.raises(ValueError, match="misma entidad"):
        requerir_clave_municipio(invalido)


def test_cobertura_municipal_cuadra_con_totales(
    features_municipales: pd.DataFrame,
) -> None:
    municipal = cobertura_por_municipio(features_municipales)
    global_ = cobertura_por_driver(features_municipales).set_index("driver")
    agregado = municipal.groupby("driver").agg(
        observaciones=("observaciones", "sum"),
        con_dato=("con_dato", "sum"),
        sin_dato=("sin_dato", "sum"),
    )

    assert agregado["observaciones"].eq(len(features_municipales)).all()
    assert agregado["con_dato"].equals(global_["con_dato"])
    assert agregado["sin_dato"].equals(global_["sin_dato"])
    assert municipal["pct_sin_dato"].between(0, 1).all()


def test_completitud_y_dispersion_municipal(
    features_municipales: pd.DataFrame,
) -> None:
    completitud = completitud_por_municipio(features_municipales)
    dispersion = dispersion_cobertura_municipal(features_municipales)

    assert completitud["completitud_promedio"].between(0, 1).all()
    assert (completitud["ciclos"] > 0).all()
    assert set(dispersion["driver"]) == set(DRIVERS)
    assert dispersion["brecha_pct_sin_dato"].between(0, 1).all()
    assert (
        dispersion["pct_max_sin_dato"] >= dispersion["pct_min_sin_dato"]
    ).all()
