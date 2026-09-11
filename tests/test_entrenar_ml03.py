"""Pruebas del clustering temporal ML-03 (US-321)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.modelos import entrenar_ml03
from src.modelos.contrato import DRIVERS
from src.modelos.entrenar_ml03 import (
    COLUMNA_COMPLETITUD,
    COLUMNAS_PROHIBIDAS,
    DRIVERS_OPERATIVOS_ML03,
    FEATURES_ML03,
    NOMBRE_MODELO,
    entrenar_y_evaluar,
    evaluar_estabilidad_semillas,
    evaluar_k_temporal,
    preparar_casos_completos,
    registrar_en_mlflow,
)


@pytest.fixture
def perfiles_sinteticos() -> pd.DataFrame:
    filas: list[dict[str, object]] = []
    ciclos = ("2020-2021", "2021-2022", "2022-2023", "2023-2024")
    centros = (
        (0.15, 0.20, 0.25, 0.20, 0.15, 0.20),
        (0.75, 0.80, 0.25, 0.30, 0.20, 0.25),
        (0.30, 0.35, 0.80, 0.85, 0.25, 0.30),
    )
    for ciclo_indice, ciclo in enumerate(ciclos):
        for grupo, centro in enumerate(centros):
            for escuela in range(6):
                variacion = (escuela - 2.5) * 0.006 + ciclo_indice * 0.002
                fila: dict[str, object] = {
                    "cct": f"09DPR{grupo}{ciclo_indice}{escuela:02d}X",
                    "id_ciclo": ciclo,
                    "cve_mun": f"0900{grupo + 1}",
                    "indice_completitud_drivers": 1.0,
                    "target_variacion_matricula": -0.1,
                }
                for driver, base in zip(DRIVERS, centro, strict=True):
                    fila[driver] = base + variacion
                    fila[f"{driver.split('_')[0]}_cobertura"] = "OK"
                filas.append(fila)
    return pd.DataFrame(filas)


def test_features_no_contienen_llaves_ni_target() -> None:
    assert set(FEATURES_ML03).isdisjoint(COLUMNAS_PROHIBIDAS)
    assert FEATURES_ML03 == DRIVERS_OPERATIVOS_ML03
    assert COLUMNA_COMPLETITUD not in FEATURES_ML03
    assert {"d5_agua", "d6_aire"}.isdisjoint(FEATURES_ML03)


def test_d5_d6_no_bloquean_el_vector_operativo(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    incompleto = perfiles_sinteticos.copy()
    incompleto["d5_agua"] = incompleto["d5_agua"].astype("Float64")
    incompleto["d6_aire"] = incompleto["d6_aire"].astype("Float64")
    incompleto.loc[:, "d5_agua"] = pd.NA
    incompleto.loc[:, "d5_cobertura"] = "SIN_DATO"
    incompleto.loc[:, "d6_aire"] = pd.NA
    incompleto.loc[:, "d6_cobertura"] = "SIN_DATO"

    completos, excluidos = preparar_casos_completos(incompleto)

    assert excluidos == 0
    assert len(completos) == len(incompleto)
    assert completos.loc[:, FEATURES_ML03].notna().all().all()


def test_casos_completos_no_imputan_drivers_operativos(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    incompleto = perfiles_sinteticos.copy()
    incompleto.loc[incompleto.index[0], "d2_inseguridad"] = None
    incompleto.loc[incompleto.index[0], "d2_cobertura"] = "SIN_DATO"

    completos, excluidos = preparar_casos_completos(incompleto)

    assert excluidos == 1
    assert len(completos) == len(incompleto) - 1
    assert completos.loc[:, FEATURES_ML03].notna().all().all()


def test_rechaza_politica_no_ratificada(perfiles_sinteticos: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="ratificación humana"):
        preparar_casos_completos(
            perfiles_sinteticos, politica_ausencia="mediana_municipal"
        )


def test_backtesting_siempre_evalua_el_futuro(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    metricas = evaluar_k_temporal(
        perfiles_sinteticos, valores_k=(2, 3, 4), n_ventanas=2
    )

    for _, fila in metricas.iterrows():
        anios_train = [int(ciclo[:4]) for ciclo in fila["ciclos_entrenamiento"].split(",")]
        assert max(anios_train) < int(fila["ciclo_prueba"][:4])
    assert metricas["silhouette"].notna().any()


def test_entrena_selecciona_k_y_perfila_negocio(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    resultado = entrenar_y_evaluar(
        perfiles_sinteticos, valores_k=(2, 3, 4), n_ventanas=2
    )

    assert resultado.k_seleccionado in {2, 3, 4}
    assert resultado.silhouette_promedio > 0
    assert len(resultado.asignaciones) == len(perfiles_sinteticos)
    assert resultado.filas_excluidas == 0
    assert COLUMNA_COMPLETITUD in resultado.asignaciones
    assert resultado.perfiles["perfil_negocio"].str.contains(
        "Presión principal"
    ).all()
    assert resultado.perfiles["perfil"].str.startswith("Presión por").all()
    assert set(resultado.perfiles["cluster"]) == set(
        resultado.asignaciones["cluster"]
    )
    assert len(resultado.evidencia) == len(perfiles_sinteticos)
    assert resultado.evidencia["pistas_disponibles"].eq(4).all()
    assert resultado.evidencia["pistas_totales"].eq(6).all()
    assert resultado.evidencia["estado_evidencia"].eq("PARCIAL").all()
    assert resultado.evidencia["descripcion"].str.contains("4 de las 6 pistas").all()
    assert resultado.evidencia["pistas_pendientes"].apply(
        lambda pistas: pistas == ("Estrés hídrico", "Calidad del aire")
    ).all()


def test_target_no_cambia_el_modelo(perfiles_sinteticos: pd.DataFrame) -> None:
    alterado = perfiles_sinteticos.copy()
    alterado["target_variacion_matricula"] = range(len(alterado))

    base = entrenar_y_evaluar(
        perfiles_sinteticos, valores_k=(3,), n_ventanas=1
    )
    otro = entrenar_y_evaluar(alterado, valores_k=(3,), n_ventanas=1)

    assert base.asignaciones["cluster"].equals(otro.asignaciones["cluster"])
    assert base.silhouette_promedio == otro.silhouette_promedio


def test_orden_de_entrada_no_cambia_el_resultado(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    base = entrenar_y_evaluar(
        perfiles_sinteticos, valores_k=(3,), n_ventanas=1
    )
    desordenado = entrenar_y_evaluar(
        perfiles_sinteticos.sample(frac=1, random_state=7),
        valores_k=(3,),
        n_ventanas=1,
    )

    assert base.silhouette_promedio == desordenado.silhouette_promedio
    assert base.asignaciones[["cct", "id_ciclo", "cluster"]].equals(
        desordenado.asignaciones[["cct", "id_ciclo", "cluster"]]
    )


def test_completitud_se_audita_sin_cambiar_el_modelo(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    alterado = perfiles_sinteticos.copy()
    alterado[COLUMNA_COMPLETITUD] = 0.5

    base = entrenar_y_evaluar(
        perfiles_sinteticos, valores_k=(3,), n_ventanas=1
    )
    otro = entrenar_y_evaluar(alterado, valores_k=(3,), n_ventanas=1)

    assert base.asignaciones["cluster"].equals(otro.asignaciones["cluster"])
    assert base.silhouette_promedio == otro.silhouette_promedio
    assert otro.perfiles["completitud_promedio"].eq(0.5).all()


def test_evidencia_insuficiente_no_inventa_cluster(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    incompleto = perfiles_sinteticos.copy()
    incompleto.loc[incompleto.index[0], "d4_conectividad"] = None
    incompleto.loc[incompleto.index[0], "d4_cobertura"] = "SIN_DATO"

    resultado = entrenar_y_evaluar(incompleto, valores_k=(3,), n_ventanas=1)
    evidencia = resultado.evidencia.iloc[0]

    assert pd.isna(evidencia["cluster"])
    assert evidencia["estado_evidencia"] == "INSUFICIENTE"
    assert evidencia["pistas_disponibles"] == 3
    assert evidencia["pistas_pendientes"] == (
        "Conectividad",
        "Estrés hídrico",
        "Calidad del aire",
    )
    assert "3 de las 6 pistas" in evidencia["descripcion"]
    assert incompleto.loc[incompleto.index[0], "d5_agua"] == perfiles_sinteticos.loc[
        perfiles_sinteticos.index[0], "d5_agua"
    ]
    assert incompleto.loc[incompleto.index[0], "d6_aire"] == perfiles_sinteticos.loc[
        perfiles_sinteticos.index[0], "d6_aire"
    ]


def test_estabilidad_semillas_ari_perfecto_en_clusters_separados(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    """Réplica reproducible del hallazgo publicado en
    `ML03_Comparacion_RISK011_20260910.json` / `Propuesta_Cierre_ML03_D1_D4.md`
    (ARI mínimo y promedio 1.0 en cinco semillas): con grupos bien separados, KMeans
    debe converger a la misma partición sin importar la semilla."""
    resultado = evaluar_estabilidad_semillas(
        perfiles_sinteticos, k=3, semillas=(7, 21, 42, 84, 2026)
    )

    assert resultado["semillas"] == [7, 21, 42, 84, 2026]
    assert resultado["k"] == 3
    assert len(resultado["ari_por_par"]) == 10  # C(5, 2)
    assert resultado["ari_minimo"] == pytest.approx(1.0)
    assert resultado["ari_promedio"] == pytest.approx(1.0)
    assert all(valor == pytest.approx(1.0) for valor in resultado["ari_por_par"].values())


def test_estabilidad_semillas_requiere_al_menos_dos(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    with pytest.raises(ValueError, match="al menos 2 semillas"):
        evaluar_estabilidad_semillas(perfiles_sinteticos, k=3, semillas=(42,))


def test_estabilidad_semillas_usa_casos_completos(
    perfiles_sinteticos: pd.DataFrame,
) -> None:
    """Debe excluir filas incompletas igual que `entrenar_y_evaluar`, no tronar con
    NaN en el vector operativo."""
    incompleto = perfiles_sinteticos.copy()
    incompleto.loc[incompleto.index[0], "d1_pobreza"] = None
    incompleto.loc[incompleto.index[0], "d1_cobertura"] = "SIN_DATO"

    resultado = evaluar_estabilidad_semillas(incompleto, k=3, semillas=(7, 21, 42))

    assert resultado["ari_minimo"] == pytest.approx(1.0)


def test_registra_version_canonica_en_mlflow(
    perfiles_sinteticos: pd.DataFrame,
    monkeypatch,
) -> None:
    resultado = entrenar_y_evaluar(
        perfiles_sinteticos, valores_k=(3,), n_ventanas=1
    )
    recibido: dict[str, object] = {}

    def registrar(modelo, config) -> str:
        recibido.update(modelo=modelo, config=config)
        return "run-ml03"

    monkeypatch.setattr(entrenar_ml03, "registrar_sklearn", registrar)

    run_id = registrar_en_mlflow(
        resultado,
        "http://mlflow:5000",
        ari_minimo=1.0,
        ari_promedio=1.0,
        semillas_estabilidad=(7, 21, 42, 84, 2026),
    )

    config = recibido["config"]
    assert run_id == "run-ml03"
    assert recibido["modelo"] is resultado.modelo
    assert config.nombre_modelo == NOMBRE_MODELO == "ML03_ClusteringEscuelas"
    assert config.registrar_modelo is True
    assert config.parametros["features"] == ",".join(FEATURES_ML03)
    assert config.parametros["semilla"] == 42
    assert config.parametros["n_init"] == 20
    assert config.parametros["semillas_estabilidad"] == "7,21,42,84,2026"
    assert config.parametros["version_scikit_learn"]
    assert config.metricas["silhouette_temporal_promedio"] > 0
    assert config.metricas["ari_minimo"] == 1.0
    assert config.metricas["ari_promedio"] == 1.0
    assert config.metricas["observaciones_cluster_0"] > 0
