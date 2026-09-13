"""La categoría más alta de `prioridad` tiene que ser alcanzable (`BUG-063`, `DEC-026`).

**El defecto que esta prueba existe para cazar.** `prioridad_de_riesgo()` exigía
`>= ANCLA_SIGMOIDE` (0.60) para marcar `ALTA`, y el máximo que ML-01 predice sobre el Gold de
producción es **0.5717**. Ninguna de las 45,276 escuelas calificaba: la tarjeta *"Recomendaciones
de prioridad ALTA"* de DB-09 —la que dice a qué escuelas entrar primero, en el tablero del
diferenciador— leía **0**. No por un defecto del modelo ni de los datos, sino porque **el corte
estaba por encima del techo del fenómeno**.

Es el mismo defecto estructural de `BUG-058` en otra columna, y ninguna prueba lo vio en ninguna de
las dos. `BUG-054` tampoco: corrigió la comparación de mayúsculas y se verificó contra un fixture
de ~55 filas donde sí había *"alta 2"* — en 45,276 filas ese 2 es 0. **Un umbral inalcanzable por
construcción no es una opinión de negocio: es un defecto detectable**, y esto lo detecta.

**Por qué sobre fixture y no contra la base conectada.** `DEC-026` pedía que la guarda contraste el
corte contra *"el máximo observado en el Gold publicado"*. Consultar la base que esté conectada
haría que la prueba dependa de qué cosecha de Gold tenga cada quien: sobre una corrida local con
máximo 0.3744, saldría roja y dejaría el CI en rojo para todo el equipo sin que nada esté mal en el
código. Aquí se afirma la propiedad —el corte tiene que quedar por debajo del techo *conocido* del
fenómeno— con ese techo declarado como dato, revisable y con procedencia.
"""
from __future__ import annotations

import pytest

from src.modelos.publicar_gold import Prioridad, prioridad_de_riesgo
from src.modelos.riesgo import ANCLA_SIGMOIDE, LINEA_DE_ALERTA

#: Techo real del fenómeno: el máximo `indice_riesgo` que ML-01 predice sobre el Gold de
#: producción (45,276 escuelas). Medido de forma independiente por C2 y C5 y asentado en
#: `DEC-019`; `DEC-026` lo reusa como base de su decisión.
#:
#: **Si el modelo se recalibra, este número cambia** — actualízalo con la corrida nueva y su
#: procedencia. No lo subas para que la prueba pase: si el corte queda por encima del techo, el
#: defecto es el corte.
MAXIMO_OBSERVADO_EN_GOLD = 0.5717


def test_la_categoria_mas_alta_es_alcanzable() -> None:
    """`BUG-063`: el corte de `ALTA` no puede quedar por encima del techo del fenómeno."""
    assert LINEA_DE_ALERTA <= MAXIMO_OBSERVADO_EN_GOLD, (
        f"El corte de ALTA ({LINEA_DE_ALERTA}) quedó por encima del máximo observado en el Gold "
        f"publicado ({MAXIMO_OBSERVADO_EN_GOLD}): ninguna escuela puede alcanzar la categoría y la "
        f"tarjeta de DB-09 leerá 0. Es BUG-063."
    )
    assert prioridad_de_riesgo(MAXIMO_OBSERVADO_EN_GOLD) is Prioridad.ALTA


def test_el_ancla_sigue_siendo_inalcanzable_y_por_eso_no_es_el_corte() -> None:
    """La razón de `DEC-026`, escrita como prueba.

    Si alguien devuelve el corte al ancla, esta prueba explica por qué no funciona: 0.60 sigue
    estando por encima del techo. El ancla no está mal — está calibrando otra cosa (`DEC-006`).
    """
    assert ANCLA_SIGMOIDE > MAXIMO_OBSERVADO_EN_GOLD
    assert prioridad_de_riesgo(MAXIMO_OBSERVADO_EN_GOLD) is not None


@pytest.mark.parametrize(
    ("riesgo", "esperada"),
    [
        (0.5717, Prioridad.ALTA),   # el techo real: tiene que calificar
        (0.50, Prioridad.ALTA),     # el corte exacto, inclusivo
        (0.4999, Prioridad.MEDIA),  # justo debajo
        (0.30, Prioridad.MEDIA),    # el corte de MEDIA, inclusivo
        (0.2999, Prioridad.BAJA),
        (0.0, Prioridad.BAJA),
    ],
)
def test_fronteras_de_cada_categoria(riesgo: float, esperada: Prioridad) -> None:
    assert prioridad_de_riesgo(riesgo) is esperada
