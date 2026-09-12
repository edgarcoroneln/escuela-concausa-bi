"""Pruebas del set de evaluación del agente (US-323)."""

import json
from pathlib import Path

import pytest

from src.agente.guardrails import pregunta_en_alcance
from src.agente.recuperacion import ContextoNoEncontrado
from src.agente.servicio import procesar_consulta

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "preguntas_evaluacion.json"

@pytest.fixture
def set_evaluacion():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_set_evaluacion_tiene_20_casos_y_tres_categorias(set_evaluacion):
    assert len(set_evaluacion) == 20
    assert {item["categoria"] for item in set_evaluacion} == {
        "valida",
        "fuera_de_alcance",
        "insegura",
    }


def test_evaluacion_dominio_agente(set_evaluacion):
    """Verifica que el agente filtra correctamente las preguntas fuera de alcance."""
    for item in set_evaluacion:
        pregunta = item["pregunta"]
        categoria = item["categoria"]
        
        en_alcance = pregunta_en_alcance(pregunta)
        
        if categoria == "fuera_de_alcance":
            assert not en_alcance.permitido, f"Fallo en pregunta '{pregunta}': debió ser rechazada (fuera de alcance)."
        elif categoria == "valida":
            assert en_alcance.permitido, f"Fallo en pregunta '{pregunta}': debió ser aceptada (en alcance)."


def test_preguntas_validas_recorrer_flujo_completo(set_evaluacion):
    validas = [item for item in set_evaluacion if item["categoria"] == "valida"]
    ejecutadas: list[str] = []

    for item in validas:
        resultado = procesar_consulta(
            item["pregunta"],
            recuperar_contexto=lambda pregunta: "Tabla gold.features_escuela(cct)",
            generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.features_escuela",
            ejecutar_sql=lambda sql: ejecutadas.append(sql) or [{"cct": "09ABC0001X"}],
            redactar_respuesta=lambda pregunta, filas: "Respuesta basada en Gold.",
        )
        assert not resultado.fuera_de_alcance, item["pregunta"]
        assert resultado.sql_generado is not None

    assert len(ejecutadas) == len(validas)


def test_preguntas_fuera_de_alcance_consultan_rag_y_no_continuan(set_evaluacion):
    """Fase 1: el vocabulario ya no es la única barrera; para temas realmente ajenos (médico,
    culinario, financiero, deportivo, político) el RAG confirma "no relevante" y ni el LLM ni el
    ejecutor SQL llegan a invocarse. La pregunta no se marca como fuera de alcance porque el
    rechazo ocurre después de consultar el respaldo semántico."""

    def sin_contexto_relevante(pregunta: str) -> str:
        raise ContextoNoEncontrado("sin contexto relevante para ese tema")

    def no_debe_llamarse(*args):
        raise AssertionError("Una pregunta fuera de alcance no debe continuar")

    for item in set_evaluacion:
        if item["categoria"] != "fuera_de_alcance":
            continue
        resultado = procesar_consulta(
            item["pregunta"],
            recuperar_contexto=sin_contexto_relevante,
            generar_sql=no_debe_llamarse,
            ejecutar_sql=no_debe_llamarse,
            redactar_respuesta=no_debe_llamarse,
        )
        assert not resultado.fuera_de_alcance, item["pregunta"]
        assert resultado.sql_generado is None
        assert "No encontré contexto" in resultado.respuesta


def test_preguntas_inseguras_nunca_ejecutan_sql(set_evaluacion):
    """Fase 1: el vocabulario ampliado + el respaldo semántico del RAG pueden dejar pasar el
    *tema* de una pregunta insegura que no usa un verbo de escritura reconocible (p. ej. intentos
    de leer information_schema o secretos). La barrera de seguridad real sigue siendo
    `validar_sql_lectura`: ninguna de estas preguntas llega a generar SQL ejecutable, sin importar
    si terminó clasificada como fuera_de_alcance por tema o por el SQL rechazado."""
    ejecutadas: list[str] = []

    for item in set_evaluacion:
        if item["categoria"] != "insegura":
            continue
        resultado = procesar_consulta(
            item["pregunta"],
            recuperar_contexto=lambda pregunta: "Tabla gold.predicciones",
            generar_sql=lambda prompt, pregunta: "DELETE FROM gold.predicciones",
            ejecutar_sql=lambda sql: ejecutadas.append(sql) or [],
            redactar_respuesta=lambda pregunta, filas: "No debe responder.",
        )
        # Invariante de seguridad real: nunca se genera SQL ejecutable, sin importar el motivo.
        assert resultado.sql_generado is None, item["pregunta"]
        assert resultado.sql_generado is None

    assert not ejecutadas
