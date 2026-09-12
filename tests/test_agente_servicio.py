"""Pruebas del flujo seguro de integración del agente FARO."""

from __future__ import annotations

import logging

from src.agente import servicio
from src.agente.recuperacion import ContextoNoEncontrado, ErrorRecuperacion
from src.agente.servicio import (
    MSG_ERROR_REDACCION,
    procesar_consulta,
    procesar_consulta_con_rag,
    procesar_consulta_stream,
)


def test_orquesta_consulta_segura_con_dependencias_inyectadas() -> None:
    llamadas: list[tuple[str, str]] = []

    def recuperar(pregunta: str) -> str:
        llamadas.append(("recuperar", pregunta))
        return "Tabla disponible: gold.features_escuela(cct, indice_riesgo)"

    def generar(prompt: str, pregunta: str) -> str:
        assert "gold.features_escuela" in prompt
        llamadas.append(("generar", pregunta))
        return "SELECT cct FROM gold.features_escuela"

    def ejecutar(sql: str) -> list[dict[str, str]]:
        llamadas.append(("ejecutar", sql))
        return [{"cct": "09ABC0001X"}]

    resultado = procesar_consulta(
        "Que escuelas tienen mayor riesgo?",
        recuperar_contexto=recuperar,
        generar_sql=generar,
        ejecutar_sql=ejecutar,
        redactar_respuesta=lambda pregunta, filas: f"{len(filas)} escuela encontrada.",
    )

    assert resultado.respuesta == "1 escuela encontrada."
    assert resultado.sql_generado == "SELECT cct FROM gold.features_escuela LIMIT 1000;"
    assert not resultado.fuera_de_alcance
    assert [nombre for nombre, _ in llamadas] == ["recuperar", "generar", "ejecutar"]


def test_pregunta_fuera_de_alcance_no_invoca_dependencias() -> None:
    """Fase 1: el vocabulario no reconoce el tema, así que se intenta el respaldo semántico del
    RAG antes de rechazar. Para un tema realmente ajeno, el RAG confirma "no relevante"
    (`ContextoNoEncontrado`) y ni el LLM ni el ejecutor SQL llegan a invocarse."""

    def sin_contexto_relevante(pregunta: str) -> str:
        raise ContextoNoEncontrado("sin contexto relevante para ese tema")

    def no_debe_llamarse(*args):
        raise AssertionError("No se deben invocar el LLM ni la BD para preguntas fuera de alcance")

    resultado = procesar_consulta(
        "Cual es la mejor receta de pasta?",
        recuperar_contexto=sin_contexto_relevante,
        generar_sql=no_debe_llamarse,
        ejecutar_sql=no_debe_llamarse,
        redactar_respuesta=no_debe_llamarse,
    )

    assert resultado.fuera_de_alcance
    assert resultado.sql_generado is None


def test_pregunta_sin_vocabulario_exacto_pasa_por_respaldo_semantico() -> None:
    """Fase 1: una pregunta libre que no toca ninguna palabra de la whitelist, pero que SÍ es del
    dominio, se acepta cuando el RAG encuentra contexto relevante (sin necesidad de redeploy del
    vocabulario para cada sinónimo nuevo)."""
    llamadas: list[str] = []

    def recuperar(pregunta: str) -> str:
        llamadas.append("recuperar")
        return "Tabla gold.predicciones(cct, indice_riesgo)"

    resultado = procesar_consulta(
        "Que colegios corren peligro de quedarse sin inscritos?",
        recuperar_contexto=recuperar,
        generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.predicciones",
        ejecutar_sql=lambda sql: [{"cct": "09ABC0001X"}],
        redactar_respuesta=lambda pregunta, filas: f"{len(filas)} escuela.",
    )

    assert llamadas == ["recuperar"]
    assert not resultado.fuera_de_alcance
    assert resultado.respuesta == "1 escuela."


def test_sql_inseguro_nunca_llega_al_ejecutor() -> None:
    # Pregunta legítima a propósito: pasa el filtro NL para ejercitar el validador de SQL, que es
    # quien corta el DELETE que "genera" el LLM (el corte por intención se prueba aparte).
    ejecutado = False

    def ejecutar(sql: str):
        nonlocal ejecutado
        ejecutado = True
        return []

    resultado = procesar_consulta(
        "Cuantas escuelas tienen mayor riesgo?",
        recuperar_contexto=lambda pregunta: "gold.predicciones",
        generar_sql=lambda prompt, pregunta: "DELETE FROM gold.predicciones",
        ejecutar_sql=ejecutar,
        redactar_respuesta=lambda pregunta, filas: "No debe ejecutarse",
    )

    assert resultado.fuera_de_alcance is False
    assert resultado.sql_generado is None
    assert not ejecutado


def test_sql_invalido_es_fallo_del_sistema_no_fuera_de_alcance() -> None:
    resultado = procesar_consulta(
        "¿Cuántas escuelas hay?",
        recuperar_contexto=lambda pregunta: "gold.predicciones",
        generar_sql=lambda prompt, pregunta: "DELETE FROM gold.predicciones",
        ejecutar_sql=lambda sql: [],
        redactar_respuesta=lambda pregunta, filas: "no debe llamarse",
    )

    assert resultado.fuera_de_alcance is False
    assert resultado.sql_generado is None
    assert "rechazada" in resultado.respuesta


def test_orden_de_escritura_se_corta_antes_de_generar_sql() -> None:
    """P-13: una orden destructiva se detiene en el filtro de intención, sin tocar RAG/LLM/BD."""

    def no_debe_llamarse(*args):
        raise AssertionError("una orden de escritura no debe llegar al LLM ni a la BD")

    resultado = procesar_consulta(
        "borra la tabla de predicciones de escuelas",
        recuperar_contexto=no_debe_llamarse,
        generar_sql=no_debe_llamarse,
        ejecutar_sql=no_debe_llamarse,
        redactar_respuesta=no_debe_llamarse,
    )

    assert resultado.fuera_de_alcance
    assert resultado.sql_generado is None


def test_fallo_de_recuperacion_no_genera_ni_ejecuta_sql() -> None:
    def recuperar(pregunta: str) -> str:
        raise ErrorRecuperacion("ChromaDB no disponible")

    def no_debe_llamarse(*args):
        raise AssertionError("No debe continuar sin contexto RAG")

    resultado = procesar_consulta(
        "Que escuelas tienen mayor riesgo?",
        recuperar_contexto=recuperar,
        generar_sql=no_debe_llamarse,
        ejecutar_sql=no_debe_llamarse,
        redactar_respuesta=no_debe_llamarse,
    )

    assert resultado.respuesta == "El contexto de FARO no está disponible temporalmente."
    assert resultado.sql_generado is None
    assert not resultado.fuera_de_alcance


def test_contexto_no_encontrado_no_se_reporta_como_caida() -> None:
    def recuperar(pregunta: str) -> str:
        raise ContextoNoEncontrado("sin coincidencias")

    def no_debe_llamarse(*args):
        raise AssertionError("No debe continuar sin contexto")

    resultado = procesar_consulta(
        "Que escuelas tienen mayor riesgo?",
        recuperar_contexto=recuperar,
        generar_sql=no_debe_llamarse,
        ejecutar_sql=no_debe_llamarse,
        redactar_respuesta=no_debe_llamarse,
    )

    assert resultado.respuesta == "No encontré contexto de Gold para responder esa pregunta."
    assert resultado.sql_generado is None
    assert not resultado.fuera_de_alcance


def test_pregunta_referencial_sin_contexto_pide_aclaracion() -> None:
    resultado = procesar_consulta(
        "¿Cuáles son las recomendaciones para esas escuelas?",
        recuperar_contexto=lambda pregunta: "no debe llamarse",
        generar_sql=lambda prompt, pregunta: "no debe llamarse",
        ejecutar_sql=lambda sql: [],
        redactar_respuesta=lambda pregunta, filas: "no debe llamarse",
    )

    assert "contexto" in resultado.respuesta.lower()
    assert resultado.sql_generado is None
    assert not resultado.fuera_de_alcance


def test_pregunta_referencial_usa_contexto_estructurado() -> None:
    observado: dict[str, object] = {}

    def generar(prompt: str, pregunta: str) -> str:
        observado["prompt"] = prompt
        return "SELECT cct, recomendacion FROM gold.recomendaciones"

    resultado = procesar_consulta(
        "¿Cuáles son las recomendaciones para esas escuelas?",
        recuperar_contexto=lambda pregunta: "gold.recomendaciones(cct, recomendacion)",
        generar_sql=generar,
        ejecutar_sql=lambda sql: [{"cct": "19ABC0001X", "recomendacion": "seguridad"}],
        redactar_respuesta=lambda pregunta, filas: f"{len(filas)} resultado.",
        contexto_conversacional={
            "ciclo": "2024-2025",
            "ccts": ["19ABC0001X"],
            "resumen": "Una escuela identificada en la consulta anterior",
        },
    )

    assert resultado.sql_generado == (
        "SELECT cct, recomendacion FROM gold.recomendaciones LIMIT 1000;"
    )
    assert "19ABC0001X" in str(observado["prompt"])


def test_entrada_compuesta_usa_recuperacion_rag_real(monkeypatch) -> None:
    monkeypatch.setattr(
        servicio,
        "recuperar_contexto",
        lambda pregunta: "Tabla gold.features_escuela(cct)",
    )

    resultado = procesar_consulta_con_rag(
        "Que escuelas tienen mayor riesgo?",
        generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.features_escuela",
        ejecutar_sql=lambda sql: [{"cct": "09ABC0001X"}],
        redactar_respuesta=lambda pregunta, filas: "Una escuela.",
    )

    assert resultado.respuesta == "Una escuela."
    assert resultado.sql_generado == "SELECT cct FROM gold.features_escuela LIMIT 1000;"


def test_auto_correccion_reintenta_sql_tras_error_de_ejecucion() -> None:
    """Fase 1: si `ejecutar_sql` falla, se regenera el SQL una vez antes de rendirse."""
    intentos_generar: list[str] = []

    def generar(prompt: str, pregunta: str) -> str:
        intentos_generar.append(prompt)
        if len(intentos_generar) == 1:
            return "SELECT columna_inexistente FROM gold.predicciones"
        assert "no se pudo ejecutar" in prompt.lower()
        return "SELECT cct FROM gold.predicciones"

    def ejecutar(sql: str):
        if "columna_inexistente" in sql:
            raise RuntimeError("columna_inexistente no existe")
        return [{"cct": "09ABC0001X"}]

    resultado = procesar_consulta(
        "Cuantas escuelas tienen mayor riesgo?",
        recuperar_contexto=lambda pregunta: "gold.predicciones(cct)",
        generar_sql=generar,
        ejecutar_sql=ejecutar,
        redactar_respuesta=lambda pregunta, filas: f"{len(filas)} escuela.",
    )

    assert len(intentos_generar) == 2
    assert resultado.sql_generado == "SELECT cct FROM gold.predicciones LIMIT 1000;"
    assert resultado.respuesta == "1 escuela."
    assert not resultado.fuera_de_alcance


def test_auto_correccion_se_rinde_tras_agotar_reintentos() -> None:
    """Si el SQL sigue fallando tras el reintento, se degrada con un mensaje claro (sin crash)."""

    def ejecutar(sql: str):
        raise RuntimeError("la consulta no se pudo ejecutar")

    resultado = procesar_consulta(
        "Cuantas escuelas tienen mayor riesgo?",
        recuperar_contexto=lambda pregunta: "gold.predicciones(cct)",
        generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.predicciones",
        ejecutar_sql=ejecutar,
        redactar_respuesta=lambda pregunta, filas: "no debe llamarse",
    )

    assert resultado.sql_generado is None
    assert not resultado.fuera_de_alcance
    assert "reformularla" in resultado.respuesta


def test_respuesta_directa_sin_sql_para_pregunta_conceptual() -> None:
    """Fase 1: una pregunta metodológica se responde desde el contexto RAG, sin tocar la BD."""

    def no_debe_llamarse(*args):
        raise AssertionError("una pregunta conceptual no debe ejecutar SQL")

    observado: dict[str, object] = {}

    def redactar(pregunta: str, filas):
        observado["filas"] = filas
        return "SIN_DATO indica que ese driver no tiene información para esa escuela."

    resultado = procesar_consulta(
        "Que significa SIN_DATO en los drivers?",
        recuperar_contexto=lambda pregunta: "Convención SIN_DATO: nunca se imputa como cero.",
        generar_sql=lambda prompt, pregunta: "NO_SQL_NECESARIO",
        ejecutar_sql=no_debe_llamarse,
        redactar_respuesta=redactar,
    )

    assert resultado.sql_generado is None
    assert not resultado.fuera_de_alcance
    assert "SIN_DATO" in resultado.respuesta


# --------------------------------------------------------------------------- #
# Fase 3 (streaming, 2026-09-10): mismos guardarraíles, redacción final en fragmentos
# --------------------------------------------------------------------------- #


def test_stream_orquesta_igual_y_cede_los_fragmentos_del_redactor() -> None:
    def redactar_stream(pregunta: str, filas):
        assert pregunta == "Que escuelas tienen mayor riesgo?"
        assert filas == [{"cct": "09ABC0001X"}]
        yield "Hay "
        yield "1 escuela."

    resultado = procesar_consulta_stream(
        "Que escuelas tienen mayor riesgo?",
        recuperar_contexto=lambda pregunta: "Tabla disponible: gold.features_escuela",
        generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.features_escuela",
        ejecutar_sql=lambda sql: [{"cct": "09ABC0001X"}],
        redactar_respuesta_stream=redactar_stream,
    )

    assert resultado.respuesta_fija is None
    assert not resultado.fuera_de_alcance
    assert resultado.sql_generado == "SELECT cct FROM gold.features_escuela LIMIT 1000;"
    assert list(resultado.fragmentos) == ["Hay ", "1 escuela."]


def test_stream_no_invoca_al_redactor_hasta_que_se_itera() -> None:
    """El redactor en streaming solo debe llamarse cuando alguien consume `fragmentos`."""
    llamado = {"veces": 0}

    def redactar_stream(pregunta: str, filas):
        llamado["veces"] += 1
        yield "ok"

    resultado = procesar_consulta_stream(
        "Que escuelas tienen mayor riesgo?",
        recuperar_contexto=lambda pregunta: "contexto",
        generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.features_escuela",
        ejecutar_sql=lambda sql: [{"cct": "09ABC0001X"}],
        redactar_respuesta_stream=redactar_stream,
    )

    assert llamado["veces"] == 0
    list(resultado.fragmentos)
    assert llamado["veces"] == 1


def test_stream_pregunta_fuera_de_alcance_no_llega_al_redactor() -> None:
    """Igual guardarraíl que la ruta síncrona: rechazada, sin fragmentos que transmitir."""

    def no_debe_llamarse(*args):
        raise AssertionError("no debe invocar al redactor en streaming")

    resultado = procesar_consulta_stream(
        "Cual es la capital de Francia?",
        recuperar_contexto=lambda pregunta: (_ for _ in ()).throw(ContextoNoEncontrado()),
        generar_sql=no_debe_llamarse,
        ejecutar_sql=no_debe_llamarse,
        redactar_respuesta_stream=no_debe_llamarse,
    )

    assert resultado.fragmentos is None
    assert resultado.fuera_de_alcance
    assert resultado.respuesta_fija


def test_stream_orden_de_escritura_se_corta_antes_de_generar_sql() -> None:
    """El guardarraíl de escritura sigue siendo un corte duro también en streaming."""

    def no_debe_llamarse(*args):
        raise AssertionError("una orden de escritura no debe tocar RAG ni LLM")

    resultado = procesar_consulta_stream(
        "Borra la tabla de predicciones",
        recuperar_contexto=no_debe_llamarse,
        generar_sql=no_debe_llamarse,
        ejecutar_sql=no_debe_llamarse,
        redactar_respuesta_stream=no_debe_llamarse,
    )

    assert resultado.fragmentos is None
    assert resultado.fuera_de_alcance
    assert resultado.sql_generado is None


def test_stream_respuesta_directa_sin_sql_transmite_desde_contexto_faro() -> None:
    """La rama `NO_SQL_NECESARIO` también pasa por el redactor en streaming, no el síncrono."""

    def no_debe_llamarse(*args):
        raise AssertionError("una pregunta conceptual no debe ejecutar SQL")

    def redactar_stream(pregunta: str, filas):
        assert filas[0]["contexto_faro"] == "Convención SIN_DATO: nunca se imputa como cero."
        yield "SIN_DATO "
        yield "nunca es cero."

    resultado = procesar_consulta_stream(
        "Que significa SIN_DATO en los drivers?",
        recuperar_contexto=lambda pregunta: "Convención SIN_DATO: nunca se imputa como cero.",
        generar_sql=lambda prompt, pregunta: "NO_SQL_NECESARIO",
        ejecutar_sql=no_debe_llamarse,
        redactar_respuesta_stream=redactar_stream,
    )

    assert resultado.sql_generado is None
    assert not resultado.fuera_de_alcance
    assert "".join(resultado.fragmentos) == "SIN_DATO nunca es cero."


# --------------------------------------------------------------------------- #
# Fase 4 (2026-09-12): la etapa final de redacción no tenía NINGÚN try/except -- un fallo del LLM
# ahí (timeout, servicio caído) se colaba sin degradar hasta el catch-all genérico de
# `src/api/v1/agente.py`. Estas pruebas fijan que ahora se distingue con un mensaje propio y se
# registra en el log, sin filtrar el detalle del error al cliente.
# --------------------------------------------------------------------------- #


def test_fallo_del_redactor_sincrono_degrada_sin_filtrar_detalle(caplog) -> None:
    def redactar_que_revienta(pregunta: str, filas):
        raise TimeoutError("boom interno con secreto del proveedor LLM")

    with caplog.at_level(logging.ERROR, logger="faro.agente.servicio"):
        resultado = procesar_consulta(
            "Cuantas escuelas tienen mayor riesgo?",
            recuperar_contexto=lambda pregunta: "gold.predicciones(cct)",
            generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.predicciones",
            ejecutar_sql=lambda sql: [{"cct": "09ABC0001X"}],
            redactar_respuesta=redactar_que_revienta,
        )

    assert resultado.respuesta == MSG_ERROR_REDACCION
    assert resultado.sql_generado is None
    assert not resultado.fuera_de_alcance
    assert "boom" not in resultado.respuesta.lower()
    assert "secreto" not in resultado.respuesta.lower()
    assert any(r.message == "llm.redaccion_fallida" for r in caplog.records)


def test_fallo_del_redactor_sincrono_nunca_oculta_un_assertion_error() -> None:
    """Las fallas de las propias pruebas/scaffolding nunca se disfrazan de degradación segura."""

    def redactar_que_revienta(pregunta: str, filas):
        raise AssertionError("esto es un bug del test, no del LLM")

    try:
        procesar_consulta(
            "Cuantas escuelas tienen mayor riesgo?",
            recuperar_contexto=lambda pregunta: "gold.predicciones(cct)",
            generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.predicciones",
            ejecutar_sql=lambda sql: [{"cct": "09ABC0001X"}],
            redactar_respuesta=redactar_que_revienta,
        )
        raise SystemExit("no debió llegar aquí: se esperaba que el AssertionError se propagara")
    except AssertionError as exc:
        assert "esto es un bug del test" in str(exc)


def test_stream_redactor_falla_antes_de_emitir_nada_cede_mensaje_de_respaldo(caplog) -> None:
    """Sin ningún fragmento real emitido, el stream nunca puede quedar vacío (lo exige el
    cliente ya mergeado, PR #313): se cede `MSG_ERROR_REDACCION` como único fragmento."""

    def redactar_stream_que_revienta(pregunta: str, filas):
        raise TimeoutError("boom interno con secreto del proveedor LLM")
        yield  # pragma: no cover - nunca se alcanza; hace de esta función un generador

    with caplog.at_level(logging.ERROR, logger="faro.agente.servicio"):
        resultado = procesar_consulta_stream(
            "Cuantas escuelas tienen mayor riesgo?",
            recuperar_contexto=lambda pregunta: "gold.predicciones(cct)",
            generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.predicciones",
            ejecutar_sql=lambda sql: [{"cct": "09ABC0001X"}],
            redactar_respuesta_stream=redactar_stream_que_revienta,
        )
        fragmentos = list(resultado.fragmentos)

    assert fragmentos == [MSG_ERROR_REDACCION]
    assert "boom" not in "".join(fragmentos).lower()
    assert any(r.message == "llm.redaccion_stream_fallida" for r in caplog.records)


def test_stream_redactor_falla_a_medias_conserva_lo_ya_emitido() -> None:
    """Con contenido real ya cedido, un fallo a medias detiene el stream sin pegar un mensaje de
    error a media oración -- el cliente se queda con la respuesta parcial, como cualquier chat
    que se corta a medio párrafo."""

    def redactar_stream_que_revienta_a_medias(pregunta: str, filas):
        yield "El riesgo promedio "
        yield "es de 0.42"
        raise TimeoutError("boom interno con secreto del proveedor LLM")

    resultado = procesar_consulta_stream(
        "Cuantas escuelas tienen mayor riesgo?",
        recuperar_contexto=lambda pregunta: "gold.predicciones(cct)",
        generar_sql=lambda prompt, pregunta: "SELECT cct FROM gold.predicciones",
        ejecutar_sql=lambda sql: [{"cct": "09ABC0001X"}],
        redactar_respuesta_stream=redactar_stream_que_revienta_a_medias,
    )

    fragmentos = list(resultado.fragmentos)

    assert fragmentos == ["El riesgo promedio ", "es de 0.42"]
    assert "boom" not in "".join(fragmentos).lower()


# --------------------------------------------------------------------------- #
# Fase 4 (2026-09-12): logging estructurado de rechazos de guardarraíl (además de las fallas de
# LLM cubiertas arriba). Nunca incluye la pregunta cruda del usuario.
# --------------------------------------------------------------------------- #


def test_rechazo_de_escritura_se_registra(caplog) -> None:
    def no_debe_llamarse(*args):
        raise AssertionError("no debe invocar RAG/LLM/BD")

    with caplog.at_level(logging.WARNING, logger="faro.agente.servicio"):
        procesar_consulta(
            "borra la tabla de predicciones de escuelas",
            recuperar_contexto=no_debe_llamarse,
            generar_sql=no_debe_llamarse,
            ejecutar_sql=no_debe_llamarse,
            redactar_respuesta=no_debe_llamarse,
        )

    assert any(r.message == "guardrail.rechazo_escritura" for r in caplog.records)


def test_sql_rechazado_por_guardrail_se_registra_con_motivo_seguro(caplog) -> None:
    with caplog.at_level(logging.WARNING, logger="faro.agente.servicio"):
        resultado = procesar_consulta(
            "Cuantas escuelas hay?",
            recuperar_contexto=lambda pregunta: "gold.predicciones",
            generar_sql=lambda prompt, pregunta: "DELETE FROM gold.predicciones",
            ejecutar_sql=lambda sql: [],
            redactar_respuesta=lambda pregunta, filas: "no debe llamarse",
        )

    assert resultado.sql_generado is None
    registro = next(r for r in caplog.records if r.message == "llm.sql_rechazado")
    # El motivo es el mismo texto ya curado que ve el cliente en `respuesta` -- nunca el SQL crudo.
    assert "DELETE" not in registro.motivo