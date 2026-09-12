"""Agente conversacional `/agente/*` (§3.5) — conectado al servicio RAG real (BUG-025).

El endpoint delega en `procesar_consulta_con_rag()` de la Célula 3 (`src/agente/servicio.py`), que
aplica los guardarraíles reales (`pregunta_en_alcance` + `preparar_sql_seguro`): rechaza preguntas
fuera de alcance y **garantiza que solo puede generarse/ejecutarse SQL de solo lectura sobre Gold**.
Esto sustituye al stub que respondía lo mismo a todo (incluida la frase destructiva más obvia).

**Seam de inyección (para Célula 3 / Andrés):** las tres colaboraciones que el servicio necesita
—`generar_sql` (LLM text-to-SQL), `ejecutar_sql` (ejecutor read-only sobre Gold) y
`redactar_respuesta` (LLM redactor)— se proveen por dependencias de FastAPI. Sus defaults degradan de
forma **segura** ("no configurado") para que la app arranque y el CI corra sin LLM ni ChromaDB;
Andrés (y C5 en despliegue) las sobreescriben con `app.dependency_overrides` / implementaciones reales.

Cualquier fallo interno del servicio se traduce a un mensaje genérico (sin filtrar detalle) — la
respuesta pública nunca expone trazas, prompts ni SQL crudo de error.

**`/consulta/stream` (US-305, PR #313 del frontend):** misma lógica servida como *Server-Sent
Events*, con *streaming* real token a token del redactor final (`procesar_consulta_stream`,
`src/agente/servicio.py`) -- no un trozado artificial de una respuesta ya completa. Comparte
`_preparar_para_redaccion` (mismos guardarraíles) con `/consulta` a través de `servicio.py` — ver
los docstrings de `_resolver_consulta`/`_resolver_consulta_stream`.
"""
from __future__ import annotations

import json
import logging
from collections.abc import Iterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.agente.recuperacion import recuperar_contexto as _recuperar_contexto_rag
from src.agente.servicio import (
    EjecutarSQL,
    GenerarSQL,
    RecuperarContexto,
    RedactarRespuesta,
    RedactarRespuestaStream,
    ResultadoConsulta,
    ResultadoConsultaStream,
    procesar_consulta,
    procesar_consulta_stream,
)
from src.api.schemas import AgenteConsultaIn, AgenteRespuestaOut

router = APIRouter(prefix="/agente", tags=["Agente"])

# Logging estructurado (Fase 4, plan 2026-09-09): solo para el catch-all de última línea de
# defensa -- los casos ya distinguidos (guardarraíl, SQL rechazado, LLM caído en cada etapa) se
# registran más cerca de la causa, en `src/agente/servicio.py`.
_logger = logging.getLogger("faro.api.agente")

#: Tamaño de cada fragmento del evento `fragmento` cuando la respuesta ya viene resuelta como
#: texto fijo (mensajes de guardarraíl/degradación, nunca del redactor real -- ese sí transmite
#: sus propios fragmentos token a token vía `procesar_consulta_stream`).
TAM_FRAGMENTO_SSE = 80

# Mensaje seguro cuando el motor RAG/LLM no está configurado o falla en este entorno.
_MSG_NO_DISPONIBLE = (
    "El agente no está disponible en este entorno todavía. Intenta más tarde o consulta los "
    "tableros."
)


class AgenteNoConfigurado(RuntimeError):
    """Una colaboración del agente (LLM/ejecutor) no está configurada en este entorno."""


def _construir_contexto_conversacional(body: AgenteConsultaIn) -> dict | None:
    """Arma el `Mapping` que espera `procesar_consulta`, con `contexto` e `historial` fusionados.

    `procesar_consulta` (Célula 3, `src/agente/servicio.py`) ya acepta un único parámetro
    `contexto_conversacional: Mapping[str, object] | None`. En vez de pedirle a C3 una firma
    nueva, el `historial` de turnos (rediseño del chat, 2026-09-10) viaja bajo la clave
    `"historial"` de ese mismo mapping — `construir_prompt_sistema` deberá leerla igual que ya
    lee `ccts`/`ciclo`/`filtros`/`resumen` (coordinado con Andrés, C3).

    Devuelve `None` cuando no hay ni `contexto` ni `historial`, para no romper la
    retrocompatibilidad de un cuerpo sin ninguno de los dos.
    """
    contexto = body.contexto.model_dump() if body.contexto else {}
    if body.historial:
        contexto["historial"] = [turno.model_dump() for turno in body.historial]
    return contexto or None


# --------------------------------------------------------------------------- #
# Proveedores inyectables (defaults seguros; C3/Andrés y C5 los sobreescriben)
# --------------------------------------------------------------------------- #


def get_recuperar_contexto() -> RecuperarContexto:
    """Recuperador de contexto. Default: RAG ChromaDB de US-304b (degrada solo si falta la lib)."""
    return _recuperar_contexto_rag


def get_generar_sql() -> GenerarSQL:
    """LLM text-to-SQL (Célula 3). Sin configurar por defecto."""

    def _no_configurado(prompt: str, pregunta: str) -> str:
        raise AgenteNoConfigurado("generar_sql no está configurado (pendiente Célula 3).")

    return _no_configurado


def get_ejecutar_sql() -> EjecutarSQL:
    """Ejecutor read-only del SQL ya validado sobre Gold. Sin configurar por defecto (US-404)."""

    def _no_configurado(sql: str):  # noqa: ANN202 - firma del Callable EjecutarSQL
        raise AgenteNoConfigurado("ejecutar_sql no está configurado (pendiente C4/US-404 + C5).")

    return _no_configurado


def get_redactar_respuesta() -> RedactarRespuesta:
    """LLM redactor de la respuesta final (Célula 3). Sin configurar por defecto."""

    def _no_configurado(pregunta: str, filas) -> str:  # noqa: ANN001 - firma del Callable
        raise AgenteNoConfigurado("redactar_respuesta no está configurado (pendiente Célula 3).")

    return _no_configurado


def get_redactar_respuesta_stream() -> RedactarRespuestaStream:
    """LLM redactor en streaming (Célula 3, Fase 3). Sin configurar por defecto."""

    def _no_configurado(pregunta: str, filas):  # noqa: ANN001 - firma del Callable
        raise AgenteNoConfigurado(
            "redactar_respuesta_stream no está configurado (pendiente Célula 3)."
        )

    return _no_configurado


def _resolver_consulta(
    body: AgenteConsultaIn,
    recuperar_contexto: RecuperarContexto,
    generar_sql: GenerarSQL,
    ejecutar_sql: EjecutarSQL,
    redactar_respuesta: RedactarRespuesta,
) -> ResultadoConsulta:
    """Corre `procesar_consulta` con degradación segura (BUG-025): nunca filtra detalle interno.

    Único punto de guardarraíles del agente para el endpoint síncrono; su contraparte en streaming
    es `_resolver_consulta_stream`, y ambas delegan en las mismas funciones de `servicio.py`
    (`_preparar_para_redaccion` es compartida) para que el streaming **nunca** sea una segunda
    puerta con reglas distintas.

    Este `except Exception` es el último recurso: los fallos ya identificables por fase (RAG caído,
    SQL rechazado, LLM caído en cada etapa) se distinguen y registran más cerca de la causa, en
    `servicio.py`. Si algo llega hasta aquí es porque no encajó en ningún caso ya conocido -- se
    registra igual, porque un catch-all silencioso es tan malo como un mensaje genérico.
    """
    try:
        return procesar_consulta(
            body.pregunta,
            recuperar_contexto=recuperar_contexto,
            generar_sql=generar_sql,
            ejecutar_sql=ejecutar_sql,
            redactar_respuesta=redactar_respuesta,
            contexto_conversacional=_construir_contexto_conversacional(body),
        )
    except Exception:  # noqa: BLE001 - degradación segura: nunca filtrar detalle interno al cliente
        _logger.exception("agente.fallo_no_clasificado")
        return ResultadoConsulta(
            respuesta=_MSG_NO_DISPONIBLE, sql_generado=None, fuera_de_alcance=False
        )


def _resolver_consulta_stream(
    body: AgenteConsultaIn,
    recuperar_contexto: RecuperarContexto,
    generar_sql: GenerarSQL,
    ejecutar_sql: EjecutarSQL,
    redactar_respuesta_stream: RedactarRespuestaStream,
) -> ResultadoConsultaStream:
    """Igual que `_resolver_consulta`, pero para la variante en streaming.

    Solo cubre la fase síncrona (guardarraíles + RAG + SQL, que `procesar_consulta_stream` ya
    resuelve antes de devolver algo). Un fallo del redactor **durante** la transmisión de
    fragmentos no pasa por aquí -- ocurre más tarde, dentro del propio generador, y ese caso ya lo
    degrada `servicio.py::procesar_consulta_stream` sin dejar el stream vacío.
    """
    try:
        return procesar_consulta_stream(
            body.pregunta,
            recuperar_contexto=recuperar_contexto,
            generar_sql=generar_sql,
            ejecutar_sql=ejecutar_sql,
            redactar_respuesta_stream=redactar_respuesta_stream,
            contexto_conversacional=_construir_contexto_conversacional(body),
        )
    except Exception:  # noqa: BLE001 - degradación segura: nunca filtrar detalle interno al cliente
        _logger.exception("agente.fallo_no_clasificado_stream")
        return ResultadoConsultaStream(
            fragmentos=None,
            respuesta_fija=_MSG_NO_DISPONIBLE,
            sql_generado=None,
            fuera_de_alcance=False,
        )


@router.post("/consulta", response_model=AgenteRespuestaOut)
def consulta(
    body: AgenteConsultaIn,
    recuperar_contexto: RecuperarContexto = Depends(get_recuperar_contexto),
    generar_sql: GenerarSQL = Depends(get_generar_sql),
    ejecutar_sql: EjecutarSQL = Depends(get_ejecutar_sql),
    redactar_respuesta: RedactarRespuesta = Depends(get_redactar_respuesta),
) -> AgenteRespuestaOut:
    """Consulta en lenguaje natural sobre Gold (rol mínimo: ciudadano).

    Aplica los guardarraíles reales del agente. Equivale a `procesar_consulta_con_rag()` con el
    recuperador inyectable, de modo que Andrés (C3) pueda enchufar su LLM/ejecutor por dependencias.

    **`contexto` (opcional, US-305)** permite resolver preguntas de seguimiento —*"¿y las
    recomendaciones para **esas** escuelas?"*— sin que el LLM invente CCTs. Es opcional y
    retrocompatible: un cuerpo sin `contexto` se comporta exactamente como antes.

    El contexto lo manda el cliente, así que **se valida como entrada hostil, no como estado de
    confianza** (`ContextoConversacionalIn`): forma de los CCT, cotas de tamaño, sin caracteres de
    control, y `extra="forbid"` para que no se pueda colar un `sql` por esta puerta. Ver el
    docstring del esquema. Lo que llega al servicio de C3 es siempre un objeto ya validado.

    **`historial` (opcional, rediseño del chat 2026-09-10)** son los turnos previos de la
    conversación (pregunta/respuesta), tal como los guarda el widget. Igual que `contexto`, es
    opcional, retrocompatible y se valida como entrada hostil (`HistorialTurnoIn`): acotado en
    cantidad de turnos y en tamaño por turno, sin caracteres de control.
    """
    resultado = _resolver_consulta(
        body, recuperar_contexto, generar_sql, ejecutar_sql, redactar_respuesta
    )
    return AgenteRespuestaOut(
        respuesta=resultado.respuesta,
        sql_generado=resultado.sql_generado,
        fuera_de_alcance=resultado.fuera_de_alcance,
    )


def _evento_sse(evento: str, data: dict) -> str:
    """Formatea un evento SSE (`event: <tipo>\\ndata: <json>\\n\\n`)."""
    return f"event: {evento}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _fragmentar(texto: str, tam: int = TAM_FRAGMENTO_SSE) -> Iterator[str]:
    """Trocea `texto` en fragmentos de a lo más `tam` caracteres, en orden.

    Siempre produce **al menos un** fragmento, incluso con `texto == ""`: el cliente ya mergeado
    (`consultar_agente_stream` en `src/frontend/agente_client.py`, PR #313) trata una lista de
    fragmentos vacía como stream inválido (`if not fragmentos: raise ValueError(...)`) -- `range()`
    solo no lo garantizaría para un texto vacío.
    """
    if not texto:
        yield texto
        return
    for inicio in range(0, len(texto), tam):
        yield texto[inicio : inicio + tam]


def _generar_eventos_sse(resultado: ResultadoConsultaStream) -> Iterator[str]:
    """Arma la secuencia `meta` → `fragmento`+ → `fin` a partir de un `ResultadoConsultaStream`.

    `meta` va primero y trae `sql_generado`/`fuera_de_alcance` completos (US-305): el cliente los
    necesita para decidir el trato de la respuesta (p. ej. mostrar el SQL auditable) sin esperar al
    último fragmento.

    Dos orígenes posibles para los `fragmento`, indistinguibles para el cliente SSE (que solo ve
    texto):
    - `resultado.fragmentos` ya viene poblado (pregunta resuelta hasta la redacción): son
      fragmentos **reales** del LLM, token a token, tal como los cede
      `procesar_consulta_stream` -- se reenvían tal cual, sin trocear de nuevo.
    - `resultado.fragmentos is None` (la pregunta se resolvió antes de llegar a redactar: rechazo
      de guardarraíl, SQL rechazado, degradación): `respuesta_fija` es un mensaje ya fijo, que se
      trocea con `_fragmentar` solo para mantener la misma cadencia de eventos incrementales.
    """
    yield _evento_sse(
        "meta",
        {"sql_generado": resultado.sql_generado, "fuera_de_alcance": resultado.fuera_de_alcance},
    )
    if resultado.fragmentos is not None:
        for fragmento in resultado.fragmentos:
            yield _evento_sse("fragmento", {"texto": fragmento})
    else:
        for fragmento in _fragmentar(resultado.respuesta_fija or ""):
            yield _evento_sse("fragmento", {"texto": fragmento})
    yield _evento_sse("fin", {})


@router.post(
    "/consulta/stream",
    summary="Consulta en lenguaje natural, servida como Server-Sent Events",
    responses={
        200: {
            "description": (
                "Stream SSE con eventos `meta` (una vez, con sql_generado/fuera_de_alcance), "
                "`fragmento` (0 o más, con un trozo de la respuesta) y `fin` (una vez, cierre)."
            ),
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
def consulta_stream(
    body: AgenteConsultaIn,
    recuperar_contexto: RecuperarContexto = Depends(get_recuperar_contexto),
    generar_sql: GenerarSQL = Depends(get_generar_sql),
    ejecutar_sql: EjecutarSQL = Depends(get_ejecutar_sql),
    redactar_respuesta_stream: RedactarRespuestaStream = Depends(get_redactar_respuesta_stream),
) -> StreamingResponse:
    """Igual que `POST /agente/consulta`, pero como *Server-Sent Events* con streaming real (US-305).

    Mismo contrato de entrada (`AgenteConsultaIn`: `pregunta`, `contexto`, `historial`) y **los
    mismos guardarraíles** -- este endpoint no es una segunda puerta: `_resolver_consulta_stream`
    llama a `procesar_consulta_stream`, que comparte `_preparar_para_redaccion` con la función que
    usa `/consulta` (`procesar_consulta`), así que el filtro de intención (P-13), la validación de
    SQL de solo lectura (`preparar_sql_seguro`) y la degradación segura ante fallas son idénticos.
    La autenticación (`Authorization: Bearer`) y el interruptor híbrido de lectura pública también
    se heredan igual: se aplican por router en `src/api/v1/__init__.py` (`require_lectura`), y este
    endpoint vive en el mismo `router` que `/consulta`.

    La etapa final (redacción) sí transmite en *streaming* real, token a token, según los va
    cediendo el LLM (`redactar_respuesta_stream_con_llm`, `src/agente/llm.py`) -- la generación y
    ejecución de SQL no se transmiten (un SQL a medias no sirve de nada), solo la redacción.
    Cuando la pregunta se resuelve antes de llegar a esa etapa (rechazo de guardarraíl, SQL
    rechazado, degradación), `_generar_eventos_sse` trocea el mensaje fijo en `TAM_FRAGMENTO_SSE`
    caracteres para mantener la misma cadencia incremental.
    """
    resultado = _resolver_consulta_stream(
        body, recuperar_contexto, generar_sql, ejecutar_sql, redactar_respuesta_stream
    )
    return StreamingResponse(
        _generar_eventos_sse(resultado),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
