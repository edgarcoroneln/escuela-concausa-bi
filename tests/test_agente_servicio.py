"""Pruebas del flujo seguro de integración del agente FARO."""

from __future__ import annotations

from src.agente import servicio
from src.agente.recuperacion import ContextoNoEncontrado, ErrorRecuperacion
from src.agente.servicio import procesar_consulta, procesar_consulta_con_rag


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
    def no_debe_llamarse(*args):
        raise AssertionError("No se deben invocar dependencias para preguntas fuera de alcance")

    resultado = procesar_consulta(
        "Cual es la mejor receta de pasta?",
        recuperar_contexto=no_debe_llamarse,
        generar_sql=no_debe_llamarse,
        ejecutar_sql=no_debe_llamarse,
        redactar_respuesta=no_debe_llamarse,
    )

    assert resultado.fuera_de_alcance
    assert resultado.sql_generado is None


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

    assert resultado.fuera_de_alcance
    assert resultado.sql_generado is None
    assert not ejecutado


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