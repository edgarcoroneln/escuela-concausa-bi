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
respuesta pública nunca expone trazas, prompts ni SQL crudo de error. **Dos mensajes genéricos, no
uno** (Fase 4, Karla Monter): *"no está disponible"* cuando una colaboración no está configurada en
este entorno, y *"no se pudo completar"* cuando sí lo está y falló en ejecución. Para la persona son
situaciones distintas —esperar vs. reintentar— y para nosotros también: el segundo caso es un
incidente y el primero es la configuración esperada del CI. Ningún mensaje cambia según el error
concreto, así que la distinción no filtra nada.

**Observabilidad (Fase 4).** Los rechazos y los fallos se registran con `logging` estructurado
(`extra`), no con texto interpolado, para poder filtrarlos en Cloud Logging. **Nunca se registra la
pregunta ni el contexto**: son texto de la persona y el proyecto es privacidad por diseño; se
registran la etapa, el tipo de excepción y las banderas del resultado.

**`POST /agente/consulta/stream` (US-305, Fase 3).** Misma orquestación, mismos guardarraíles y mismo
contrato de entrada que `/consulta`; lo único distinto es que la redacción final viaja por
Server-Sent Events en vez de esperar el texto completo. La implementación es de Andrés González (C3),
que la retiró de su PR por ownership (`c4f8e52`); se integra aquí, en el alcance de `src/api/**`.
Ver `procesar_consulta_stream` en `src/agente/servicio.py` para el porqué: generar el SQL no produce
nada útil a medias, así que solo se transmite la última etapa.
"""
from __future__ import annotations

import json
import logging
from collections.abc import Iterator, Mapping

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.agente.recuperacion import recuperar_contexto as _recuperar_contexto_rag
from src.agente.servicio import (
    EjecutarSQL,
    GenerarSQL,
    RecuperarContexto,
    RedactarRespuesta,
    RedactarRespuestaStream,
    procesar_consulta,
    procesar_consulta_stream,
)
from src.api.schemas import AgenteConsultaIn, AgenteRespuestaOut

router = APIRouter(prefix="/agente", tags=["Agente"])

logger = logging.getLogger(__name__)

# Mensaje seguro cuando una colaboración del agente **no está configurada** en este entorno
# (sin `ANTHROPIC_API_KEY`, sin DSN read-only): no hay nada que reintentar.
_MSG_NO_DISPONIBLE = (
    "El agente no está disponible en este entorno todavía. Intenta más tarde o consulta los "
    "tableros."
)

# Mensaje seguro cuando el motor **sí está configurado** y falló en ejecución (timeout del LLM,
# corte de red, SQL rechazado por el guardarraíl). Aquí reintentar sí tiene sentido, y por eso el
# texto es distinto: decirle "no está disponible" a alguien que puede reintentar es información
# falsa. Es genérico igual que el otro -- no cambia según el error, así que no filtra detalle.
_MSG_FALLO_TEMPORAL = (
    "No se pudo completar la consulta en este momento. Vuelve a intentarlo en unos segundos."
)

# Cierre cuando el fallo ocurrió **con fragmentos ya transmitidos**: el texto parcial se conserva
# (ya viajó) y esta nota explica por qué se corta, en vez de dejar una frase a medias sin aviso.
_MSG_CORTE_PARCIAL = " […] La respuesta quedó incompleta por un problema al redactarla."


class AgenteNoConfigurado(RuntimeError):
    """Una colaboración del agente (LLM/ejecutor) no está configurada en este entorno."""


def _registrar_fallo(etapa: str, exc: BaseException, *, configurado: bool) -> None:
    """Registra un fallo del agente sin escribir la pregunta ni el contexto (privacidad).

    `extra` en vez de interpolar: en Cloud Logging cada campo queda filtrable, y el mensaje humano
    no se vuelve una cadena distinta por cada error. `exc_info` solo cuando **sí** estaba
    configurado: ahí la traza es un incidente que alguien debe ver; la degradación esperada del CI
    no necesita una traza por petición.
    """
    logger.warning(
        "fallo del agente",
        extra={
            "agente_etapa": etapa,
            "agente_error": type(exc).__name__,
            "agente_configurado": configurado,
        },
        exc_info=configurado,
    )


def _mensaje_de_fallo(exc: BaseException) -> str:
    """Traduce la excepción a uno de los dos mensajes genéricos, sin filtrar su detalle."""
    return _MSG_NO_DISPONIBLE if isinstance(exc, AgenteNoConfigurado) else _MSG_FALLO_TEMPORAL


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
    """LLM redactor en streaming (Fase 3, Célula 3). Sin configurar por defecto."""

    def _no_configurado(pregunta: str, filas):  # noqa: ANN001, ANN202 - firma del Callable
        raise AgenteNoConfigurado("redactar_respuesta_stream no está configurado (pendiente C3).")
        yield  # pragma: no cover - hace de _no_configurado un generador, nunca se alcanza

    return _no_configurado


# --------------------------------------------------------------------------- #
# `/consulta/stream` (Fase 3): framing SSE
# --------------------------------------------------------------------------- #


def _evento_sse(nombre: str, datos: Mapping[str, object]) -> str:
    """Un evento `text/event-stream`: `event: <nombre>` + `data: <json de una sola línea>`.

    `json.dumps` escapa los saltos de línea, así que un `\\n` dentro del texto del LLM nunca puede
    partir el `data:` y falsificar un evento nuevo en el cliente.
    """
    cuerpo = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    return f"event: {nombre}\ndata: {cuerpo}\n\n"


def _cierre_degradado(texto: str) -> Iterator[str]:
    """Un último fragmento con el mensaje genérico y el `fin`: el cliente nunca queda colgado."""
    yield _evento_sse("fragmento", {"texto": texto})
    yield _evento_sse("fin", {})


def _generar_eventos_stream(
    body: AgenteConsultaIn,
    recuperar_contexto: RecuperarContexto,
    generar_sql: GenerarSQL,
    ejecutar_sql: EjecutarSQL,
    redactar_respuesta_stream: RedactarRespuestaStream,
) -> Iterator[str]:
    """Arma los eventos SSE de una consulta: `meta` primero, luego `fragmento`+ y `fin` al final.

    Invariantes que fijan las pruebas: **siempre** hay un `meta` al inicio, **al menos un**
    `fragmento` y un `fin` al final, pase lo que pase. Ningún fallo —guardarraíles, RAG, SQL, o el
    LLM ya a mitad de transmitir— expone una traza ni SQL crudo de error dentro del stream.

    **Fase 4 (Karla Monter):** el mensaje distingue *no configurado* de *falló en ejecución*, y si
    ya se habían transmitido fragmentos, **el texto parcial se conserva** y solo se agrega la nota
    de corte. Volver a mandar el mensaje completo de error borraría de la pantalla lo que la persona
    ya estaba leyendo.
    """
    try:
        resultado = procesar_consulta_stream(
            body.pregunta,
            recuperar_contexto=recuperar_contexto,
            generar_sql=generar_sql,
            ejecutar_sql=ejecutar_sql,
            redactar_respuesta_stream=redactar_respuesta_stream,
            contexto_conversacional=_construir_contexto_conversacional(body),
        )
    except Exception as exc:  # noqa: BLE001 - degradación segura, igual que /consulta
        _registrar_fallo(
            "stream:preparacion", exc, configurado=not isinstance(exc, AgenteNoConfigurado)
        )
        yield _evento_sse("meta", {"sql_generado": None, "fuera_de_alcance": False})
        yield from _cierre_degradado(_mensaje_de_fallo(exc))
        return

    yield _evento_sse(
        "meta",
        {"sql_generado": resultado.sql_generado, "fuera_de_alcance": resultado.fuera_de_alcance},
    )
    if resultado.fragmentos is None:
        # Rechazada o degradada antes de llegar a redactar: un solo fragmento con el texto fijo.
        # Un rechazo del guardarraíl trae su propia explicación y NO es un fallo: no se registra
        # como tal, pero sí se cuenta, que es lo que permite ver si el filtro se pasa de estricto.
        if resultado.fuera_de_alcance:
            logger.info("consulta fuera de alcance", extra={"agente_etapa": "stream:guardarrail"})
        yield _evento_sse("fragmento", {"texto": resultado.respuesta_fija or _MSG_NO_DISPONIBLE})
        yield _evento_sse("fin", {})
        return

    emitidos = 0
    try:
        for fragmento in resultado.fragmentos:
            if fragmento:
                emitidos += 1
                yield _evento_sse("fragmento", {"texto": fragmento})
    except Exception as exc:  # noqa: BLE001 - el LLM puede fallar a mitad de transmitir
        _registrar_fallo(
            "stream:redaccion", exc, configurado=not isinstance(exc, AgenteNoConfigurado)
        )
        # Con texto ya en pantalla se agrega la nota de corte; sin nada emitido, el mensaje entero.
        yield from _cierre_degradado(
            _MSG_CORTE_PARCIAL if emitidos else _mensaje_de_fallo(exc)
        )
        return
    if not emitidos:
        # Un redactor que termina sin ceder nada dejaría una burbuja vacía en el chat.
        logger.warning("el redactor no transmitió nada", extra={"agente_etapa": "stream:redaccion"})
        yield from _cierre_degradado(_MSG_FALLO_TEMPORAL)
        return
    yield _evento_sse("fin", {})


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
    try:
        resultado = procesar_consulta(
            body.pregunta,
            recuperar_contexto=recuperar_contexto,
            generar_sql=generar_sql,
            ejecutar_sql=ejecutar_sql,
            redactar_respuesta=redactar_respuesta,
            contexto_conversacional=_construir_contexto_conversacional(body),
        )
    except Exception as exc:  # noqa: BLE001 - degradación segura: nunca filtrar detalle al cliente
        _registrar_fallo("consulta", exc, configurado=not isinstance(exc, AgenteNoConfigurado))
        return AgenteRespuestaOut(
            respuesta=_mensaje_de_fallo(exc), sql_generado=None, fuera_de_alcance=False
        )
    return AgenteRespuestaOut(
        respuesta=resultado.respuesta,
        sql_generado=resultado.sql_generado,
        fuera_de_alcance=resultado.fuera_de_alcance,
    )


@router.post(
    "/consulta/stream",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": (
                "Server-Sent Events. `meta` una vez al inicio: `{sql_generado, fuera_de_alcance}`; "
                "`fragmento` una o más veces: `{texto}`; `fin` una vez al final: `{}`."
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
    """Igual que `/consulta`, pero transmite la redacción final por Server-Sent Events (Fase 3).

    Mismos guardarraíles, mismo RBAC (`require_lectura`, a nivel de router) y el mismo contrato de
    entrada (`contexto`, `historial`) que `/consulta`; lo único que cambia es cómo viaja la salida.
    Tres tipos de evento, en este orden:

    - `meta` (una vez, al inicio): `{"sql_generado": ..., "fuera_de_alcance": ...}`, los mismos
      campos de `AgenteRespuestaOut`, para que el cliente los tenga sin esperar el fin.
    - `fragmento` (una o más veces): `{"texto": "..."}`, cada pedazo de la respuesta según llega.
    - `fin` (una vez, al final): `{}`. Siempre llega, también cuando algo falló a medio camino.

    `X-Accel-Buffering: no` le pide a nginx que no acumule la respuesta: sin eso, el proxy del
    frontend (ADR-012) entregaría todos los fragmentos juntos al final y el streaming no se notaría.
    """
    return StreamingResponse(
        _generar_eventos_stream(
            body, recuperar_contexto, generar_sql, ejecutar_sql, redactar_respuesta_stream
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
