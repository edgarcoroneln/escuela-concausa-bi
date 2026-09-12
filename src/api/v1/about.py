"""Sección "Cómo funciona FARO" (US-601): backend, modelo de datos, capas, cubos, memoria
técnica, decisiones de arquitectura y modelos de ML, servidos como contrato agnóstico de
frontend (hoy lo consume Streamlit; el mismo contrato sirve para React/Angular más adelante).

**Por qué dos rutas y no siete.** Este hotfix corre en paralelo con el resto del equipo: Gold
puede ganar columnas o cubos, hay ADRs `proposed` que pueden pasar a `accepted`, y los tres Model
Cards de C3 siguen `in_review`. Si cada sección fuera un endpoint con su propio *shape*, cualquiera
de esos cambios obligaría a tocar también la página de Streamlit. En vez de eso, `/secciones`
publica un **manifest** (qué secciones hay) y `/secciones/{id}` responde siempre el mismo **sobre
genérico** de bloques (`markdown` | `mermaid` | `tabla` | `metricas` | `mapa` | `barras` |
`diagrama_flujo`): agregar, quitar o reordenar una sección es un cambio de este archivo
únicamente, la página no se vuelve a tocar. Los tres últimos tipos (mapa/barras/diagrama_flujo)
se renderizan con D3 vía HTML embebido -- no con widgets nativos de Streamlit -- porque Streamlit
se va a dejar de usar pronto (migración a React/Angular); HTML/JS puro es lo único de esta página
que sobrevive esa migración sin reescritura.

**Contenido fijo, decisión explícita (no bloquea esta entrega, ver PLAN_US225_COMO_FUNCIONA.md).**
El texto y las tablas de todas las secciones salvo `capas` son una copia literal de la doc
canónica de cada dueño -- Diana Alvarez (`Data_Model.md`), el propio `CLAUDE.md`, el índice de
ADRs y los Model Cards de C3 -- **no** se parsean en vivo. Cada bloque cita su fuente exacta en
`fuente` para que quien revise note de inmediato si el original cambió y esta copia quedó atrás;
sustituir esto por lectura en vivo queda anotado como *follow-up* explícito del plan, no se hace
en este hotfix. Único dato realmente vivo: los conteos de fila de la sección `capas`
(`RepositorioAbout`, ver `src/api/repositorio_about.py`).
"""
from __future__ import annotations

import json
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.repositorio_about import RepositorioAbout, get_repositorio_about

router = APIRouter(prefix="/about", tags=["Cómo funciona"])

# Assets geográficos versionados (INEGI/CONABIO vía el espejo comunitario PhantomInsights/
# mexico-geojson, MIT). `municipios_scope.geojson` ya lo consume el coroplético de Superset
# (US-203); `mexico_silueta.geojson` es nuevo (US-601, pedido explícito del usuario tras ver el
# mapa sin fondo nacional) -- un contorno **decorativo**, no fronteras administrativas exactas,
# generado por `superset/generar_geojson_silueta_nacional.py` (rasteriza los 32 estados y traza
# el contorno con marching squares; ver ese script para el detalle y las limitaciones). Ambos se
# leen del disco una sola vez por proceso: ningún bloque de esta sección llama a una red externa.
_RAIZ = Path(__file__).resolve().parents[3]
_ASSET_MUNICIPIOS = _RAIZ / "superset" / "assets" / "geojson" / "municipios_scope.geojson"
_ASSET_SILUETA_NACIONAL = _RAIZ / "superset" / "assets" / "geojson" / "mexico_silueta.geojson"


@lru_cache
def _geojson_municipios_scope() -> dict:
    return json.loads(_ASSET_MUNICIPIOS.read_text(encoding="utf-8"))


@lru_cache
def _geojson_silueta_nacional() -> dict:
    return json.loads(_ASSET_SILUETA_NACIONAL.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# El sobre genérico: 7 tipos de bloque, cada uno con su propio renderer en la página.
# --------------------------------------------------------------------------- #


class BloqueMarkdown(BaseModel):
    tipo: Literal["markdown"] = "markdown"
    texto: str


class BloqueMermaid(BaseModel):
    tipo: Literal["mermaid"] = "mermaid"
    codigo: str
    #: Alto sugerido en px para el contenedor del frontend. `components.html` de Streamlit no
    #: tiene mecanismo de auto-resize (verificado: ignora `postMessage({type:
    #: "streamlit:setFrameHeight"})` fuera de un custom component registrado), así que el alto es
    #: fijo por diagrama, elegido a mano por quien lo redactó -- un mismo valor para los 4 E-R
    #: dejaba mucho espacio en blanco bajo Bronze/Silver (mucho más chicos que Gold) o, si se
    #: encogía para ajustarlos a ellos, dejaba a Gold ilegible sin hacer zoom primero. `None` usa
    #: el alto por defecto del cliente.
    alto: int | None = None


class BloqueTabla(BaseModel):
    tipo: Literal["tabla"] = "tabla"
    columnas: list[str]
    filas: list[list[str]]


class MetricaItem(BaseModel):
    etiqueta: str
    valor: str | None  # None => SIN_DATO explícito (tabla no materializada, no un 0 inventado)
    nota: str | None = None


class BloqueMetricas(BaseModel):
    tipo: Literal["metricas"] = "metricas"
    items: list[MetricaItem]


class ResaltadoMapa(BaseModel):
    cve_ent: str
    nombre: str
    color: str


class BloqueMapa(BaseModel):
    """Mapa de municipios (D3, sin librería de mapas): el frontend colorea cada feature del
    `geojson` según `cve_ent` contra `resaltados`. `fondo`, si viene, es la silueta nacional
    simplificada (gris, detrás de los 4 estados resaltados) -- pedido explícito del usuario
    después de ver el mapa sin contexto nacional."""

    tipo: Literal["mapa"] = "mapa"
    geojson: dict
    resaltados: list[ResaltadoMapa]
    fondo: dict | None = None


class ItemBarra(BaseModel):
    etiqueta: str
    valor: float | None  # None => SIN_DATO explícito (capa sin ninguna tabla materializada)
    nota: str | None = None


class BloqueBarras(BaseModel):
    """Barras horizontales simples (D3). Reemplaza al icicle original (US-601): con una
    disparidad de datos como bronze/silver/gold (silver es ~6x más chica que gold), un icicle
    reparte el ANCHO por proporción y la capa chica se vuelve una franja casi invisible -- una
    barra por categoría, cada una con su propia fila y etiqueta, no compite por espacio."""

    tipo: Literal["barras"] = "barras"
    items: list[ItemBarra]


class NodoFlujo(BaseModel):
    id: str
    columna: int  # 0, 1 o 2 -- de izquierda a derecha
    etiqueta: str


class EnlaceFlujo(BaseModel):
    origen: str
    destino: str


class BloqueDiagramaFlujo(BaseModel):
    """Diagrama de 3 columnas con curvas (D3, sin plugin de Sankey): nodos por columna +
    enlaces entre IDs de nodo. El frontend resalta al pasar el mouse los enlaces de un nodo."""

    tipo: Literal["diagrama_flujo"] = "diagrama_flujo"
    nodos: list[NodoFlujo]
    enlaces: list[EnlaceFlujo]


Bloque = Annotated[
    BloqueMarkdown | BloqueMermaid | BloqueTabla | BloqueMetricas | BloqueMapa | BloqueBarras
    | BloqueDiagramaFlujo,
    Field(discriminator="tipo"),
]


class SeccionResumen(BaseModel):
    """Una entrada del manifest (`GET /secciones`)."""

    id: str
    titulo: str
    orden: int


class SeccionOut(BaseModel):
    """El contenido de una sección (`GET /secciones/{id}`), siempre con esta forma."""

    id: str
    titulo: str
    fuente: list[str]
    advertencias: list[str] = Field(default_factory=list)
    bloques: list[Bloque]


# --------------------------------------------------------------------------- #
# Contenido de cada sección. Todas reciben el repositorio por uniformidad de firma, aunque solo
# `_seccion_capas` lo use -- así el registro de abajo no necesita distinguir "necesita datos
# vivos" de "no los necesita".
# --------------------------------------------------------------------------- #


def _seccion_arquitectura(_repo: RepositorioAbout) -> SeccionOut:
    return SeccionOut(
        id="arquitectura",
        titulo="Arquitectura del backend",
        fuente=[
            "CLAUDE.md §4 Arquitectura",
            "CLAUDE.md §5 Stack técnico",
            "CLAUDE.md §6 Equipo",
            "vault/_Meta/ownership.yml",
        ],
        bloques=[
            BloqueMarkdown(
                texto=(
                    "FARO va de 8 fuentes públicas a una página única con dashboards, un panel "
                    "de ML y un agente conversacional, pasando por tres capas de datos "
                    "(bronze/silver/gold) y tres modelos de Machine Learning registrados en "
                    "MLflow. Cada componente tiene un dueño de célula distinto."
                )
            ),
            BloqueTabla(
                columnas=["Componente", "Responsabilidad", "Dueño"],
                filas=[
                    ["Apache Airflow", "Orquesta la ingesta de las 8 fuentes hacia Bronze", "C1 · Diana Alvarez"],
                    ["dbt-core", "Transforma Bronze → Silver → Gold (esquema estrella y cubos)", "C1 · Diana Alvarez"],
                    ["Great Expectations + Pydantic", "Valida calidad por conjunto (capa) y por registro (ingesta)", "C1 · Diana Alvarez"],
                    ["PostgreSQL", "Almacén de bronze/silver/gold (Cloud SQL en producción)", "C1 · Diana Alvarez / C5 · Luis Téllez"],
                    ["scikit-learn / XGBoost + MLflow", "Entrena y registra los 3 modelos de ML (ML-01/02/03)", "C3 · Andrés González Habib"],
                    ["FastAPI + OAuth2/JWT + RBAC", "Expone Gold, predicciones, el agente y esta misma sección", "C4 · Christian Ruiz"],
                    ["ChromaDB + sentence-transformers", "Recuperación de contexto (RAG) del agente conversacional", "C3 · Carlos Mayorga"],
                    ["Apache Superset", "Los 10 dashboards del proyecto", "C2 · Manuel Serranía / Marina García / Monserrat Miranda / Oscar Quiroz"],
                    ["Streamlit (FARO Web)", "Shell único: dashboards + panel de ML + chat + login por rol", "C2 · Manuel Serranía"],
                    ["Docker + docker-compose / GCP Cloud Run", "Empaqueta y despliega todo el sistema con URL pública", "C5 · Luis Téllez"],
                ],
            ),
            BloqueMarkdown(
                texto=(
                    "**Cómo se dividió el equipo.** Cada fila de la tabla de arriba tiene un "
                    "dueño de célula porque el backend se construyó como 5 franjas verticales, "
                    "no una sola pila compartida: cada célula es dueña de punta a punta de su "
                    "parte del pipeline, desde el código hasta las pruebas."
                )
            ),
            BloqueTabla(
                columnas=["Célula", "Integrantes", "A grandes rasgos, en qué trabajó"],
                filas=[
                    [
                        "C1 · Data Engineering & Quality",
                        "Diana Alvarez (TL) · Deni Garrido · Luis García · Emilio Galnares",
                        (
                            "Extractores de las 8 fuentes hacia Bronze, los modelos dbt de "
                            "Bronze→Silver→Gold y las suites de Great Expectations por capa."
                        ),
                    ],
                    [
                        "C2 · Analytics & BI",
                        "Manuel Serranía (TL) · Marina García · Monserrat Miranda · Oscar Quiroz",
                        (
                            "Los 10 dashboards de Superset y FARO Web (el shell de Streamlit, "
                            "login, y esta misma sección)."
                        ),
                    ],
                    [
                        "C3 · ML & Agente IA",
                        (
                            "Andrés González Habib (TL) · Héctor Morales · Estefany Hernández · "
                            "Carlos Mayorga"
                        ),
                        (
                            "Los 3 modelos de ML (ML-01/02/03) registrados en MLflow y el agente "
                            "conversacional RAG sobre ChromaDB."
                        ),
                    ],
                    [
                        "C4 · Backend, API & Seguridad",
                        "Christian Ruiz (TL) · Karla Monter · Juan Macías · Eloisa González",
                        (
                            "El contrato REST de FastAPI, OAuth2/JWT y RBAC — la puerta única por "
                            "la que Gold, las predicciones y el agente llegan al frontend."
                        ),
                    ],
                    [
                        "C5 · Cloud & DevOps",
                        "Luis Téllez (TL) · Edgar Jiménez · Alejandro Velázquez · Edward Ruiz",
                        (
                            "Docker, docker-compose y el despliegue a GCP Cloud Run que pone todo "
                            "lo anterior detrás de una URL pública."
                        ),
                    ],
                ],
            ),
        ],
    )


#: Compartido entre `modelo-datos` (responde "cómo está estructurado Gold") y `capas` (responde
#: "en qué cambió Gold respecto a Silver") -- misma figura, dos preguntas, para no mantener dos
#: copias del mismo diagrama que puedan desalinearse.
_ER_GOLD_MERMAID = (
    "erDiagram\n"
    "  dim_escuela   ||--o{ fact_escuela_ciclo : cct\n"
    "  dim_municipio ||--o{ fact_escuela_ciclo : cve_mun\n"
    "  dim_tiempo    ||--o{ fact_escuela_ciclo : id_ciclo\n"
    "  dim_driver    ||--o{ recomendaciones : driver_dominante\n"
    "  fact_escuela_ciclo ||--o{ predicciones : \"cct,id_ciclo\"\n"
    "  fact_escuela_ciclo ||--o{ recomendaciones : \"cct,id_ciclo\"\n"
    "  fact_escuela_ciclo ||--|| features_escuela : \"cct,id_ciclo\""
)

#: Los 4 estados de SCOPE_ENTIDADES, con el mismo color que usa el bloque `mapa` de esta sección.
#: Un color por entidad, no una escala -- no hay orden entre estados, así que una escala secuencial
#: sería engañosa (ver `dataviz` §paleta categórica).
_SCOPE_COLORES: dict[str, tuple[str, str]] = {
    "09": ("Ciudad de México", "#4C72B0"),
    "15": ("México (Edomex)", "#DD8452"),
    "19": ("Nuevo León", "#55A868"),
    "14": ("Jalisco", "#C44E52"),
}


def _seccion_modelo_datos(_repo: RepositorioAbout) -> SeccionOut:
    return SeccionOut(
        id="modelo-datos",
        titulo="Modelo de datos",
        fuente=[
            "vault/03_Architecture/Data_Model.md §4 (esquema estrella)",
            "Data_Model.md §6 (diccionario)",
            "Data_Model.md §7 (SCOPE_ENTIDADES)",
            "CLAUDE.md §4 (los 6 drivers)",
            "superset/assets/geojson/municipios_scope.geojson (INEGI/CONABIO, MIT)",
        ],
        bloques=[
            BloqueMarkdown(
                texto=(
                    "Gold es un esquema estrella acotado a `SCOPE_ENTIDADES`: el sistema es "
                    "nacional por diseño (Bronze y Silver cubren las 32 entidades), pero Gold, "
                    "los modelos y los dashboards se acotan a estos 4 estados **por cobertura de "
                    "datos, no por capacidad** — ampliar el alcance es cambiar una línea, sin "
                    "reingestar nada."
                )
            ),
            BloqueMarkdown(
                texto=(
                    "**Cómo leer el mapa de abajo** — cada color es una de las 4 entidades de "
                    "`SCOPE_ENTIDADES`; el municipio es la unidad mínima que se colorea. No es una "
                    "escala de valor (no hay un número detrás del color, es categórico) y el gris "
                    "de fondo **no es `SIN_DATO`** — es el resto de México como contexto geográfico, "
                    "fuera del alcance del proyecto. Corte: municipios vigentes del asset versionado "
                    "(INEGI/CONABIO), no una consulta en vivo."
                )
            ),
            BloqueMapa(
                geojson=_geojson_municipios_scope(),
                fondo=_geojson_silueta_nacional(),
                resaltados=[
                    ResaltadoMapa(cve_ent=cve, nombre=nombre, color=color)
                    for cve, (nombre, color) in _SCOPE_COLORES.items()
                ],
            ),
            BloqueMarkdown(
                texto=(
                    "**¿Qué es `gold.fact_escuela_ciclo`?** Es el hecho central del esquema "
                    "estrella: una fila por cada combinación real de **escuela (CCT) × ciclo "
                    "escolar** que el sistema observó. Ahí viven únicamente **hechos medidos** — "
                    "matrícula, su variación, qué tan completos están los 6 drivers — nunca una "
                    "predicción. `indice_riesgo` (ML-01) y `driver_dominante` (ML-02) **no** son "
                    "columnas de esta tabla: viven en `gold.predicciones`/`gold.recomendaciones` "
                    "y se traen por `JOIN` sobre `cct, id_ciclo`. La razón es evitar que un cambio "
                    "en el pipeline de ML tenga que tocar la tabla de hechos, y que nunca se pueda "
                    "confundir \"lo que se midió\" con \"lo que el modelo predijo\"."
                )
            ),
            # Gold es el más grande de los 4 E-R (8 entidades, esquema estrella completo) --
            # alto generoso para que se lea sin tener que hacer zoom primero.
            BloqueMermaid(codigo=_ER_GOLD_MERMAID, alto=540),
            BloqueMarkdown(
                texto=(
                    "### Diccionario de columnas — `gold.fact_escuela_ciclo`\n"
                    "La tabla de abajo **no es todo Gold**: son solo las columnas del hecho central "
                    "que se acaba de dibujar arriba (el recuadro `fact_escuela_ciclo` del E-R), "
                    "copiadas de `Data_Model.md §6` — cada dimensión (`dim_escuela`, "
                    "`dim_municipio`, `dim_tiempo`, `dim_driver`) tiene su propio diccionario en ese "
                    "mismo documento, no repetido aquí. Sirve para responder, columna por columna, "
                    "la pregunta de arriba: qué es un hecho medido (`matricula_total`, "
                    "`variacion_matricula`, `d1`…`d6`) y qué falta explícitamente marcado "
                    "(`d1_cobertura`…`d6_cobertura`, `indice_completitud_drivers`) — nunca una "
                    "predicción."
                )
            ),
            BloqueTabla(
                columnas=["Columna", "Tipo", "Descripción"],
                filas=[
                    ["cct", "str(10)", "Llave de escuela"],
                    ["id_ciclo", "str", "Ciclo escolar, p. ej. 2024-2025"],
                    ["cve_mun", "str(5)", "Clave INEGI de municipio"],
                    ["matricula_total", "int", "Matrícula del ciclo"],
                    ["variacion_matricula", "float", "Δ vs. ciclo anterior"],
                    ["indice_completitud_drivers", "float [0,1]", "Fracción de los 6 drivers con dato observado"],
                    ["d1 … d6", "float | SIN_DATO", "Score normalizado por driver"],
                    ["d1_cobertura … d6_cobertura", "enum OK/SIN_DATO", "Bandera de cobertura por driver"],
                ],
            ),
            BloqueMarkdown(
                texto=(
                    "**¿Qué son los drivers?** Son los 6 factores del territorio que el proyecto "
                    "usa para explicar —no solo predecir— por qué una escuela puede perder "
                    "matrícula. Cada driver es un score normalizado [0,1] con su propia bandera "
                    "de cobertura; el driver con el valor más alto entre los disponibles es el "
                    "`driver_dominante` que arma la recomendación (ML-02)."
                )
            ),
            BloqueTabla(
                columnas=["ID", "Driver", "Fuente", "Cobertura"],
                filas=[
                    ["D1", "Pobreza y rezago social", "CONEVAL + CONAPO", "Nacional"],
                    ["D2", "Inseguridad del entorno", "SESNSP", "Nacional"],
                    ["D3", "Infraestructura escolar", "CEMABE", "Nacional · nivel escuela"],
                    ["D4", "Conectividad digital", "CEMABE", "Nacional · nivel escuela"],
                    ["D5", "Estrés hídrico", "CONAGUA SINA", "Regional"],
                    ["D6", "Calidad del aire", "SINAICA", "~80 zonas urbanas"],
                ],
            ),
        ],
    )


#: Las 8 fuentes, tal como las documenta CLAUDE.md §4 -- es de aquí de donde sale Bronze.
_FUENTES_BRONZE = [
    ["DS-01", "SEP Formato 911 (SIGED / datos.gob.mx)", "Anual"],
    ["DS-02", "SEP Catálogo CCT", "Continua"],
    ["DS-03", "SEP CEMABE", "Censo 2013"],
    ["DS-04", "SESNSP incidencia delictiva", "Mensual"],
    ["DS-05", "SINAICA calidad del aire (API)", "Horaria"],
    ["DS-06", "CONAGUA SINA", "Diaria"],
    ["DS-07", "CONEVAL rezago social", "Bienal"],
    ["DS-08", "CONAPO proyecciones", "Anual"],
]


def _barras_capas(conteos: list[dict]) -> BloqueBarras:
    """Una barra por capa (bronze/silver/gold) con su total de filas -- reemplaza al icicle
    original: con gold (~3,300 filas) más de 6 veces más grande que silver (~500), un icicle
    reparte el ANCHO por proporción y silver se vuelve una franja casi invisible. Una barra por
    capa siempre tiene su propia fila del mismo alto y su propia etiqueta, no compite por
    espacio con las demás -- se lee de un vistazo, sin necesitar leyenda ni explicación previa."""
    items: list[ItemBarra] = []
    for capa in ("bronze", "silver", "gold"):
        valores = [c["filas"] for c in conteos if c["capa"] == capa and c["filas"] is not None]
        if valores:
            items.append(ItemBarra(etiqueta=capa.capitalize(), valor=float(sum(valores))))
        else:
            items.append(
                ItemBarra(
                    etiqueta=capa.capitalize(),
                    valor=None,
                    nota=f"Ninguna tabla de {capa.capitalize()} materializada todavía.",
                )
            )
    return BloqueBarras(items=items)


def _seccion_capas(repo: RepositorioAbout) -> SeccionOut:
    conteos = repo.conteos_capas()

    def _suma(capa: str) -> int | None:
        valores = [c["filas"] for c in conteos if c["capa"] == capa and c["filas"] is not None]
        return sum(valores) if valores else None

    def _metrica_capa(capa: str, etiqueta: str) -> MetricaItem:
        total = _suma(capa)
        if total is not None:
            return MetricaItem(etiqueta=etiqueta, valor=str(total))
        return MetricaItem(
            etiqueta=etiqueta,
            valor=None,
            nota=f"Ninguna tabla de {capa.capitalize()} materializada todavía.",
        )

    sumas = [_suma("bronze"), _suma("silver"), _suma("gold")]
    conocidas = [s for s in sumas if s is not None]
    total_item = (
        MetricaItem(etiqueta="Total de filas (bronze + silver + gold)", valor=str(sum(conocidas)))
        if conocidas
        else MetricaItem(
            etiqueta="Total de filas (bronze + silver + gold)",
            valor=None,
            nota="Ninguna capa materializada todavía.",
        )
    )

    metricas = [
        _metrica_capa("bronze", "Filas en Bronze (nacional)"),
        _metrica_capa("silver", "Filas en Silver (nacional)"),
        _metrica_capa("gold", "Filas en Gold (4 entidades)"),
    ]

    tabla_detalle = BloqueTabla(
        columnas=["Capa", "Tabla", "Filas", "Nota"],
        filas=[
            [c["capa"], c["tabla"], str(c["filas"]) if c["filas"] is not None else "—", c["nota"] or ""]
            for c in conteos
        ],
    )

    return SeccionOut(
        id="capas",
        titulo="Capas: bronze, silver, gold",
        fuente=[
            "Data_Model.md §1-§3 (definición de capas)",
            "Data_Model.md §7 (SCOPE_ENTIDADES)",
            "CLAUDE.md §4 (las 8 fuentes)",
            "dbt/models/sources.yml (entidades de Bronze)",
            "dbt/models/silver/*.sql (llaves de conformación de Silver)",
        ],
        bloques=[
            BloqueMarkdown(
                texto=(
                    "**Bronze**: copia cruda 1:1 de cada fuente, particionada por fecha de "
                    "ingesta, con metadatos `_ingested_at`/`_source`/`_source_url`. Cobertura "
                    "nacional, sin filtrar.\n\n"
                    "**Silver**: datos tipados, deduplicados, con CCT y clave INEGI homologados "
                    "y `SIN_DATO` resuelto explícitamente donde una fuente no cubre una escuela o "
                    "municipio (nunca `0` ni `NULL` silencioso). Cobertura nacional.\n\n"
                    "**Gold**: esquema estrella, cubos y salidas de ML. El filtro "
                    "`WHERE cve_ent IN SCOPE_ENTIDADES` se aplica únicamente en la frontera "
                    "Silver → Gold, para que Bronze/Silver sigan sirviendo de base nacional "
                    "reutilizable y el análisis de cobertura (`indice_completitud_drivers`) no "
                    "pierda contexto nacional."
                )
            ),
            BloqueMarkdown(
                texto=(
                    "**¿De dónde sale Bronze?** De estas 8 fuentes públicas, cada una con su "
                    "propia frecuencia de actualización — el extractor de cada una corre "
                    "independiente, así que una fuente lenta (CONEVAL, bienal) nunca bloquea a "
                    "una rápida (SINAICA, horaria)."
                )
            ),
            BloqueTabla(columnas=["Fuente", "Descripción", "Frecuencia"], filas=_FUENTES_BRONZE),
            BloqueMetricas(items=[total_item]),
            BloqueMarkdown(
                texto=(
                    "**Cómo leer las barras de abajo** — una fila por capa, largo proporcional a "
                    "su conteo de filas (0 hasta la capa más grande, sin transformar). El recuadro "
                    "punteado \"SIN_DATO\" (no una barra de longitud cero) significa que esa tabla "
                    "todavía no está materializada en este ambiente — cero significaría que existe "
                    "pero está vacía, un caso distinto. Bronze/Silver son nacionales (32 entidades); "
                    "Gold ya está acotado a `SCOPE_ENTIDADES`. El corte es el ciclo vigente en "
                    "Postgres al momento de la consulta, en vivo."
                )
            ),
            _barras_capas(conteos),
            BloqueMarkdown(
                texto=(
                    "### E-R — Bronze\n"
                    "Tablas de aterrizaje **independientes**, una por artefacto físico de cada "
                    "fuente (§2). No hay llave foránea real entre ellas a este nivel: las líneas "
                    "punteadas marcan la llave natural que **Silver** usará para conformarlas, no "
                    "una restricción de Postgres. `bronze.conagua_presas` se muestra aunque no "
                    "exista todavía en este ambiente (§5 del runbook): es la fuente de "
                    "`gold.cubo_pipeline`, la única tabla que sigue `SIN_DATO`."
                )
            ),
            BloqueMermaid(
                codigo=(
                    "erDiagram\n"
                    '  cct ||..o{ formato911 : "cct (sin FK)"\n'
                    '  cct ||..o{ formato911_historico : "cct (sin FK)"\n'
                    '  cct ||..o{ cemabe : "cct (sin FK)"\n'
                    '  conapo ||..o{ sesnsp : "clave municipio (sin FK)"\n'
                    '  conapo ||..o{ coneval_irs : "clave municipio, hash (sin FK)"\n'
                    '  conapo ||..o{ coneval_pobreza : "clave municipio, hash (sin FK)"\n'
                    '  sinaica_estaciones ||..o{ sinaica_observaciones : "id_estacion (sin FK)"\n'
                    "  conagua_presas {\n"
                    "    string estado \"SIN_DATO en este ambiente (DB-10)\"\n"
                    "  }"
                ),
                # Medido en vivo con Playwright: Bronze renderiza a ~110px de alto natural, muy
                # por debajo de lo que Silver/Gold necesitan -- un alto compartido dejaba mucho
                # espacio en blanco aquí.
                alto=220,
            ),
            BloqueMarkdown(
                texto=(
                    "### E-R — Silver\n"
                    "**Qué cambió respecto a Bronze**: las mismas fuentes, ahora tipadas, "
                    "deduplicadas y conformadas por `cct`/`cve_mun` — las líneas punteadas de "
                    "Bronze (llave natural, sin garantía) se vuelven relaciones reales aquí. Las "
                    "relaciones hacia `aire_estacion`/`agua_region` siguen punteadas a propósito: "
                    "no son un `JOIN` por llave, D5/D6 se asignan por interpolación espacial (IDW, "
                    "ADR-006), no por coincidencia de clave."
                )
            ),
            BloqueMermaid(
                codigo=(
                    "erDiagram\n"
                    "  escuela ||--o{ matricula : cct\n"
                    "  escuela ||--o{ matricula_historica : cct\n"
                    "  escuela ||--o| cemabe : cct\n"
                    "  escuela }o--|| poblacion_municipio : cve_mun\n"
                    "  poblacion_municipio ||--o| rezago_municipio : cve_mun\n"
                    "  poblacion_municipio ||--o{ delitos_municipio : cve_mun\n"
                    '  escuela }o..o{ aire_estacion : "IDW ADR-006, no FK"\n'
                    '  escuela }o..o{ agua_region : "IDW ADR-006, no FK"'
                ),
                # Medido en vivo con Playwright: Silver renderiza a ~260px de alto natural.
                alto=340,
            ),
            BloqueMarkdown(
                texto=(
                    "### E-R — Gold\n"
                    "**Qué cambió respecto a Silver**: las tablas por fuente desaparecen; se "
                    "reorganizan en un **esquema estrella** con un hecho central "
                    "(`fact_escuela_ciclo`) y dimensiones compartidas (`dim_escuela`, "
                    "`dim_municipio`, `dim_tiempo`, `dim_driver`). Aquí también se acota por "
                    "primera vez a `SCOPE_ENTIDADES` — Silver seguía siendo nacional. Detalle de "
                    "columnas y diccionario completo en la sección **Modelo de datos**."
                )
            ),
            # Gold es el más grande de los 4 E-R (8 entidades, esquema estrella completo) --
            # alto generoso para que se lea sin tener que hacer zoom primero.
            BloqueMermaid(codigo=_ER_GOLD_MERMAID, alto=540),
            BloqueMetricas(items=metricas),
            tabla_detalle,
        ],
    )


#: Fuentes reales de cada cubo, verificadas contra el `FROM`/`JOIN` de cada
#: `dbt/models/gold/cubo_*.sql` (no inventado) -- no la tabla cubo→dashboard que ya bastaba antes,
#: sino de qué tablas sale cada uno. `cubo_pipeline` es el único que no nace de Gold: audita la
#: ingesta, así que sus fuentes son Silver/Bronze.
_CUBOS_INFO: dict[str, dict] = {
    "cubo_matricula": {
        "fuentes": ["gold.fact_escuela_ciclo", "gold.dim_escuela", "gold.dim_municipio", "gold.dim_tiempo", "gold.predicciones"],
        "dashboards": ["DB-01", "DB-06"],
        "grano": "municipio × nivel × ciclo",
    },
    "cubo_riesgo_territorial": {
        "fuentes": ["gold.fact_escuela_ciclo", "gold.dim_escuela", "gold.dim_municipio", "gold.dim_tiempo", "gold.predicciones"],
        "dashboards": ["DB-02"],
        "grano": "municipio × nivel × ciclo",
    },
    "cubo_escuela_360": {
        "fuentes": ["gold.fact_escuela_ciclo", "gold.dim_escuela", "gold.dim_municipio", "gold.dim_tiempo", "gold.dim_driver", "gold.predicciones", "gold.recomendaciones"],
        "dashboards": ["DB-03"],
        "grano": "cct × ciclo",
    },
    "cubo_comparador_municipio": {
        "fuentes": ["gold.fact_escuela_ciclo", "gold.dim_escuela", "gold.dim_municipio", "gold.dim_tiempo", "gold.predicciones"],
        "dashboards": ["DB-04"],
        "grano": "municipio × nivel × ciclo",
    },
    "cubo_driver": {
        "fuentes": ["gold.fact_escuela_ciclo", "gold.dim_escuela", "gold.dim_municipio", "gold.dim_tiempo", "gold.recomendaciones"],
        "dashboards": ["DB-05"],
        "grano": "driver × municipio × nivel × ciclo",
    },
    "cubo_completitud": {
        "fuentes": ["gold.fact_escuela_ciclo", "gold.dim_escuela", "gold.dim_municipio", "gold.dim_tiempo", "gold.dim_driver"],
        "dashboards": ["DB-07"],
        "grano": "municipio × nivel × driver × ciclo",
    },
    "cubo_pivot": {
        "fuentes": ["gold.fact_escuela_ciclo", "gold.dim_escuela", "gold.dim_municipio", "gold.dim_tiempo", "gold.dim_driver", "gold.predicciones", "gold.recomendaciones"],
        "dashboards": ["DB-08"],
        "grano": "cct × driver × ciclo",
    },
    "cubo_recomendaciones": {
        "fuentes": ["gold.fact_escuela_ciclo", "gold.dim_escuela", "gold.dim_municipio", "gold.dim_tiempo", "gold.dim_driver", "gold.recomendaciones"],
        "dashboards": ["DB-09"],
        "grano": "cct × ciclo",
    },
    "cubo_pipeline": {
        "fuentes": [
            "silver.escuela", "silver.matricula", "silver.cemabe", "silver.delitos_municipio",
            "silver.aire_estacion", "silver.poblacion_municipio", "silver.rezago_municipio",
            "bronze.conagua_presas",
        ],
        "dashboards": ["DB-10"],
        "grano": "fuente × fecha_ingesta",
    },
}


def _diagrama_cubos() -> BloqueDiagramaFlujo:
    fuentes_ids = sorted({f for info in _CUBOS_INFO.values() for f in info["fuentes"]})
    dashboards_ids = sorted({d for info in _CUBOS_INFO.values() for d in info["dashboards"]})

    nodos = (
        [NodoFlujo(id=f, columna=0, etiqueta=f) for f in fuentes_ids]
        + [
            NodoFlujo(id=cubo, columna=1, etiqueta=f"{cubo}\n({info['grano']})")
            for cubo, info in _CUBOS_INFO.items()
        ]
        + [NodoFlujo(id=d, columna=2, etiqueta=d) for d in dashboards_ids]
    )
    enlaces = [
        EnlaceFlujo(origen=fuente, destino=cubo)
        for cubo, info in _CUBOS_INFO.items()
        for fuente in info["fuentes"]
    ] + [
        EnlaceFlujo(origen=cubo, destino=dashboard)
        for cubo, info in _CUBOS_INFO.items()
        for dashboard in info["dashboards"]
    ]
    return BloqueDiagramaFlujo(nodos=nodos, enlaces=enlaces)


def _seccion_cubos(_repo: RepositorioAbout) -> SeccionOut:
    return SeccionOut(
        id="cubos",
        titulo="Cubos de Gold",
        fuente=["Data_Model.md §4.3 (cubos materializados)", "dbt/models/gold/cubo_*.sql (fuentes reales por cubo)"],
        bloques=[
            BloqueMarkdown(
                texto=(
                    "Los cubos son agregaciones precalculadas para que Superset responda rápido: "
                    "en vez de que cada dashboard recalcule un `JOIN`/`GROUP BY` sobre las tablas "
                    "de Gold en cada clic, dbt los materializa una sola vez y Superset solo lee "
                    "el resultado ya agregado."
                )
            ),
            BloqueMarkdown(
                texto=(
                    "**Cómo leer el diagrama de abajo** — son 3 columnas, de izquierda a derecha:\n\n"
                    "1. **Tablas fuente** — de dónde salen los datos: casi todas de Gold "
                    "(`fact_escuela_ciclo`, las dimensiones, `predicciones`, `recomendaciones`); "
                    "`cubo_pipeline` es la excepción, se compone directo de Silver/Bronze porque "
                    "audita la ingesta, no el análisis.\n"
                    "2. **Los 9 cubos** — cada uno combina un subconjunto distinto de la columna 1 "
                    "(entre 5 y 7 tablas fuente cada uno).\n"
                    "3. **Los 10 dashboards** — a qué tablero(s) de Superset alimenta cada cubo "
                    "(`cubo_matricula` alimenta dos).\n\n"
                    "Pasa el mouse sobre cualquier nodo para resaltar solo sus conexiones y apagar "
                    "el resto — con 63 enlaces a la vez es difícil seguir uno sin esa ayuda."
                )
            ),
            _diagrama_cubos(),
        ],
    )


def _seccion_stack(_repo: RepositorioAbout) -> SeccionOut:
    return SeccionOut(
        id="stack",
        titulo="Memoria técnica",
        fuente=["CLAUDE.md §5 Stack técnico"],
        bloques=[
            BloqueMarkdown(texto="Python 3.11 en todo el backend (PEP 8, docstrings, type hints)."),
            BloqueTabla(
                columnas=["Capa", "Herramienta"],
                filas=[
                    ["Orquestación", "Apache Airflow"],
                    ["Transformación", "dbt-core"],
                    ["Calidad de datos", "Great Expectations + Pydantic"],
                    ["Almacén", "PostgreSQL (Cloud SQL en producción)"],
                    ["ML", "scikit-learn, XGBoost + MLflow"],
                    ["API", "FastAPI + OAuth2/JWT + RBAC"],
                    ["Agente", "ChromaDB + sentence-transformers"],
                    ["BI", "Apache Superset"],
                    ["Contenedores", "Docker + docker-compose"],
                    ["Nube", "GCP (Cloud Run + Cloud SQL + Artifact Registry)"],
                ],
            ),
        ],
    )


def _seccion_decisiones(_repo: RepositorioAbout) -> SeccionOut:
    return SeccionOut(
        id="decisiones",
        titulo="Decisiones de arquitectura (ADRs)",
        fuente=["vault/03_Architecture/ADRs/_index.md"],
        advertencias=[
            (
                "Snapshot al momento de escribir esta sección: sujeto a cambio conforme el "
                "equipo acepte o agregue ADRs esta semana. Ver "
                "vault/03_Architecture/ADRs/_index.md para la lista viva."
            ),
        ],
        bloques=[
            BloqueTabla(
                columnas=["ADR", "Título", "Estado", "Fecha"],
                filas=[
                    ["ADR-002", "Frontend integrado en Streamlit sobre Superset + API", "accepted", "2026-08-07"],
                    ["ADR-003", "Estrategia de modelado ML: partición temporal, backtesting y cobertura parcial", "accepted", "2026-08-09"],
                    ["ADR-004", "Autenticación: OAuth2 con Google + JWT propio (access/refresh)", "proposed", "2026-08-17"],
                    ["ADR-005", "Mapeo de D3/D4 en dim_driver: infraestructura y conectividad desde CEMABE", "accepted", "2026-08-17"],
                    ["ADR-006", "Interpolación IDW de D5/D6 (agua/aire) hacia cada escuela", "accepted", "2026-08-19"],
                    ["ADR-007", "Unidad de target_variacion_matricula: fracción, no diferencia absoluta", "accepted", "2026-08-29"],
                    ["ADR-008", "Contenerización propia de Airflow con SQLAlchemy fijado en 1.4.x", "accepted", "2026-08-25"],
                    ["ADR-009", "Monitoreo de runs de MLflow con alertas por webhook genérico", "proposed", "2026-08-31"],
                    ["ADR-010", "Puente OAuth → frontend: código de un solo uso, nunca tokens en la URL", "proposed", "2026-09-03"],
                ],
            ),
        ],
    )


def _seccion_modelos_ml(_repo: RepositorioAbout) -> SeccionOut:
    return SeccionOut(
        id="modelos-ml",
        titulo="Modelos de Machine Learning",
        fuente=[
            "vault/15_ML_Models/ML01_Model_Card.md",
            "vault/15_ML_Models/ML02_Model_Card.md",
            "vault/15_ML_Models/ML03_Model_Card.md",
        ],
        advertencias=[
            (
                "Los tres Model Cards siguen en estado in_review: las métricas mostradas "
                "pueden cambiar con la próxima corrida de C3."
            ),
        ],
        bloques=[
            BloqueTabla(
                columnas=["Modelo", "Propósito", "Métrica actual", "Estado"],
                filas=[
                    [
                        "ML-01 · Regresión de matrícula",
                        "Predice la variación de matrícula por escuela (o municipio × nivel); su salida se transforma en un índice de riesgo [0,1].",
                        "MAE < 0.03, RMSE < 0.05 — provienen de datos sintéticos, la corrida con datos reales está bloqueada por un error interno de scikit-learn.",
                        "in_review",
                    ],
                    [
                        "ML-02 · Clasificación del driver dominante",
                        "Clasifica cuál de los 6 drivers explica mejor el riesgo de una escuela — el corazón prescriptivo del proyecto.",
                        "F1 macro ≥ 0.60, Precision ≥ 0.50 por clase — el target sigue siendo un proxy pendiente de confirmación experta.",
                        "in_review",
                    ],
                    [
                        "ML-03 · Clustering de escuelas",
                        "Agrupa escuelas con perfiles similares, independientemente de su índice de riesgo directo.",
                        "Silhouette Score = 0.1086 — por debajo del umbral mínimo de aceptación (≥ 0.30); requiere iteración adicional.",
                        "in_review",
                    ],
                ],
            ),
        ],
    )


_REGISTRO: dict[str, tuple[str, int, Callable[[RepositorioAbout], SeccionOut]]] = {
    "arquitectura": ("Arquitectura del backend", 1, _seccion_arquitectura),
    "modelo-datos": ("Modelo de datos", 2, _seccion_modelo_datos),
    "capas": ("Capas: bronze, silver, gold", 3, _seccion_capas),
    "cubos": ("Cubos de Gold", 4, _seccion_cubos),
    "stack": ("Memoria técnica", 5, _seccion_stack),
    "decisiones": ("Decisiones de arquitectura (ADRs)", 6, _seccion_decisiones),
    "modelos-ml": ("Modelos de Machine Learning", 7, _seccion_modelos_ml),
}


@router.get("/secciones", response_model=list[SeccionResumen])
def listar_secciones() -> list[SeccionResumen]:
    """El manifest: qué secciones hay hoy, en qué orden. Agregar una sección nueva es agregar
    una entrada aquí (+ su función de contenido) -- la página no cambia."""
    return [
        SeccionResumen(id=id_, titulo=titulo, orden=orden)
        for id_, (titulo, orden, _constructor) in sorted(_REGISTRO.items(), key=lambda kv: kv[1][1])
    ]


@router.get("/secciones/{id_seccion}", response_model=SeccionOut)
def obtener_seccion(
    id_seccion: str,
    repo: RepositorioAbout = Depends(get_repositorio_about),
) -> SeccionOut:
    """El contenido de una sección, siempre con el sobre `{id, titulo, fuente, advertencias,
    bloques}` -- ver el docstring del módulo."""
    entrada = _REGISTRO.get(id_seccion)
    if entrada is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sección inexistente.")
    _titulo, _orden, constructor = entrada
    return constructor(repo)
