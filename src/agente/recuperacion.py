"""Módulo de recuperación (RAG) para el agente FARO (US-304b)."""

from __future__ import annotations

import logging
import os
from typing import Any

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    chromadb = None
    SentenceTransformer = None

NOMBRE_COLECCION = "faro_gold_schema"
NOMBRE_MODELO_EMBEDDINGS = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K_DEFAULT = 5

# Distancia coseno (ChromaDB, hnsw:space="cosine": 0=identico, 2=opuesto) por debajo de la cual
# el mejor resultado se considera lo bastante relevante como para usarse como señal semántica de
# alcance en `servicio.py` (Fase 1, plan 2026-09-09). Es un punto de partida conservador con solo
# 7 documentos en la colección; se afina con el set de preguntas "golden" (Fase 4) sin redeploy,
# vía la env var.
UMBRAL_DISTANCIA_DEFAULT = 1.1

logger = logging.getLogger(__name__)
_modelo_cache = None


def _umbral_distancia() -> float:
    try:
        return float(os.getenv("AGENTE_RAG_UMBRAL_DISTANCIA", str(UMBRAL_DISTANCIA_DEFAULT)))
    except ValueError:
        return UMBRAL_DISTANCIA_DEFAULT


class ErrorRecuperacion(RuntimeError):
    """La capa RAG no está disponible."""


class ContextoNoEncontrado(ErrorRecuperacion):
    """La capa RAG respondió, pero no encontró contexto para la pregunta."""


def _cargar_modelo() -> Any:
    global _modelo_cache
    if _modelo_cache is not None:
        return _modelo_cache

    if SentenceTransformer is None:
        raise ErrorRecuperacion("sentence-transformers no está instalado.")
    try:
        _modelo_cache = SentenceTransformer(
            os.getenv("EMBEDDING_MODEL", NOMBRE_MODELO_EMBEDDINGS)
        )
        return _modelo_cache
    except Exception as exc:
        logger.exception("Falló la descarga o inicialización del modelo de embeddings %r.", NOMBRE_MODELO_EMBEDDINGS)
        raise ErrorRecuperacion("No se pudo cargar el modelo de embeddings.") from exc


def recuperar_contexto(
    pregunta: str,
    top_k: int = TOP_K_DEFAULT,
    host: str = "localhost",
    port: int = 8001,
    *,
    modelo: Any | None = None,
    cliente: Any | None = None,
    umbral_distancia: float | None = None,
) -> str:
    """Recupera descripciones del esquema Gold relevantes para una pregunta.

    Si el mejor resultado viene con una distancia (`distances`, cuando el cliente la expone) por
    encima del umbral, se trata como "sin contexto relevante" (`ContextoNoEncontrado`) aunque
    ChromaDB haya devuelto documentos: son sus vecinos más cercanos, no necesariamente relevantes.
    Clientes/mocks que no exponen `distances` preservan el comportamiento anterior (sin filtrar).
    """
    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    if top_k < 1:
        raise ValueError("top_k debe ser mayor que cero.")

    modelo = modelo or _cargar_modelo()
    if cliente is None:
        if chromadb is None:
            raise ErrorRecuperacion("chromadb no está instalado.")
        try:
            cliente = chromadb.HttpClient(
                host=os.getenv("CHROMA_HOST", host),
                port=int(os.getenv("CHROMA_PORT", port)),
            )
        except Exception as exc:
            raise ErrorRecuperacion("No se pudo conectar con ChromaDB.") from exc

    try:
        coleccion = cliente.get_collection(name=NOMBRE_COLECCION)
    except Exception as exc:
        raise ErrorRecuperacion(
            f"La colección {NOMBRE_COLECCION!r} no existe; ejecuta indexar_esquema.py."
        ) from exc

    try:
        vector_pregunta = modelo.encode(pregunta).tolist()
        resultados = coleccion.query(
            query_embeddings=[vector_pregunta],
            n_results=top_k,
            include=["documents", "distances"],
        )
    except Exception as exc:
        raise ErrorRecuperacion("Falló la consulta de contexto en ChromaDB.") from exc

    documentos = resultados.get("documents", [[]])[0]
    if not documentos:
        raise ContextoNoEncontrado("No se encontró contexto para la pregunta.")

    distancias = resultados.get("distances", [[]])[0]
    if distancias:
        umbral = umbral_distancia if umbral_distancia is not None else _umbral_distancia()
        if distancias[0] > umbral:
            raise ContextoNoEncontrado(
                "El contexto más cercano no es lo bastante relevante para la pregunta."
            )

    return "Tablas relevantes del esquema Gold:\n" + "".join(
        f"- {documento}\n" for documento in documentos
    )
