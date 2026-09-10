"""Pruebas del endpoint `/agente/consulta` conectado al servicio RAG real (BUG-025, US-304a/305).

Cubren que el endpoint ya NO es el stub: aplica los guardarraíles reales, nunca ejecuta SQL
destructivo y expone el seam de inyección para que la Célula 3 enchufe su LLM/ejecutor.

Offline: no requieren ChromaDB ni LLM. El recuperador de contexto se sustituye por dependency
override; los casos fuera de alcance y de degradación no lo necesitan siquiera.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.api.app import API_PREFIX, app
from src.api.v1 import agente as agente_mod
from src.agente.recuperacion import ContextoNoEncontrado

# Respuesta fija del stub anterior (BUG-025): no debe volver a aparecer nunca.
_RESPUESTA_STUB_VIEJO = "En el alcance actual hay 4 escuelas; 2 superan el umbral de riesgo (0.5)."


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _post(client: TestClient, pregunta: str) -> dict:
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": pregunta})
    assert r.status_code == 200, r.text
    return r.json()


def test_pregunta_fuera_de_alcance_se_rechaza(client: TestClient) -> None:
    """Una pregunta ajena al dominio se marca fuera_de_alcance (guardarraíl NL real).

    Fase 1 (puerta híbrida): el vocabulario no reconoce el tema, así que se intenta el respaldo
    semántico del RAG antes de rechazar. Para un tema realmente ajeno, el RAG confirma "no
    relevante" (`ContextoNoEncontrado`); sin este override usaría el RAG real (sin ChromaDB en
    CI) y fallaría con `ErrorRecuperacion` (servicio caído), un caso distinto y no lo que prueba
    este test.
    """
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: (_ for _ in ()).throw(ContextoNoEncontrado("sin contexto relevante"))
    )

    cuerpo = _post(client, "¿cuál es la capital de Francia?")
    assert cuerpo["fuera_de_alcance"] is True
    assert cuerpo["sql_generado"] is None


def test_no_devuelve_la_respuesta_hardcodeada_del_stub(client: TestClient) -> None:
    """En alcance pero sin LLM configurado: degrada seguro, nunca la respuesta fija del stub."""
    cuerpo = _post(client, "¿cuántas escuelas hay en riesgo?")
    assert cuerpo["respuesta"] != _RESPUESTA_STUB_VIEJO


def test_sql_destructivo_generado_nunca_se_ejecuta(client: TestClient) -> None:
    """Núcleo de BUG-025: la pregunta es de lectura y pasa el filtro NL, pero si el LLM devolviera
    un DELETE el guardarraíl **de SQL** lo bloquea y el ejecutor jamás se llama.

    La pregunta debe ser legítima a propósito: así ejercita el validador de SQL (no el filtro de
    intención de P-13, que se prueba aparte en `test_orden_de_escritura_se_corta_en_el_filtro_nl`).
    """
    llamadas_ejecutor: list[str] = []

    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.predicciones(cct, indice_riesgo)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: "DELETE FROM gold.predicciones"
    )
    app.dependency_overrides[agente_mod.get_ejecutar_sql] = lambda: (
        lambda sql: llamadas_ejecutor.append(sql) or []
    )
    app.dependency_overrides[agente_mod.get_redactar_respuesta] = lambda: (
        lambda pregunta, filas: "no debería llegar aquí"
    )

    cuerpo = _post(client, "¿cuántas escuelas hay en riesgo por inseguridad?")
    assert cuerpo["fuera_de_alcance"] is False
    assert cuerpo["sql_generado"] is None
    assert llamadas_ejecutor == []  # el ejecutor NUNCA se invocó


def test_orden_de_escritura_se_corta_en_el_filtro_nl(client: TestClient) -> None:
    """P-13 (defensa en profundidad): una orden destructiva se rechaza en el filtro de preguntas,
    ANTES de invocar al LLM — no depende del validador de SQL."""
    llamadas_generar: list[str] = []

    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: llamadas_generar.append(pregunta) or "SELECT cct FROM gold.x"
    )

    cuerpo = _post(client, "borra la tabla de predicciones de escuelas")
    assert cuerpo["fuera_de_alcance"] is True
    assert cuerpo["sql_generado"] is None
    assert llamadas_generar == []  # el LLM nunca se invocó: cortó el filtro NL


def test_happy_path_por_el_seam_di(client: TestClient) -> None:
    """El seam completo funciona: recuperar → generar SELECT → ejecutar → redactar → contrato."""
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.features_escuela(cct)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: "SELECT cct FROM gold.features_escuela"
    )
    app.dependency_overrides[agente_mod.get_ejecutar_sql] = lambda: (
        lambda sql: [{"cct": "09ABC0001X"}]
    )
    app.dependency_overrides[agente_mod.get_redactar_respuesta] = lambda: (
        lambda pregunta, filas: f"{len(filas)} escuela encontrada."
    )

    cuerpo = _post(client, "¿cuántas escuelas hay?")
    assert cuerpo["fuera_de_alcance"] is False
    assert cuerpo["respuesta"] == "1 escuela encontrada."
    assert cuerpo["sql_generado"].lower().startswith("select cct from gold.features_escuela")


def test_falla_interna_degrada_sin_filtrar_detalle(client: TestClient) -> None:
    """Si una colaboración revienta con la pregunta en alcance, se devuelve mensaje genérico."""
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.features_escuela(cct)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: (_ for _ in ()).throw(RuntimeError("boom interno con secreto"))
    )

    cuerpo = _post(client, "escuelas en riesgo por municipio")
    assert cuerpo["fuera_de_alcance"] is False
    assert "boom" not in cuerpo["respuesta"].lower()
    assert "secreto" not in cuerpo["respuesta"].lower()
