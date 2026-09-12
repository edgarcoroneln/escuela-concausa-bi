"""Pruebas offline del adaptador Anthropic del agente FARO."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Self

import pytest

from src.agente.llm import (
    ErrorLLM,
    generar_sql_con_llm,
    redactar_respuesta_con_llm,
    redactar_respuesta_stream_con_llm,
)


class MensajesFake:
    def __init__(self, contenido: str | Exception) -> None:
        self.contenido = contenido
        self.llamadas: list[dict] = []

    def create(self, **parametros):
        self.llamadas.append(parametros)
        if isinstance(self.contenido, Exception):
            raise self.contenido
        return SimpleNamespace(
            stop_reason="end_turn",
            content=[SimpleNamespace(type="text", text=self.contenido)],
        )


def _cliente(contenido: str | Exception) -> SimpleNamespace:
    return SimpleNamespace(messages=MensajesFake(contenido))


class _StreamContextoFake:
    """Imita el context manager que devuelve `cliente.messages.stream(...)`."""

    def __init__(self, textos: list[str], stop_reason: str = "end_turn") -> None:
        self._textos = textos
        self._stop_reason = stop_reason

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    @property
    def text_stream(self):
        return iter(self._textos)

    def get_final_message(self) -> SimpleNamespace:
        return SimpleNamespace(stop_reason=self._stop_reason)


class MensajesStreamFake:
    def __init__(self, textos_o_excepcion: list[str] | Exception, stop_reason: str = "end_turn") -> None:
        self.textos_o_excepcion = textos_o_excepcion
        self.stop_reason = stop_reason
        self.llamadas: list[dict] = []

    def stream(self, **parametros):
        self.llamadas.append(parametros)
        if isinstance(self.textos_o_excepcion, Exception):
            raise self.textos_o_excepcion
        return _StreamContextoFake(self.textos_o_excepcion, self.stop_reason)


def _cliente_stream(textos: list[str] | Exception, stop_reason: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(messages=MensajesStreamFake(textos, stop_reason))


def test_generar_sql_usa_salida_estructurada_y_configuracion(monkeypatch) -> None:
    monkeypatch.setenv("AGENTE_MODELO", "claude-sonnet-5")
    monkeypatch.setenv("AGENTE_MAX_TOKENS", "2048")
    monkeypatch.setenv("AGENTE_TIMEOUT_S", "30")
    cliente = _cliente('{"sql":"SELECT cct FROM gold.dim_escuela"}')

    sql = generar_sql_con_llm("Solo lectura sobre gold.", "Cuantas escuelas hay?", cliente=cliente)

    assert sql == "SELECT cct FROM gold.dim_escuela"
    assert len(cliente.messages.llamadas) == 1
    parametros = cliente.messages.llamadas[0]
    assert parametros["model"] == "claude-sonnet-5"
    assert parametros["max_tokens"] == 2048
    assert parametros["system"] == "Solo lectura sobre gold."
    assert parametros["output_config"]["format"]["schema"]["required"] == ["sql"]


def test_redactar_respuesta_serializa_filas_sin_ascii_forzado() -> None:
    cliente = _cliente('{"respuesta":"Se encontraron 2 escuelas en Mérida."}')

    respuesta = redactar_respuesta_con_llm(
        "Cuantas escuelas hay en Merida?",
        [{"municipio": "Mérida", "total": 2}],
        cliente=cliente,
    )

    assert respuesta == "Se encontraron 2 escuelas en Mérida."
    mensaje = cliente.messages.llamadas[0]["messages"][0]["content"]
    assert '"municipio":"Mérida"' in mensaje
    assert "datos no confiables" in mensaje


def test_redactar_respuesta_colapsa_saltos_de_linea_y_tabs() -> None:
    """La respuesta puede reenviarse tal cual como turno de `historial` (HistorialTurnoIn
    rechaza caracteres de control, US-305/US-611): no puede traer saltos de línea ni tabs."""
    cliente = _cliente('{"respuesta":"Escuela A\\n- Escuela B\\r\\n\\tEscuela C"}')

    respuesta = redactar_respuesta_con_llm("Que escuelas hay?", [], cliente=cliente)

    assert respuesta == "Escuela A - Escuela B Escuela C"
    assert respuesta.isprintable()


def test_fallo_del_sdk_no_reintenta_ni_filtra_detalle() -> None:
    cliente = _cliente(RuntimeError("token secreto expuesto"))

    with pytest.raises(ErrorLLM) as error:
        generar_sql_con_llm("Solo lectura.", "Escuelas en riesgo?", cliente=cliente)

    assert len(cliente.messages.llamadas) == 1
    assert "secreto" not in str(error.value).lower()


@pytest.mark.parametrize("contenido", ['{"sql":""}', "[]", "sin json"])
def test_generar_sql_rechaza_salida_invalida(contenido: str) -> None:
    with pytest.raises(ErrorLLM):
        generar_sql_con_llm("Solo lectura.", "Escuelas en riesgo?", cliente=_cliente(contenido))


def test_rechaza_configuracion_invalida_antes_de_llamar(monkeypatch) -> None:
    monkeypatch.setenv("AGENTE_MAX_TOKENS", "cero")
    cliente = _cliente('{"sql":"SELECT 1"}')

    with pytest.raises(ErrorLLM, match="configuracion"):
        generar_sql_con_llm("Solo lectura.", "Escuelas en riesgo?", cliente=cliente)

    assert cliente.messages.llamadas == []


# --------------------------------------------------------------------------- #
# Fase 3: redactor en streaming
# --------------------------------------------------------------------------- #


def test_redactar_respuesta_stream_cede_fragmentos_normalizados() -> None:
    cliente = _cliente_stream(["Escuela A\n", "- Escuela B\r\n\t", "Escuela C"])

    fragmentos = list(
        redactar_respuesta_stream_con_llm(
            "Que escuelas hay?", [{"municipio": "Mérida"}], cliente=cliente
        )
    )

    assert fragmentos == ["Escuela A ", "- Escuela B ", "Escuela C"]
    assert "".join(fragmentos).isprintable()
    mensaje = cliente.messages.llamadas[0]["messages"][0]["content"]
    assert '"municipio":"Mérida"' in mensaje
    # La variante en streaming no pide salida estructurada (un JSON a medias no sirve de nada).
    assert "output_config" not in cliente.messages.llamadas[0]


def test_redactar_respuesta_stream_no_llama_a_la_red_hasta_iterarse() -> None:
    """Es un generador: crear el iterador no debe disparar la llamada al SDK todavía."""
    cliente = _cliente_stream(["hola"])

    generador = redactar_respuesta_stream_con_llm("Que escuelas hay?", [], cliente=cliente)

    assert cliente.messages.llamadas == []
    next(generador)
    assert len(cliente.messages.llamadas) == 1


def test_redactar_respuesta_stream_pregunta_vacia_lanza_value_error() -> None:
    generador = redactar_respuesta_stream_con_llm("   ", [])
    with pytest.raises(ValueError):
        next(generador)


@pytest.mark.parametrize("stop_reason", ["refusal", "max_tokens"])
def test_redactar_respuesta_stream_rechaza_stop_reason_invalido(stop_reason: str) -> None:
    cliente = _cliente_stream(["texto parcial"], stop_reason=stop_reason)

    with pytest.raises(ErrorLLM):
        list(redactar_respuesta_stream_con_llm("Que escuelas hay?", [], cliente=cliente))


def test_redactar_respuesta_stream_sin_contenido_lanza_error() -> None:
    cliente = _cliente_stream([])

    with pytest.raises(ErrorLLM):
        list(redactar_respuesta_stream_con_llm("Que escuelas hay?", [], cliente=cliente))


def test_redactar_respuesta_stream_fallo_del_sdk_no_filtra_detalle() -> None:
    cliente = _cliente_stream(RuntimeError("token secreto expuesto"))

    with pytest.raises(ErrorLLM) as error:
        list(redactar_respuesta_stream_con_llm("Que escuelas hay?", [], cliente=cliente))

    assert "secreto" not in str(error.value).lower()