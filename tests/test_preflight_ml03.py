"""Pruebas del preflight agregado para US-631."""

from __future__ import annotations

from src.modelos.preflight_ml03 import (
    DRIVERS_AUDITORIA,
    FEATURES_CANDIDATAS,
    generar_preflight,
)


def test_preflight_no_expone_cct_y_no_usa_d5_d6(features) -> None:
    base = generar_preflight(features)
    datos = features.copy()
    for driver in DRIVERS_AUDITORIA:
        datos[driver] = None
        datos[f"{driver.split('_')[0]}_cobertura"] = "SIN_DATO"

    resultado = generar_preflight(datos)

    assert resultado["vector_candidato"] == list(FEATURES_CANDIDATAS)
    assert resultado["filas_elegibles"] == base["filas_elegibles"]
    assert resultado["filas_excluidas"] == base["filas_excluidas"]
    assert not any(cct in str(resultado) for cct in datos["cct"].unique())
    assert all(not fila["incluido_en_vector"] for fila in resultado["auditoria_d5_d6"])
    assert all(not fila["afecta_elegibilidad_d1_d4"] for fila in resultado["auditoria_d5_d6"])


def test_preflight_reporta_causa_de_exclusion_por_driver(features) -> None:
    base = generar_preflight(features)
    datos = features.copy()
    elegibles = datos.index[
        datos[[f"{driver.split('_')[0]}_cobertura" for driver in FEATURES_CANDIDATAS]]
        .eq("OK")
        .all(axis=1)
    ][:2]
    datos.loc[elegibles, "d2_inseguridad"] = None
    datos.loc[elegibles, "d2_cobertura"] = "SIN_DATO"

    resultado = generar_preflight(datos)

    assert resultado["filas_excluidas"] == base["filas_excluidas"] + 2
    causas_d2 = [
        fila
        for fila in resultado["causas_exclusion_ciclo_entidad"]
        if fila["driver"] == "d2_inseguridad"
    ]
    base_causas_d2 = [
        fila
        for fila in base["causas_exclusion_ciclo_entidad"]
        if fila["driver"] == "d2_inseguridad"
    ]
    assert sum(fila["filas_sin_dato"] for fila in causas_d2) == (
        sum(fila["filas_sin_dato"] for fila in base_causas_d2) + 2
    )
    assert all("cct" not in fila for fila in resultado["elegibilidad_ciclo_entidad"])
