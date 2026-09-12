"""Sección "Cómo funciona FARO" (US-601): backend (con su diagrama y su memoria técnica),
modelo de datos, capas, cubos, decisiones de arquitectura y modelos de ML, servidos como contrato agnóstico de
frontend (hoy lo consume Streamlit; el mismo contrato sirve para React/Angular más adelante).

**Por qué dos rutas y no siete.** Este hotfix corre en paralelo con el resto del equipo: Gold
puede ganar columnas o cubos, hay ADRs `proposed` que pueden pasar a `accepted`, y los tres Model
Cards de C3 siguen `in_review`. Si cada sección fuera un endpoint con su propio *shape*, cualquiera
de esos cambios obligaría a tocar también la página de Streamlit. En vez de eso, `/secciones`
publica un **manifest** (qué secciones hay) y `/secciones/{id}` responde siempre el mismo **sobre
genérico** de bloques (`markdown` | `mermaid` | `tabla` | `metricas` | `mapa` | `barras` |
`diagrama_flujo` | `svg`): agregar, quitar o reordenar una sección es un cambio de este archivo
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

import html
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
# El sobre genérico: 8 tipos de bloque, cada uno con su propio renderer en la página.
# --------------------------------------------------------------------------- #


class BloqueMarkdown(BaseModel):
    tipo: Literal["markdown"] = "markdown"
    texto: str


class BloqueMermaid(BaseModel):
    """Diagrama en código mermaid, para que el frontend lo dibuje.

    **Hoy ninguna sección emite este tipo.** Los cuatro E-R que lo usaban pasaron a `svg`
    (`_er_gold`, `_er_bronze`, `_er_silver`) porque obligaba a cada interfaz a traer un motor de
    diagramas: en la SPA de React la única librería disponible arrastra dos avisos de severidad
    alta, 69 paquetes transitivos y 123 MB.

    Se conserva en el contrato **a propósito y con fecha de revisión**: el tipo lo diseñó Manuel
    Serranía y retirarlo es una decisión suya, no un efecto colateral de esta portación. Si al
    revisarlo se confirma que no vuelve, quitarlo deja el contrato honestamente libre de
    dependencias de dibujo — que es lo que permite estrenar un frontend sin negociar librerías.
    """

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


class BloqueSvg(BaseModel):
    """Diagrama dibujado a mano, servido como SVG ya armado.

    Es el único bloque que no manda datos para que el frontend los dibuje. La razón es que su
    disposición es una decisión editorial, no un resultado de los datos: qué componente va al
    lado de cuál, por dónde rodea una flecha para no cruzar una caja, cuáles llevan borde grueso.
    Mandar nodos y aristas obligaría a escribir un motor de layout en el cliente para reproducir
    una colocación que de todas formas se fijó a mano -- y cualquier reacomodo automático
    volvería a cruzar las cajas que este trazo evita a propósito.

    El SVG se arma en `_diagrama_arquitectura()` a partir de tablas de datos (`_ARQ_COMPONENTES`,
    `_ARQ_FLECHAS`), así que editar el diagrama es editar esas tablas, no el marcado.

    `alt` viaja aparte porque el frontend lo necesita para el texto alternativo del iframe: el
    `aria-label` del `<svg>` no llega a un lector de pantalla desde dentro de `components.html`.
    """

    tipo: Literal["svg"] = "svg"
    codigo: str
    alt: str
    #: Alto en px del iframe, por el mismo motivo que `BloqueMermaid.alto`: `components.html` no
    #: hace auto-resize. `None` usa el alto por defecto del cliente.
    alto: int | None = None


Bloque = Annotated[
    BloqueMarkdown | BloqueMermaid | BloqueTabla | BloqueMetricas | BloqueMapa | BloqueBarras
    | BloqueDiagramaFlujo | BloqueSvg,
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


#: Color por célula dueña. Los tres primeros son los que ya usa el diagrama de cubos
#: (`_flujo_html` en el frontend); C3/C4/C5 extienden la misma familia para que las cinco
#: convivan sin desentonar. El color codifica **quién es dueño**, no en qué etapa va el
#: componente: la sección afirma que el backend son "5 franjas verticales" y el diagrama lo
#: enseña en vez de repetirlo.
_ARQ_CELULAS: dict[str, tuple[str, str]] = {
    "C1": ("#4C72B0", "C1 · Data Engineering & Quality"),
    "C2": ("#55A868", "C2 · Analytics & BI"),
    "C3": ("#8172B2", "C3 · ML & Agente IA"),
    "C4": ("#C44E52", "C4 · Backend, API & Seguridad"),
    "C5": ("#937860", "C5 · Cloud & DevOps"),
}

#: Cajas del diagrama. `enfasis` marca los tres puntos por los que pasa todo lo demás (borde
#: grueso); `punteado` marca lo que no es código nuestro. `celula=None` => sin dueño interno.
#: Las coordenadas son a mano y están verificadas contra `_ARQ_FLECHAS` para que ninguna
#: etiqueta caiga encima de una caja -- ver `tests/test_about_diagrama.py`.
_ARQ_COMPONENTES: list[dict] = [
    {"x": 24, "y": 250, "w": 150, "h": 70, "celula": None, "punteado": True,
     "titulo": "8 fuentes públicas", "subs": ["DS-01 … DS-08"], "centrado": True},
    {"x": 224, "y": 250, "w": 160, "h": 70, "celula": "C1",
     "titulo": "Apache Airflow", "subs": ["Orquesta la ingesta", "6 cadencias de DAG"]},
    {"x": 434, "y": 120, "w": 220, "h": 56, "celula": "C1",
     "titulo": "dbt-core", "subs": ["9 modelos Silver · 15 Gold"]},
    {"x": 434, "y": 222, "w": 220, "h": 126, "celula": "C1", "enfasis": True,
     "titulo": "PostgreSQL", "subs": ["Cloud SQL en producción"], "capas": True,
     "subs_bajas": ["Bronze y Silver nacionales", "Gold acotado a 4 entidades"]},
    {"x": 434, "y": 396, "w": 220, "h": 62, "celula": "C1",
     "titulo": "Great Expectations", "subs": ["+ Pydantic — por capa", "y por registro"]},
    {"x": 714, "y": 196, "w": 180, "h": 78, "celula": "C3",
     "titulo": "scikit-learn · XGBoost",
     "subs": ["+ MLflow (registro)", "ML-01 · ML-02 · ML-03", "partición temporal"]},
    {"x": 714, "y": 330, "w": 180, "h": 78, "celula": "C3",
     "titulo": "ChromaDB",
     "subs": ["+ sentence-transformers", "recuperación de contexto", "(RAG) del agente"]},
    {"x": 954, "y": 250, "w": 180, "h": 82, "celula": "C4", "enfasis": True,
     "titulo": "FastAPI",
     "subs": ["OAuth2 · JWT · RBAC", "Gold, predicciones,", "agente y esta sección"]},
    {"x": 954, "y": 110, "w": 180, "h": 64, "celula": "C2",
     "titulo": "Apache Superset", "subs": ["10 dashboards", "sobre los 9 cubos"]},
    {"x": 1194, "y": 200, "w": 150, "h": 112, "celula": "C2", "enfasis": True,
     "titulo": "FARO Web",
     "subs": ["Streamlit — shell único", "· dashboards", "· panel de ML",
              "· chat del agente", "· login por rol"]},
]

#: Las tres capas dentro de la caja de PostgreSQL, con los mismos colores que las barras de
#: la sección "Capas" (`_barras_capas`), para que se lean como la misma cosa en las dos.
_ARQ_CAPAS: list[tuple[int, int, str, str]] = [
    (450, 62, "BRONZE", "#B08968"),
    (518, 58, "SILVER", "#8D99AE"),
    (582, 56, "GOLD", "#D4AF37"),
]

#: Flechas. `d` es un `path` cuando la flecha tiene que rodear una caja; `linea` cuando es
#: recta. `punteada` = escritura de vuelta sobre una capa que ya existía.
_ARQ_FLECHAS: list[dict] = [
    {"linea": (174, 285, 218, 285), "etq": "descarga", "ex": 196, "ey": 277, "anc": "middle"},
    {"linea": (384, 285, 428, 285), "etq": "carga", "ex": 406, "ey": 277, "anc": "middle"},
    {"linea": (544, 176, 544, 216), "etq": "bronze → silver → gold", "ex": 552, "ey": 200},
    {"linea": (544, 396, 544, 354), "etq": "valida cada capa", "ex": 552, "ey": 380},
    {"linea": (660, 238, 708, 224), "etq": "features_escuela", "ex": 666, "ey": 214,
     "anc": "middle"},
    {"linea": (708, 256, 660, 270), "etq": "predicciones", "ex": 690, "ey": 290,
     "anc": "middle", "punteada": True},
    {"d": "M 660 232 H 684 V 142 H 948", "etq": "9 cubos de Gold", "ex": 820, "ey": 134,
     "anc": "middle"},
    {"linea": (894, 240, 948, 266), "etq": "models:/", "ex": 921, "ey": 238, "anc": "middle"},
    {"linea": (894, 360, 948, 318), "etq": "contexto RAG", "ex": 935, "ey": 382,
     "anc": "middle"},
    {"d": "M 660 332 H 690 V 478 H 1044 V 338",
     "etq": "lee Gold · predicciones · recomendaciones", "ex": 866, "ey": 470, "anc": "middle"},
    {"linea": (1134, 288, 1188, 272), "etq": "REST", "ex": 1161, "ey": 303, "anc": "middle"},
    {"d": "M 1134 142 H 1164 V 230 H 1188", "etq": "embebido", "ex": 1160, "ey": 192,
     "anc": "end"},
]

_ARQ_ANCHO, _ARQ_ALTO = 1360, 620
_ARQ_ALT = (
    "Diagrama de flujo de la arquitectura de FARO: ocho fuentes públicas entran por Apache "
    "Airflow a PostgreSQL, donde dbt-core transforma bronze a silver a gold y Great "
    "Expectations valida cada capa; desde gold, scikit-learn con MLflow entrena los modelos y "
    "escribe predicciones de vuelta, ChromaDB aporta contexto RAG, FastAPI expone todo por "
    "REST, Apache Superset lee los nueve cubos, y FARO Web en Streamlit reúne dashboards, "
    "panel de ML y chat. Docker y GCP Cloud Run empaquetan y despliegan el sistema completo."
)


def _diagrama_arquitectura() -> BloqueSvg:
    """Arma el SVG del diagrama a partir de `_ARQ_COMPONENTES` y `_ARQ_FLECHAS`.

    Todo va con atributos de presentación en línea, sin clases ni `<style>`: el bloque vive en
    su propio iframe (`components.html`) y así no depende de que el frontend defina un CSS que
    haga juego. Los colores son los mismos que ya usa la página, no una paleta nueva.
    """
    e = html.escape
    p: list[str] = [
        (
            f'<svg viewBox="0 0 {_ARQ_ANCHO} {_ARQ_ALTO}" role="img" aria-label="{e(_ARQ_ALT)}" '
            'style="width:100%;min-width:1100px;height:auto;display:block">'
        ),
        (
            '<defs><marker id="arq-f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/></marker></defs>'
        ),
    ]
    rotulo = 'font-family="sans-serif" font-size="10.5" font-weight="600" letter-spacing="0.9" fill="#94a3b8"'  # noqa: E501
    titulo = 'font-family="sans-serif" font-size="12.5" font-weight="600" fill="#0f172a"'
    sub = 'font-family="sans-serif" font-size="10.5" fill="#64748b"'
    flecha = 'font-family="sans-serif" font-size="10" fill="#64748b"'

    for x, txt in ((99, "FUENTES"), (304, "INGESTA"), (544, "ALMACÉN Y TRANSFORMACIÓN"),
                   (804, "INTELIGENCIA"), (1044, "EXPOSICIÓN"), (1269, "PRESENTACIÓN")):
        p.append(f'<text x="{x}" y="34" text-anchor="middle" {rotulo}>{e(txt)}</text>')

    for c in _ARQ_COMPONENTES:
        borde = "#94a3b8" if c.get("enfasis") else "#cbd5e1"
        grosor = "1.6" if c.get("enfasis") else "1"
        relleno = "#f8fafc" if c.get("punteado") else "#ffffff"
        guion = ' stroke-dasharray="4 3"' if c.get("punteado") else ""
        p.append(
            f'<rect x="{c["x"]}" y="{c["y"]}" width="{c["w"]}" height="{c["h"]}" rx="4" '
            f'fill="{relleno}" stroke="{borde}" stroke-width="{grosor}"{guion}/>'
        )
        if c.get("centrado"):
            cx = c["x"] + c["w"] / 2
            p.append(f'<text x="{cx}" y="{c["y"] + 30}" text-anchor="middle" {titulo}>{e(c["titulo"])}</text>')  # noqa: E501
            for i, s in enumerate(c["subs"]):
                p.append(f'<text x="{cx}" y="{c["y"] + 48 + i * 15}" text-anchor="middle" {sub}>{e(s)}</text>')  # noqa: E501
            continue

        tx, ty = c["x"] + 16, c["y"] + 18
        if c["celula"]:
            p.append(f'<circle cx="{tx}" cy="{ty}" r="4.5" fill="{_ARQ_CELULAS[c["celula"]][0]}"/>')
        p.append(f'<text x="{tx + 13}" y="{ty + 4}" {titulo}>{e(c["titulo"])}</text>')
        for i, s in enumerate(c["subs"]):
            p.append(f'<text x="{tx}" y="{ty + 23 + i * 15}" {sub}>{e(s)}</text>')

        if c.get("capas"):
            for cx0, ancho, nombre, color in _ARQ_CAPAS:
                p.append(f'<rect x="{cx0}" y="278" width="{ancho}" height="22" rx="3" fill="{color}"/>')  # noqa: E501
                p.append(
                    f'<text x="{cx0 + ancho / 2}" y="293" text-anchor="middle" '
                    f'font-family="sans-serif" font-size="9.5" font-weight="600" '
                    f'fill="#ffffff">{e(nombre)}</text>'
                )
            for i, s in enumerate(c.get("subs_bajas", [])):
                p.append(f'<text x="{c["x"] + 16}" y="{323 + i * 15}" {sub}>{e(s)}</text>')

    for f in _ARQ_FLECHAS:
        guion = ' stroke-dasharray="4 3"' if f.get("punteada") else ""
        if "d" in f:
            p.append(
                f'<path d="{f["d"]}" fill="none" stroke="#94a3b8" stroke-width="1.3"'
                f'{guion} marker-end="url(#arq-f)"/>'
            )
        else:
            x1, y1, x2, y2 = f["linea"]
            p.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#94a3b8" '
                f'stroke-width="1.3"{guion} marker-end="url(#arq-f)"/>'
            )
        anc = f' text-anchor="{f["anc"]}"' if f.get("anc") else ""
        p.append(f'<text x="{f["ex"]}" y="{f["ey"]}"{anc} {flecha}>{e(f["etq"])}</text>')

    # Banda de despliegue: no es un paso del flujo, envuelve a los demás -- por eso va como
    # banda punteada al pie y no como una caja más en la fila.
    p.append(
        '<rect x="24" y="500" width="1320" height="58" rx="4" fill="#f8fafc" stroke="#cbd5e1" '
        'stroke-width="1" stroke-dasharray="5 4"/>'
    )
    p.append(f'<circle cx="44" cy="522" r="4.5" fill="{_ARQ_CELULAS["C5"][0]}"/>')
    p.append(f'<text x="57" y="526" {titulo}>Docker + docker-compose · GCP Cloud Run</text>')
    p.append(
        f'<text x="44" y="545" {sub}>Empaqueta y despliega todo lo anterior detrás de una URL '
        'pública. No es un paso del flujo: envuelve los nueve componentes de arriba.</text>'
    )

    for cx0, clave in ((30, "C1"), (266, "C2"), (436, "C3"), (616, "C4"), (850, "C5")):
        color, nombre = _ARQ_CELULAS[clave]
        p.append(f'<circle cx="{cx0}" cy="590" r="4.5" fill="{color}"/>')
        p.append(
            f'<text x="{cx0 + 12}" y="594" font-family="sans-serif" font-size="11" '
            f'fill="#334155">{e(nombre)}</text>'
        )

    p.append("</svg>")
    return BloqueSvg(codigo="".join(p), alt=_ARQ_ALT, alto=560)


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
            BloqueMarkdown(
                texto=(
                    "**Cómo leer el diagrama de abajo.** El color de cada punto indica la "
                    "célula dueña, no la etapa del flujo. Las flechas dicen qué le pasa a "
                    "quién: si una desaparece, algo deja de funcionar. La única punteada "
                    "—`predicciones`— es una escritura de vuelta: los modelos leen de Gold y "
                    "publican en Gold, no en una base aparte. Los tres recuadros de borde "
                    "grueso (PostgreSQL, FastAPI y FARO Web) son los puntos por los que pasa "
                    "todo lo demás. El recuadro punteado de las fuentes no tiene dueño porque "
                    "no es código nuestro: son los portales públicos de las dependencias."
                )
            ),
            _diagrama_arquitectura(),
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
            BloqueMarkdown(
                texto=(
                    "### Memoria técnica\n"
                    "Las mismas piezas de arriba, vistas por capa en vez de por dueño. Python "
                    "3.11 en todo el backend (PEP 8, docstrings, type hints)."
                )
            ),
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


#: Compartido entre `modelo-datos` (responde "cómo está estructurado Gold") y `capas` (responde
#: "en qué cambió Gold respecto a Silver") -- misma figura, dos preguntas, para no mantener dos
#: copias del mismo diagrama que puedan desalinearse.

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
            _er_gold(),
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
            _er_bronze(),
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
            _er_silver(),
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
            _er_gold(),
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
                    ["ADR-011", "Rediseño UX/UI narrativo con gráficas nativas como experiencia principal", "accepted", "2026-09-10"],
                    ["ADR-012", "Retiro del embebido de Superset/Streamlit: frontend nativo en React", "accepted", "2026-09-10"],
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
    "decisiones": ("Decisiones de arquitectura (ADRs)", 5, _seccion_decisiones),
    "modelos-ml": ("Modelos de Machine Learning", 6, _seccion_modelos_ml),
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


# --------------------------------------------------------------------------- #
# Diagramas E-R servidos como SVG (US-601)
#
# **Por qué dejaron de ser `mermaid`.** Los cuatro E-R se servían como código mermaid y el
# frontend los dibujaba. Eso obligaba a que CADA interfaz trajera un motor de diagramas: en la
# SPA de React la única librería disponible arrastra `chevrotain` → `lodash-es` con dos avisos de
# severidad alta, 69 paquetes transitivos y 123 MB — para dibujar cuatro cajas con flechas.
#
# Dibujarlos aquí una sola vez los vuelve `svg`, el mismo tipo de bloque que ya usa el diagrama
# de arquitectura: **cero dependencias en cualquier frontend, presente o futuro**, y un solo
# lugar donde se edita. Es también lo que hace posible retirar Streamlit (`ADR-012`) sin perder
# los diagramas por el camino.
#
# La disposición es a mano, como en `_diagrama_arquitectura`, y por la misma razón: colocar cajas
# y rodear flechas es una decisión editorial. `tests/test_about_diagrama.py` la protege.
# --------------------------------------------------------------------------- #

#: Una caja del E-R: (x, y, ancho, alto, nombre, nota). `nota` va en segunda línea, más chica.
_Entidad = tuple[int, int, int, int, str, str]

#: Una relación: (desde, hacia, etiqueta, cardinalidad, punteada). `cardinalidad` se imprime tal
#: cual ("1 · N", "1 · 1"); `punteada` marca un cruce que **no** está respaldado por una llave
#: foránea — en Bronze ninguna lo está, y eso es justo lo que el diagrama debe dejar ver.
_Relacion = tuple[str, str, str, str, bool]


def _caja_por_nombre(entidades: list[_Entidad], nombre: str) -> _Entidad:
    for e in entidades:
        if e[4] == nombre:
            return e
    raise KeyError(f"El E-R referencia una entidad inexistente: {nombre!r}")


def _borde_hacia(origen: _Entidad, destino: _Entidad) -> tuple[float, float, float, float]:
    """Punto de salida y de llegada entre dos cajas, por el lado que las enfrenta.

    Sale del borde, no del centro: una flecha que arranca dentro de la caja se ve como si la
    atravesara.
    """
    ox, oy, ow, oh, _n, _t = origen
    dx, dy, dw, dh, _n2, _t2 = destino
    ocx, ocy = ox + ow / 2, oy + oh / 2
    dcx, dcy = dx + dw / 2, dy + dh / 2

    if abs(dcx - ocx) >= abs(dcy - ocy):  # se enfrentan de lado
        if dcx > ocx:
            return ox + ow, ocy, dx, dcy
        return ox, ocy, dx + dw, dcy
    if dcy > ocy:  # se enfrentan de arriba a abajo
        return ocx, oy + oh, dcx, dy
    return ocx, oy, dcx, dy + dh


def _er_a_svg(
    entidades: list[_Entidad],
    relaciones: list[_Relacion],
    ancho: int,
    alto: int,
    alt: str,
) -> BloqueSvg:
    """Dibuja un diagrama entidad-relación con la misma paleta que el resto de la sección."""
    e = html.escape
    titulo = 'font-family="sans-serif" font-size="12" font-weight="600" fill="#0f172a"'
    nota = 'font-family="sans-serif" font-size="9.5" fill="#64748b"'
    etiqueta = 'font-family="sans-serif" font-size="9.5" fill="#64748b"'

    p: list[str] = [
        (
            f'<svg viewBox="0 0 {ancho} {alto}" role="img" aria-label="{e(alt)}" '
            'style="width:100%;min-width:820px;height:auto;display:block">'
        ),
        (
            '<defs><marker id="er-f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/></marker></defs>'
        ),
    ]

    # Las relaciones van primero: así ninguna línea queda encima de una caja.
    for desde, hacia, texto, cardinalidad, punteada in relaciones:
        origen = _caja_por_nombre(entidades, desde)
        destino = _caja_por_nombre(entidades, hacia)
        x1, y1, x2, y2 = _borde_hacia(origen, destino)
        guion = ' stroke-dasharray="4 3"' if punteada else ""
        p.append(
            f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#94a3b8" '
            f'stroke-width="1.2"{guion} marker-end="url(#er-f)"/>'
        )
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        p.append(
            f'<text x="{mx:.0f}" y="{my - 5:.0f}" text-anchor="middle" {etiqueta}>'
            f"{e(texto)}</text>"
        )
        if cardinalidad:
            p.append(
                f'<text x="{mx:.0f}" y="{my + 8:.0f}" text-anchor="middle" {etiqueta}>'
                f"{e(cardinalidad)}</text>"
            )

    for x, y, w, h, nombre, texto in entidades:
        p.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#ffffff" '
            'stroke="#cbd5e1" stroke-width="1"/>'
        )
        p.append(f'<text x="{x + 12}" y="{y + 21}" {titulo}>{e(nombre)}</text>')
        if texto:
            p.append(f'<text x="{x + 12}" y="{y + 36}" {nota}>{e(texto)}</text>')

    p.append("</svg>")
    return BloqueSvg(codigo="".join(p), alt=alt, alto=alto + 40)


# ── Gold: el esquema estrella ────────────────────────────────────────────────
_ER_GOLD_ENTIDADES: list[_Entidad] = [
    (20, 44, 200, 58, "dim_escuela", "cct · nivel · lat/lon"),
    (20, 166, 200, 58, "dim_municipio", "cve_mun · rezago"),
    (20, 288, 200, 58, "dim_tiempo", "id_ciclo"),
    (316, 150, 244, 90, "fact_escuela_ciclo", "grano: cct × id_ciclo"),
    (316, 392, 244, 54, "dim_driver", "D1…D6 · catálogo"),
    (660, 44, 232, 58, "features_escuela", "6 drivers + target"),
    (660, 158, 232, 58, "gold.predicciones", "valor · indice_riesgo"),
    (660, 288, 232, 58, "gold.recomendaciones", "driver_dominante · SHAP"),
]
_ER_GOLD_RELACIONES: list[_Relacion] = [
    ("dim_escuela", "fact_escuela_ciclo", "cct", "1 · N", False),
    ("dim_municipio", "fact_escuela_ciclo", "cve_mun", "1 · N", False),
    ("dim_tiempo", "fact_escuela_ciclo", "id_ciclo", "1 · N", False),
    ("fact_escuela_ciclo", "features_escuela", "cct · id_ciclo", "1 · 1", False),
    ("fact_escuela_ciclo", "gold.predicciones", "cct · id_ciclo", "1 · N", False),
    ("fact_escuela_ciclo", "gold.recomendaciones", "cct · id_ciclo", "1 · N", False),
    ("dim_driver", "gold.recomendaciones", "driver_dominante", "1 · N", False),
]
_ER_GOLD_ALT = (
    "Esquema estrella de Gold: dim_escuela, dim_municipio y dim_tiempo se unen al hecho central "
    "fact_escuela_ciclo por cct, cve_mun e id_ciclo; el hecho se une uno a uno con "
    "features_escuela y uno a muchos con gold.predicciones y gold.recomendaciones; dim_driver se "
    "une a recomendaciones por driver_dominante."
)

# ── Bronze: crudo, sin una sola llave foránea ────────────────────────────────
_ER_BRONZE_ENTIDADES: list[_Entidad] = [
    (20, 96, 180, 54, "cct", "catálogo SEP"),
    (330, 20, 220, 48, "formato911", ""),
    (330, 88, 220, 48, "formato911_historico", ""),
    (330, 156, 220, 48, "cemabe", ""),
    (20, 300, 180, 54, "conapo", "población"),
    (330, 240, 220, 48, "sesnsp", ""),
    (330, 308, 220, 48, "coneval_irs", ""),
    (330, 376, 220, 48, "coneval_pobreza", ""),
    (690, 60, 230, 48, "sinaica_estaciones", ""),
    (690, 168, 230, 48, "sinaica_observaciones", ""),
    (690, 320, 230, 62, "conagua_presas", "SIN_DATO en este ambiente"),
]
_ER_BRONZE_RELACIONES: list[_Relacion] = [
    ("cct", "formato911", "cct", "sin FK", True),
    ("cct", "formato911_historico", "cct", "sin FK", True),
    ("cct", "cemabe", "cct", "sin FK", True),
    ("conapo", "sesnsp", "clave municipio", "sin FK", True),
    ("conapo", "coneval_irs", "clave municipio", "sin FK", True),
    ("conapo", "coneval_pobreza", "clave municipio", "sin FK", True),
    ("sinaica_estaciones", "sinaica_observaciones", "id_estacion", "sin FK", True),
]
_ER_BRONZE_ALT = (
    "Bronze: el catálogo cct cruza con formato911, formato911_historico y cemabe; conapo cruza "
    "con sesnsp, coneval_irs y coneval_pobreza por clave de municipio; sinaica_estaciones con "
    "sinaica_observaciones por id_estacion. Todas las líneas van punteadas porque ninguna está "
    "respaldada por una llave foránea: en Bronze los cruces son posibles, no obligados. "
    "conagua_presas aparece sin relaciones porque la fuente no se ha ingerido."
)

# ── Silver: tipado y conformado, con llaves ya homologadas ───────────────────
_ER_SILVER_ENTIDADES: list[_Entidad] = [
    (30, 150, 200, 58, "escuela", "cct homologado a 10"),
    (350, 30, 220, 48, "matricula", ""),
    (350, 98, 220, 48, "matricula_historica", ""),
    (350, 166, 220, 48, "cemabe", ""),
    (350, 300, 230, 58, "poblacion_municipio", "cve_mun a 5 dígitos"),
    (700, 250, 220, 48, "rezago_municipio", ""),
    (700, 330, 220, 48, "delitos_municipio", ""),
    (700, 40, 220, 48, "aire_estacion", ""),
    (700, 120, 220, 48, "agua_region", ""),
]
_ER_SILVER_RELACIONES: list[_Relacion] = [
    ("escuela", "matricula", "cct", "1 · N", False),
    ("escuela", "matricula_historica", "cct", "1 · N", False),
    ("escuela", "cemabe", "cct", "1 · 0..1", False),
    ("escuela", "poblacion_municipio", "cve_mun", "N · 1", False),
    ("poblacion_municipio", "rezago_municipio", "cve_mun", "1 · 0..1", False),
    ("poblacion_municipio", "delitos_municipio", "cve_mun", "1 · N", False),
    ("escuela", "aire_estacion", "IDW · ADR-006", "sin FK", True),
    ("escuela", "agua_region", "IDW · ADR-006", "sin FK", True),
]
_ER_SILVER_ALT = (
    "Silver: escuela se une a matricula, matricula_historica y cemabe por cct ya homologado, y a "
    "poblacion_municipio por clave INEGI de 5 dígitos, que a su vez se une a rezago_municipio y "
    "delitos_municipio. Las dos líneas punteadas hacia aire_estacion y agua_region no son llaves "
    "foráneas sino interpolación espacial IDW (ADR-006)."
)


@lru_cache
def _er_gold() -> BloqueSvg:
    return _er_a_svg(_ER_GOLD_ENTIDADES, _ER_GOLD_RELACIONES, 920, 470, _ER_GOLD_ALT)


@lru_cache
def _er_bronze() -> BloqueSvg:
    return _er_a_svg(_ER_BRONZE_ENTIDADES, _ER_BRONZE_RELACIONES, 950, 450, _ER_BRONZE_ALT)


@lru_cache
def _er_silver() -> BloqueSvg:
    return _er_a_svg(_ER_SILVER_ENTIDADES, _ER_SILVER_RELACIONES, 950, 390, _ER_SILVER_ALT)
