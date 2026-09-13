"""Preflight auditable para cerrar la integración de ML-03 (US-631).

El preflight no entrena, no imputa y no publica asignaciones. Convierte el
contrato de ``gold.features_escuela`` en agregados de elegibilidad para la
variante candidata D1--D4. D5/D6 se auditan, pero no participan del cálculo:
su cobertura parcial no se transforma en una señal de clustering.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.modelos.analizar_features import validar_features_para_analisis
from src.modelos.contrato import columna_cobertura, entidad_de_cct

FEATURES_CANDIDATAS: tuple[str, ...] = (
    "d1_pobreza",
    "d2_inseguridad",
    "d3_infraestructura",
    "d4_conectividad",
)
DRIVERS_AUDITORIA: tuple[str, ...] = ("d5_agua", "d6_aire")


def _agregados_json(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convierte tablas agregadas a valores serializables sin exponer CCT."""
    return df.to_dict(orient="records")


def generar_preflight(df: pd.DataFrame) -> dict[str, Any]:
    """Genera evidencia agregada de elegibilidad para la variante D1--D4.

    La salida contiene conteos por ciclo y entidad, además de las causas de
    exclusión por driver. Una fila puede faltar en más de un driver; por eso
    el total de causas no debe sumarse para obtener las filas excluidas.
    """
    validar_features_para_analisis(df)
    detalle = df.loc[:, ["cct", "id_ciclo", *FEATURES_CANDIDATAS]].copy()
    detalle["entidad"] = detalle["cct"].map(entidad_de_cct)

    coberturas = pd.DataFrame(
        {
            driver: df[columna_cobertura(driver)].eq("OK")
            for driver in FEATURES_CANDIDATAS
        }
    )
    detalle["elegible_d1_d4"] = coberturas.all(axis=1)

    elegibilidad = (
        detalle.groupby(["id_ciclo", "entidad"], sort=True)
        .agg(
            filas=("cct", "size"),
            elegibles=("elegible_d1_d4", "sum"),
        )
        .reset_index()
    )
    elegibilidad["elegibles"] = elegibilidad["elegibles"].astype(int)
    elegibilidad["excluidas"] = elegibilidad["filas"] - elegibilidad["elegibles"]

    causas: list[dict[str, Any]] = []
    for driver in FEATURES_CANDIDATAS:
        sin_dato = ~coberturas[driver]
        por_grupo = (
            pd.DataFrame(
                {
                    "id_ciclo": detalle["id_ciclo"],
                    "entidad": detalle["entidad"],
                    "sin_dato": sin_dato,
                }
            )
            .groupby(["id_ciclo", "entidad"], sort=True)["sin_dato"]
            .sum()
            .reset_index(name="filas_sin_dato")
        )
        for fila in _agregados_json(por_grupo):
            fila["driver"] = driver
            fila["filas_sin_dato"] = int(fila["filas_sin_dato"])
            causas.append(fila)

    auditoria_parcial = []
    for driver in DRIVERS_AUDITORIA:
        sin_dato = df[columna_cobertura(driver)].eq("SIN_DATO")
        auditoria_parcial.append(
            {
                "driver": driver,
                "observaciones": len(df),
                "sin_dato": int(sin_dato.sum()),
                "pct_sin_dato": float(sin_dato.mean()),
                "incluido_en_vector": False,
                "afecta_elegibilidad_d1_d4": False,
            }
        )

    return {
        "estado": "evidencia_para_revision",
        "vector_candidato": list(FEATURES_CANDIDATAS),
        "politica_ausencia": "casos_completos_solo_d1_d4",
        "filas_totales": len(detalle),
        "filas_elegibles": int(detalle["elegible_d1_d4"].sum()),
        "filas_excluidas": int((~detalle["elegible_d1_d4"]).sum()),
        "elegibilidad_ciclo_entidad": _agregados_json(elegibilidad),
        "causas_exclusion_ciclo_entidad": causas,
        "auditoria_d5_d6": auditoria_parcial,
        "limites": [
            "D5 y D6 se auditan; no se imputan ni entran al vector candidato.",
            "Las filas excluidas no representan escuelas sanas ni un cluster adicional.",
            "Este preflight no registra MLflow, no publica Gold y no cierra RISK-011.",
        ],
    }
