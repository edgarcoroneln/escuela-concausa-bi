"""Guarda de `BUG-063`: la categoría más alta de `prioridad` tiene que ser **alcanzable** (`DEC-026`).

**El defecto que previene.** `prioridad_de_riesgo` cortaba `alta` en `ANCLA_SIGMOIDE` (0.60), y el
máximo que ML-01 predice sobre el Gold de producción es **0.5717**: un corte por encima del techo
del fenómeno. Ninguna escuela podía salir en `alta` y la tarjeta de DB-09 leía 0 sin que nada
fallara. Es la misma clase de error que `BUG-058`: un corte que nadie contrasta contra el dato.

**Por qué NO consulta la base.** Cada quien tiene un Gold distinto: una corrida personal puede
tener un máximo de 0.3744 y la prueba saldría roja en esa máquina y en el CI, que no tiene base.
El techo de producción se fija como **constante con procedencia**: si el Gold autoritativo se
republica con otro máximo, se actualiza aquí a mano y en el mismo PR, con la cifra medida.

**Por qué el corte se localiza por bisección** en vez de leer una constante: la prueba verifica el
**comportamiento** de la función, así que sigue siendo válida sin importar cómo se llame —o dónde
viva— la constante que use.

> **Procedencia de este archivo.** El diseño —bisección y techo como constante— es de Christian
> Imanol Ruiz Hurtado (`@ImanolRuiz00`), que lo propuso al ofrecer la guarda. Se adopta tal cual
> con un solo cambio: `LINEA_DE_ALERTA` se importa de `src/modelos/riesgo.py`, la fuente canónica
> desde `DEC-026`, y no de `src/api/repositorio_gold.py`. Su versión hacía que una prueba de la
> capa de modelos dependiera de la capa que los expone; `tests/test_linea_de_alerta_unica.py` ata
> las dos copias a la canónica, así que la garantía es la misma sin invertir la dependencia.
"""
from __future__ import annotations

from argparse import Namespace

import pytest

from src.modelos.publicar_gold import (
    Prioridad,
    _verificar_shap_antes_de_publicar,
    prioridad_de_riesgo,
)
from src.modelos.riesgo import ANCLA_SIGMOIDE, LINEA_DE_ALERTA, RIESGO_ESTABLE

#: Máximo de `indice_riesgo` (ML-01) medido sobre el Gold de **producción**, registrado en
#: `BUG-063` y usado por `DEC-026` como base de su decisión. Medido de forma independiente por C2
#: y C5 sobre las 45,276 filas.
#:
#: No se consulta en la prueba: ver el docstring del módulo. **Si el modelo se recalibra y el Gold
#: autoritativo se republica, se actualiza aquí con la cifra medida** — nunca se sube para que la
#: prueba pase: si el corte queda por encima del techo, el defecto es el corte.
TECHO_OBSERVADO_GOLD_PROD = 0.5717


def _corte_de(categoria: Prioridad) -> float:
    """Menor riesgo en [0, 1] que la función clasifica en `categoria` o por encima (bisección)."""
    orden = [Prioridad.BAJA, Prioridad.MEDIA, Prioridad.ALTA]

    def alcanza(riesgo: float) -> bool:
        return orden.index(prioridad_de_riesgo(riesgo)) >= orden.index(categoria)

    assert alcanza(1.0), f"ni con riesgo 1.0 se llega a {categoria.value}"
    bajo, alto = 0.0, 1.0
    for _ in range(60):
        medio = (bajo + alto) / 2
        if alcanza(medio):
            alto = medio
        else:
            bajo = medio
    return alto


def test_la_prioridad_alta_es_alcanzable_con_el_techo_observado() -> None:
    """La guarda de `BUG-063`: con el Gold de producción, **al menos una escuela** puede ser `alta`."""
    corte = _corte_de(Prioridad.ALTA)
    assert corte <= TECHO_OBSERVADO_GOLD_PROD, (
        f"el corte de `alta` ({corte:.4f}) queda por encima del máximo observado en Gold "
        f"({TECHO_OBSERVADO_GOLD_PROD}): ninguna escuela puede salir en `alta` (BUG-063)"
    )
    assert prioridad_de_riesgo(TECHO_OBSERVADO_GOLD_PROD) is Prioridad.ALTA


def test_el_corte_alto_es_la_linea_de_alerta() -> None:
    """`DEC-026`: `alta` corta en la línea de alerta de `DEC-019`, la misma con la que la API cuenta
    `escuelas_en_riesgo`. Así DB-09 y el KPI-04 dejan de contar cosas distintas con el mismo nombre."""
    assert _corte_de(Prioridad.ALTA) == pytest.approx(LINEA_DE_ALERTA, abs=1e-9)
    assert prioridad_de_riesgo(LINEA_DE_ALERTA) is Prioridad.ALTA


def test_el_corte_medio_no_cambia() -> None:
    assert _corte_de(Prioridad.MEDIA) == pytest.approx(RIESGO_ESTABLE, abs=1e-9)


def test_el_ancla_de_calibracion_no_se_usa_como_corte() -> None:
    """`DEC-026` baja el corte, **no** la calibración: `ANCLA_SIGMOIDE` sigue en 0.60 (`DEC-006`) y
    una escuela en el ancla sigue siendo `alta`, pero el corte ya no es el ancla."""
    assert ANCLA_SIGMOIDE == 0.60
    assert _corte_de(Prioridad.ALTA) < ANCLA_SIGMOIDE
    assert prioridad_de_riesgo(ANCLA_SIGMOIDE) is Prioridad.ALTA


def test_el_techo_declarado_sigue_siendo_el_de_bug063() -> None:
    """Si alguien sube el techo para hacer pasar la prueba de arriba, esto lo hace explícito.

    El número no es libre: es una medición sobre el Gold de producción. Cambiarlo exige haber
    republicado y medido de nuevo, y en ese caso esta prueba se actualiza **en el mismo PR** con
    la cifra nueva y su procedencia.
    """
    assert TECHO_OBSERVADO_GOLD_PROD == 0.5717


# --------------------------------------------------------------------------- #
# Guarda de `--con-shap` (`DEC-026`, hallazgo de Christian Imanol Ruiz Hurtado)
#
# `escribir()` hace `on_conflict_do_update` con `set_` sobre TODAS las columnas menos las llaves.
# Sin `--con-shap`, `shap_d1..d6` viajan en `None` y el upsert **sobrescribe con NULL el SHAP ya
# publicado** en las 45,276 filas. Es silencioso y destructivo, así que lo rechaza el script.
# --------------------------------------------------------------------------- #

def _args(**cambios) -> Namespace:
    base = {
        "desde_gold": True,
        "solo_predicciones": False,
        "con_shap": False,
        "sin_shap_a_proposito": False,
    }
    return Namespace(**{**base, **cambios})


def test_desde_gold_sin_shap_se_rechaza() -> None:
    """El defecto: republicar así deja en NULL el SHAP de las 45,276 filas."""
    with pytest.raises(SystemExit) as exc:
        _verificar_shap_antes_de_publicar(_args())
    mensaje = str(exc.value)
    assert "shap_d1..d6" in mensaje
    assert "--con-shap" in mensaje and "--sin-shap-a-proposito" in mensaje


def test_con_shap_pasa() -> None:
    pytest.importorskip("shap")
    _verificar_shap_antes_de_publicar(_args(con_shap=True))


def test_se_puede_publicar_sin_shap_si_se_declara() -> None:
    """El caso legítimo —un ambiente donde el SHAP nunca se pobló— pero hay que declararlo."""
    _verificar_shap_antes_de_publicar(_args(sin_shap_a_proposito=True))


def test_contra_el_fixture_no_hace_falta_declarar_nada() -> None:
    """Sin `--desde-gold` no hay SHAP publicado que perder."""
    _verificar_shap_antes_de_publicar(_args(desde_gold=False))


def test_solo_predicciones_no_toca_recomendaciones() -> None:
    """`--solo-predicciones` ni siquiera escribe en `gold.recomendaciones`."""
    _verificar_shap_antes_de_publicar(_args(solo_predicciones=True))


def test_con_shap_sin_el_paquete_falla_antes_de_entrenar(monkeypatch) -> None:
    """Descubrirlo al final costaría la corrida completa de ML-01 y ML-02."""
    import builtins

    real = builtins.__import__

    def _sin_shap(nombre, *a, **k):
        if nombre == "shap":
            raise ImportError("no shap")
        return real(nombre, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _sin_shap)
    with pytest.raises(SystemExit) as exc:
        _verificar_shap_antes_de_publicar(_args(con_shap=True))
    assert "no está instalado" in str(exc.value)
