"""La línea de alerta vale lo mismo en todas las capas (`RISK-010`).

**Por qué existe este archivo.** `RISK-010` dice, literalmente, que el corte de riesgo *«está
escrito a mano en ~11 sitios de cuatro células y no hay una sola fuente»*, y que **«nada impide que
los sitios diverjan en silencio: no hay prueba que los ate»**. Esta es esa prueba.

Ya pasó una vez con este número exacto: `BUG-060` documenta que el camino mock del KPI-04 contaba
con `>= 0.50` y el camino real con `>= 0.60`, o sea que el mismo KPI daba cifras distintas según
hubiera base de datos o no — y **cada camino se probaba contra sí mismo**, así que la divergencia
era invisible para la suite. Coincidieron después por accidente, no por diseño.

`src/modelos/riesgo.py::LINEA_DE_ALERTA` es la fuente canónica desde `DEC-026`. C4 y C2 conservan
su propia copia; retirarlas es trabajo de sus dueños. Mientras existan, esta prueba las ata.
"""
from __future__ import annotations

import importlib

import pytest

from src.modelos.riesgo import ANCLA_SIGMOIDE, LINEA_DE_ALERTA

#: Cada copia conocida: (módulo, nombre de la constante, dueño a quien avisar si diverge).
_COPIAS = [
    ("src.api.repositorio_gold", "LINEA_DE_ALERTA", "C4 · Christian Ruiz"),
    ("src.frontend.prediccion_client", "LINEA_DE_ALERTA", "C2 · Marina García del Buey"),
]


@pytest.mark.parametrize(("modulo", "constante", "dueno"), _COPIAS, ids=[c[0] for c in _COPIAS])
def test_cada_copia_vale_lo_mismo_que_la_canonica(modulo: str, constante: str, dueno: str) -> None:
    try:
        mod = importlib.import_module(modulo)
    except ImportError as exc:  # pragma: no cover - depende del entorno
        pytest.skip(f"{modulo} no importable en este entorno: {exc}")

    valor = getattr(mod, constante, None)
    assert valor is not None, (
        f"{modulo}.{constante} desapareció. Si {dueno} la retiró para importar la canónica, "
        f"quita su fila de _COPIAS; si la renombró, actualízala aquí."
    )
    assert valor == LINEA_DE_ALERTA, (
        f"{modulo}.{constante} = {valor} pero la fuente canónica "
        f"(src/modelos/riesgo.py::LINEA_DE_ALERTA) = {LINEA_DE_ALERTA}. "
        f"Es la divergencia silenciosa que describe RISK-010 — avisa a {dueno}."
    )


def test_la_linea_de_alerta_no_se_confunde_con_el_ancla() -> None:
    """Son dos números distintos haciendo dos trabajos distintos (`DEC-019`).

    Que vuelvan a ser iguales sería la regresión que `BUG-058` y `BUG-063` causaron: el ancla
    calibra la sigmoide y la línea decide cuándo hay alerta. Igualarlas devuelve el corte por
    encima del techo del fenómeno.
    """
    assert LINEA_DE_ALERTA < ANCLA_SIGMOIDE
    assert (LINEA_DE_ALERTA, ANCLA_SIGMOIDE) == (0.50, 0.60)
