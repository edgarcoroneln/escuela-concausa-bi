"""Pruebas del índice de riesgo de ML-01 (US-311).

La prueba clave es `test_cumple_el_contrato_de_la_api`: construye un `PrediccionOut` real con el
valor calculado, así que si alguien recalibra la sigmoide fuera de [0,1] el CI lo detiene antes de
que la API falle en producción.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.api.schemas import PrediccionOut
from src.modelos.riesgo import (
    ANCLA_SIGMOIDE,
    CALIBRACION,
    RIESGO_ESTABLE,
    RIESGO_UMBRAL,
    VARIACION_EN_RIESGO,
    VARIACION_ESTABLE,
    CalibracionRiesgo,
    indice_riesgo,
    variacion_equivalente,
    verificar_escala_variacion,
)

# --------------------------------------------------------------------------- anclas


def test_reproduce_el_ancla_de_escuela_estable() -> None:
    assert indice_riesgo(VARIACION_ESTABLE) == pytest.approx(RIESGO_ESTABLE)


def test_reproduce_el_ancla_del_umbral_de_negocio() -> None:
    """Perder 5 % de matrícula cae exactamente en el ancla alta de DEC-006."""
    assert indice_riesgo(VARIACION_EN_RIESGO) == pytest.approx(ANCLA_SIGMOIDE)


def test_el_alias_historico_sigue_apuntando_al_ancla() -> None:
    """`RIESGO_UMBRAL` se conserva por compatibilidad; DEC-019 lo renombró, no lo movió."""
    assert RIESGO_UMBRAL == ANCLA_SIGMOIDE


def test_dec019_no_recalibra_la_sigmoide() -> None:
    """El ancla se queda en 0.60 aunque la línea de alerta haya bajado a 0.50.

    `DEC-019` separó dos números que eran uno: cambió el criterio de alerta, no la calibración.
    Si alguien "actualiza" el ancla a 0.50 creyendo que es el mismo cambio, recalibra la sigmoide
    y mueve **todos** los `indice_riesgo` publicados — justo lo que la decisión prohíbe.
    """
    assert ANCLA_SIGMOIDE == 0.60


def test_la_linea_de_alerta_equivale_al_menos_34_por_ciento() -> None:
    """El 0.50 de DEC-019 se eligió porque equivale a proyectar −3.4 %.

    Es el argumento de negocio de la decisión: 3.4 % queda justo por debajo del 3.7 % de deserción
    real en secundaria, así que la alerta enciende antes de alcanzar la norma nacional. Si alguien
    recalibra la sigmoide, esa equivalencia deja de ser cierta y la decisión pierde su fundamento
    sin que nadie se entere. Esta prueba lo convierte en un fallo visible.
    """
    assert float(variacion_equivalente(0.50)) == pytest.approx(-0.0338, abs=5e-4)


# --------------------------------------------------------------------------- propiedades


def test_es_monotona_decreciente() -> None:
    """Cuanto más cae la matrícula, mayor el riesgo. Sin excepciones."""
    variaciones = np.linspace(-0.5, 0.5, 200)
    riesgos = indice_riesgo(variaciones)
    assert np.all(np.diff(riesgos) < 0)


def test_esta_acotada_incluso_en_extremos() -> None:
    """El contrato de la API exige [0,1]; la sigmoide nunca se sale, ni con valores absurdos."""
    extremos = np.array([-1e6, -10.0, -0.5, 0.0, 0.5, 10.0, 1e6])
    riesgos = indice_riesgo(extremos)
    assert np.all(riesgos >= 0.0)
    assert np.all(riesgos <= 1.0)
    assert not np.any(np.isnan(riesgos))


def test_una_caida_mayor_da_mas_riesgo_que_el_umbral() -> None:
    assert indice_riesgo(-0.20) > RIESGO_UMBRAL


def test_crecer_en_matricula_da_riesgo_bajo() -> None:
    assert indice_riesgo(0.10) < RIESGO_ESTABLE


# --------------------------------------------------------------------------- vectorización


def test_vectorizado_coincide_con_escalar() -> None:
    valores = [-0.3, -0.05, 0.0, 0.2]
    esperado = [indice_riesgo(v) for v in valores]
    assert indice_riesgo(np.array(valores)) == pytest.approx(esperado)


def test_funciona_sobre_una_serie_de_pandas() -> None:
    """Se aplica directo sobre la salida de `model.predict()` sin conversiones intermedias."""
    serie = pd.Series([-0.10, 0.0, 0.05], name="variacion")
    riesgos = indice_riesgo(serie)
    assert len(riesgos) == 3
    assert bool(np.all((riesgos >= 0) & (riesgos <= 1)))


# --------------------------------------------------------------------------- inversa


def test_la_inversa_recupera_la_variacion() -> None:
    for variacion in (-0.25, -0.05, 0.0, 0.15):
        assert variacion_equivalente(indice_riesgo(variacion)) == pytest.approx(variacion)


def test_la_inversa_traduce_el_umbral_del_tablero() -> None:
    """Un riesgo de 0.60 en el tablero significa perder 5 % de matrícula."""
    assert variacion_equivalente(RIESGO_UMBRAL) == pytest.approx(VARIACION_EN_RIESGO)


def test_la_inversa_rechaza_riesgos_inalcanzables() -> None:
    for invalido in (0.0, 1.0, -0.2, 1.5):
        with pytest.raises(ValueError, match="abierto"):
            variacion_equivalente(invalido)


# --------------------------------------------------------------------------- calibración


def test_calibracion_rechaza_anclas_no_monotonas() -> None:
    with pytest.raises(ValueError, match="variacion_alta debe ser menor"):
        CalibracionRiesgo(variacion_baja=0.0, variacion_alta=0.1)


def test_calibracion_rechaza_riesgos_invertidos() -> None:
    with pytest.raises(ValueError, match="riesgo_alto debe ser mayor"):
        CalibracionRiesgo(riesgo_bajo=0.8, riesgo_alto=0.2)


def test_calibracion_rechaza_riesgos_fuera_del_intervalo() -> None:
    with pytest.raises(ValueError, match=r"\(0,1\) abierto"):
        CalibracionRiesgo(riesgo_bajo=0.0)


def test_calibracion_alterna_se_respeta() -> None:
    """Recalibrar mueve el umbral sin tocar el código que la consume."""
    estricta = CalibracionRiesgo(variacion_alta=-0.02, riesgo_alto=0.75)
    assert indice_riesgo(-0.02, estricta) == pytest.approx(0.75)
    assert indice_riesgo(-0.02, estricta) > indice_riesgo(-0.02, CALIBRACION)


# --------------------------------------------------------------------------- contrato API


def test_cumple_el_contrato_de_la_api() -> None:
    """El valor calculado valida contra `PrediccionOut` de la Célula 4 (US-401)."""
    for variacion in (-2.0, -0.05, 0.0, 3.0):
        salida = PrediccionOut(
            cct="09DPR0001X",
            id_ciclo="2023-2024",
            indice_riesgo=float(indice_riesgo(variacion)),
            driver_dominante="D2",
            recomendacion="Intervención en seguridad del entorno escolar.",
            cluster=1,
            mlflow_run_id="0" * 32,
        )
        assert 0.0 <= salida.indice_riesgo <= 1.0


# ------------------------------------------------------- escala de la variación (BUG-016)


def test_acepta_variaciones_expresadas_como_fraccion() -> None:
    """Lo normal: pérdidas y ganancias de unos pocos puntos porcentuales, en fracción."""
    verificar_escala_variacion([-0.03, 0.01, -0.12, 0.0, -0.25])


def test_rechaza_variaciones_en_puntos_porcentuales() -> None:
    """El caso real: si Gold entrega -5.0 en vez de -0.05, la sigmoide satura en silencio."""
    with pytest.raises(ValueError, match="no parece venir en fracción"):
        verificar_escala_variacion([-3.0, 1.0, -12.0, -8.5])


def test_el_mensaje_dice_cuanto_se_satura() -> None:
    """Sin el porcentaje, el mensaje no transmite por qué esto no es un detalle menor."""
    with pytest.raises(ValueError, match="100.0% de las filas"):
        verificar_escala_variacion([-3.0, -12.0, -8.5, -20.0])


def test_una_variacion_extrema_aislada_no_dispara_la_alarma() -> None:
    """Se mira la mediana, no el máximo: una escuela que triplica matrícula no es un error."""
    verificar_escala_variacion([-0.02, 0.03, -0.01, 0.04, 25.0])


def test_ignora_nan_e_infinitos() -> None:
    verificar_escala_variacion([np.nan, -0.05, np.inf, 0.02])
    verificar_escala_variacion([np.nan, np.nan])


def test_la_saturacion_que_denuncia_es_real() -> None:
    """La prueba que le da sentido a la guarda: con esa escala el riesgo pierde toda resolución."""
    en_puntos = np.array([-3.0, -8.0, -15.0, -0.5])
    riesgos = indice_riesgo(en_puntos)

    assert np.all(riesgos > 0.999), "todas saturan arriba: el tablero no distingue ninguna"
    assert riesgos.max() - riesgos.min() < 1e-3, "el orden entre escuelas se vuelve ruido"
