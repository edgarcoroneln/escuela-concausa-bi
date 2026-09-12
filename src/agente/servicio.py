"""Orquestación segura e inyectable del agente FARO (US-304a)."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from src.agente.guardrails import (
    RAZON_SOLO_LECTURA,
    pregunta_en_alcance,
    preparar_sql_seguro,
)
from src.agente.prompt import NO_SQL_NECESARIO, construir_prompt_sistema
from src.agente.recuperacion import (
    ContextoNoEncontrado,
    ErrorRecuperacion,
    recuperar_contexto,
)

# Logging estructurado (Fase 4, plan 2026-09-09): registra rechazos de guardarraíl y errores del
# LLM para diagnosticar problemas antes de que los vea el profesor. Nunca incluye la pregunta
# cruda del usuario ni SQL generado en texto plano -- solo motivos ya curados (los mismos que ya
# se consideran seguros para el cliente) y longitudes/conteos. El *sink* real (Cloud Logging) es
# de Alejandro; aquí solo se emite el registro con `logging` estándar.
_logger = logging.getLogger("faro.agente.servicio")

#: Mensaje seguro cuando la etapa final de redacción falla (LLM caído o timeout tras generar/
#: ejecutar el SQL con éxito). Distinto del mensaje de "no configurado" (`AgenteNoConfigurado`,
#: `src/api/v1/agente.py`): aquí sí había una colaboración configurada y sí llegó a intentarse,
#: solo falló en tiempo de ejecución -- por eso invita a reintentar en vez de sugerir que el
#: entorno no está listo.
MSG_ERROR_REDACCION = "No pude redactar la respuesta final; intenta de nuevo en unos segundos."

RecuperarContexto = Callable[[str], str]
GenerarSQL = Callable[[str, str], str]
EjecutarSQL = Callable[[str], Sequence[Mapping[str, Any]]]
RedactarRespuesta = Callable[[str, Sequence[Mapping[str, Any]]], str]
# Fase 3 (streaming, plan 2026-09-09): la generación de SQL no se transmite en streaming útil al
# usuario (un SQL a medias no sirve de nada); solo la redacción final cede texto según llega.
RedactarRespuestaStream = Callable[[str, Sequence[Mapping[str, Any]]], Iterator[str]]
PREGUNTA_REFERENCIAL = re.compile(
    r"\b(estas|esas|los anteriores|las anteriores|ese grupo|esa lista|sus recomendaciones)\b",
    re.IGNORECASE,
)

# Reintentos de auto-corrección (Fase 1, plan 2026-09-09): si el SQL ya validado falla al
# ejecutarse (columna/tabla mal referenciada, etc.), se le devuelve el error al LLM para que
# regenere una versión corregida, acotado para no disparar costo/latencia sin límite.
MAX_REINTENTOS_SQL = 1


@dataclass(frozen=True)
class ResultadoConsulta:
    """Resultado interno alineado con el contrato público del agente."""

    respuesta: str
    sql_generado: str | None
    fuera_de_alcance: bool


@dataclass(frozen=True)
class PreparacionRedaccion:
    """Todo lo necesario para la etapa final de redacción, ya lista para invocarse.

    Es el punto de corte entre "todo lo que decide SI se responde" (guardarraíles, RAG, SQL con
    auto-corrección) y "cómo se entrega el texto final". `filas` ya trae la forma que espera el
    redactor tanto para resultados de SQL como para el caso conceptual sin SQL (`contexto_faro`) —
    la única etapa que Fase 3 transmite en streaming, porque un SQL a medias no sirve de nada.
    """

    pregunta: str
    filas: Sequence[Mapping[str, Any]]
    sql_generado: str | None


@dataclass(frozen=True)
class ResultadoConsultaStream:
    """Resultado en streaming: o hay fragmentos que transmitir, o una respuesta fija ya resuelta.

    `fragmentos` es `None` cuando la pregunta se resolvió sin llegar a la redacción (rechazada o
    degradada) — en ese caso `respuesta_fija` trae el texto completo, igual que `ResultadoConsulta`.
    """

    fragmentos: Iterator[str] | None
    respuesta_fija: str | None
    sql_generado: str | None
    fuera_de_alcance: bool


def _preparacion_sin_sql(pregunta: str, contexto: str) -> PreparacionRedaccion:
    """Fila de contexto conceptual (`NO_SQL_NECESARIO`), ya lista para la etapa de redacción."""
    return PreparacionRedaccion(
        pregunta=pregunta,
        filas=[
            {
                "contexto_faro": contexto,
                "nota": "Respuesta conceptual basada en documentación de FARO, sin consulta SQL.",
            }
        ],
        sql_generado=None,
    )


def _preparar_para_redaccion(
    pregunta: str,
    recuperar_contexto: RecuperarContexto,
    generar_sql: GenerarSQL,
    ejecutar_sql: EjecutarSQL,
    contexto_conversacional: Mapping[str, object] | None = None,
) -> ResultadoConsulta | PreparacionRedaccion:
    """Corre guardarraíles, RAG, generación y ejecución de SQL (con auto-corrección).

    Devuelve un `ResultadoConsulta` ya resuelto si la pregunta se rechaza o falla antes de llegar
    a redactar (fuera de alcance, error de recuperación, SQL rechazado, fallo tras reintentos), o
    una `PreparacionRedaccion` con las filas listas para la llamada final al redactor. Compartida
    por `procesar_consulta` (síncrono) y `procesar_consulta_stream` (Fase 3): los guardarraíles no
    tienen una versión "en streaming", son los mismos para las dos rutas.
    """
    alcance = pregunta_en_alcance(pregunta)
    if not alcance.permitido and alcance.razon == RAZON_SOLO_LECTURA:
        # Intención de escritura: se corta aquí, sin tocar RAG ni LLM (P-13, defensa en profundidad).
        _logger.warning("guardrail.rechazo_escritura")
        return ResultadoConsulta(
            respuesta=alcance.razon,
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

    if not alcance.permitido:
        # El vocabulario no reconoció el tema: antes de rechazar, se le da una segunda oportunidad
        # a la pregunta vía la señal semántica del RAG (Fase 1). No es un hueco de seguridad: la
        # intención de escritura ya se descartó arriba, y el SQL sigue pasando por
        # `preparar_sql_seguro` + el rol read-only pase lo que pase aquí.
        try:
            contexto = recuperar_contexto(pregunta)
        except ContextoNoEncontrado:
            _logger.info("guardrail.rechazo_fuera_de_alcance_semantico")
            return ResultadoConsulta(
                respuesta=alcance.razon or "Pregunta fuera del alcance de FARO.",
                sql_generado=None,
                fuera_de_alcance=True,
            )
        except ErrorRecuperacion:
            _logger.exception("agente.rag_no_disponible")
            return ResultadoConsulta(
                respuesta="El contexto de FARO no está disponible temporalmente.",
                sql_generado=None,
                fuera_de_alcance=False,
            )
    else:
        try:
            contexto = recuperar_contexto(pregunta)
        except ContextoNoEncontrado:
            return ResultadoConsulta(
                respuesta="No encontré contexto de Gold para responder esa pregunta.",
                sql_generado=None,
                fuera_de_alcance=False,
            )
        except ErrorRecuperacion:
            _logger.exception("agente.rag_no_disponible")
            return ResultadoConsulta(
                respuesta="El contexto de FARO no está disponible temporalmente.",
                sql_generado=None,
                fuera_de_alcance=False,
            )

    prompt = construir_prompt_sistema(contexto, contexto_conversacional)
    try:
        sql_crudo = generar_sql(prompt, pregunta)
    except ValueError as exc:
        _logger.warning("llm.sql_rechazado", extra={"motivo": str(exc)})
        return ResultadoConsulta(
            respuesta=f"La consulta generada fue rechazada: {exc}",
            sql_generado=None,
            fuera_de_alcance=False,
        )

    if sql_crudo.strip() == NO_SQL_NECESARIO:
        return _preparacion_sin_sql(pregunta, contexto)

    try:
        sql_actual = preparar_sql_seguro(sql_crudo)
    except ValueError as exc:
        _logger.warning("llm.sql_rechazado", extra={"motivo": str(exc)})
        return ResultadoConsulta(
            respuesta=f"La consulta generada fue rechazada: {exc}",
            sql_generado=None,
            fuera_de_alcance=False,
        )

    intentos = 0
    while True:
        try:
            filas = ejecutar_sql(sql_actual)
            break
        except AssertionError:
            raise  # nunca ocultar fallas de las propias pruebas/scaffolding
        except Exception as exc:
            # SQLAlchemyError envuelto por ejecutor_gold.py; en pruebas, cualquier Exception de
            # prueba); cualquier fallo de ejecución dispara el mismo reintento de auto-corrección.
            intentos += 1
            _logger.warning("agente.sql_no_ejecutable", extra={"intento": intentos}, exc_info=True)
            if intentos > MAX_REINTENTOS_SQL:
                _logger.error("agente.sql_reintentos_agotados", extra={"intentos": intentos})
                return ResultadoConsulta(
                    respuesta=(
                        "No pude construir una consulta que se ejecutara correctamente para esa "
                        "pregunta; intenta reformularla."
                    ),
                    sql_generado=None,
                    fuera_de_alcance=False,
                )
            prompt_reintento = (
                f"{prompt}\n\nTu consulta anterior no se pudo ejecutar (intento {intentos}):\n"
                f"{sql_actual}\n"
                f"Error: {exc}\n"
                "Revisa el esquema (columnas, tablas, filtros de grano/modelo) y genera una "
                "nueva consulta SELECT/WITH corregida sobre gold.*."
            )
            try:
                sql_crudo_reintento = generar_sql(prompt_reintento, pregunta)
            except AssertionError:
                raise
            except Exception:
                # ErrorLLM u otra falla del LLM); si tampoco puede regenerar, se degrada igual.
                _logger.exception("llm.reintento_fallido")
                return ResultadoConsulta(
                    respuesta=(
                        "No pude construir una consulta que se ejecutara correctamente para esa "
                        "pregunta; intenta reformularla."
                    ),
                    sql_generado=None,
                    fuera_de_alcance=False,
                )
            if sql_crudo_reintento.strip() == NO_SQL_NECESARIO:
                return _preparacion_sin_sql(pregunta, contexto)
            try:
                sql_actual = preparar_sql_seguro(sql_crudo_reintento)
            except ValueError as exc2:
                _logger.warning("llm.sql_rechazado", extra={"motivo": str(exc2)})
                return ResultadoConsulta(
                    respuesta=f"La consulta generada fue rechazada: {exc2}",
                    sql_generado=None,
                    fuera_de_alcance=False,
                )

    return PreparacionRedaccion(pregunta=pregunta, filas=filas, sql_generado=sql_actual)


def procesar_consulta(
    pregunta: str,
    recuperar_contexto: RecuperarContexto,
    generar_sql: GenerarSQL,
    ejecutar_sql: EjecutarSQL,
    redactar_respuesta: RedactarRespuesta,
    contexto_conversacional: Mapping[str, object] | None = None,
) -> ResultadoConsulta:
    """Procesa una pregunta sin acoplarse a RAG, LLM, base de datos ni API."""
    preparacion = _preparar_para_redaccion(
        pregunta, recuperar_contexto, generar_sql, ejecutar_sql, contexto_conversacional
    )
    if isinstance(preparacion, ResultadoConsulta):
        return preparacion
    try:
        respuesta = redactar_respuesta(preparacion.pregunta, preparacion.filas)
    except AssertionError:
        raise  # nunca ocultar fallas de las propias pruebas/scaffolding
    except Exception:
        # u otra falla del LLM en la etapa final; distinta de "no configurado" -- aquí sí hubo un
        # intento real, así que el mensaje invita a reintentar en vez de señalar el entorno.
        _logger.exception("llm.redaccion_fallida")
        return ResultadoConsulta(respuesta=MSG_ERROR_REDACCION, sql_generado=None, fuera_de_alcance=False)
    return ResultadoConsulta(
        respuesta=respuesta,
        sql_generado=preparacion.sql_generado,
        fuera_de_alcance=False,
    )


def procesar_consulta_stream(
    pregunta: str,
    recuperar_contexto: RecuperarContexto,
    generar_sql: GenerarSQL,
    ejecutar_sql: EjecutarSQL,
    redactar_respuesta_stream: RedactarRespuestaStream,
    contexto_conversacional: Mapping[str, object] | None = None,
) -> ResultadoConsultaStream:
    """Igual que `procesar_consulta`, pero la redacción final se transmite en fragmentos (Fase 3).

    Los guardarraíles, el RAG y la generación/ejecución de SQL corren igual de estrictos y de
    forma síncrona antes de devolver algo — lo único que cambia es la última llamada.
    `redactar_respuesta_stream(...)` se invoca aquí (para que la firma sea simétrica con
    `procesar_consulta`), pero si es una función generadora, su cuerpo no ejecuta nada (ninguna
    llamada de red al LLM) hasta que quien reciba `fragmentos` empiece a iterarlo.
    """
    preparacion = _preparar_para_redaccion(
        pregunta, recuperar_contexto, generar_sql, ejecutar_sql, contexto_conversacional
    )
    if isinstance(preparacion, ResultadoConsulta):
        return ResultadoConsultaStream(
            fragmentos=None,
            respuesta_fija=preparacion.respuesta,
            sql_generado=preparacion.sql_generado,
            fuera_de_alcance=preparacion.fuera_de_alcance,
        )

    def iterar_redaccion() -> Iterator[str]:
        """Cede fragmentos reales; si el LLM falla, degrada sin dejar el stream vacío.

        Con contenido ya emitido, un fallo a media generación simplemente detiene el stream (el
        cliente se queda con la respuesta parcial real, igual que cualquier chat que se corta a
        medio párrafo) -- agregar un mensaje de error DESPUÉS de texto real produciría una
        oración partida y confusa. Sin nada emitido todavía, sí hace falta un fragmento de
        respaldo: un stream vacío viola el contrato que ya exige el cliente (PR #313,
        `consultar_agente_stream`: `if not fragmentos: raise ValueError(...)`).
        """
        emitio_contenido = False
        try:
            for fragmento in redactar_respuesta_stream(preparacion.pregunta, preparacion.filas):
                emitio_contenido = True
                yield fragmento
        except AssertionError:
            raise
        except Exception:
            _logger.exception("llm.redaccion_stream_fallida")
            if not emitio_contenido:
                yield MSG_ERROR_REDACCION

    return ResultadoConsultaStream(
        fragmentos=iterar_redaccion(),
        respuesta_fija=None,
        sql_generado=preparacion.sql_generado,
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


def procesar_consulta_con_rag_stream(
    pregunta: str,
    generar_sql: GenerarSQL,
    ejecutar_sql: EjecutarSQL,
    redactar_respuesta_stream: RedactarRespuestaStream,
    contexto_conversacional: Mapping[str, object] | None = None,
) -> ResultadoConsultaStream:
    """Versión en streaming de `procesar_consulta_con_rag` (Fase 3)."""
    return procesar_consulta_stream(
        pregunta,
        recuperar_contexto=recuperar_contexto,
        generar_sql=generar_sql,
        ejecutar_sql=ejecutar_sql,
        redactar_respuesta_stream=redactar_respuesta_stream,
        contexto_conversacional=contexto_conversacional,
    )
