"""Publicación de predicciones y recomendaciones a Gold (US-313).

Job batch que escribe `gold.predicciones` y `gold.recomendaciones`, las dos tablas que alimentan
**DB-06 (Predicciones)** y **DB-09 (Recomendaciones prescriptivas)** de Superset y los endpoints de
inferencia de la Célula 4.

## Contrato

Definido en `vault/03_Architecture/Data_Model.md` §4.5, tras **DEC-005/006**:

- `gold.predicciones` — `cct`, `id_ciclo`, `modelo`, `valor` (variación cruda, la que conserva la
  unidad para MAE/RMSE), `indice_riesgo` (derivado, ver `src/modelos/riesgo.py`), `probabilidad`,
  `mlflow_run_id`, `generado_at`.
- `gold.recomendaciones` — `cct`, `id_ciclo`, `driver_dominante`, `recomendacion`, `prioridad`.

## Idempotencia

El job se puede correr N veces con el mismo resultado: escribe con **UPSERT** sobre la llave
natural (`cct`, `id_ciclo`, `modelo`) y (`cct`, `id_ciclo`). No borra particiones ni trunca tablas;
volver a correrlo tras reentrenar simplemente actualiza los valores y el `mlflow_run_id`.

## Alcance hoy

ML-01 puebla `gold.predicciones` y ML-02 produce el driver dominante que alimenta
`gold.recomendaciones`. Ambos modelos usan el mismo corte por `cct` e `id_ciclo`; la publicación
falla si las features de alguna predicción no están disponibles para ML-02.
"""

from __future__ import annotations

import argparse
import math
import os
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

import pandas as pd
from pydantic import (
    BaseModel,
    Field,
    StrictFloat,
    StrictStr,
    field_validator,
    model_validator,
)
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Index,
    MetaData,
    String,
    Table,
    create_engine,
    text,
)
from sqlalchemy.engine import Engine

from src.modelos.contrato import DRIVERS
from src.modelos.entrenar_ml01 import (
    cargar_features,
    cargar_features_desde_gold,
    entrenar_y_evaluar,
)
from src.modelos.entrenar_ml02 import (
    COLUMNA_TARGET_PROXY,
    COLUMNA_TARGET_REAL,
    explicar_driver,
    generar_driver_dominante_proxy,
    predecir_driver,
)
from src.modelos.entrenar_ml02 import entrenar_y_evaluar as entrenar_ml02
from src.modelos.particion_temporal import (
    COLUMNA_CICLO,
    ciclos_ordenados,
    ventanas_posibles,
)
from src.modelos.recomendaciones import CODIGOS_DRIVER, RECOMENDACION_POR_DRIVER
from src.modelos.riesgo import (
    RIESGO_ESTABLE,
    RIESGO_UMBRAL,
    indice_riesgo,
    verificar_escala_variacion,
)

ESQUEMA_GOLD = "gold"
TABLA_PREDICCIONES = "predicciones"
TABLA_RECOMENDACIONES = "recomendaciones"
COLUMNAS_SHAP = tuple(f"shap_d{i}" for i in range(1, 7))

class Prioridad(str, Enum):
    """Urgencia de la intervención, derivada del `indice_riesgo`."""

    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class Grano(str, Enum):
    """Discriminador de grano de `gold.predicciones` (DEC-010).

    ML-01 puede predecir a `municipio × nivel` (DEC-007) mientras las features y el driver dominante
    viven a nivel escuela. En vez de **repartir** el valor del grupo a cada escuela —lo que le
    atribuiría a una escuela un dato que no se midió ahí—, la fila declara su propio grano.
    """

    ESCUELA = "escuela"
    MUNICIPIO_NIVEL = "municipio_nivel"


class PrediccionGold(BaseModel):
    """Contrato ejecutable de una fila de `gold.predicciones` (§4.5, grano dual DEC-010)."""

    model_config = {"extra": "forbid"}

    grano: Grano
    cct: StrictStr | None = Field(default=None, min_length=10, max_length=10)
    cve_mun: StrictStr | None = Field(default=None, min_length=5, max_length=5)
    nivel: StrictStr | None = None
    id_ciclo: StrictStr
    modelo: StrictStr
    valor: StrictFloat
    indice_riesgo: StrictFloat = Field(ge=0, le=1)
    probabilidad: StrictFloat | None
    mlflow_run_id: StrictStr
    generado_at: datetime

    @model_validator(mode="after")
    def _llave_coherente_con_el_grano(self) -> PrediccionGold:
        """Exactamente una llave poblada según el grano — nunca ambas, nunca ninguna.

        Es la restricción textual del `Data_Model` §4.5 convertida en validación ejecutable: una
        fila con las dos llaves no se sabe a qué se refiere, y una sin ninguna no se sabe de quién
        habla. Ambas son peores que un error.
        """
        if self.grano is Grano.ESCUELA:
            if self.cct is None:
                raise ValueError("grano 'escuela' exige `cct`.")
            if self.cve_mun is not None or self.nivel is not None:
                raise ValueError("grano 'escuela' no debe traer `cve_mun` ni `nivel`.")
        else:
            if self.cve_mun is None or self.nivel is None:
                raise ValueError("grano 'municipio_nivel' exige `cve_mun` y `nivel`.")
            if self.cct is not None:
                raise ValueError("grano 'municipio_nivel' no debe traer `cct`.")
        return self


class RecomendacionGold(BaseModel):
    """Contrato ejecutable de una fila de `gold.recomendaciones` (§4.5)."""

    model_config = {"extra": "forbid"}

    cct: StrictStr = Field(min_length=10, max_length=10)
    id_ciclo: StrictStr
    driver_dominante: StrictStr
    recomendacion: StrictStr
    prioridad: Prioridad
    shap_d1: StrictFloat | None = None
    shap_d2: StrictFloat | None = None
    shap_d3: StrictFloat | None = None
    shap_d4: StrictFloat | None = None
    shap_d5: StrictFloat | None = None
    shap_d6: StrictFloat | None = None

    @field_validator(*COLUMNAS_SHAP)
    @classmethod
    def _shap_finito_o_sin_dato(cls, valor: float | None) -> float | None:
        if valor is not None and not math.isfinite(valor):
            raise ValueError("una contribución SHAP debe ser finita o None")
        return valor


def prioridad_de_riesgo(riesgo: float) -> Prioridad:
    """Traduce el `indice_riesgo` a urgencia de intervención.

    **No inventa umbrales nuevos**: reutiliza las dos anclas ya ratificadas de
    `DOC-INDICE-RIESGO` — 0.60 es el umbral de "escuela en riesgo" que usan los tableros
    (confirmado por Manuel Serranía en el PR #27) y 0.30 corresponde a una escuela con matrícula
    estable.

    >>> prioridad_de_riesgo(0.85).value
    'alta'
    >>> prioridad_de_riesgo(0.45).value
    'media'
    >>> prioridad_de_riesgo(0.10).value
    'baja'
    """
    if riesgo >= RIESGO_UMBRAL:
        return Prioridad.ALTA
    if riesgo >= RIESGO_ESTABLE:
        return Prioridad.MEDIA
    return Prioridad.BAJA


def _metadatos(esquema: str | None = ESQUEMA_GOLD) -> tuple[MetaData, Table, Table]:
    """Define las dos tablas de Gold. `esquema=None` para motores sin esquemas (SQLite)."""
    metadata = MetaData(schema=esquema)
    # Grano dual (DEC-010): no hay llave primaria única posible, porque `cct` y `cve_mun`+`nivel`
    # se excluyen entre sí y una PK no admite nulos. Se usan **dos índices únicos parciales**, uno
    # por grano, más un CHECK que hace cumplir la exclusión en la propia base de datos.
    predicciones = Table(
        TABLA_PREDICCIONES,
        metadata,
        Column("grano", String, nullable=False),
        Column("cct", String(10), nullable=True),
        Column("cve_mun", String(5), nullable=True),
        Column("nivel", String, nullable=True),
        Column("id_ciclo", String, nullable=False),
        Column("modelo", String, nullable=False),
        Column("valor", Float, nullable=False),
        Column("indice_riesgo", Float, nullable=False),
        Column("probabilidad", Float, nullable=True),
        Column("mlflow_run_id", String, nullable=False),
        Column("generado_at", DateTime(timezone=True), nullable=False),
        CheckConstraint(
            "(grano = 'escuela' AND cct IS NOT NULL AND cve_mun IS NULL AND nivel IS NULL)"
            " OR (grano = 'municipio_nivel' AND cct IS NULL"
            " AND cve_mun IS NOT NULL AND nivel IS NOT NULL)",
            name="ck_predicciones_llave_segun_grano",
        ),
        Index(
            "ux_predicciones_escuela",
            "cct",
            "id_ciclo",
            "modelo",
            unique=True,
            sqlite_where=text("grano = 'escuela'"),
            postgresql_where=text("grano = 'escuela'"),
        ),
        Index(
            "ux_predicciones_municipio_nivel",
            "cve_mun",
            "nivel",
            "id_ciclo",
            "modelo",
            unique=True,
            sqlite_where=text("grano = 'municipio_nivel'"),
            postgresql_where=text("grano = 'municipio_nivel'"),
        ),
    )
    recomendaciones = Table(
        TABLA_RECOMENDACIONES,
        metadata,
        Column("cct", String(10), primary_key=True),
        Column("id_ciclo", String, primary_key=True),
        Column("driver_dominante", String, nullable=False),
        Column("recomendacion", String, nullable=False),
        Column("prioridad", String, nullable=False),
        Column("shap_d1", Float, nullable=True),
        Column("shap_d2", Float, nullable=True),
        Column("shap_d3", Float, nullable=True),
        Column("shap_d4", Float, nullable=True),
        Column("shap_d5", Float, nullable=True),
        Column("shap_d6", Float, nullable=True),
    )
    return metadata, predicciones, recomendaciones


def construir_predicciones(
    features: pd.DataFrame,
    modelo,
    mlflow_run_id: str,
    id_ciclo_objetivo: str | None = None,
    generado_at: datetime | None = None,
) -> pd.DataFrame:
    """Genera las filas de `gold.predicciones` para ML-01.

    Predice sobre el ciclo más reciente disponible (el que interesa al negocio: "¿qué escuelas van
    a perder matrícula el próximo ciclo?") y adjunta tanto la variación cruda como su traducción a
    `indice_riesgo`.

    Args:
        features: tabla conforme al contrato `FeaturesEscuela`.
        modelo: estimador ya entrenado (`ResultadoEntrenamiento.modelo`).
        mlflow_run_id: corrida que produjo el modelo; queda como trazabilidad de la predicción.
        id_ciclo_objetivo: ciclo a predecir. Por defecto, el más reciente.
        generado_at: marca de tiempo; por defecto, ahora en UTC.

    Returns:
        DataFrame con las columnas de `gold.predicciones`.

    Raises:
        ValueError: si el ciclo objetivo no existe en las features.
    """
    ciclos = ciclos_ordenados(features)
    objetivo = id_ciclo_objetivo or ciclos[-1]
    if objetivo not in ciclos:
        raise ValueError(f"El ciclo {objetivo!r} no está en las features. Disponibles: {ciclos}.")

    corte = features[features[COLUMNA_CICLO] == objetivo]
    # Las columnas de predicción deben ser las mismas con las que se entrenó: si un driver quedó
    # 100% SIN_DATO y se excluyó, pasarlo aquí haría fallar el predict por desajuste de forma.
    columnas = list(getattr(modelo, "feature_names_in_", DRIVERS))
    variacion = modelo.predict(corte[columnas])
    # Antes de traducir a indice_riesgo: si las unidades no son fracción la sigmoide no falla,
    # satura. Un tablero lleno de riesgo 1.00 es peor que una corrida que se detiene.
    verificar_escala_variacion(variacion, origen="variación predicha por ML-01")

    filas = pd.DataFrame(
        {
            "grano": Grano.ESCUELA.value,
            "cct": corte["cct"].to_numpy(),
            "cve_mun": None,
            "nivel": None,
            "id_ciclo": objetivo,
            "modelo": "ML-01",
            "valor": variacion.astype(float),
            "indice_riesgo": indice_riesgo(variacion).astype(float),
            # ML-01 es regresión: no produce probabilidad. NULL explícito, nunca 0.
            "probabilidad": None,
            "mlflow_run_id": mlflow_run_id,
            "generado_at": generado_at or datetime.now(tz=UTC),
        }
    )
    for fila in filas.to_dict(orient="records"):
        PrediccionGold(**fila)
    return filas


def construir_predicciones_municipio_nivel(
    agregado: pd.DataFrame,
    modelo,
    mlflow_run_id: str,
    id_ciclo_objetivo: str | None = None,
    generado_at: datetime | None = None,
) -> pd.DataFrame:
    """Genera filas de `gold.predicciones` con `grano = municipio_nivel` (DEC-010 + DEC-007).

    Cierra el circuito del target híbrido: `target_hibrido.agregar_a_municipio_nivel()` produce el
    agregado y esta función publica su predicción **declarando su grano**, en vez de repartir el
    valor a cada escuela del grupo.

    `indice_riesgo` se calcula igual, pero conviene leer la advertencia del `Data_Model` §4.5: hoy
    **sólo tiene sentido pleno a nivel escuela**, porque las anclas del índice se fijaron sobre la
    variación de una escuela concreta. A nivel municipio × nivel es una lectura agregada, no una
    alerta por plantel.

    Args:
        agregado: salida de `agregar_a_municipio_nivel`, con `cve_mun`, `nivel` e `id_ciclo`.
        modelo: estimador entrenado sobre el grano agregado.
        mlflow_run_id: corrida que lo produjo.
        id_ciclo_objetivo: ciclo a predecir; por defecto el más reciente.
        generado_at: marca de tiempo; por defecto ahora en UTC.

    Returns:
        DataFrame con las columnas de `gold.predicciones` para el grano agregado.

    Raises:
        ValueError: si faltan las llaves del grano o el ciclo objetivo no existe.
    """
    faltantes = {"cve_mun", "nivel", COLUMNA_CICLO} - set(agregado.columns)
    if faltantes:
        raise ValueError(f"El agregado no trae {sorted(faltantes)}; DEC-010 las exige como llave.")

    ciclos = ciclos_ordenados(agregado)
    objetivo = id_ciclo_objetivo or ciclos[-1]
    if objetivo not in ciclos:
        raise ValueError(f"El ciclo {objetivo!r} no está en el agregado. Disponibles: {ciclos}.")

    corte = agregado[agregado[COLUMNA_CICLO] == objetivo]
    columnas = list(getattr(modelo, "feature_names_in_", DRIVERS))
    variacion = modelo.predict(corte[columnas])
    # Antes de traducir a indice_riesgo: si las unidades no son fracción la sigmoide no falla,
    # satura. Un tablero lleno de riesgo 1.00 es peor que una corrida que se detiene.
    verificar_escala_variacion(variacion, origen="variación predicha por ML-01")

    filas = pd.DataFrame(
        {
            "grano": Grano.MUNICIPIO_NIVEL.value,
            "cct": None,
            "cve_mun": corte["cve_mun"].to_numpy(),
            "nivel": corte["nivel"].to_numpy(),
            "id_ciclo": objetivo,
            "modelo": "ML-01",
            "valor": variacion.astype(float),
            "indice_riesgo": indice_riesgo(variacion).astype(float),
            "probabilidad": None,
            "mlflow_run_id": mlflow_run_id,
            "generado_at": generado_at or datetime.now(tz=UTC),
        }
    )
    for fila in filas.to_dict(orient="records"):
        PrediccionGold(**fila)
    return filas


def construir_recomendaciones(
    predicciones: pd.DataFrame,
    driver_por_escuela: dict[str, str],
    contribuciones_por_escuela: dict[str, dict[str, float | None]] | None = None,
) -> pd.DataFrame:
    """Genera las filas de `gold.recomendaciones` a partir del driver dominante.

    El driver **se recibe, no se calcula**: es salida de ML-02 (US-302, Andrés). Desde el PR #58
    `construir_recomendaciones_ml02()` conecta esa salida aquí; esta función se mantiene genérica
    para poder publicar recomendaciones desde cualquier origen de driver, incluido un diagnóstico
    manual.

    Args:
        predicciones: salida de `construir_predicciones` (aporta `cct`, `id_ciclo`, riesgo).
        driver_por_escuela: CCT → código de driver (`D1`…`D6`).

    Returns:
        DataFrame con las columnas de `gold.recomendaciones`, sólo para los CCT con driver conocido.

    Raises:
        ValueError: si algún driver no está en el catálogo.
    """
    desconocidos = set(driver_por_escuela.values()) - set(CODIGOS_DRIVER)
    if desconocidos:
        raise ValueError(
            f"Drivers fuera del catálogo: {sorted(desconocidos)}. Esperados: {CODIGOS_DRIVER}."
        )

    con_driver = predicciones[predicciones["cct"].isin(driver_por_escuela)].copy()
    drivers = con_driver["cct"].map(driver_por_escuela)
    contribuciones_por_escuela = contribuciones_por_escuela or {}

    filas = pd.DataFrame(
        {
            "cct": con_driver["cct"].to_numpy(),
            "id_ciclo": con_driver["id_ciclo"].to_numpy(),
            "driver_dominante": drivers.to_numpy(),
            "recomendacion": drivers.map(RECOMENDACION_POR_DRIVER).to_numpy(),
            "prioridad": [
                prioridad_de_riesgo(r).value for r in con_driver["indice_riesgo"].to_numpy()
            ],
            **{
                f"shap_d{i}": [
                    contribuciones_por_escuela.get(cct, {}).get(f"D{i}")
                    for cct in con_driver["cct"]
                ]
                for i in range(1, 7)
            },
        }
    )
    for fila in filas.astype(object).where(pd.notna(filas), None).to_dict(orient="records"):
        RecomendacionGold(**fila)
    return filas


def filtrar_con_driver_observado(features: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Aparta las filas que no pueden tener driver dominante.

    ML-02 responde "¿cuál de los seis drivers explica el riesgo?". Una fila sin respuesta posible
    no se fuerza: forzarla sería inventar el diferenciador del proyecto.

    **Cuál es la fila sin respuesta depende de quién produce el target.** Si Gold ya trae la
    `driver_dominante` real de US-302, ella es la autoridad y basta con mirar dónde quedó `NULL`;
    inferirlo por nuestra cuenta abre un hueco, porque C1 exige `dN_cobertura = 'OK'` **además** de
    valor no nulo y nosotros sólo veríamos el valor. Una fila con dato pero cobertura `SIN_DATO`
    sobreviviría aquí y llegaría a `validar_target_ml02` con la etiqueta en nulo.

    Sin esa columna —fixtures, o Gold anterior a US-302— se cae al criterio del proxy: al menos un
    driver observado.

    Las apartadas **conservan su predicción de ML-01**: la variación de matrícula no necesita
    drivers. Lo que no reciben es recomendación, que es la regla de cobertura parcial: `SIN_DATO`
    explícito, nunca un driver inventado.

    Args:
        features: tabla conforme al contrato `FeaturesEscuela`.

    Returns:
        Las filas que sí admiten driver dominante, y cuántas se apartaron.
    """
    if COLUMNA_TARGET_REAL in features.columns:
        utiles = features[COLUMNA_TARGET_REAL].notna()
    else:
        utiles = features[list(DRIVERS)].notna().any(axis=1)
    return features[utiles].copy(), int((~utiles).sum())


def construir_recomendaciones_ml02(
    predicciones: pd.DataFrame,
    features: pd.DataFrame,
    modelo_ml02,
    incluir_shap: bool = False,
) -> pd.DataFrame:
    """Conecta las clases de ML-02 con las recomendaciones del mismo ciclo de ML-01."""
    llaves = ["cct", "id_ciclo"]
    corte = predicciones[llaves].merge(
        features,
        on=llaves,
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    faltantes = corte.loc[corte["_merge"] != "both", "cct"].tolist()
    if faltantes:
        raise ValueError(f"Faltan features de ML-02 para los CCT: {faltantes}.")

    salida_ml02 = predecir_driver(modelo_ml02, corte.drop(columns="_merge"))
    drivers = dict(
        zip(salida_ml02["cct"], salida_ml02["driver_dominante"], strict=True)
    )
    contribuciones = None
    if incluir_shap:
        explicaciones = explicar_driver(
            modelo_ml02,
            referencia=features,
            filas=corte.drop(columns="_merge"),
        )
        contribuciones = {
            explicacion["cct"]: explicacion["contribuciones"]
            for explicacion in explicaciones
        }
    return construir_recomendaciones(predicciones, drivers, contribuciones)


def _objetivo_de_conflicto(df: pd.DataFrame, tabla: Table):
    """Elige el índice único contra el que hace UPSERT este lote.

    Con grano dual (DEC-010) la tabla no tiene una llave primaria única: tiene **dos índices
    parciales**, uno por grano. El lote debe ser homogéneo para saber a cuál apuntar; mezclar granos
    en una sola escritura haría ambiguo el objetivo de conflicto.

    Returns:
        Tupla (columnas del índice, predicado parcial). `(llaves, None)` si la tabla tiene PK propia
        —como `gold.recomendaciones`, que sigue a grano escuela.

    Raises:
        ValueError: si el lote mezcla granos.
    """
    if "grano" not in df.columns:
        return [c.name for c in tabla.primary_key.columns], None

    granos = set(df["grano"].unique())
    if len(granos) > 1:
        raise ValueError(
            f"El lote mezcla granos {sorted(granos)}. Publica un grano por llamada: el objetivo de "
            "conflicto del UPSERT es distinto para cada uno."
        )

    grano = granos.pop()
    if grano == Grano.ESCUELA.value:
        return ["cct", "id_ciclo", "modelo"], text("grano = 'escuela'")
    if grano == Grano.MUNICIPIO_NIVEL.value:
        return ["cve_mun", "nivel", "id_ciclo", "modelo"], text("grano = 'municipio_nivel'")
    raise ValueError(f"Grano desconocido: {grano!r}. Esperado uno de {[g.value for g in Grano]}.")


def escribir(
    df: pd.DataFrame,
    tabla: Table,
    engine: Engine,
    metadata: MetaData,
) -> int:
    """Escribe con UPSERT sobre la llave primaria. Idempotente por diseño.

    Correr el job dos veces deja exactamente las mismas filas: la segunda corrida actualiza
    valores y `mlflow_run_id` en vez de duplicar. No borra ni trunca nada.

    Args:
        df: filas a publicar.
        tabla: tabla destino.
        engine: motor SQLAlchemy (PostgreSQL en producción, SQLite en pruebas).
        metadata: metadatos que contienen la tabla; se crean si no existen.

    Returns:
        Número de filas publicadas.

    Raises:
        NotImplementedError: si el motor no soporta UPSERT nativo.
    """
    if df.empty:
        return 0

    dialecto = engine.dialect.name
    if dialecto == "postgresql":
        from sqlalchemy.dialects.postgresql import insert
    elif dialecto == "sqlite":
        from sqlalchemy.dialects.sqlite import insert
    else:  # pragma: no cover - sólo usamos estos dos motores
        raise NotImplementedError(f"UPSERT no implementado para el dialecto {dialecto!r}.")

    llaves, filtro = _objetivo_de_conflicto(df, tabla)
    registros = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

    with engine.begin() as conexion:
        if tabla.schema:
            conexion.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{tabla.schema}"')
        metadata.create_all(conexion, tables=[tabla])
        if tabla.name == TABLA_RECOMENDACIONES:
            from sqlalchemy import inspect

            existentes = {
                columna["name"]
                for columna in inspect(conexion).get_columns(tabla.name, schema=tabla.schema)
            }
            nombre_tabla = (
                f'"{tabla.schema}"."{tabla.name}"' if tabla.schema else f'"{tabla.name}"'
            )
            for columna in (f"shap_d{i}" for i in range(1, 7)):
                if columna not in existentes:
                    conexion.exec_driver_sql(
                        f'ALTER TABLE {nombre_tabla} ADD COLUMN "{columna}" FLOAT'
                    )

        sentencia = insert(tabla).values(registros)
        actualizables = {
            c.name: sentencia.excluded[c.name] for c in tabla.columns if c.name not in llaves
        }
        conexion.execute(
            sentencia.on_conflict_do_update(
                index_elements=llaves, index_where=filtro, set_=actualizables
            )
        )
    return len(registros)


def _motor(url: str | None = None) -> Engine:
    """Crea el motor desde `--url`, `DATABASE_URL` o el `docker-compose.yml` local."""
    destino = url or os.environ.get("DATABASE_URL")
    if not destino:
        raise ValueError(
            "Falta el destino. Usa --url o define DATABASE_URL "
            "(p. ej. postgresql://postgres:...@localhost:5432/escuela_concausa_db)."
        )
    return create_engine(destino)


def main() -> int:
    """Entrena ML-01, construye las filas de Gold y las publica."""
    parser = argparse.ArgumentParser(description="Publica predicciones y recomendaciones (US-313).")
    parser.add_argument(
        "--features",
        type=Path,
        default=Path("tests/fixtures/features_escuela_mock.csv"),
        help="ruta al fixture; se ignora con --desde-gold",
    )
    parser.add_argument(
        "--desde-gold",
        action="store_true",
        help="lee `gold.features_escuela` de la base en vez del fixture (BUG-013)",
    )
    parser.add_argument("--url", default=None, help="URL SQLAlchemy; por defecto DATABASE_URL")
    parser.add_argument("--run-id", default="local-sin-mlflow", help="mlflow_run_id a registrar")
    parser.add_argument("--esquema", default=ESQUEMA_GOLD)
    parser.add_argument(
        "--ventanas",
        type=int,
        default=None,
        help="ventanas de backtesting; por defecto, el máximo que permitan los ciclos disponibles",
    )
    parser.add_argument(
        "--solo-predicciones",
        action="store_true",
        help="omite el entrenamiento de ML-02 y gold.recomendaciones",
    )
    parser.add_argument(
        "--con-shap",
        action="store_true",
        help="calcula y persiste SHAP en batch; requiere el stack completo de C3",
    )
    args = parser.parse_args()

    engine = _motor(args.url)
    if args.desde_gold:
        features = cargar_features_desde_gold(engine, esquema=args.esquema)
        print(
            f"Features desde gold.features_escuela: {len(features)} filas · "
            f"{features['cct'].nunique()} escuelas · ciclos {sorted(features['id_ciclo'].unique())}"
        )
    else:
        features = cargar_features(args.features)
        print(f"Features desde el fixture {args.features} — DATOS SINTÉTICOS")
    ventanas = args.ventanas or ventanas_posibles(features)
    if args.ventanas is None:
        print(f"Ventanas de backtesting: {ventanas} (máximo que permiten los ciclos disponibles)")
    resultado = entrenar_y_evaluar(features, n_ventanas=ventanas)
    print(f"ML-01 entrenado — MAE {resultado.mae_promedio:.4f} ± {resultado.mae_desviacion:.4f}")

    predicciones = construir_predicciones(features, resultado.modelo, args.run_id)
    print(f"Predicciones construidas: {len(predicciones)} filas (ciclo {predicciones['id_ciclo'].iloc[0]})")

    metadata, tabla_pred, tabla_rec = _metadatos(args.esquema)
    escritas = escribir(predicciones, tabla_pred, engine, metadata)
    print(f"gold.{TABLA_PREDICCIONES}: {escritas} filas publicadas (upsert idempotente)")

    if args.solo_predicciones:
        print("gold.recomendaciones omitida por --solo-predicciones.")
        return 0

    features_ml02, sin_driver = filtrar_con_driver_observado(features)
    if sin_driver:
        print(
            f"⚠️  {sin_driver} filas sin ningún driver observado quedan fuera de ML-02: no puede "
            "haber driver dominante donde no hay drivers. Conservan su predicción de ML-01; lo que "
            "no reciben es recomendación (SIN_DATO explícito, nunca un driver inventado)."
        )
    if features_ml02.empty:
        raise ValueError(
            "Ninguna fila observa algún driver: no hay con qué entrenar ML-02. Revisa la cobertura "
            "de drivers en `gold.features_escuela`."
        )
    if COLUMNA_TARGET_REAL not in features_ml02.columns:
        features_ml02[COLUMNA_TARGET_PROXY] = generar_driver_dominante_proxy(features_ml02)
    resultado_ml02 = entrenar_ml02(features_ml02, n_ventanas=ventanas)
    # Las escuelas apartadas conservan su predicción pero no reciben recomendación. Se excluyen
    # aquí y no relajando la verificación de sincronía de `construir_recomendaciones_ml02`: esa
    # verificación debe seguir cazando desajustes de verdad, no el hueco que abrimos a propósito.
    con_recomendacion = predicciones[predicciones["cct"].isin(set(features_ml02["cct"]))]
    recomendaciones = construir_recomendaciones_ml02(
        con_recomendacion,
        features_ml02,
        resultado_ml02.modelo,
        incluir_shap=args.con_shap,
    )
    escritas = escribir(recomendaciones, tabla_rec, engine, metadata)
    print(
        f"ML-02 entrenado — F1 macro {resultado_ml02.f1_macro_promedio:.4f} ± "
        f"{resultado_ml02.f1_macro_desviacion:.4f}"
    )
    print(f"gold.{TABLA_RECOMENDACIONES}: {escritas} filas publicadas (upsert idempotente)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
