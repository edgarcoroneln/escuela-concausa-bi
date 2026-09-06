"""Pruebas del entrenamiento y backtesting de ML-01 (US-311, TEST-005).

Sólo ejercitan `entrenar_y_evaluar`, que es puro respecto a MLflow: el CI no necesita levantar
tracking ni escribir artefactos. El registro se valida a mano y queda evidenciado en el DevLog.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from src.modelos.contrato import DRIVERS
from src.modelos.entrenar_ml01 import (
    COLUMNA_TARGET,
    HIPERPARAMETROS,
    MetricasVentana,
    _matriz,
    cargar_features,
    cargar_features_desde_gold,
    entrenar_y_evaluar,
    registrar_en_mlflow,
)
from src.modelos.generar_fixture import SCOPE_ENTIDADES
from src.modelos.particion_temporal import ParticionTemporal, _anio_inicial

# --------------------------------------------------------------------------- carga


def test_carga_el_fixture_por_defecto(features: pd.DataFrame) -> None:
    assert len(features) == 400
    assert COLUMNA_TARGET in features.columns


def test_falla_si_no_existe_la_ruta() -> None:
    with pytest.raises(FileNotFoundError, match="generar_fixture"):
        cargar_features(Path("no/existe/features.csv"))


def test_falla_si_la_tabla_no_cumple_el_contrato(tmp_path: Path) -> None:
    """Si la Célula 1 publica una tabla sin las columnas acordadas, se detecta al cargar."""
    ruta = tmp_path / "incompleta.csv"
    pd.DataFrame({"cct": ["09DPR0001X"], "id_ciclo": ["2023-2024"]}).to_csv(ruta, index=False)
    with pytest.raises(ValueError, match="no cumple el contrato"):
        cargar_features(ruta)


# --------------------------------------------------------------------------- backtesting


@pytest.fixture(scope="module")
def resultado(features: pd.DataFrame):
    return entrenar_y_evaluar(features, n_ventanas=3)


def test_genera_las_ventanas_pedidas(resultado) -> None:
    assert len(resultado.ventanas) == 3


def test_la_perdida_default_es_robusta_a_outliers() -> None:
    assert HIPERPARAMETROS["loss"] == "absolute_error"


def test_ninguna_ventana_tiene_fuga_temporal(resultado) -> None:
    """Todo ciclo de entrenamiento es anterior a todo ciclo de prueba, en cada ventana."""
    for ventana in resultado.ventanas:
        ultimo_train = max(_anio_inicial(c) for c in ventana.particion.ciclos_entrenamiento)
        primero_test = min(_anio_inicial(c) for c in ventana.particion.ciclos_prueba)
        assert ultimo_train < primero_test


def test_el_entrenamiento_crece_con_cada_ventana(resultado) -> None:
    tamanos = [v.n_entrena for v in resultado.ventanas]
    assert tamanos == sorted(tamanos)
    assert tamanos[0] < tamanos[-1]


def test_le_gana_al_baseline_en_todas_las_ventanas(resultado) -> None:
    """Si el modelo no supera a predecir la media, no hay modelo."""
    for ventana in resultado.ventanas:
        assert ventana.mae < ventana.mae_baseline
        assert ventana.mejora_sobre_baseline > 0


def test_las_metricas_son_finitas_y_positivas(resultado) -> None:
    for ventana in resultado.ventanas:
        assert np.isfinite([ventana.mae, ventana.rmse, ventana.mae_baseline]).all()
        assert ventana.mae > 0
        assert ventana.rmse >= ventana.mae  # RMSE nunca es menor que MAE


def test_la_ventana_de_produccion_evalua_el_ciclo_mas_reciente(
    resultado, features: pd.DataFrame
) -> None:
    ciclo_mas_reciente = max(features["id_ciclo"], key=_anio_inicial)
    assert resultado.ventana_produccion.particion.ciclos_prueba == (ciclo_mas_reciente,)


def test_agrega_metricas_como_promedio_y_desviacion(resultado) -> None:
    """ADR-003 exige reportar promedio ± desviación de las ventanas."""
    maes = [v.mae for v in resultado.ventanas]
    assert resultado.mae_promedio == pytest.approx(float(np.mean(maes)))
    assert resultado.mae_desviacion == pytest.approx(float(np.std(maes)))


# --------------------------------------------------------------------------- SIN_DATO


def test_no_imputa_los_sin_dato(features: pd.DataFrame) -> None:
    """Regla 4: los `SIN_DATO` llegan al modelo como `NaN`, nunca como cero.

    Compara la matriz que el pipeline entrega al estimador contra la fuente: si alguien mete un
    `fillna(0)` (o cualquier imputación) dentro de `_matriz`, el conteo de nulos cae y esto falla.
    """
    nulos_origen = int(features[list(DRIVERS)].isna().to_numpy().sum())
    assert nulos_origen > 0, "el fixture debería traer SIN_DATO"

    matriz = _matriz(features)
    assert int(matriz.isna().to_numpy().sum()) == nulos_origen, (
        "el pipeline imputó valores ausentes; los SIN_DATO deben llegar como NaN"
    )


def test_el_modelo_predice_con_drivers_ausentes(resultado, features: pd.DataFrame) -> None:
    """Una escuela sin dato de agua ni de aire sigue recibiendo predicción."""
    fila = features[list(DRIVERS)].head(1).copy()
    fila.loc[:, ["d5_agua", "d6_aire"]] = np.nan
    prediccion = resultado.modelo.predict(fila)
    assert np.isfinite(prediccion).all()


# --------------------------------------------------------------------------- error por entidad


def test_desglosa_el_error_por_entidad(resultado) -> None:
    """Insumo de US-312: el análisis de error por entidad."""
    tabla = resultado.error_por_entidad
    assert set(tabla.columns) == {"entidad", "escuelas", "mae"}
    assert set(tabla["entidad"]) <= set(SCOPE_ENTIDADES)
    assert (tabla["mae"] >= 0).all()
    assert tabla["mae"].is_monotonic_decreasing  # ordenado de peor a mejor


# --------------------------------------------------------------------------- métricas


def test_mejora_sobre_baseline_es_una_fraccion() -> None:
    ventana = MetricasVentana(
        particion=ParticionTemporal(("2019-2020",), ("2020-2021",)),
        mae=0.5,
        rmse=0.6,
        mae_baseline=1.0,
        n_entrena=10,
        n_prueba=5,
    )
    assert ventana.mejora_sobre_baseline == pytest.approx(0.5)


def test_mejora_sobre_baseline_es_negativa_si_el_modelo_es_peor() -> None:
    ventana = MetricasVentana(
        particion=ParticionTemporal(("2019-2020",), ("2020-2021",)),
        mae=2.0,
        rmse=2.5,
        mae_baseline=1.0,
        n_entrena=10,
        n_prueba=5,
    )
    assert ventana.mejora_sobre_baseline < 0


# ------------------------------------------------- lectura desde Gold (BUG-013)


def _engine_tmp(tmp_path):
    from sqlalchemy import create_engine

    return create_engine(f"sqlite:///{tmp_path / 'gold.db'}")


def test_lee_las_features_desde_la_tabla_de_gold(features: pd.DataFrame, tmp_path) -> None:
    """El camino que cierra BUG-013: publicar desde `gold.features_escuela`, no del fixture."""
    engine = _engine_tmp(tmp_path)
    features.to_sql("features_escuela", engine, index=False)

    leidas = cargar_features_desde_gold(engine, esquema=None)

    assert len(leidas) == len(features)
    assert set(leidas["id_ciclo"]) == set(features["id_ciclo"])


def test_falla_con_mensaje_accionable_si_gold_no_esta_materializada(tmp_path) -> None:
    """El error debe decir qué hacer, no sólo que algo no existe."""
    with pytest.raises(ValueError, match="dbt run"):
        cargar_features_desde_gold(_engine_tmp(tmp_path), esquema=None)


def test_falla_si_la_tabla_de_gold_esta_vacia(features: pd.DataFrame, tmp_path) -> None:
    """Una tabla vacía es distinto de una ausente, y se avisa distinto."""
    engine = _engine_tmp(tmp_path)
    features.head(0).to_sql("features_escuela", engine, index=False)

    with pytest.raises(ValueError, match="está vacía"):
        cargar_features_desde_gold(engine, esquema=None)


def test_falla_si_gold_no_cumple_el_contrato(features: pd.DataFrame, tmp_path) -> None:
    """Si la C1 publica la tabla sin una columna acordada, se detecta al leer."""
    engine = _engine_tmp(tmp_path)
    features.drop(columns=["d1_pobreza"]).to_sql("features_escuela", engine, index=False)

    with pytest.raises(ValueError, match="d1_pobreza"):
        cargar_features_desde_gold(engine, esquema=None)


# ------------------------------------- quoted_name de SQLAlchemy (BUG-041)


def test_las_columnas_leidas_de_gold_son_str_puro(features: pd.DataFrame, tmp_path) -> None:
    """BUG-041: SQLAlchemy entrega `quoted_name`, y sklearn sólo acepta `str` exacto.

    `quoted_name` es subclase de `str`, así que todo lo demás funciona y el defecto no se ve.
    Pero scikit-learn comprueba `type(x) is str` para reconocer nombres de features: con
    `quoted_name` **no puebla `feature_names_in_`**, sin error ni aviso.
    """
    engine = _engine_tmp(tmp_path)
    features.to_sql("features_escuela", engine, index=False)

    leidas = cargar_features_desde_gold(engine, esquema=None)

    assert all(type(c) is str for c in leidas.columns), (
        f"columnas que no son str puro: "
        f"{[(c, type(c).__name__) for c in leidas.columns if type(c) is not str]}"
    )


def test_entrenar_desde_gold_puebla_feature_names_in(features: pd.DataFrame, tmp_path) -> None:
    """El síntoma real de BUG-041, con el driver vacío que lo dispara.

    Sin normalizar los nombres, `feature_names_in_` queda sin poblar y
    `getattr(modelo, "feature_names_in_", DRIVERS)` cae al fallback de los 6 drivers,
    reintroduciendo el que se descartó por estar 100 % `SIN_DATO`. La predicción entonces truena
    con `X has 6 features, but ... expecting 5`.

    Es el eslabón que anulaba el fix de BUG-015/018/023 justo en el path de producción.
    """
    sin_agua = features.copy()
    sin_agua["d5_agua"] = float("nan")  # el caso real: DS-06 sin descarga verificada
    engine = _engine_tmp(tmp_path)
    sin_agua.to_sql("features_escuela", engine, index=False)

    resultado = entrenar_y_evaluar(cargar_features_desde_gold(engine, esquema=None), n_ventanas=1)

    assert "d5_agua" in resultado.drivers_excluidos
    nombres = getattr(resultado.modelo, "feature_names_in_", None)
    assert nombres is not None, "feature_names_in_ sin poblar: el fallback DRIVERS se dispararía"
    # Lo que importa no es que el atributo exista, sino que NO reintroduzca el driver descartado.
    assert list(nombres) == list(resultado.drivers_usados)
    assert "d5_agua" not in nombres


def test_predecir_desde_gold_no_cae_al_fallback_de_los_6_drivers(
    features: pd.DataFrame, tmp_path
) -> None:
    """La reproducción end-to-end: leer de la BD, entrenar y predecir sin `ValueError`."""
    from src.modelos.publicar_gold import construir_predicciones

    sin_agua = features.copy()
    sin_agua["d5_agua"] = float("nan")
    engine = _engine_tmp(tmp_path)
    sin_agua.to_sql("features_escuela", engine, index=False)

    leidas = cargar_features_desde_gold(engine, esquema=None)
    resultado = entrenar_y_evaluar(leidas, n_ventanas=1)

    # Antes del fix esto reventaba con "X has 6 features, but ... expecting 5".
    predicciones = construir_predicciones(leidas, resultado.modelo, "run-bug041")

    assert not predicciones.empty


# ------------------------------- driver sin ningún dato (caso real de gold.features_escuela)


def test_un_driver_sin_ningun_dato_no_rompe_el_entrenamiento(features: pd.DataFrame) -> None:
    """Reproduce el fallo del Gold real: D5 (agua) está 100% en SIN_DATO porque DS-06 no llega.

    Sin este manejo, `HistGradientBoostingRegressor` falla dentro del binning con
    `window shape cannot be larger than input array shape`, un error que no dice nada de la causa.
    """
    sin_agua = features.copy()
    sin_agua["d5_agua"] = np.nan
    sin_agua["d5_cobertura"] = "SIN_DATO"

    resultado = entrenar_y_evaluar(sin_agua, n_ventanas=2)

    assert "d5_agua" in resultado.drivers_excluidos
    assert "d5_agua" not in resultado.drivers_usados
    assert len(resultado.drivers_usados) == 5
    assert all(np.isfinite(v.mae) for v in resultado.ventanas)


def test_la_exclusion_de_drivers_queda_registrada(features: pd.DataFrame) -> None:
    """Excluir un driver nunca es silencioso: es un hallazgo del proyecto, no un detalle."""
    resultado = entrenar_y_evaluar(features, n_ventanas=2)
    assert resultado.drivers_excluidos == ()
    assert len(resultado.drivers_usados) == 6


def test_una_columna_constante_si_es_utilizable(features: pd.DataFrame) -> None:
    """Sin varianza no es lo mismo que sin datos: el modelo puede ignorarla por su cuenta."""
    constante = features.copy()
    constante["d6_aire"] = 0.5

    resultado = entrenar_y_evaluar(constante, n_ventanas=2)

    assert "d6_aire" in resultado.drivers_usados


def test_falla_con_mensaje_claro_si_ningun_driver_tiene_datos(features: pd.DataFrame) -> None:
    vacio = features.copy()
    for driver in DRIVERS:
        vacio[driver] = np.nan

    with pytest.raises(ValueError, match="Ningún driver tiene datos"):
        entrenar_y_evaluar(vacio, n_ventanas=2)


def test_se_puede_publicar_aunque_falte_un_driver(features: pd.DataFrame) -> None:
    """El circuito completo con un driver ausente: entrenar y construir las filas de Gold."""
    from src.modelos.publicar_gold import construir_predicciones

    sin_agua = features.copy()
    sin_agua["d5_agua"] = np.nan

    resultado = entrenar_y_evaluar(sin_agua, n_ventanas=2)
    filas = construir_predicciones(sin_agua, resultado.modelo, "run-sin-d5")

    assert len(filas) == sin_agua["cct"].nunique()
    assert filas["indice_riesgo"].between(0, 1).all()


def test_un_driver_vacio_solo_dentro_de_la_ventana_no_rompe(features: pd.DataFrame) -> None:
    """El caso que sobrevivió al primer arreglo: cobertura global sí, cobertura por ventana no.

    D6 (aire) llega por la interpolación IDW de US-105 y sólo cubre el ciclo más reciente. Mirado
    sobre el conjunto completo el driver "tiene datos", pero el tramo con el que se entrena está
    entero en `NaN` — y sklearn falla al binear con el mismo error que no dice por qué.
    """
    tres = features[features["id_ciclo"].isin(["2021-2022", "2022-2023", "2023-2024"])].copy()
    tres.loc[tres["id_ciclo"] != "2023-2024", "d6_aire"] = np.nan

    assert tres["d6_aire"].notna().any(), "globalmente el driver sí tiene datos"

    resultado = entrenar_y_evaluar(tres, n_ventanas=1)

    assert "d6_aire" in resultado.drivers_excluidos
    assert all(np.isfinite(v.mae) for v in resultado.ventanas)


def test_falla_si_la_ventana_de_entrenamiento_queda_sin_drivers(features: pd.DataFrame) -> None:
    """El mensaje debe nombrar la ventana, no sólo decir que faltan datos."""
    tres = features[features["id_ciclo"].isin(["2021-2022", "2022-2023", "2023-2024"])].copy()
    for driver in DRIVERS:
        tres.loc[tres["id_ciclo"] != "2023-2024", driver] = np.nan

    with pytest.raises(ValueError, match="ventana de entrenamiento"):
        entrenar_y_evaluar(tres, n_ventanas=1)


def test_reporta_que_driver_quedo_fuera_en_cada_ventana(features: pd.DataFrame) -> None:
    """La cobertura varía entre ventanas; el resultado tiene que dejar ver cuál y dónde."""
    tres = features[features["id_ciclo"].isin(["2021-2022", "2022-2023", "2023-2024"])].copy()
    tres.loc[tres["id_ciclo"] != "2023-2024", "d6_aire"] = np.nan

    resultado = entrenar_y_evaluar(tres, n_ventanas=1)

    assert len(resultado.excluidos_por_ventana) == 1
    ventana, fuera = next(iter(resultado.excluidos_por_ventana.items()))
    assert "2021-2022" in ventana, "la llave nombra la ventana, para poder ubicarla"
    assert "d6_aire" in fuera


# ------------------------------------------------- registro de drivers en MLflow


class _CorridaFalsa:
    """Contexto de `mlflow.start_run` que sólo necesita existir."""

    info = SimpleNamespace(run_id="run-falso")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class _MlflowFalso:
    """Doble de `mlflow` que apunta lo registrado.

    Se inyecta en `sys.modules` en vez de depender del paquete real: el CI instala sólo
    `requirements.txt`, donde `mlflow` no está, así que una prueba que lo importara se **omitiría**
    en silencio — y una prueba omitida no es una prueba verde.
    """

    def __init__(self) -> None:
        self.params: dict[str, object] = {}
        self.tags: dict[str, object] = {}
        self.params_hijas: list[dict[str, object]] = []
        self._en_hija = False

    #: `registrar_en_mlflow` guarda el artefacto del modelo; el doble sólo necesita devolver algo
    #: con `model_uri`, porque lo que se prueba aquí es qué parámetros se registran.
    sklearn = SimpleNamespace(
        log_model=lambda modelo, name=None: SimpleNamespace(model_uri="modelo://falso")
    )

    def set_tracking_uri(self, uri): ...
    def set_experiment(self, nombre): ...
    def log_metrics(self, metricas): ...
    def log_metric(self, clave, valor): ...

    def start_run(self, run_name=None, nested=False):
        self._en_hija = nested
        if nested:
            self.params_hijas.append({})
        return _CorridaFalsa()

    def log_param(self, clave, valor):
        destino = self.params_hijas[-1] if self._en_hija else self.params
        destino[clave] = valor

    def log_params(self, params):
        for k, v in params.items():
            self.log_param(k, v)

    def set_tag(self, clave, valor):
        self.tags[clave] = valor

    def register_model(self, uri, nombre): ...


@pytest.fixture
def mlflow_falso(monkeypatch):
    doble = _MlflowFalso()
    monkeypatch.setitem(sys.modules, "mlflow", doble)
    monkeypatch.setattr(
        "src.modelos.mlflow_utils.verificar_compatibilidad", lambda *a, **k: None
    )
    return doble


def test_registra_los_drivers_usados_y_excluidos(features: pd.DataFrame, mlflow_falso) -> None:
    """Que un driver quede fuera es un hallazgo del proyecto: tiene que sobrevivir a la corrida."""
    sin_agua = features.copy()
    sin_agua["d5_agua"] = np.nan
    resultado = entrenar_y_evaluar(sin_agua, n_ventanas=2)

    registrar_en_mlflow(resultado, tracking_uri="sqlite:///no-se-usa.db")

    assert mlflow_falso.params["drivers_excluidos"] == ["d5_agua"]
    assert "d5_agua" not in mlflow_falso.params["drivers_usados"]
    assert mlflow_falso.params["n_drivers_usados"] == len(DRIVERS) - 1
    assert mlflow_falso.tags["cobertura_drivers"] == f"{len(DRIVERS) - 1} de {len(DRIVERS)}"


def test_cada_ventana_registra_sus_propios_drivers_sin_datos(
    features: pd.DataFrame, mlflow_falso
) -> None:
    """La exclusión es por ventana: el agregado del padre no sustituye el detalle de cada tramo."""
    solo_reciente = features.copy()
    ciclo = solo_reciente["id_ciclo"].max()
    solo_reciente.loc[solo_reciente["id_ciclo"] != ciclo, "d6_aire"] = np.nan
    resultado = entrenar_y_evaluar(solo_reciente, n_ventanas=2)

    registrar_en_mlflow(resultado, tracking_uri="sqlite:///no-se-usa.db")

    assert len(mlflow_falso.params_hijas) == len(resultado.ventanas)
    assert any("d6_aire" in h["drivers_sin_datos"] for h in mlflow_falso.params_hijas)


def test_sin_exclusiones_lo_registra_vacio_y_no_lo_omite(
    features: pd.DataFrame, mlflow_falso
) -> None:
    """Un parámetro ausente no se distingue de uno no medido; la lista vacía sí afirma algo."""
    resultado = entrenar_y_evaluar(features, n_ventanas=2)

    registrar_en_mlflow(resultado, tracking_uri="sqlite:///no-se-usa.db")

    assert mlflow_falso.params["drivers_excluidos"] == []
    assert mlflow_falso.tags["cobertura_drivers"] == f"{len(DRIVERS)} de {len(DRIVERS)}"
