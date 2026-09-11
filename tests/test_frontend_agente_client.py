"""Pruebas del cliente HTTP del widget de chat (US-305)."""

from __future__ import annotations

import httpx
import pytest

from src.frontend.agente_client import (
    ErrorAutorizacionAgente,
    consultar_agente,
    consultar_agente_stream,
)


class RespuestaHTTPFake:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


def test_consulta_el_endpoint_con_el_contrato_canonico() -> None:
    def post(url: str, **kwargs) -> RespuestaHTTPFake:
        assert url == "http://api:8000/api/v1/agente/consulta"
        assert kwargs["json"] == {"pregunta": "Cuantas escuelas hay?"}
        assert kwargs["headers"] is None
        assert kwargs["timeout"] == 15.0
        return RespuestaHTTPFake(
            {
                "respuesta": "Hay cuatro escuelas.",
                "sql_generado": "SELECT count(*) FROM gold.dim_escuela",
                "fuera_de_alcance": False,
            }
        )

    respuesta = consultar_agente(
        "http://api:8000/",
        " Cuantas escuelas hay? ",
        post=post,
    )

    assert respuesta.respuesta == "Hay cuatro escuelas."
    assert respuesta.sql_generado == "SELECT count(*) FROM gold.dim_escuela"
    assert not respuesta.fuera_de_alcance


def test_propaga_access_token_como_bearer() -> None:
    def post(url: str, **kwargs) -> RespuestaHTTPFake:
        assert kwargs["headers"] == {"Authorization": "Bearer jwt-prueba"}
        return RespuestaHTTPFake(
            {
                "respuesta": "Respuesta autenticada.",
                "sql_generado": None,
                "fuera_de_alcance": False,
            }
        )

    respuesta = consultar_agente(
        "http://api:8000",
        "Pregunta autenticada",
        post=post,
        access_token="jwt-prueba",
    )

    assert respuesta.respuesta == "Respuesta autenticada."


@pytest.mark.parametrize("pregunta", ["x", "x" * 501])
def test_rechaza_preguntas_fuera_del_tamano_del_contrato(pregunta: str) -> None:
    with pytest.raises(ValueError, match="entre 3 y 500"):
        consultar_agente("http://api:8000", pregunta)


@pytest.mark.parametrize(
    "payload",
    [
        {"respuesta": "Incompleta"},
        {"respuesta": None, "sql_generado": None, "fuera_de_alcance": False},
        {"respuesta": "Texto", "sql_generado": 42, "fuera_de_alcance": False},
        {"respuesta": "Texto", "sql_generado": None, "fuera_de_alcance": "false"},
    ],
)
def test_rechaza_una_respuesta_con_contrato_invalido(payload: dict) -> None:
    def post(*args, **kwargs) -> RespuestaHTTPFake:
        return RespuestaHTTPFake(payload)

    with pytest.raises(ValueError, match="respuesta de agente inválida"):
        consultar_agente("http://api:8000", "Pregunta valida", post=post)


def test_convierte_un_error_http_en_error_de_conexion() -> None:
    def post(*args, **kwargs) -> RespuestaHTTPFake:
        request = httpx.Request("POST", "http://api:8000/api/v1/agente/consulta")
        raise httpx.ConnectError("sin conexión", request=request)

    with pytest.raises(ConnectionError, match="API del agente no está disponible"):
        consultar_agente("http://api:8000", "Pregunta valida", post=post)


@pytest.mark.parametrize(
    ("status_code", "mensaje"),
    [
        (401, "sesión no es válida o expiró"),
        (403, "rol no tiene permiso"),
    ],
)
def test_distingue_errores_de_autorizacion(status_code: int, mensaje: str) -> None:
    def post(*args, **kwargs) -> RespuestaHTTPFake:
        request = httpx.Request("POST", "http://api:8000/api/v1/agente/consulta")
        response = httpx.Response(status_code, request=request)
        raise httpx.HTTPStatusError("rechazada", request=request, response=response)

    with pytest.raises(ErrorAutorizacionAgente, match=mensaje):
        consultar_agente("http://api:8000", "Pregunta valida", post=post)


def test_consulta_stream_parsea_meta_fragmentos_y_fin() -> None:
    class RespuestaStreamFake:
        def __init__(self) -> None:
            self._lineas = [
                b"event: meta",
                b'data: {"sql_generado":"SELECT 1","fuera_de_alcance":false}',
                b"",
                b"event: fragmento",
                b'data: {"texto":"1 escuela "}',
                b"event: fragmento",
                b'data: {"texto":"encontrada."}',
                b"event: fin",
                b"data: {}",
            ]

        def raise_for_status(self) -> None:
            return None

        def iter_lines(self):
            return iter(self._lineas)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback) -> None:
            return None

    fragmentos: list[str] = []

    def stream(method: str, url: str, **kwargs) -> RespuestaStreamFake:
        assert method == "POST"
        assert url == "http://api:8000/api/v1/agente/consulta/stream"
        assert kwargs["json"] == {"pregunta": "Cuantas escuelas hay?"}
        assert kwargs["timeout"] == 15.0
        return RespuestaStreamFake()

    respuesta = consultar_agente_stream(
        "http://api:8000/",
        " Cuantas escuelas hay? ",
        stream=stream,
        on_fragment=lambda texto: fragmentos.append(texto),
    )

    assert respuesta.respuesta == "1 escuela encontrada."
    assert respuesta.sql_generado == "SELECT 1"
    assert respuesta.fuera_de_alcance is False
    assert fragmentos == ["1 escuela ", "encontrada."]