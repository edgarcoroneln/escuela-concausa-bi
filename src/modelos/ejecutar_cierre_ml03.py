"""Evidencia agregada desde Gold para US-321, US-322 y US-325.

El comando no exporta observaciones individuales ni imputa ausencias. Lee
``gold.features_escuela``, valida su contrato, produce agregados de EDA y
cobertura y ejecuta ML-03 únicamente cuando la política vigente de casos
completos deja observaciones suficientes.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import create_engine

from src.modelos.analizar_features import (
    cobertura_por_driver,
    cobertura_por_entidad,
    cobertura_por_municipio,
    completitud_por_entidad,
    completitud_por_municipio,
    correlaciones_drivers,
    dispersion_cobertura_municipal,
    resumen_eda,
)
from src.modelos.entrenar_ml01 import cargar_features_desde_gold
from src.modelos.entrenar_ml03 import (
    FEATURES_ML03,
    SEMILLAS_ESTABILIDAD_DEFAULT,
    entrenar_y_evaluar,
    evaluar_estabilidad_semillas,
    registrar_en_mlflow,
)


def _registros(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convierte una tabla agregada a valores JSON nativos."""
    return json.loads(df.to_json(orient="records"))


def _resumen_ml03(
    df: pd.DataFrame,
    evaluar_estabilidad: bool = False,
    semillas_estabilidad: tuple[int, ...] = SEMILLAS_ESTABILIDAD_DEFAULT,
) -> tuple[dict[str, Any], Any | None]:
    """Ejecuta ML-03 o conserva el bloqueo honesto de la política vigente.

    `evaluar_estabilidad=True` agrega el bloque `estabilidad` (ARI entre
    `semillas_estabilidad`, ver `evaluar_estabilidad_semillas`) -- es el cálculo
    reproducible detrás de `ari_minimo`/`ari_promedio` en
    `ML03_Comparacion_RISK011_20260910.json`. Se deja opcional porque repite el
    entrenamiento una vez por semilla adicional (5 por defecto).
    """
    try:
        resultado = entrenar_y_evaluar(df)
    except ValueError as error:
        return (
            {
                "estado": "bloqueado",
                "politica_ausencia": "casos_completos",
                "motivo": str(error),
            },
            None,
        )

    resumen: dict[str, Any] = {
        "estado": "ejecutado",
        "politica_ausencia": resultado.politica_ausencia,
        "features": list(FEATURES_ML03),
        "filas_totales": resultado.filas_totales,
        "filas_entrenadas": resultado.filas_entrenadas,
        "filas_excluidas": resultado.filas_excluidas,
        "k_seleccionado": resultado.k_seleccionado,
        "silhouette_temporal_promedio": resultado.silhouette_promedio,
        "metricas_temporales": _registros(resultado.metricas),
        "perfiles_agregados": _registros(resultado.perfiles),
    }
    if evaluar_estabilidad:
        resumen["estabilidad"] = evaluar_estabilidad_semillas(
            df, resultado.k_seleccionado, semillas=semillas_estabilidad
        )

    return resumen, resultado


def _registro_mlflow_confirmado(
    tracking_uri: str | None, confirmar_registro: bool
) -> bool:
    """Evita registrar una corrida antes de revisar su evidencia agregada."""
    if tracking_uri and not confirmar_registro:
        raise ValueError(
            "--tracking-uri requiere --confirmar-registro; primero revisa k, "
            "Silhouette y perfiles agregados."
        )
    if confirmar_registro and not tracking_uri:
        raise ValueError("--confirmar-registro requiere --tracking-uri.")
    return bool(tracking_uri)


def generar_evidencia(
    df: pd.DataFrame,
    evaluar_estabilidad: bool = False,
    semillas_estabilidad: tuple[int, ...] = SEMILLAS_ESTABILIDAD_DEFAULT,
) -> tuple[dict[str, Any], Any | None]:
    """Genera evidencia agregada sin incluir llaves de escuelas individuales."""
    eda = resumen_eda(df)
    reporte: dict[str, Any] = {
        "fuente": "gold.features_escuela",
        "grano": "cct × id_ciclo",
        "metadatos": {
            "filas": len(df),
            "escuelas": int(df["cct"].nunique()),
            "ciclos": sorted(df["id_ciclo"].astype(str).unique().tolist()),
            "duplicados_cct_ciclo": int(df.duplicated(["cct", "id_ciclo"]).sum()),
        },
        "eda": _registros(eda),
        "correlaciones_sin_target": _registros(
            correlaciones_drivers(df).reset_index(names="feature")
        ),
        "cobertura_driver": _registros(cobertura_por_driver(df)),
        "cobertura_entidad": _registros(cobertura_por_entidad(df)),
        "completitud_entidad": _registros(completitud_por_entidad(df)),
    }

    if "cve_mun" in df.columns and not bool(df["cve_mun"].isna().any()):
        reporte["municipal"] = {
            "estado": "disponible",
            "cobertura": _registros(cobertura_por_municipio(df)),
            "completitud": _registros(completitud_por_municipio(df)),
            "dispersion": _registros(dispersion_cobertura_municipal(df)),
        }
    else:
        reporte["municipal"] = {
            "estado": "bloqueado",
            "motivo": "Gold no contiene cve_mun completa; coordinar el contrato con Célula 1.",
        }

    reporte["ml03"], resultado = _resumen_ml03(
        df, evaluar_estabilidad=evaluar_estabilidad, semillas_estabilidad=semillas_estabilidad
    )
    return reporte, resultado


def main() -> int:
    """Lee Gold, imprime evidencia agregada y opcionalmente registra ML-03."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--url",
        default=os.environ.get("DATABASE_URL"),
        help="URL SQLAlchemy; se recomienda definir DATABASE_URL para no exponer credenciales",
    )
    parser.add_argument("--esquema", default="gold")
    parser.add_argument("--salida", type=Path, help="JSON agregado opcional")
    parser.add_argument(
        "--tracking-uri",
        help="registra la corrida sólo si ML-03 se ejecutó y esta opción fue indicada",
    )
    parser.add_argument(
        "--confirmar-registro",
        action="store_true",
        help="confirma que la evidencia agregada de la corrida fue revisada antes de MLflow",
    )
    parser.add_argument(
        "--estabilidad",
        action="store_true",
        help=(
            "agrega el bloque 'estabilidad' (ARI entre semillas, ver "
            "evaluar_estabilidad_semillas) -- repite el entrenamiento una vez por "
            "semilla adicional, además de la corrida principal"
        ),
    )
    parser.add_argument(
        "--semillas-estabilidad",
        type=int,
        nargs="+",
        default=list(SEMILLAS_ESTABILIDAD_DEFAULT),
        help=f"semillas para --estabilidad (default: {list(SEMILLAS_ESTABILIDAD_DEFAULT)})",
    )
    args = parser.parse_args()
    if not args.url:
        parser.error("define DATABASE_URL o usa --url para leer gold.features_escuela")
    try:
        registrar_mlflow = _registro_mlflow_confirmado(
            args.tracking_uri, args.confirmar_registro
        )
    except ValueError as error:
        parser.error(str(error))

    engine = create_engine(args.url)
    features = cargar_features_desde_gold(engine, esquema=args.esquema)
    evidencia, resultado = generar_evidencia(
        features,
        evaluar_estabilidad=args.estabilidad,
        semillas_estabilidad=tuple(args.semillas_estabilidad),
    )

    if registrar_mlflow:
        if resultado is None:
            evidencia["mlflow"] = {
                "estado": "no_registrado",
                "motivo": "ML-03 no produjo una corrida válida.",
            }
        else:
            estabilidad = evidencia["ml03"].get("estabilidad")
            evidencia["mlflow"] = {
                "estado": "registrado",
                "run_id": registrar_en_mlflow(
                    resultado,
                    args.tracking_uri,
                    ari_minimo=estabilidad["ari_minimo"] if estabilidad else None,
                    ari_promedio=estabilidad["ari_promedio"] if estabilidad else None,
                    semillas_estabilidad=tuple(estabilidad["semillas"]) if estabilidad else (),
                ),
            }

    contenido = json.dumps(evidencia, ensure_ascii=False, indent=2)
    if args.salida:
        args.salida.write_text(f"{contenido}\n", encoding="utf-8")
    print(contenido)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
