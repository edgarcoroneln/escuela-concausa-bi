"""Job idempotente para indexar el esquema de Gold en ChromaDB (US-304b)."""

from __future__ import annotations

import os
from typing import Any

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    chromadb = None
    SentenceTransformer = None

# Definiciones estáticas de la capa Gold. Se vectorizan para que el agente recupere sólo lo
# relevante a cada pregunta y escriba SQL contra columnas que EXISTEN.
#
# Los nombres salen de los modelos dbt, no de memoria. Si cambian allá, hay que cambiarlos aquí:
#   dbt/models/gold/{dim_escuela,dim_municipio,fact_escuela_ciclo,features_escuela}.sql
#   src/modelos/publicar_gold.py  (predicciones y recomendaciones)
#
# Ojo con los dos juegos de nombres de driver, que NO son intercambiables:
#   fact_escuela_ciclo → d1 … d6            (nombres cortos)
#   features_escuela   → d1_pobreza … d6_aire (nombres largos)
ESQUEMA_GOLD = [
    {
        "id": "dim_escuela",
        "texto": (
            "Tabla dim_escuela (Dimensión de Escuela). Información estática de cada Centro de "
            "Trabajo (CCT). Columnas: cct (llave primaria, 10 caracteres), nombre, nivel "
            "(ej. PRIMARIA, SECUNDARIA), sostenimiento, latitud, longitud, cve_ent (clave "
            "entidad, 2 caracteres), cve_mun (clave municipio, 5 caracteres), y la "
            "infraestructura del censo CEMABE: agua, drenaje, electricidad, sanitarios, "
            "internet, computadoras. Esas seis últimas responden preguntas de los drivers D3 "
            "(infraestructura) y D4 (conectividad), y valen 'SIN_DATO' cuando la escuela no "
            "aparece en el censo."
        )
    },
    {
        "id": "dim_municipio",
        "texto": (
            "Tabla dim_municipio (Dimensión de Municipio). Datos a nivel municipal. Columnas: "
            "cve_mun (llave primaria, 5 caracteres), cve_ent (clave entidad, 2 caracteres), "
            "nombre_municipio, nombre_entidad, poblacion (total de habitantes), "
            "indice_rezago_social, grado_rezago, pobreza_pct (porcentaje en pobreza). "
            "Es la fuente del driver D1 (pobreza y rezago social)."
        )
    },
    {
        "id": "fact_escuela_ciclo",
        "texto": (
            "Tabla fact_escuela_ciclo (Hecho). Matrícula observada por escuela y ciclo escolar; "
            "es la tabla principal para saber cuántos alumnos hay y cuánto cambió la matrícula. "
            "Columnas: cct (llave foránea), id_ciclo (ej. 2024-2025), cve_mun, matricula_total, "
            "variacion_matricula (cambio proporcional respecto al ciclo anterior), "
            "indice_completitud_drivers (fracción de 0 a 1 de drivers con dato), los seis "
            "puntajes de driver d1, d2, d3, d4, d5, d6 con NOMBRE CORTO, y sus banderas "
            "d1_cobertura … d6_cobertura."
        )
    },
    {
        "id": "predicciones",
        "texto": (
            "Tabla predicciones (Salida de ML-01). Riesgo estimado de pérdida de matrícula. "
            "Columnas: grano, cct, cve_mun, nivel, id_ciclo, modelo, valor, indice_riesgo, "
            "probabilidad, mlflow_run_id, generado_at. Convive el grano de escuela con el "
            "agregado de municipio × nivel, así que TODA consulta a nivel escuela debe filtrar "
            "grano = 'escuela' y modelo = 'ML-01'; sin ese filtro se suman granos distintos y el "
            "resultado es incorrecto. En el grano 'escuela' cct viene lleno y cve_mun/nivel "
            "vienen nulos; en el grano agregado es al revés. Sólo lectura."
        )
    },
    {
        "id": "recomendaciones",
        "texto": (
            "Tabla recomendaciones (Salida de ML-02). El driver dominante que explica el riesgo "
            "de cada escuela. Columnas: cct, id_ciclo, driver_dominante, recomendacion, "
            "prioridad. El campo recomendacion es el diferenciador prescriptivo del proyecto: "
            "dos escuelas con el mismo riesgo reciben recomendaciones distintas según su driver "
            "dominante. Sólo lectura."
        )
    },
    {
        "id": "features_escuela",
        "texto": (
            "Tabla features_escuela (Contrato de ML). Drivers calculados que alimentan a ML-01. "
            "Columnas: cct, id_ciclo, los seis puntajes con NOMBRE LARGO d1_pobreza, "
            "d2_inseguridad, d3_infraestructura, d4_conectividad, d5_agua, d6_aire, sus banderas "
            "d1_cobertura … d6_cobertura, indice_completitud_drivers, target_variacion_matricula "
            "y driver_dominante. driver_dominante es la etiqueta operativa D1…D6 derivada por "
            "argmax entre drivers con cobertura OK; no es una observación causal independiente. "
            "Cuidado: aquí los drivers llevan nombre largo, a diferencia de fact_escuela_ciclo, "
            "donde son d1 … d6."
        )
    },
    {
        "id": "convencion_sin_dato",
        "texto": (
            "Convención de cobertura parcial de todo el proyecto. Cada driver dN trae una bandera "
            "dN_cobertura que vale 'OK' cuando hay dato y 'SIN_DATO' cuando no lo hay, y en ese "
            "caso el puntaje viene NULL. SIN_DATO NUNCA significa cero: contar un SIN_DATO como "
            "cero inventa un dato que no existe. Al agregar o promediar drivers hay que excluir "
            "las filas con SIN_DATO y decir sobre cuántas escuelas se calculó. Hoy D5 (agua) está "
            "completo en SIN_DATO porque la fuente DS-06 (CONAGUA) aún no tiene descarga "
            "verificada."
        )
    },
    {
        "id": "cobertura_geografica",
        "texto": (
            "Cobertura geográfica del proyecto (alcance intencional de diseño, NO un hueco de "
            "datos). Gold, los modelos de ML y este agente cubren EXCLUSIVAMENTE 4 entidades "
            "(SCOPE_ENTIDADES): Ciudad de México (cve_ent '09'), Estado de México (cve_ent "
            "'15'), Nuevo León (cve_ent '19') y Jalisco (cve_ent '14'). Bronze y Silver son "
            "nacionales, pero el filtro a estas 4 entidades se aplica en la frontera hacia Gold "
            "vía dim_escuela/dim_municipio.cve_ent. Si una pregunta menciona otra entidad (por "
            "ejemplo Oaxaca, Chiapas, Puebla, Yucatán), no hay datos porque esa entidad está "
            "fuera del alcance del proyecto por diseño — no es un error del sistema ni un hueco "
            "de cobertura de driver. La respuesta debe explicar esta limitación de alcance en "
            "vez de solo decir 'no hay datos disponibles' sin contexto."
        )
    }
]


class ErrorIndexacion(RuntimeError):
    """El esquema no pudo indexarse en ChromaDB."""


def indexar_esquema(
    host: str = "localhost",
    port: int = 8001,
    *,
    cliente: Any | None = None,
    modelo: Any | None = None,
) -> int:
    """Genera embeddings y hace upsert idempotente del catálogo Gold."""
    try:
        if cliente is None:
            if chromadb is None:
                raise ErrorIndexacion("chromadb no está instalado.")
            cliente = chromadb.HttpClient(
                host=os.getenv("CHROMA_HOST", host),
                port=int(os.getenv("CHROMA_PORT", port)),
            )
        if modelo is None:
            if SentenceTransformer is None:
                raise ErrorIndexacion("sentence-transformers no está instalado.")
            modelo = SentenceTransformer(
                os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
            )

        coleccion = cliente.get_or_create_collection(
            name="faro_gold_schema",
            metadata={"hnsw:space": "cosine"},
        )
        textos = [doc["texto"] for doc in ESQUEMA_GOLD]
        ids = [doc["id"] for doc in ESQUEMA_GOLD]
        embeddings = modelo.encode(textos).tolist()
        coleccion.upsert(ids=ids, documents=textos, embeddings=embeddings)
        return len(ids)
    except ErrorIndexacion:
        raise
    except Exception as exc:
        raise ErrorIndexacion("No se pudo indexar el esquema Gold en ChromaDB.") from exc

if __name__ == "__main__":
    total = indexar_esquema()
    print(f"{total} documentos indexados en faro_gold_schema.")
