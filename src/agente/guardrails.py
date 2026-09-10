"""Guardarrailes de seguridad para el agente conversacional (US-304a).

Este modulo no ejecuta SQL ni depende del RAG de US-304b. Su responsabilidad es acotar la
pregunta y la consulta generada antes de que otra capa decida recuperar contexto o consultar Gold.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Vocabulario del dominio FARO (Fase 1, plan 2026-09-09): whitelist ampliada con sinónimos y
# frases naturales para que preguntas libres no se rechacen solo por no calzar una palabra exacta.
# Es la primera barrera (rápida, determinista); `servicio.py` complementa con una señal semántica
# del RAG cuando ninguna de estas palabras aparece. El filtro de intención de escritura (abajo) es
# independiente y sigue siendo la barrera de seguridad real junto con `validar_sql_lectura`.
PALABRAS_AMBITO = frozenset(
    {
        # Escuelas / planteles (sinónimos)
        "escuela",
        "escuelas",
        "colegio",
        "colegios",
        "plantel",
        "planteles",
        "centro",
        "centros",
        # Matrícula / alumnado
        "matricula",
        "matriculas",
        "inscripcion",
        "inscripciones",
        "inscritos",
        "alumno",
        "alumnos",
        "alumnado",
        "estudiante",
        "estudiantes",
        "poblacion",
        "docente",
        "docentes",
        "maestro",
        "maestros",
        # Riesgo / peligro de perder matrícula
        "riesgo",
        "riesgos",
        "peligro",
        "vulnerable",
        "vulnerables",
        "abandono",
        "desercion",
        "perder",
        "caida",
        # Drivers (los 6 y sinónimos de sus temas)
        "driver",
        "drivers",
        "factor",
        "factores",
        "causa",
        "causas",
        "pobreza",
        "rezago",
        "marginacion",
        "inseguridad",
        "seguridad",
        "delito",
        "delitos",
        "delincuencia",
        "criminalidad",
        "infraestructura",
        "conectividad",
        "internet",
        "electricidad",
        "drenaje",
        "sanitarios",
        "computadoras",
        "agua",
        "hidrico",
        "aire",
        "calidad",
        "ambiental",
        "clima",
        # Geografía
        "municipio",
        "municipios",
        "entidad",
        "entidades",
        "estado",
        "estados",
        "ciudad",
        "region",
        "zona",
        "cve_mun",
        "cve_ent",
        # ML / predicciones / recomendaciones
        "prediccion",
        "predicciones",
        "modelo",
        "machine",
        "recomendacion",
        "recomendaciones",
        "recomienda",
        "explicacion",
        "metodologia",
        "shap",
        "cluster",
        "clustering",
        "agrupacion",
        "perfil",
        "prioridad",
        # Identificadores / metadatos del proyecto
        "cct",
        "ciclo",
        "ciclos",
        "escolar",
        "faro",
        "gold",
        "dato",
        "datos",
        "cobertura",
        "sin_dato",
        "completitud",
        # Niveles educativos
        "total",
        "secundaria",
        "preescolar",
        "primaria",
        "primarias",
        "especial",
        "telesecundaria",
        "indigena",
        "comunitaria",
        "bachillerato",
        "rural",
        "urbana",
        "sostenimiento",
        "publico",
        "privado",
        # Verbos/adjetivos de análisis frecuentes en preguntas libres
        "comparar",
        "comparacion",
        "tendencia",
        "evolucion",
        "historico",
        "promedio",
        "porcentaje",
        "cantidad",
        "numero",
        "mejores",
        "peores",
        "ranking",
        "clasificacion",
        "top",
    }
)


VERBOS_PROHIBIDOS = frozenset(
    {
        "alter",
        "create",
        "delete",
        "drop",
        "insert",
        "into",
        "merge",
        "replace",
        "truncate",
        "update",
        "upsert",
        "vacuum",
    }
)

# --- Clasificación de INTENCIÓN de la pregunta (defensa en profundidad, P-13) ---
# `pregunta_en_alcance` clasificaba solo por TEMA: "borra la tabla de predicciones" pasaba por
# contener "predicciones". El validador de SQL (`validar_sql_lectura`) siempre fue —y sigue siendo—
# la barrera real sobre el SQL. Al conectar el LLM conviene además rechazar la intención de escritura
# desde la pregunta. El match es por token exacto: capta imperativos/infinitivos (cómo se dan las
# órdenes) sin atrapar conjugaciones de preguntas legítimas ("¿qué escuelas se actualizaron?").
# Limitación conocida: PATRON_PALABRA no capta acentos, así que solo cubre formas sin tilde; lo que
# se escape lo detiene el validador de SQL.
VERBOS_ESCRITURA_DIRECTOS = frozenset(
    {
        "borra",
        "borrar",
        "borren",
        "borrame",
        "elimina",
        "eliminar",
        "eliminen",
        "suprime",
        "suprimir",
        "trunca",
        "truncar",
        "destruye",
        "destruir",
        "dropea",
        "dropear",
        "delete",
        "drop",
        "truncate",
        "wipe",
        "erase",
    }
)

# Verbos que también aparecen en preguntas legítimas ("¿cuántas escuelas se crearon?"): solo cuentan
# como orden de escritura si además nombran un objeto de datos (tabla, registro, columna, ...).
VERBOS_ESCRITURA_AMBIGUOS = frozenset(
    {
        "actualiza",
        "actualizar",
        "modifica",
        "modificar",
        "inserta",
        "insertar",
        "altera",
        "alterar",
        "crea",
        "crear",
        "reemplaza",
        "reemplazar",
        "sobrescribe",
        "sobreescribe",
        "update",
        "insert",
        "alter",
        "create",
        "remove",
        "replace",
    }
)

OBJETOS_DE_DATOS = frozenset(
    {
        "tabla",
        "tablas",
        "registro",
        "registros",
        "fila",
        "filas",
        "dato",
        "datos",
        "columna",
        "columnas",
        "campo",
        "campos",
        "esquema",
        "bd",
        "gold",
        "indice",
        "índice",
        # Fase 1 (2026-09-09): el vocabulario de PALABRAS_AMBITO se amplió con sustantivos de
        # negocio que SON columnas reales de Gold (dim_escuela.nivel, recomendaciones.prioridad,
        # etc.). Sin ellos aquí, "Modifica el nivel de la primaria X" pasaba el filtro de
        # intención por no reconocer "nivel" como objeto de datos (regresión de seguridad ya
        # corregida una vez, ver DevLog 2026-09-08 — se reabrió al ampliar la whitelist y se
        # cierra aquí en la raíz en vez de volver a angostar el vocabulario).
        "nivel",
        "prioridad",
        "cobertura",
        "completitud",
        "sostenimiento",
        "cluster",
        "perfil",
        "matricula",
        "recomendacion",
        "recomendaciones",
        "prediccion",
        "predicciones",
    }
)

RAZON_SOLO_LECTURA = "FARO solo responde consultas de lectura; no ejecuta cambios sobre los datos."

PATRON_PALABRA = re.compile(r"\b\w+\b", re.UNICODE)
PATRON_LIMIT = re.compile(r"\blimit\s+(\d+)\b", re.IGNORECASE)
PATRON_COMENTARIO = re.compile(r"(--|/\*|\*/)")
PATRON_REFERENCIA = re.compile(
    r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
    re.IGNORECASE,
)
PATRON_CTE = re.compile(
    r"(?:\bwith\b|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s*\(",
    re.IGNORECASE,
)
PATRON_JOIN_COMA = re.compile(
    r"\bfrom\s+[a-zA-Z_][a-zA-Z0-9_.]*(?:\s+(?:as\s+)?[a-zA-Z_][a-zA-Z0-9_]*)?\s*,",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ResultadoGuardrail:
    """Resultado de aplicar una regla de seguridad."""

    permitido: bool
    razon: str | None = None


def _intencion_de_escritura(tokens: set[str]) -> bool:
    """True si la pregunta ORDENA mutar datos, no solo menciona un tema del proyecto.

    Un verbo destructivo directo (borra, elimina, trunca, drop, ...) basta; los verbos ambiguos
    (actualiza, crea, ...) solo cuentan si además nombran un objeto de datos, para no rechazar
    preguntas legítimas de lectura.
    """
    if tokens & VERBOS_ESCRITURA_DIRECTOS:
        return True
    return bool(tokens & VERBOS_ESCRITURA_AMBIGUOS) and bool(tokens & OBJETOS_DE_DATOS)


def pregunta_en_alcance(pregunta: str) -> ResultadoGuardrail:
    """Valida si una pregunta pertenece al dominio de FARO y no ordena escribir.

    Dos filtros complementarios:
    1. TEMA: al menos una palabra debe pertenecer al vocabulario del proyecto (regla conservadora;
       Carlos/US-304b podra enriquecerla con recuperacion semantica).
    2. INTENCION (P-13): rechaza ordenes de escritura ("borra la tabla de predicciones") aunque
       toquen un tema valido. Es defensa en profundidad; `validar_sql_lectura` sigue siendo la
       barrera real sobre el SQL que genere el LLM.
    """
    tokens = {token.lower() for token in PATRON_PALABRA.findall(pregunta)}
    if not (tokens & PALABRAS_AMBITO):
        return ResultadoGuardrail(False, "Pregunta fuera del alcance de FARO.")
    if _intencion_de_escritura(tokens):
        return ResultadoGuardrail(False, RAZON_SOLO_LECTURA)
    return ResultadoGuardrail(True)


def validar_sql_lectura(sql: str) -> ResultadoGuardrail:
    """Permite solo SQL de lectura auditable sobre Gold.

    Rechaza comentarios, sentencias multiples y cualquier verbo de escritura o DDL. El agente debe
    producir una sola consulta `SELECT` o `WITH ... SELECT`.
    """
    consulta = sql.strip()
    if not consulta:
        return ResultadoGuardrail(False, "SQL vacio.")
    if PATRON_COMENTARIO.search(consulta):
        return ResultadoGuardrail(False, "SQL con comentarios no permitido.")
    if ";" in consulta.rstrip(";"):
        return ResultadoGuardrail(False, "SQL con multiples sentencias no permitido.")

    tokens = [token.lower() for token in PATRON_PALABRA.findall(consulta)]
    if not tokens:
        return ResultadoGuardrail(False, "SQL sin tokens validos.")
    if tokens[0] not in {"select", "with"}:
        return ResultadoGuardrail(False, "Solo se permiten consultas SELECT o WITH.")

    prohibidos = sorted(set(tokens) & VERBOS_PROHIBIDOS)
    if prohibidos:
        return ResultadoGuardrail(False, f"SQL contiene verbo prohibido: {', '.join(prohibidos)}.")
    if PATRON_JOIN_COMA.search(consulta):
        return ResultadoGuardrail(False, "SQL con unión por coma no permitido; usa JOIN explícito.")

    referencias = [referencia.lower() for referencia in PATRON_REFERENCIA.findall(consulta)]
    if not referencias:
        return ResultadoGuardrail(False, "SQL sin tabla de Gold.")
    ctes = {cte.lower() for cte in PATRON_CTE.findall(consulta)}
    fuera_de_gold = [
        referencia
        for referencia in referencias
        if not referencia.startswith("gold.") and referencia not in ctes
    ]
    if fuera_de_gold:
        return ResultadoGuardrail(
            False,
            f"SQL fuera del esquema Gold: {', '.join(sorted(set(fuera_de_gold)))}.",
        )
    return ResultadoGuardrail(True)


def aplicar_limit(sql: str, limite: int = 1000) -> str:
    """Garantiza un `LIMIT` maximo para respuestas auditables y acotadas."""
    consulta = sql.strip().rstrip(";")
    match = PATRON_LIMIT.search(consulta)
    if match:
        actual = int(match.group(1))
        if actual <= limite:
            return f"{consulta};"
        inicio, fin = match.span(1)
        return f"{consulta[:inicio]}{limite}{consulta[fin:]};"
    return f"{consulta} LIMIT {limite};"


def preparar_sql_seguro(sql: str, limite: int = 1000) -> str:
    """Valida y normaliza SQL de solo lectura.

    Raises:
        ValueError: si la consulta viola los guardarrailes.
    """
    resultado = validar_sql_lectura(sql)
    if not resultado.permitido:
        raise ValueError(resultado.razon)
    return aplicar_limit(sql, limite=limite)
