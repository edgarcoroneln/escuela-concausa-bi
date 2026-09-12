"""Pruebas offline del runner golden de Fase 4."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.agente.evaluar_golden import _cumple_expectativa, _cargar_fixture


FIXTURE = Path(__file__).parent / "fixtures" / "preguntas_evaluacion.json"


def test_fixture_golden_tiene_20_casos_y_categorias_esperadas() -> None:
    casos = _cargar_fixture(FIXTURE)

    assert len(casos) == 20
    assert {caso["categoria"] for caso in casos} == {
        "valida",
        "fuera_de_alcance",
        "insegura",
    }


@pytest.mark.parametrize(
    ("categoria", "fuera_de_alcance", "tiene_sql", "esperado"),
    [
        ("valida", False, True, True),
        ("valida", True, True, False),
        ("fuera_de_alcance", True, False, True),
        ("fuera_de_alcance", False, False, False),
        ("insegura", True, False, True),
        ("insegura", False, True, False),
    ],
)
def test_expectativas_por_categoria(
    categoria: str,
    fuera_de_alcance: bool,
    tiene_sql: bool,
    esperado: bool,
) -> None:
    assert _cumple_expectativa(categoria, fuera_de_alcance, tiene_sql) is esperado


def test_fixture_no_contiene_secreto() -> None:
    contenido = FIXTURE.read_text(encoding="utf-8")

    assert "ANTHROPIC_API_KEY" not in contenido
    assert "sk-ant-" not in contenido


def test_resultado_golden_no_incluye_sql_ni_respuesta() -> None:
    from dataclasses import fields

    from src.agente.evaluar_golden import ResultadoGolden

    nombres = {campo.name for campo in fields(ResultadoGolden)}

    assert "sql_generado" not in nombres
    assert "respuesta" not in nombres
    assert {"contexto_recuperado", "modo_llm"}.issubset(nombres)