"""Orquestación segura e inyectable del agente FARO (US-304a)."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any
import re

from src.agente.guardrails import pregunta_en_alcance, preparar_sql_seguro
from src.agente.prompt import construir_prompt_sistema
from src.agente.recuperacion import (
    ContextoNoEncontrado,
    ErrorRecuperacion,
    recuperar_contexto,
)

RecuperarContexto = Callable[[str], str]
GenerarSQL = Callable[[str, str], str]
EjecutarSQL = Callable[[str], Sequence[Mapping[str, Any]]]
RedactarRespuesta = Callable[[str, Sequence[Mapping[str, Any]]], str]
PREGUNTA_REFERENCIAL = re.compile(
    r"\b(estas|esas|los anteriores|las anteriores|ese grupo|esa lista|sus recomendaciones)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ResultadoConsulta:
    """Resultado interno alineado con el contrato público del agente."""

    respuesta: str
    sql_generado: str | None
    fuera_de_alcance: bool


def procesar_consulta(
    pregunta: str,
    recuperar_contexto: RecuperarContexto,
    generar_sql: GenerarSQL,
    ejecutar_sql: EjecutarSQL,
    redactar_respuesta: RedactarRespuesta,
    contexto_conversacional: Mapping[str, object] | None = None,
) -> ResultadoConsulta:
    """Procesa una pregunta sin acoplarse a RAG, LLM, base de datos ni API."""
    alcance = pregunta_en_alcance(pregunta)
    if not alcance.permitido:
        return ResultadoConsulta(
            respuesta=alcance.razon or "Pregunta fuera del alcance de FARO.",
            sql_generado=None,
            fuera_de_alcance=True,
        )
    if PREGUNTA_REFERENCIAL.search(pregunta) and not contexto_conversacional:
        return ResultadoConsulta(
            respuesta=(
                "Necesito el contexto de la consulta anterior. Indica las escuelas, CCT o ciclo "
                "a los que te refieres."
            ),
            sql_generado=None,
            fuera_de_alcance=False,
        )

    try:
        contexto = recuperar_contexto(pregunta)
    except ContextoNoEncontrado:
        return ResultadoConsulta(
            respuesta="No encontré contexto de Gold para responder esa pregunta.",
            sql_generado=None,
            fuera_de_alcance=False,
        )
    except ErrorRecuperacion:
        return ResultadoConsulta(
            respuesta="El contexto de FARO no está disponible temporalmente.",
            sql_generado=None,
            fuera_de_alcance=False,
        )
    prompt = construir_prompt_sistema(contexto, contexto_conversacional)
    try:
        sql_seguro = preparar_sql_seguro(generar_sql(prompt, pregunta))
    except ValueError as exc:
        return ResultadoConsulta(
            respuesta=f"La consulta generada fue rechazada: {exc}",
            sql_generado=None,
            fuera_de_alcance=True,
        )

    filas = ejecutar_sql(sql_seguro)
    return ResultadoConsulta(
        respuesta=redactar_respuesta(pregunta, filas),
        sql_generado=sql_seguro,
        fuera_de_alcance=False,
    )


def procesar_consulta_con_rag(
    pregunta: str,
    generar_sql: GenerarSQL,
    ejecutar_sql: EjecutarSQL,
    redactar_respuesta: RedactarRespuesta,
    contexto_conversacional: Mapping[str, object] | None = None,
) -> ResultadoConsulta:
    """Procesa una pregunta usando la recuperación ChromaDB de US-304b."""
    return procesar_consulta(
        pregunta,
        recuperar_contexto=recuperar_contexto,
        generar_sql=generar_sql,
        ejecutar_sql=ejecutar_sql,
        redactar_respuesta=redactar_respuesta,
        contexto_conversacional=contexto_conversacional,
    )