"""Pruebas del endpoint `/agente/consulta` conectado al servicio RAG real (BUG-025, US-304a/305).

Cubren que el endpoint ya NO es el stub: aplica los guardarraíles reales, nunca ejecuta SQL
destructivo y expone el seam de inyección para que la Célula 3 enchufe su LLM/ejecutor.

Offline: no requieren ChromaDB ni LLM. El recuperador de contexto se sustituye por dependency
override; los casos fuera de alcance y de degradación no lo necesitan siquiera.

También cubre `/agente/consulta/stream` (US-305): mismo servicio, guardarraíles y overrides,
servido como Server-Sent Events para el widget de chat (PR #313 del frontend).
"""
from __future__ import annotations

import re
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


def _parsear_eventos_sse(cuerpo: str) -> list[tuple[str, dict]]:
    """Parsea un cuerpo `text/event-stream` en `[(evento, data_json), ...]`, en orden."""
    import json

    eventos = []
    for bloque in cuerpo.split("\n\n"):
        bloque = bloque.strip()
        if not bloque:
            continue
        m_evento = re.search(r"^event: (.+)$", bloque, re.MULTILINE)
        m_data = re.search(r"^data: (.+)$", bloque, re.MULTILINE)
        assert m_evento and m_data, f"bloque SSE mal formado: {bloque!r}"
        eventos.append((m_evento.group(1), json.loads(m_data.group(1))))
    return eventos


def _post_stream(client: TestClient, pregunta: str) -> list[tuple[str, dict]]:
    r = client.post(f"{API_PREFIX}/agente/consulta/stream", json={"pregunta": pregunta})
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("text/event-stream")
    return _parsear_eventos_sse(r.text)


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


# --------------------------------------------------------------------------- #
# `/agente/consulta/stream` (US-305, SSE) -- mismo servicio, guardarraíles y overrides que arriba,
# solo cambia el transporte. No se repite la matriz completa de guardarraíles (ya cubierta arriba);
# aquí solo se prueba que el streaming respeta el mismo contrato de guardarraíles y el formato SSE.
# --------------------------------------------------------------------------- #


def test_stream_happy_path_emite_meta_fragmentos_y_fin(client: TestClient) -> None:
    """El streaming completo: `meta` primero (con sql_generado/fuera_de_alcance), luego los
    fragmentos de la respuesta en orden, y `fin` al final."""
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

    eventos = _post_stream(client, "¿cuántas escuelas hay?")

    assert eventos[0][0] == "meta"
    assert eventos[-1][0] == "fin"
    assert all(e in {"meta", "fragmento", "fin"} for e, _ in eventos)

    _, meta = eventos[0]
    assert meta["fuera_de_alcance"] is False
    assert meta["sql_generado"].lower().startswith("select cct from gold.features_escuela")

    fragmentos = [d["texto"] for e, d in eventos if e == "fragmento"]
    assert "".join(fragmentos) == "1 escuela encontrada."


def test_stream_pregunta_fuera_de_alcance_se_rechaza_igual_que_el_sincrono(
    client: TestClient,
) -> None:
    """Mismo guardarraíl que `/consulta`: una pregunta ajena se marca `fuera_de_alcance` en `meta`."""
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: (_ for _ in ()).throw(ContextoNoEncontrado("sin contexto relevante"))
    )

    eventos = _post_stream(client, "¿cuál es la capital de Francia?")

    _, meta = eventos[0]
    assert meta["fuera_de_alcance"] is True
    assert meta["sql_generado"] is None


def test_stream_sql_destructivo_generado_nunca_se_ejecuta(client: TestClient) -> None:
    """Núcleo de BUG-025 también en el streaming: el ejecutor nunca se llama con un SQL destructivo."""
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

    eventos = _post_stream(client, "¿cuántas escuelas hay en riesgo por inseguridad?")

    _, meta = eventos[0]
    assert meta["fuera_de_alcance"] is False
    assert meta["sql_generado"] is None
    assert llamadas_ejecutor == []


def test_stream_falla_interna_degrada_sin_filtrar_detalle(client: TestClient) -> None:
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.features_escuela(cct)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: (_ for _ in ()).throw(RuntimeError("boom interno con secreto"))
    )

    eventos = _post_stream(client, "escuelas en riesgo por municipio")

    fragmentos = "".join(d["texto"] for e, d in eventos if e == "fragmento")
    assert "boom" not in fragmentos.lower()
    assert "secreto" not in fragmentos.lower()


def test_stream_fragmenta_respuestas_largas(client: TestClient) -> None:
    """Una respuesta más larga que `TAM_FRAGMENTO_SSE` se parte en más de un evento `fragmento`."""
    respuesta_larga = "Escuela en riesgo. " * 20  # > 80 caracteres (TAM_FRAGMENTO_SSE)
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.features_escuela(cct)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: "SELECT cct FROM gold.features_escuela"
    )
    app.dependency_overrides[agente_mod.get_ejecutar_sql] = lambda: (lambda sql: [{"cct": "x"}])
    app.dependency_overrides[agente_mod.get_redactar_respuesta] = lambda: (
        lambda pregunta, filas: respuesta_larga
    )

    eventos = _post_stream(client, "¿cuántas escuelas hay?")

    fragmentos = [d["texto"] for e, d in eventos if e == "fragmento"]
    assert len(fragmentos) > 1
    assert all(len(f) <= agente_mod.TAM_FRAGMENTO_SSE for f in fragmentos)
    assert "".join(fragmentos) == respuesta_larga


def test_stream_integra_con_el_cliente_real_del_frontend(client: TestClient) -> None:
    """Regresión de contrato: `consultar_agente_stream` (PR #313, `src/frontend/agente_client.py`)
    ya está en `main` y consume esta ruta -- si el formato SSE del servidor y el parser del
    cliente se desincronizan, esta prueba lo detecta sin depender de una demo manual.
    """
    from src.frontend.agente_client import consultar_agente_stream

    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.features_escuela(cct)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: "SELECT cct FROM gold.features_escuela"
    )
    app.dependency_overrides[agente_mod.get_ejecutar_sql] = lambda: (
        lambda sql: [{"cct": "09ABC0001X"}, {"cct": "09ABC0002X"}]
    )
    app.dependency_overrides[agente_mod.get_redactar_respuesta] = lambda: (
        lambda pregunta, filas: f"{len(filas)} escuelas encontradas."
    )

    fragmentos_incrementales: list[str] = []
    resultado = consultar_agente_stream(
        api_base_url="",
        pregunta="¿cuántas escuelas hay?",
        stream=client.stream,
        post=client.post,
        on_fragment=fragmentos_incrementales.append,
    )

    assert resultado.respuesta == "2 escuelas encontradas."
    assert resultado.fuera_de_alcance is False
    assert resultado.sql_generado.lower().startswith("select cct from gold.features_escuela")
    assert fragmentos_incrementales  # el cliente sí recibió al menos un fragmento incremental
