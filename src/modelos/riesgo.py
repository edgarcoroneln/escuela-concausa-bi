"""Traducción de la predicción de ML-01 al `indice_riesgo` ∈ [0,1] (US-311).

## Por qué existe este módulo

ML-01 predice `target_variacion_matricula`: un **float con signo y sin cota** (la variación de
matrícula respecto al ciclo anterior; negativo = la escuela pierde alumnos).

Pero todo lo que consume ML-01 aguas abajo espera un **`indice_riesgo` acotado a [0,1]**, donde
más alto = más riesgo:

- `src/api/schemas.py::PrediccionOut.indice_riesgo` — `Field(ge=0, le=1)`, y su prueba lo verifica.
- `vault/03_Architecture/Data_Model.md` §4.5 — vive en `gold.predicciones` como `valor` con `modelo='ML-01'`.
- `vault/04_UX_Design/Screen_Specs.md` — los tableros ordenan y cuentan escuelas por este índice.
  **El corte con el que cuentan no se define aquí** (ver "Ancla y línea de alerta", abajo).

Nadie había definido la conversión entre ambas cosas. Este módulo la define en un solo lugar para
que la API, los cubos de Superset y FARO Web lean el mismo número.

## Cómo se define

Una **sigmoide monótona decreciente** en la variación, fijada por dos anclas de negocio:

| Variación de matrícula | `indice_riesgo` | Lectura |
|---|---|---|
| `0.00` (matrícula estable) | **0.30** | riesgo bajo, no nulo |
| `-0.05` (pierde 5 %) | **0.60** | el umbral de negocio de `DEC-006`: "la escuela está en riesgo" |

Dos puntos determinan de forma única el centro y la escala de la sigmoide, así que la calibración
queda documentada por sus anclas y no por constantes mágicas.

**Por qué una sigmoide y no un min-max ni un percentil:**

- *Min-max sobre el conjunto* daría un índice que cambia si entra una escuela atípica, y no sería
  comparable entre ciclos.
- *Percentil (ECDF)* es relativo: si un año todas las escuelas caen, la mitad seguiría saliendo con
  riesgo bajo. Mala propiedad para un sistema de alerta.
- *Sigmoide* es **absoluta y estable**: la misma variación produce siempre el mismo riesgo, sea cual
  sea el resto del universo o el ciclo. Además está acotada por construcción, así que nunca viola el
  contrato de la API.

## Ancla y línea de alerta son dos cosas distintas (`DEC-019`)

Hasta el 6 de septiembre `0.60` hacía **dos trabajos a la vez** y este módulo los confundía: era el
ancla que calibra la sigmoide **y** el corte con el que los tableros contaban escuelas. `DEC-019`
los separó, y aquí sólo vive el primero:

| | Valor | Qué es | Dónde vive |
|---|---|---|---|
| **Ancla de la sigmoide** | `0.60` | calibración: `-0.05` de variación ↦ `0.60` de riesgo (`DEC-006`) | `ANCLA_SIGMOIDE`, en este módulo |
| **Línea de alerta** | `0.50` | corte de negocio para *contar* escuelas en riesgo (`DEC-019`) | `src/api/repositorio_gold.py::LINEA_DE_ALERTA` (C4) |

**`ANCLA_SIGMOIDE` se queda en 0.60.** `DEC-019` cambió el criterio de alerta, no la calibración:
no se recalibra, no se re-entrena y no cambia un solo `indice_riesgo` ya publicado.

**Este módulo no define la línea de alerta a propósito.** `RISK-010` sigue abierto porque `0.50` ya
está escrito dos veces (C4 y C2); definirlo aquí una tercera vez agravaría justo lo que ese riesgo
señala. La fuente única —una `var` de dbt y una constante importada, más una prueba que ate los
sitios— es trabajo post-freeze.

> **Estatus:** la unidad del target quedó ratificada en `ADR-007` (fracción, 29-ago) y el umbral de
> −5 % en `DEC-006` (13-ago). **Queda abierta una sola ancla: el `0.30` de escuela estable**, que es
> un juicio de negocio. Ver `vault/15_ML_Models/Indice_Riesgo_ML01.md` §4.1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar

import numpy as np
from scipy.special import expit, logit

#: Variación de matrícula de referencia: la escuela conserva su matrícula.
VARIACION_ESTABLE = 0.0
#: Riesgo asignado a una escuela estable. No es cero: toda escuela tiene riesgo de base.
RIESGO_ESTABLE = 0.30

#: Variación que el negocio considera "escuela en riesgo": pierde 5 % de su matrícula (`DEC-006`).
VARIACION_EN_RIESGO = -0.05
#: Ancla alta de la sigmoide: el riesgo que corresponde a `VARIACION_EN_RIESGO`. **No es la línea
#: de alerta de los tableros**, que `DEC-019` fijó en 0.50 y vive en `repositorio_gold.py` (C4).
#: Mismo nombre que usan C4 (`src/api/repositorio_gold.py`) y C2 (`src/frontend/prediccion_client.py`).
ANCLA_SIGMOIDE = 0.60

#: Alias histórico de `ANCLA_SIGMOIDE`. El nombre viejo daba a entender que era el corte de los
#: tableros; `DEC-019` mostró que no lo es. Se conserva para no romper importaciones existentes.
RIESGO_UMBRAL = ANCLA_SIGMOIDE

#: Cota para la mediana de |variación| si el target viene como **fracción**, que es lo que la
#: sigmoide supone. Una escuela no puede perder más del 100 % de su matrícula y la mediana real
#: ronda 0.05–0.15, así que 1.0 es holgadísimo: sólo se dispara si las unidades no son fracción.
MEDIANA_MAXIMA_FRACCION = 1.0

T = TypeVar("T", float, np.ndarray)


@dataclass(frozen=True)
class CalibracionRiesgo:
    """Calibración de la sigmoide, definida por dos anclas de negocio.

    Args:
        variacion_baja: variación del ancla de riesgo bajo (típicamente 0.0).
        riesgo_bajo: riesgo asignado a `variacion_baja`.
        variacion_alta: variación del ancla de riesgo alto; debe ser **menor** que
            `variacion_baja` (más negativa = peor).
        riesgo_alto: riesgo asignado a `variacion_alta`; debe ser **mayor** que `riesgo_bajo`.

    Raises:
        ValueError: si las anclas no definen una relación monótona decreciente válida.
    """

    variacion_baja: float = VARIACION_ESTABLE
    riesgo_bajo: float = RIESGO_ESTABLE
    variacion_alta: float = VARIACION_EN_RIESGO
    riesgo_alto: float = RIESGO_UMBRAL

    centro: float = field(init=False)
    escala: float = field(init=False)

    def __post_init__(self) -> None:
        for nombre, riesgo in (("riesgo_bajo", self.riesgo_bajo), ("riesgo_alto", self.riesgo_alto)):
            if not 0.0 < riesgo < 1.0:
                raise ValueError(f"{nombre} debe estar en (0,1) abierto, recibido {riesgo}.")
        if self.variacion_alta >= self.variacion_baja:
            raise ValueError(
                "variacion_alta debe ser menor que variacion_baja (más negativa = más riesgo): "
                f"{self.variacion_alta} >= {self.variacion_baja}."
            )
        if self.riesgo_alto <= self.riesgo_bajo:
            raise ValueError(
                "riesgo_alto debe ser mayor que riesgo_bajo: "
                f"{self.riesgo_alto} <= {self.riesgo_bajo}."
            )

        # Dos anclas determinan la sigmoide:
        #   riesgo(v) = expit((centro - v) / escala)
        # Despejando de logit(riesgo_i) = (centro - v_i) / escala en ambos puntos.
        escala = (self.variacion_alta - self.variacion_baja) / (
            float(logit(self.riesgo_bajo)) - float(logit(self.riesgo_alto))
        )
        object.__setattr__(self, "escala", escala)
        object.__setattr__(
            self, "centro", self.variacion_baja + escala * float(logit(self.riesgo_bajo))
        )


#: Calibración vigente. Cambiarla aquí la cambia para la API, los cubos y los tableros a la vez.
CALIBRACION = CalibracionRiesgo()


def indice_riesgo(variacion: T, calibracion: CalibracionRiesgo = CALIBRACION) -> T:
    """Convierte la variación de matrícula predicha por ML-01 en `indice_riesgo` ∈ (0,1).

    Monótona decreciente: cuanto más cae la matrícula, mayor el riesgo. Acotada por construcción,
    así que el resultado siempre cumple `Field(ge=0, le=1)` del contrato de la API.

    Args:
        variacion: variación predicha (escalar, `np.ndarray` o `pd.Series`).
        calibracion: anclas a usar. Por defecto, las de negocio vigentes.

    Returns:
        El índice de riesgo, del mismo tipo que la entrada.

    Example:
        >>> round(float(indice_riesgo(0.0)), 4)          # matrícula estable
        0.3
        >>> round(float(indice_riesgo(-0.05)), 4)        # ancla alta: pierde 5 % (DEC-006)
        0.6
        >>> bool(indice_riesgo(-0.20) > indice_riesgo(-0.05))  # caída mayor, más riesgo
        True
    """
    return expit((calibracion.centro - variacion) / calibracion.escala)


def variacion_equivalente(riesgo: T, calibracion: CalibracionRiesgo = CALIBRACION) -> T:
    """Inversa de `indice_riesgo`: qué variación produce un riesgo dado.

    Sirve para explicar un índice en lenguaje de negocio ("un riesgo de 0.60 equivale a perder
    5 % de la matrícula") y para fijar cortes al revés — incluida la línea de alerta de `DEC-019`:
    `variacion_equivalente(0.50)` ≈ `-0.034`, o sea proyectar una caída de 3.4 %.

    Args:
        riesgo: índice en (0,1) abierto.
        calibracion: anclas a usar.

    Returns:
        La variación de matrícula correspondiente.

    Raises:
        ValueError: si `riesgo` cae fuera de (0,1) abierto, donde la inversa no existe.
    """
    arr = np.asarray(riesgo, dtype=float)
    if np.any((arr <= 0.0) | (arr >= 1.0)):
        raise ValueError("riesgo debe estar en (0,1) abierto; 0 y 1 no son alcanzables.")
    return calibracion.centro - calibracion.escala * logit(riesgo)


def verificar_escala_variacion(
    variacion: np.ndarray | list[float],
    origen: str = "target_variacion_matricula",
    calibracion: CalibracionRiesgo = CALIBRACION,
) -> None:
    """Falla si la variación no parece venir expresada como fracción.

    La sigmoide está anclada en fracciones: `-0.05` significa "pierde 5 % de su matrícula". Si el
    dato llega en puntos porcentuales (`-5.0`) o como diferencia absoluta de alumnos, la conversión
    no da error —da `indice_riesgo` **saturado en 0 o en 1 para casi todas las filas**. Eso es peor
    que fallar: el tablero se ve lleno y cuenta como "en riesgo" a todo el universo.

    Se mira la **mediana** de `|variación|`, no el máximo, para no confundir unidades equivocadas
    con unos cuantos valores extremos legítimos.

    Args:
        variacion: variaciones predichas u observadas.
        origen: nombre de la columna, para que el mensaje diga dónde mirar.
        calibracion: anclas contra las que se compara.

    Raises:
        ValueError: si la mediana de `|variación|` excede `MEDIANA_MAXIMA_FRACCION`.

    Examples:
        >>> verificar_escala_variacion([-0.03, 0.01, -0.12])   # fracciones: pasa
        >>> verificar_escala_variacion([-3.0, 1.0, -12.0])
        Traceback (most recent call last):
        ValueError: target_variacion_matricula no parece venir en fracción...
    """
    arr = np.asarray(variacion, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return
    mediana = float(np.median(np.abs(arr)))
    if mediana <= MEDIANA_MAXIMA_FRACCION:
        return
    saturadas = float(
        np.mean((indice_riesgo(arr, calibracion) <= 0.01) | (indice_riesgo(arr, calibracion) >= 0.99))
    )
    raise ValueError(
        f"{origen} no parece venir en fracción: la mediana de |variación| es {mediana:.4g}, "
        f"pero la sigmoide está calibrada con {calibracion.variacion_alta} = "
        f"'pierde 5 % de la matrícula'. Con esta escala, {saturadas:.1%} de las filas quedarían "
        "con indice_riesgo saturado en 0 o en 1, y el tablero contaría como en riesgo a todo el "
        "universo. Causa conocida (BUG-017): `features_escuela.sql` produce esta columna como "
        "`matricula_total - matricula_ciclo_anterior`, es decir **alumnos absolutos**, mientras que "
        "`target_hibrido.variacion_desde_serie` la produce como fracción. La unidad se decide en "
        "ADR-007; hasta que se ratifique, publicar aquí saturaría el índice en silencio."
    )
