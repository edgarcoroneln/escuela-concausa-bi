"""Cliente HTTP del agente FARO para el widget de US-305."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class RespuestaAgente:
    """Respuesta estable del contrato `AgenteRespuestaOut`."""

    respuesta: str
    sql_generado: str | None
    fuera_de_alcance: bool


class ErrorAutorizacionAgente(PermissionError):
    """La API rechazó la sesión o el rol del usuario."""


def _validar_pregunta(pregunta: str) -> str:
    texto = pregunta.strip()
    if not 3 <= len(texto) <= 500:
        raise ValueError("La pregunta debe tener entre 3 y 500 caracteres.")
    return texto


def _validar_respuesta_canonica(payload: dict[str, Any]) -> RespuestaAgente:
    try:
        respuesta = payload["respuesta"]
        sql_generado = payload.get("sql_generado")
        fuera_de_alcance = payload["fuera_de_alcance"]
        if not isinstance(respuesta, str):
            raise TypeError
        if sql_generado is not None and not isinstance(sql_generado, str):
            raise TypeError
        if not isinstance(fuera_de_alcance, bool):
            raise TypeError
        return RespuestaAgente(
            respuesta=respuesta,
            sql_generado=sql_generado,
            fuera_de_alcance=fuera_de_alcance,
        )
    except (AttributeError, KeyError, TypeError) as exc:
        raise ValueError("La API devolvió una respuesta de agente inválida.") from exc


def consultar_agente(
    api_base_url: str,
    pregunta: str,
    post: Callable[..., Any] = httpx.post,
    access_token: str | None = None,
) -> RespuestaAgente:
    """Consulta `/api/v1/agente/consulta` y valida su respuesta mínima."""
    texto = _validar_pregunta(pregunta)

    headers = {"Authorization": f"Bearer {access_token}"} if access_token else None

    try:
        response = post(
            f"{api_base_url.rstrip('/')}/api/v1/agente/consulta",
            json={"pregunta": texto},
            headers=headers,
            timeout=15.0,
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise ErrorAutorizacionAgente(
                "La sesión no es válida o expiró; inicia sesión nuevamente."
            ) from exc
        if exc.response.status_code == 403:
            raise ErrorAutorizacionAgente(
                "Tu rol no tiene permiso para consultar el agente."
            ) from exc
        raise ConnectionError("La API del agente rechazó la solicitud.") from exc
    except httpx.HTTPError as exc:
        raise ConnectionError("La API del agente no está disponible.") from exc

    return _validar_respuesta_canonica(payload)


def consultar_agente_stream(
    api_base_url: str,
    pregunta: str,
    stream: Callable[..., Any] = httpx.stream,
    access_token: str | None = None,
    on_fragment: Callable[[str], None] | None = None,
) -> RespuestaAgente:
    """Consulta `/api/v1/agente/consulta/stream` y devuelve la respuesta final con streaming."""
    texto = _validar_pregunta(pregunta)
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else None
    sql_generado: str | None = None
    fuera_de_alcance = False
    fragmentos: list[str] = []
    evento_actual: str | None = None

    try:
        with stream(
            "POST",
            f"{api_base_url.rstrip('/')}/api/v1/agente/consulta/stream",
            json={"pregunta": texto},
            headers=headers,
            timeout=15.0,
        ) as response:
            response.raise_for_status()
            for linea in response.iter_lines():
                if not linea:
                    continue
                if isinstance(linea, bytes):
                    linea = linea.decode("utf-8")
                if linea.startswith("event: "):
                    evento_actual = linea.removeprefix("event: ").strip()
                    continue
                if linea.startswith("data: "):
                    if evento_actual is None:
                        continue
                    cuerpo = linea.removeprefix("data: ").strip()
                    try:
                        payload = json.loads(cuerpo)
                    except json.JSONDecodeError as exc:
                        raise ValueError("La API devolvió un stream de agente inválido.") from exc
                    if evento_actual == "meta":
                        sql_generado = payload.get("sql_generado")
                        fuera_de_alcance = bool(payload.get("fuera_de_alcance", False))
                    elif evento_actual == "fragmento":
                        texto_fragmento = payload.get("texto", "")
                        if not isinstance(texto_fragmento, str):
                            raise TypeError
                        fragmentos.append(texto_fragmento)
                        if on_fragment is not None:
                            on_fragment(texto_fragmento)
                    evento_actual = None
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise ErrorAutorizacionAgente(
                "La sesión no es válida o expiró; inicia sesión nuevamente."
            ) from exc
        if exc.response.status_code == 403:
            raise ErrorAutorizacionAgente(
                "Tu rol no tiene permiso para consultar el agente."
            ) from exc
        raise ConnectionError("La API del agente rechazó la solicitud.") from exc
    except httpx.HTTPError as exc:
        raise ConnectionError("La API del agente no está disponible.") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError("La API devolvió una respuesta de agente inválida.") from exc

    if not fragmentos:
        raise ValueError("La API del agente no devolvió fragmentos en streaming.")

    return RespuestaAgente(
        respuesta="".join(fragmentos),
        sql_generado=sql_generado,
        fuera_de_alcance=fuera_de_alcance,
    )