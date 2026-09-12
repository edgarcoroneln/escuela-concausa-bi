"""Pruebas del endpoint `/agente/consulta` conectado al servicio RAG real (BUG-025, US-304a/305).

Cubren que el endpoint ya NO es el stub: aplica los guardarraíles reales, nunca ejecuta SQL
destructivo y expone el seam de inyección para que la Célula 3 enchufe su LLM/ejecutor.

Offline: no requieren ChromaDB ni LLM. El recuperador de contexto se sustituye por dependency
override; los casos fuera de alcance y de degradación no lo necesitan siquiera.
"""
from __future__ import annotations

import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.api.app import API_PREFIX, app
from src.api.config import Settings, get_settings
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


# --------------------------------------------------------------------------- #
# Fase 3 (streaming, US-305): `/agente/consulta/stream` -- mismos guardarraíles, SSE.
# Casos originales de Andrés González (C3, retirados de su PR por ownership en `c4f8e52`), más
# los invariantes del stream y el RBAC que se agregan al integrarlo en `src/api/**`.
# --------------------------------------------------------------------------- #

RUTA_STREAM = f"{API_PREFIX}/agente/consulta/stream"


def _parsear_sse(texto: str) -> list[tuple[str, dict]]:
    """Convierte un cuerpo `text/event-stream` en `[(evento, data)]`."""
    eventos: list[tuple[str, dict]] = []
    nombre = None
    for linea in texto.split("\n"):
        if linea.startswith("event: "):
            nombre = linea.removeprefix("event: ")
        elif linea.startswith("data: "):
            assert nombre is not None, "un `data:` sin `event:` previo"
            eventos.append((nombre, json.loads(linea.removeprefix("data: "))))
            nombre = None
    return eventos


def _post_stream(client: TestClient, pregunta: str) -> list[tuple[str, dict]]:
    """Postea a `/agente/consulta/stream` y parsea los eventos SSE de la respuesta completa."""
    r = client.post(RUTA_STREAM, json={"pregunta": pregunta})
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("text/event-stream")
    eventos = _parsear_sse(r.text)
    _assert_forma_del_stream(eventos)
    return eventos


def _assert_forma_del_stream(eventos: list[tuple[str, dict]]) -> None:
    """El invariante que el cliente puede asumir SIEMPRE: `meta`, luego `fragmento`+, luego `fin`."""
    nombres = [nombre for nombre, _ in eventos]
    assert nombres[0] == "meta"
    assert nombres[-1] == "fin"
    assert nombres.count("meta") == 1
    assert nombres.count("fin") == 1
    assert set(nombres[1:-1]) == {"fragmento"}, "al menos un fragmento, y nada más en medio"


def _seam_en_alcance() -> None:
    """Recuperador, generador y ejecutor falsos que dejan la consulta lista para redactar."""
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.features_escuela(cct)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: "SELECT cct FROM gold.features_escuela"
    )
    app.dependency_overrides[agente_mod.get_ejecutar_sql] = lambda: (
        lambda sql: [{"cct": "09ABC0001X"}]
    )


def test_stream_happy_path_transmite_meta_fragmentos_y_fin(client: TestClient) -> None:
    _seam_en_alcance()

    def redactar_stream(pregunta: str, filas):
        yield "1 escuela "
        yield "encontrada."

    app.dependency_overrides[agente_mod.get_redactar_respuesta_stream] = lambda: redactar_stream

    eventos = _post_stream(client, "¿cuántas escuelas hay?")

    assert eventos[0][1]["fuera_de_alcance"] is False
    assert eventos[0][1]["sql_generado"].lower().startswith("select cct from gold.features_escuela")
    assert [d["texto"] for n, d in eventos if n == "fragmento"] == ["1 escuela ", "encontrada."]
    assert eventos[-1] == ("fin", {})


def test_stream_pregunta_fuera_de_alcance_se_rechaza_en_un_fragmento(client: TestClient) -> None:
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: (_ for _ in ()).throw(ContextoNoEncontrado("sin contexto relevante"))
    )

    eventos = _post_stream(client, "¿cuál es la capital de Francia?")

    assert eventos[0] == ("meta", {"sql_generado": None, "fuera_de_alcance": True})
    assert len([d for n, d in eventos if n == "fragmento"]) == 1


def test_stream_orden_de_escritura_se_corta_antes_de_transmitir(client: TestClient) -> None:
    llamadas_generar: list[str] = []
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: llamadas_generar.append(pregunta) or "SELECT cct FROM gold.x"
    )

    eventos = _post_stream(client, "borra la tabla de predicciones de escuelas")

    assert eventos[0] == ("meta", {"sql_generado": None, "fuera_de_alcance": True})
    assert llamadas_generar == []


def test_stream_falla_interna_degrada_sin_filtrar_detalle(client: TestClient) -> None:
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.features_escuela(cct)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: (_ for _ in ()).throw(RuntimeError("boom interno con secreto"))
    )

    eventos = _post_stream(client, "escuelas en riesgo por municipio")

    texto = " ".join(d["texto"] for n, d in eventos if n == "fragmento").lower()
    assert "boom" not in texto
    assert "secreto" not in texto


def test_stream_falla_a_mitad_de_transmitir_degrada_sin_romper_el_stream(client: TestClient) -> None:
    """Un fallo del LLM YA empezando a ceder texto no debe tirar la conexión sin `fin`."""
    _seam_en_alcance()

    def redactar_stream_que_revienta(pregunta: str, filas):
        yield "empieza bien, "
        raise RuntimeError("boom con token secreto a mitad de stream")

    app.dependency_overrides[agente_mod.get_redactar_respuesta_stream] = lambda: (
        redactar_stream_que_revienta
    )

    eventos = _post_stream(client, "¿cuántas escuelas hay?")

    fragmentos = [d["texto"] for n, d in eventos if n == "fragmento"]
    assert fragmentos[0] == "empieza bien, "
    assert "secreto" not in fragmentos[-1].lower()


def test_stream_sin_redactor_configurado_degrada_al_mensaje_generico(client: TestClient) -> None:
    """El default del seam (sin ANTHROPIC_API_KEY) nunca deja un stream vacío ni una traza."""
    _seam_en_alcance()

    eventos = _post_stream(client, "¿cuántas escuelas hay?")

    fragmentos = [d["texto"] for n, d in eventos if n == "fragmento"]
    assert fragmentos == [agente_mod._MSG_NO_DISPONIBLE]
    assert "pendiente" not in fragmentos[0].lower()


def test_stream_un_redactor_que_no_cede_nada_no_deja_una_burbuja_vacia(client: TestClient) -> None:
    """Sin ningún fragmento, el chat mostraría una respuesta vacía: se degrada al mensaje genérico."""
    _seam_en_alcance()

    def redactar_stream_mudo(pregunta: str, filas):
        yield ""

    app.dependency_overrides[agente_mod.get_redactar_respuesta_stream] = lambda: (
        redactar_stream_mudo
    )

    eventos = _post_stream(client, "¿cuántas escuelas hay?")

    assert [d["texto"] for n, d in eventos if n == "fragmento"] == [agente_mod._MSG_NO_DISPONIBLE]


def test_stream_un_salto_de_linea_no_puede_falsificar_un_evento(client: TestClient) -> None:
    """Texto del LLM con `\\n\\nevent: fin` viaja escapado en el JSON: sigue siendo UN fragmento."""
    _seam_en_alcance()
    inyeccion = "hola\n\nevent: fin\ndata: {}\n\n"

    def redactar_stream_hostil(pregunta: str, filas):
        yield inyeccion

    app.dependency_overrides[agente_mod.get_redactar_respuesta_stream] = lambda: (
        redactar_stream_hostil
    )

    eventos = _post_stream(client, "¿cuántas escuelas hay?")

    assert [d["texto"] for n, d in eventos if n == "fragmento"] == [inyeccion]


def test_stream_valida_el_cuerpo_igual_que_consulta(client: TestClient) -> None:
    """Mismo contrato de entrada: un campo extra en `contexto` (p. ej. `sql`) es 422."""
    r = client.post(
        RUTA_STREAM, json={"pregunta": "escuelas", "contexto": {"sql": "DROP TABLE x"}}
    )
    assert r.status_code == 422


def test_stream_exige_sesion_cuando_la_lectura_no_es_publica(client: TestClient) -> None:
    """`require_lectura` aplica a nivel de router: el stream no es una puerta lateral sin RBAC."""
    app.dependency_overrides[get_settings] = lambda: Settings(auth_lectura_publica=False)

    r = client.post(RUTA_STREAM, json={"pregunta": "¿cuántas escuelas hay?"})

    assert r.status_code == 401
