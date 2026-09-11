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
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.agente.recuperacion import recuperar_contexto as _recuperar_contexto_rag
from src.agente.servicio import (
    EjecutarSQL,
    GenerarSQL,
    RecuperarContexto,
    RedactarRespuesta,
    procesar_consulta,
)
from src.api.schemas import AgenteConsultaIn, AgenteRespuestaOut

router = APIRouter(prefix="/agente", tags=["Agente"])

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
    except Exception:  # noqa: BLE001 - degradación segura: nunca filtrar detalle interno al cliente
        return AgenteRespuestaOut(
            respuesta=_MSG_NO_DISPONIBLE, sql_generado=None, fuera_de_alcance=False
        )
    return AgenteRespuestaOut(
        respuesta=resultado.respuesta,
        sql_generado=resultado.sql_generado,
        fuera_de_alcance=resultado.fuera_de_alcance,
    )
