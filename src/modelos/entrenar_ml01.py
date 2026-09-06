"""Entrenamiento y backtesting de ML-01 — regresión de variación de matrícula (US-311).

Cierra el entregable central de US-311: entrenar el modelo, evaluarlo con **backtesting temporal**
y registrarlo en MLflow con parámetros, métricas y artefacto (AC-003.2 y AC-003.4).

## Decisiones y por qué

**`HistGradientBoostingRegressor`.** Maneja `NaN` de forma nativa, así que un driver `SIN_DATO`
llega al modelo **como ausencia real y nunca se imputa a cero** (regla 4 de `vault/15_ML_Models/_index`).
El estimador aprende a qué lado del árbol mandar las ausencias, que es justo la señal que queremos
conservar: no tener dato de aire es información, no un cero.

**Baseline obligatorio.** Cada ventana se compara contra `DummyRegressor(strategy="mean")`. Una
métrica sin baseline no dice nada: un MAE de 0.015 puede ser excelente o ridículo según la escala.
Si el modelo no le gana a predecir la media, no hay modelo.

**Partición temporal verificada, no asumida.** Antes de cada `fit()` se llama a
`verificar_sin_fuga()`. Es barato y convierte la regla en garantía de ejecución.

**Métrica agregada = promedio ± desviación de las ventanas**, conforme a ADR-003 (Andrés).

**Pérdida absoluta.** Los targets reales contienen una cola pequeña de altas administrativas y
escuelas de matrícula previa muy baja. `absolute_error` evita que esos outliers dominen el ajuste;
la evaluación sigue reportando MAE/RMSE y se compara contra el mismo baseline temporal.

## Uso

    python -m src.modelos.entrenar_ml01                      # contra el fixture simulado
    python -m src.modelos.entrenar_ml01 --ventanas 3 --sin-mlflow
    python -m src.modelos.entrenar_ml01 --features ruta/al/gold_features.csv

## Nota sobre los datos

Por defecto entrena contra `tests/fixtures/features_escuela_mock.csv`, que es **sintético**. Las
métricas resultantes validan que el pipeline funciona, **no son resultados de negocio**. Cuando la
Célula 1 publique `gold.features_escuela` (US-104) sólo cambia `--features`.

ADR-003 fija 4 ventanas de backtesting; el fixture sólo tiene 5 ciclos, así que el default aquí es
3. Con los ciclos reales del Formato 911 se sube a 4 sin tocar código.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from src.modelos.contrato import DRIVERS, entidad_de_cct
from src.modelos.particion_temporal import (
    COLUMNA_CICLO,
    ParticionTemporal,
    generar_backtesting,
    verificar_sin_fuga,
)
from src.modelos.riesgo import indice_riesgo

#: Columna objetivo, según el contrato `FeaturesEscuela` (`Data_Model` §5.3).
COLUMNA_TARGET = "target_variacion_matricula"

#: Nombre canónico del modelo en el registry de MLflow (`ML_Strategy` §7).
NOMBRE_MODELO = "ML01_RegresionMatricula"

#: Fixture simulado por defecto. Ver la nota de datos en el docstring del módulo.
FEATURES_POR_DEFECTO = Path("tests/fixtures/features_escuela_mock.csv")

#: Hiperparámetros. Modestos a propósito: afinarlos contra datos sintéticos no aporta nada.
HIPERPARAMETROS: dict[str, object] = {
    "loss": "absolute_error",
    "max_iter": 200,
    "learning_rate": 0.05,
    "max_depth": 4,
    "min_samples_leaf": 10,
    "random_state": 0,
}


@dataclass(frozen=True)
class MetricasVentana:
    """Resultado de una ventana de backtesting."""

    particion: ParticionTemporal
    mae: float
    rmse: float
    mae_baseline: float
    n_entrena: int
    n_prueba: int

    @property
    def mejora_sobre_baseline(self) -> float:
        """Fracción de MAE que el modelo reduce respecto a predecir la media.

        Positiva = el modelo aporta. Negativa = es peor que no tener modelo.
        """
        if self.mae_baseline == 0:
            return 0.0
        return (self.mae_baseline - self.mae) / self.mae_baseline


@dataclass(frozen=True)
class ResultadoEntrenamiento:
    """Resultado completo del backtesting más el modelo de producción.

    `drivers_usados` y `drivers_excluidos` describen el modelo que queda en `modelo` —el de la
    última ventana—, no todas las ventanas. La cobertura se evalúa por ventana y puede variar
    entre ellas: `excluidos_por_ventana` guarda ese detalle para poder diagnosticarlo.
    """

    ventanas: tuple[MetricasVentana, ...]
    modelo: HistGradientBoostingRegressor
    error_por_entidad: pd.DataFrame
    drivers_usados: tuple[str, ...] = DRIVERS
    drivers_excluidos: tuple[str, ...] = ()
    excluidos_por_ventana: dict[str, tuple[str, ...]] = field(default_factory=dict)

    @property
    def mae_promedio(self) -> float:
        return float(np.mean([v.mae for v in self.ventanas]))

    @property
    def mae_desviacion(self) -> float:
        return float(np.std([v.mae for v in self.ventanas]))

    @property
    def rmse_promedio(self) -> float:
        return float(np.mean([v.rmse for v in self.ventanas]))

    @property
    def rmse_desviacion(self) -> float:
        return float(np.std([v.rmse for v in self.ventanas]))

    @property
    def ventana_produccion(self) -> MetricasVentana:
        """La ventana más reciente: entrena con todo el pasado y evalúa el último ciclo."""
        return self.ventanas[-1]


def cargar_features(ruta: Path = FEATURES_POR_DEFECTO) -> pd.DataFrame:
    """Lee la tabla de features desde CSV o Parquet.

    Raises:
        FileNotFoundError: si la ruta no existe.
        ValueError: si falta la columna objetivo o alguno de los 6 drivers.
    """
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe {ruta}. Genera el fixture con: python -m src.modelos.generar_fixture"
        )
    # `cve_mun` es puramente numérica ("09001"): sin dtype explícito pandas la infiere int64 y se
    # come el cero de la izquierda, con lo que "09001" llega como 9001 y el join contra
    # `dim_municipio` -- y la agregación de DEC-007 -- fallan en silencio para las 9 entidades
    # cuya clave INEGI empieza en cero, CDMX incluida.
    df = (
        pd.read_parquet(ruta)
        if ruta.suffix == ".parquet"
        else pd.read_csv(ruta, dtype={"cve_mun": str})
    )
    return _validar_contrato(df, "La tabla de features")


def _validar_contrato(df: pd.DataFrame, origen: str) -> pd.DataFrame:
    """Comprueba que la tabla traiga las columnas del contrato `FeaturesEscuela` (§5.3)."""
    faltantes = ({COLUMNA_TARGET, COLUMNA_CICLO, "cct"} | set(DRIVERS)) - set(df.columns)
    if faltantes:
        raise ValueError(
            f"{origen} no cumple el contrato de `gold.features_escuela`; faltan: {sorted(faltantes)}"
        )
    return df


def cargar_features_desde_gold(
    engine,
    esquema: str = "gold",
    tabla: str = "features_escuela",
) -> pd.DataFrame:
    """Lee `gold.features_escuela` directamente de la base, en vez del fixture (cierra BUG-013).

    `publicar_gold` nació apuntando al fixture sintético porque la Célula 1 aún no materializaba
    Gold. Con la tabla real disponible, seguir leyendo el fixture publica predicciones de un ciclo
    que el hecho real no tiene: el `JOIN` por `(cct, id_ciclo)` da cero y DB-03 muestra
    `SIN_DATO` en el 100 % de las escuelas.

    Args:
        engine: motor SQLAlchemy apuntando al Postgres donde vive Gold.
        esquema: esquema de la tabla.
        tabla: nombre de la tabla de features.

    Returns:
        DataFrame con el contrato `FeaturesEscuela`.

    Raises:
        ValueError: si la tabla no existe, está vacía o no cumple el contrato.
    """
    from sqlalchemy import inspect as _inspect

    if not _inspect(engine).has_table(tabla, schema=esquema):
        raise ValueError(
            f"No existe `{esquema}.{tabla}` en la base. Materialízala con `dbt run` antes de "
            "publicar (US-104, Célula 1)."
        )

    df = pd.read_sql_table(tabla, engine, schema=esquema)

    # SQLAlchemy devuelve los nombres de columna como `quoted_name`, subclase de `str` pero NO
    # `str` puro. scikit-learn exige `type(x) is str` exacto para reconocer nombres de features,
    # así que con las columnas tal cual **nunca puebla `feature_names_in_`** — sin error, sin aviso.
    # Aguas abajo, `getattr(modelo, "feature_names_in_", DRIVERS)` cae entonces al fallback de los
    # 6 DRIVERS y **reintroduce el driver que se descartó por estar 100 % `SIN_DATO`**, con lo que
    # la predicción truena con `X has 6 features, but ... expecting 5`.
    #
    # Es el eslabón que anula el fix de BUG-015/018/023: aquellos enseñaron al lado de predicción a
    # confiar en `feature_names_in_`, y este tipo de columna deja ese atributo vacío. Sólo ocurre
    # leyendo de la BD; los fixtures CSV dan `str` puro, por eso la suite no lo veía (BUG-041).
    df.columns = [str(c) for c in df.columns]

    if df.empty:
        raise ValueError(f"`{esquema}.{tabla}` existe pero está vacía; no hay nada que publicar.")
    return _validar_contrato(df, f"`{esquema}.{tabla}`")


def _matriz(df: pd.DataFrame, columnas: list[str] | None = None) -> pd.DataFrame:
    """Extrae los drivers utilizables. Los `SIN_DATO` quedan como `NaN`, sin imputar."""
    return df[list(columnas if columnas is not None else DRIVERS)]


def drivers_utilizables(df: pd.DataFrame) -> list[str]:
    """Drivers con al menos un valor observado en este conjunto.

    Un driver **100 % `SIN_DATO`** —cero valores en todo el conjunto— rompe el binning de
    `HistGradientBoostingRegressor`: al no haber ningún valor distinto, sklearn falla con
    `window shape cannot be larger than input array shape`, un error que no dice nada sobre la
    causa real.

    Ese caso no es hipotético: en `gold.features_escuela` real, **D5 (agua) está completo en
    `SIN_DATO`** porque DS-06 (CONAGUA) sigue sin descarga verificada. Un driver así no aporta
    información y **se excluye**, pero **nunca en silencio**: la exclusión se reporta, porque
    "este driver no aportó nada" es un hallazgo del proyecto, no un detalle de implementación.

    Una columna **constante** sí es utilizable: sklearn la maneja, y su ausencia de varianza es
    información legítima que el modelo puede ignorar por su cuenta.
    """
    return [d for d in DRIVERS if df[d].notna().any()]


def _entidades_de(df: pd.DataFrame) -> list[str]:
    """Deriva la clave de entidad, sea el grano escuela o `municipio × nivel`.

    `features_escuela` no trae `cve_ent`, así que la entidad se deduce de la llave disponible: los
    dos primeros caracteres del `cct` a nivel escuela, o los de `cve_mun` en el grano agregado de
    DEC-007. Ambas claves INEGI empiezan con la entidad, así que el desglose de US-312 funciona en
    los dos granos sin pedir columnas nuevas.

    Raises:
        ValueError: si el DataFrame no trae ninguna de las dos llaves.
    """
    if "cct" in df.columns:
        return [entidad_de_cct(c) for c in df["cct"]]
    if "cve_mun" in df.columns:
        return [str(m)[:2] for m in df["cve_mun"]]
    raise ValueError(
        "No hay de dónde derivar la entidad: se esperaba `cct` (grano escuela) o `cve_mun` "
        "(grano municipio_nivel, DEC-007)."
    )


def _error_por_entidad(df_prueba: pd.DataFrame, predicho: np.ndarray) -> pd.DataFrame:
    """Desglosa el error por entidad federativa (insumo de US-312).

    Funciona en los dos granos: la entidad se deriva de `cct` o de `cve_mun`, según cuál esté.
    """
    detalle = pd.DataFrame(
        {
            "entidad": _entidades_de(df_prueba),
            "real": df_prueba[COLUMNA_TARGET].to_numpy(),
            "predicho": predicho,
        }
    )
    detalle["error_absoluto"] = (detalle["real"] - detalle["predicho"]).abs()
    return (
        detalle.groupby("entidad")
        .agg(escuelas=("error_absoluto", "size"), mae=("error_absoluto", "mean"))
        .reset_index()
        .sort_values("mae", ascending=False, ignore_index=True)
    )


def entrenar_y_evaluar(
    df: pd.DataFrame,
    n_ventanas: int = 3,
    hiperparametros: dict[str, object] | None = None,
) -> ResultadoEntrenamiento:
    """Ejecuta el backtesting walk-forward y devuelve métricas y modelo de producción.

    Función **pura respecto a MLflow**: no registra nada. Eso la hace barata de probar y permite
    reutilizarla desde US-312 (evaluación) y US-313 (job batch) sin arrastrar el tracking.

    Args:
        df: tabla de features conforme al contrato `FeaturesEscuela`.
        n_ventanas: ventanas de backtesting, de la más antigua a la más reciente.
        hiperparametros: sobrescribe `HIPERPARAMETROS`.

    Returns:
        `ResultadoEntrenamiento` con una entrada por ventana, el modelo entrenado en la ventana
        de producción y el desglose de error por entidad.
    """
    params = {**HIPERPARAMETROS, **(hiperparametros or {})}

    sin_datos_global = [d for d in DRIVERS if d not in drivers_utilizables(df)]
    if sin_datos_global:
        print(
            f"⚠️  Drivers sin ningún dato en todo el conjunto: {sin_datos_global}. "
            "Quedan fuera del modelo."
        )

    ventanas: list[MetricasVentana] = []
    usables: list[str] = []
    excluidos_por_ventana: dict[str, tuple[str, ...]] = {}
    modelo: HistGradientBoostingRegressor | None = None
    error_entidad = pd.DataFrame()

    for particion in generar_backtesting(df, n_ventanas=n_ventanas):
        entrena, prueba = particion.aplicar(df)
        verificar_sin_fuga(entrena, prueba)  # garantía ejecutable de AC-003.3

        # La cobertura se evalúa DENTRO de la ventana, no sobre el conjunto completo: un driver
        # puede tener datos sólo en el ciclo más reciente —como D6 tras la interpolación IDW de
        # US-105— y quedar totalmente vacío en el tramo con el que se entrena. Comprobarlo global
        # no lo detecta, y sklearn falla al binear con un error que no dice por qué.
        usables = drivers_utilizables(entrena)
        if not usables:
            raise ValueError(
                f"Ningún driver tiene datos en la ventana de entrenamiento {particion}. "
                "No hay con qué entrenar; revisa la cobertura por ciclo de `gold.features_escuela`."
            )
        fuera = [d for d in DRIVERS if d not in usables]
        if fuera:
            excluidos_por_ventana[str(particion)] = tuple(fuera)
            print(
                f"⚠️  {particion}: sin datos en el entrenamiento {fuera}; "
                f"se entrena con {len(usables)} de {len(DRIVERS)} drivers."
            )

        x_entrena, y_entrena = _matriz(entrena, usables), entrena[COLUMNA_TARGET]
        x_prueba, y_prueba = _matriz(prueba, usables), prueba[COLUMNA_TARGET]

        modelo = HistGradientBoostingRegressor(**params).fit(x_entrena, y_entrena)
        predicho = modelo.predict(x_prueba)
        baseline = DummyRegressor(strategy="mean").fit(x_entrena, y_entrena).predict(x_prueba)

        ventanas.append(
            MetricasVentana(
                particion=particion,
                mae=float(mean_absolute_error(y_prueba, predicho)),
                rmse=float(root_mean_squared_error(y_prueba, predicho)),
                mae_baseline=float(mean_absolute_error(y_prueba, baseline)),
                n_entrena=len(entrena),
                n_prueba=len(prueba),
            )
        )
        error_entidad = _error_por_entidad(prueba, predicho)  # se queda el de la última ventana

    if modelo is None:  # pragma: no cover - generar_backtesting ya valida esto
        raise RuntimeError("El backtesting no produjo ninguna ventana.")

    return ResultadoEntrenamiento(
        ventanas=tuple(ventanas),
        modelo=modelo,
        error_por_entidad=error_entidad,
        drivers_usados=tuple(usables),
        drivers_excluidos=tuple(d for d in DRIVERS if d not in usables),
        excluidos_por_ventana=excluidos_por_ventana,
    )


def registrar_en_mlflow(
    resultado: ResultadoEntrenamiento,
    tracking_uri: str,
    experimento: str = "ML-01-regresion-matricula",
    registrar_modelo: bool = False,
) -> str:
    """Registra el backtesting en MLflow: una corrida padre y una hija por ventana.

    MLflow 3.x **deprecó el file store** (`file:./mlruns`), así que el URI debe apuntar a una base
    de datos. En local, `sqlite:///mlflow.db`.

    Args:
        resultado: salida de `entrenar_y_evaluar`.
        tracking_uri: URI de tracking de MLflow.
        experimento: nombre del experimento.
        registrar_modelo: si además se publica en el Model Registry como `ML01_RegresionMatricula`.

    Returns:
        El `run_id` de la corrida padre, que es el que va a `gold.predicciones.mlflow_run_id`.
    """
    import mlflow  # import diferido: entrenar no debe requerir MLflow instalado

    from src.modelos.mlflow_utils import verificar_compatibilidad

    # Falla temprano si el servidor es de otra versión mayor: si no, las métricas se registran
    # pero el modelo se pierde con un 404 poco evidente.
    verificar_compatibilidad(tracking_uri)

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experimento)

    with mlflow.start_run(run_name="backtesting-walk-forward") as padre:
        mlflow.log_params({f"modelo__{k}": v for k, v in HIPERPARAMETROS.items()})
        mlflow.log_param("n_ventanas", len(resultado.ventanas))
        mlflow.log_param("particion", "temporal walk-forward (nunca aleatoria)")
        # Un driver excluido es una fuente que no está llegando, no un ajuste técnico: queda como
        # parámetro de la corrida para poder responder "¿con qué datos se entrenó esto?" meses
        # después, cuando el print de la consola ya no exista.
        mlflow.log_param("drivers_usados", list(resultado.drivers_usados))
        mlflow.log_param("drivers_excluidos", list(resultado.drivers_excluidos))
        mlflow.log_param("n_drivers_usados", len(resultado.drivers_usados))
        mlflow.set_tag(
            "cobertura_drivers",
            f"{len(resultado.drivers_usados)} de {len(DRIVERS)}",
        )
        mlflow.log_metrics(
            {
                "mae_promedio": resultado.mae_promedio,
                "mae_desviacion": resultado.mae_desviacion,
                "rmse_promedio": resultado.rmse_promedio,
                "rmse_desviacion": resultado.rmse_desviacion,
                "mae_produccion": resultado.ventana_produccion.mae,
                "mejora_sobre_baseline": resultado.ventana_produccion.mejora_sobre_baseline,
            }
        )

        for i, ventana in enumerate(resultado.ventanas, start=1):
            with mlflow.start_run(run_name=f"ventana-{i}", nested=True):
                mlflow.log_param("ciclos_entrenamiento", list(ventana.particion.ciclos_entrenamiento))
                mlflow.log_param(
                    "drivers_sin_datos",
                    list(resultado.excluidos_por_ventana.get(str(ventana.particion), ())),
                )
                mlflow.log_param("ciclos_prueba", list(ventana.particion.ciclos_prueba))
                mlflow.log_metrics(
                    {
                        "mae": ventana.mae,
                        "rmse": ventana.rmse,
                        "mae_baseline": ventana.mae_baseline,
                        "mejora_sobre_baseline": ventana.mejora_sobre_baseline,
                        "n_entrena": ventana.n_entrena,
                        "n_prueba": ventana.n_prueba,
                    }
                )

        info = mlflow.sklearn.log_model(resultado.modelo, name="modelo")
        if registrar_modelo:
            mlflow.register_model(info.model_uri, NOMBRE_MODELO)
        return padre.info.run_id


def _imprimir_reporte(resultado: ResultadoEntrenamiento) -> None:
    """Reporte legible en consola: es la evidencia que va al PR y al DevLog."""
    print(f"\n{'ventana':52} {'MAE':>8} {'RMSE':>8} {'baseline':>9} {'mejora':>8}")
    print("-" * 90)
    for ventana in resultado.ventanas:
        print(
            f"{ventana.particion!s:52} {ventana.mae:8.4f} {ventana.rmse:8.4f} "
            f"{ventana.mae_baseline:9.4f} {ventana.mejora_sobre_baseline:7.1%}"
        )
    print("-" * 90)
    print(
        f"MAE  {resultado.mae_promedio:.4f} ± {resultado.mae_desviacion:.4f}    "
        f"RMSE {resultado.rmse_promedio:.4f} ± {resultado.rmse_desviacion:.4f}"
        "   (promedio ± desviación de las ventanas, ADR-003)"
    )

    produccion = resultado.ventana_produccion
    print(f"\nVentana de producción: {produccion.particion}")
    print(f"  MAE {produccion.mae:.4f} · mejora sobre baseline {produccion.mejora_sobre_baseline:.1%}")

    print("\nError por entidad (ventana de producción):")
    print(resultado.error_por_entidad.to_string(index=False))

    # El índice de riesgo es capa de presentación: no cambia el modelo ni la métrica.
    ejemplos = np.array([-0.10, -0.05, 0.0, 0.05])
    riesgos = indice_riesgo(ejemplos)
    print("\nTraducción a indice_riesgo (DOC-INDICE-RIESGO):")
    for variacion, riesgo in zip(ejemplos, riesgos, strict=True):
        print(f"  variación {variacion:+.2f} → riesgo {riesgo:.3f}")


def main() -> int:
    """Punto de entrada: entrena, evalúa, reporta y registra en MLflow."""
    parser = argparse.ArgumentParser(description="Entrena y evalúa ML-01 (US-311).")
    parser.add_argument("--features", type=Path, default=FEATURES_POR_DEFECTO)
    parser.add_argument("--ventanas", type=int, default=3, help="ventanas de backtesting")
    parser.add_argument(
        "--tracking-uri",
        default=os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"),
        help="URI de MLflow; el file store está deprecado desde MLflow 3.x",
    )
    parser.add_argument("--sin-mlflow", action="store_true", help="sólo entrena y reporta")
    parser.add_argument(
        "--registrar-modelo", action="store_true", help=f"publica en el registry como {NOMBRE_MODELO}"
    )
    args = parser.parse_args()

    df = cargar_features(args.features)
    print(f"Features: {args.features} — {len(df)} filas, {df['cct'].nunique()} escuelas")

    resultado = entrenar_y_evaluar(df, n_ventanas=args.ventanas)
    _imprimir_reporte(resultado)

    if not args.sin_mlflow:
        run_id = registrar_en_mlflow(
            resultado, tracking_uri=args.tracking_uri, registrar_modelo=args.registrar_modelo
        )
        print(f"\nMLflow run_id: {run_id}  (va a gold.predicciones.mlflow_run_id)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
