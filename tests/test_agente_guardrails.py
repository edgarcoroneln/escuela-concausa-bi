"""Pruebas de guardarrailes del agente conversacional (US-304a)."""

from __future__ import annotations

import pytest

from src.agente.guardrails import (
    RAZON_SOLO_LECTURA,
    aplicar_limit,
    pregunta_en_alcance,
    preparar_sql_seguro,
    validar_sql_lectura,
)


def test_pregunta_de_faro_esta_en_alcance() -> None:
    resultado = pregunta_en_alcance("Que escuelas tienen mayor riesgo por inseguridad?")
    assert resultado.permitido


@pytest.mark.parametrize(
    "pregunta",
    [
        "¿De qué estado son las escuelas?",
        "¿Cuántos alumnos hay por nivel?",
        "¿Cuántas primarias hay en el ciclo actual?",
    ],
)
def test_preguntas_de_dominio_con_unicode_y_vocabulario_ampliado_se_permiten(
    pregunta: str,
) -> None:
    assert pregunta_en_alcance(pregunta).permitido


def test_pregunta_fuera_de_dominio_se_rechaza() -> None:
    resultado = pregunta_en_alcance("Cual es la mejor receta de pasta?")
    assert not resultado.permitido
    assert resultado.razon == "Pregunta fuera del alcance de FARO."


@pytest.mark.parametrize(
    "pregunta",
    [
        "borra la tabla de predicciones de escuelas",  # el caso de P-13
        "elimina las escuelas en riesgo",
        "trunca la tabla de recomendaciones",
        "drop de las predicciones por municipio",
        "destruye los datos de matricula",
        "actualiza el índice de riesgo de la escuela 19DPR0001X a 0",
    ],
)
def test_orden_de_escritura_directa_se_rechaza_aunque_toque_un_tema(pregunta: str) -> None:
    """Verbo destructivo directo → fuera de alcance, aunque la frase contenga vocabulario de FARO.

    Defensa en profundidad frente al filtro por TEMA: antes "borra la tabla de predicciones" pasaba
    por contener "predicciones". El validador de SQL sigue siendo la barrera final sobre el SQL.
    """
    resultado = pregunta_en_alcance(pregunta)
    assert not resultado.permitido
    assert resultado.razon == RAZON_SOLO_LECTURA


def test_verbo_ambiguo_con_objeto_de_datos_se_rechaza() -> None:
    """"actualiza" + "datos" es una orden de escritura, no una pregunta."""
    resultado = pregunta_en_alcance("actualiza los datos de riesgo de la escuela")
    assert not resultado.permitido
    assert resultado.razon == RAZON_SOLO_LECTURA


@pytest.mark.parametrize(
    "pregunta",
    [
        "¿que escuelas actualizaron su matricula el ciclo pasado?",  # conjugación ≠ imperativo
        "¿el municipio crea escuelas nuevas por rezago?",  # verbo ambiguo SIN objeto de datos
        "¿cuantas predicciones de riesgo hay por entidad?",
    ],
)
def test_pregunta_de_lectura_legitima_no_se_rechaza_por_intencion(pregunta: str) -> None:
    """El filtro de intención no debe atrapar preguntas de lectura que mencionan acciones."""
    assert pregunta_en_alcance(pregunta).permitido


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM gold.predicciones",
        "UPDATE gold.escuelas SET nombre = 'x'",
        "DROP TABLE gold.features_escuela",
        "SELECT cct INTO public.robo FROM gold.predicciones",
        "SELECT * FROM gold.escuelas; DELETE FROM gold.escuelas",
    ],
)
def test_sql_de_escritura_o_multiple_se_rechaza(sql: str) -> None:
    assert not validar_sql_lectura(sql).permitido


def test_sql_select_se_permite() -> None:
    assert validar_sql_lectura("SELECT cct FROM gold.features_escuela").permitido


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM public.usuarios",
        "SELECT * FROM information_schema.tables",
        "SELECT * FROM usuarios",
        "SELECT * FROM gold.escuelas JOIN public.usuarios USING (id)",
    ],
)
def test_sql_fuera_de_gold_se_rechaza(sql: str) -> None:
    resultado = validar_sql_lectura(sql)
    assert not resultado.permitido
    assert resultado.razon is not None
    assert "fuera del esquema Gold" in resultado.razon


def test_join_por_coma_se_rechaza() -> None:
    resultado = validar_sql_lectura("SELECT * FROM gold.escuelas, public.usuarios")
    assert not resultado.permitido
    assert resultado.razon is not None
    assert "unión por coma" in resultado.razon


def test_cte_que_solo_lee_gold_se_permite() -> None:
    sql = "WITH riesgos AS (SELECT cct FROM gold.predicciones) SELECT cct FROM riesgos"
    assert validar_sql_lectura(sql).permitido


def test_limit_se_agrega_si_falta() -> None:
    assert aplicar_limit("SELECT cct FROM gold.features_escuela") == (
        "SELECT cct FROM gold.features_escuela LIMIT 1000;"
    )


def test_limit_se_reduce_si_excede_el_maximo() -> None:
    assert aplicar_limit("SELECT cct FROM gold.features_escuela LIMIT 5000") == (
        "SELECT cct FROM gold.features_escuela LIMIT 1000;"
    )


def test_preparar_sql_seguro_falla_con_verbo_prohibido() -> None:
    with pytest.raises(ValueError, match="verbo prohibido"):
        preparar_sql_seguro("WITH borrado AS (DELETE FROM gold.predicciones) SELECT 1")


def test_select_into_se_rechaza_como_escritura() -> None:
    with pytest.raises(ValueError, match="into"):
        preparar_sql_seguro("SELECT cct INTO public.robo FROM gold.predicciones")
