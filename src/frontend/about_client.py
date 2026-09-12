"""Cliente HTTP de la sección "Cómo funciona" de FARO Web (US-601).

Consume `/api/v1/about/secciones` (el manifest) y `/api/v1/about/secciones/{id}` (el contenido),
devolviendo objetos estables para que la página no sepa de HTTP ni de códigos de estado — mismo
patrón que `prediccion_client.py`/`agente_client.py`: el verbo HTTP es un **seam inyectable**
(`get`), así que las pruebas ejercitan el cliente completo sin red y sin API levantada.

**Por qué el parseo de bloques vive aquí y no en un modelo compartido con la API.** La página
nunca conoce la forma interna de una sección — solo sabe pintar los 7 tipos de bloque
(`markdown`/`mermaid`/`tabla`/`metricas`/`mapa`/`barras`/`diagrama_flujo`). Si mañana se agrega
un tipo de bloque nuevo del lado de la API, `_parsear_bloque` lo captura como `BloqueDesconocido`
en vez de tronar: la sección se pinta con una advertencia en su propio espacio, nunca tumba la
página completa (US-601, ver el plan de flexibilidad).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import httpx


class AboutNoDisponible(ConnectionError):
    """La API de "Cómo funciona" no respondió o no está disponible."""


@dataclass(frozen=True)
class SeccionResumen:
    id: str
    titulo: str
    orden: int


@dataclass(frozen=True)
class BloqueMarkdown:
    texto: str


@dataclass(frozen=True)
class BloqueMermaid:
    codigo: str
    alto: int | None = None


@dataclass(frozen=True)
class BloqueTabla:
    columnas: list[str]
    filas: list[list[str]]


@dataclass(frozen=True)
class MetricaItem:
    etiqueta: str
    valor: str | None  # None => SIN_DATO explícito, la página lo pinta como tal, nunca como "0"
    nota: str | None = None


@dataclass(frozen=True)
class BloqueMetricas:
    items: list[MetricaItem]


@dataclass(frozen=True)
class ResaltadoMapa:
    cve_ent: str
    nombre: str
    color: str


@dataclass(frozen=True)
class BloqueMapa:
    geojson: dict
    resaltados: list[ResaltadoMapa]
    fondo: dict | None = None


@dataclass(frozen=True)
class ItemBarra:
    etiqueta: str
    valor: float | None  # None => SIN_DATO explícito, nunca "0"
    nota: str | None = None


@dataclass(frozen=True)
class BloqueBarras:
    items: list[ItemBarra]


@dataclass(frozen=True)
class NodoFlujo:
    id: str
    columna: int
    etiqueta: str


@dataclass(frozen=True)
class EnlaceFlujo:
    origen: str
    destino: str


@dataclass(frozen=True)
class BloqueDiagramaFlujo:
    nodos: list[NodoFlujo]
    enlaces: list[EnlaceFlujo]


@dataclass(frozen=True)
class BloqueSvg:
    """Diagrama ya dibujado del lado de la API (ver `BloqueSvg` en `src/api/v1/about.py`).

    `alt` viaja aparte del marcado porque el `aria-label` de un `<svg>` dentro de
    `components.html` no llega al lector de pantalla del documento padre: la página lo repite
    fuera del iframe.
    """

    codigo: str
    alt: str
    alto: int | None = None


@dataclass(frozen=True)
class BloqueDesconocido:
    """Un `tipo` de bloque que este cliente todavía no sabe pintar.

    Contrato hacia adelante: un tipo de bloque nuevo el día de mañana no debe romper la página,
    solo esa sección se pinta con una advertencia en vez de su contenido.
    """

    tipo: str


Bloque = (
    BloqueMarkdown
    | BloqueMermaid
    | BloqueTabla
    | BloqueMetricas
    | BloqueMapa
    | BloqueBarras
    | BloqueDiagramaFlujo
    | BloqueSvg
    | BloqueDesconocido
)


@dataclass(frozen=True)
class Seccion:
    id: str
    titulo: str
    fuente: list[str]
    advertencias: list[str]
    bloques: list[Bloque] = field(default_factory=list)


def _cabeceras(access_token: str | None) -> dict[str, str] | None:
    return {"Authorization": f"Bearer {access_token}"} if access_token else None


def _parsear_bloque(payload: dict) -> Bloque:
    tipo = payload.get("tipo")
    try:
        if tipo == "markdown":
            return BloqueMarkdown(texto=str(payload["texto"]))
        if tipo == "mermaid":
            alto = payload.get("alto")
            return BloqueMermaid(
                codigo=str(payload["codigo"]),
                alto=int(alto) if alto is not None else None,
            )
        if tipo == "tabla":
            return BloqueTabla(
                columnas=[str(c) for c in payload["columnas"]],
                filas=[[str(v) for v in fila] for fila in payload["filas"]],
            )
        if tipo == "metricas":
            return BloqueMetricas(
                items=[
                    MetricaItem(
                        etiqueta=str(item["etiqueta"]),
                        valor=None if item.get("valor") is None else str(item["valor"]),
                        nota=item.get("nota"),
                    )
                    for item in payload["items"]
                ]
            )
        if tipo == "mapa":
            return BloqueMapa(
                geojson=payload["geojson"],
                fondo=payload.get("fondo"),
                resaltados=[
                    ResaltadoMapa(
                        cve_ent=str(r["cve_ent"]), nombre=str(r["nombre"]), color=str(r["color"])
                    )
                    for r in payload["resaltados"]
                ],
            )
        if tipo == "barras":
            return BloqueBarras(
                items=[
                    ItemBarra(
                        etiqueta=str(item["etiqueta"]),
                        valor=None if item.get("valor") is None else float(item["valor"]),
                        nota=item.get("nota"),
                    )
                    for item in payload["items"]
                ]
            )
        if tipo == "diagrama_flujo":
            return BloqueDiagramaFlujo(
                nodos=[
                    NodoFlujo(id=str(n["id"]), columna=int(n["columna"]), etiqueta=str(n["etiqueta"]))
                    for n in payload["nodos"]
                ],
                enlaces=[
                    EnlaceFlujo(origen=str(e["origen"]), destino=str(e["destino"]))
                    for e in payload["enlaces"]
                ],
            )
        if tipo == "svg":
            alto = payload.get("alto")
            return BloqueSvg(
                codigo=str(payload["codigo"]),
                alt=str(payload["alt"]),
                alto=int(alto) if alto is not None else None,
            )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Bloque de tipo '{tipo}' fuera de contrato.") from exc
    return BloqueDesconocido(tipo=str(tipo))


def listar_secciones(
    api_base_url: str,
    get: Callable[..., Any] = httpx.get,
    access_token: str | None = None,
) -> list[SeccionResumen]:
    """El manifest: qué secciones hay y en qué orden pintarlas."""
    try:
        response = get(
            f"{api_base_url.rstrip('/')}/api/v1/about/secciones",
            headers=_cabeceras(access_token),
            timeout=15.0,
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise AboutNoDisponible("No se pudo obtener el manifest de 'Cómo funciona'.") from exc

    try:
        secciones = [
            SeccionResumen(id=str(s["id"]), titulo=str(s["titulo"]), orden=int(s["orden"]))
            for s in payload
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("El manifest de 'Cómo funciona' llegó fuera de contrato.") from exc

    return sorted(secciones, key=lambda s: s.orden)


def obtener_seccion(
    api_base_url: str,
    id_seccion: str,
    get: Callable[..., Any] = httpx.get,
    access_token: str | None = None,
) -> Seccion:
    """Contenido de una sección. Los bloques con `tipo` desconocido no rompen el parseo — ver
    `BloqueDesconocido`."""
    try:
        response = get(
            f"{api_base_url.rstrip('/')}/api/v1/about/secciones/{id_seccion}",
            headers=_cabeceras(access_token),
            timeout=15.0,
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise LookupError(f"La sección '{id_seccion}' no existe.") from exc
        raise AboutNoDisponible(f"La API rechazó la sección '{id_seccion}'.") from exc
    except httpx.HTTPError as exc:
        raise AboutNoDisponible(f"No se pudo obtener la sección '{id_seccion}'.") from exc

    try:
        return Seccion(
            id=str(payload["id"]),
            titulo=str(payload["titulo"]),
            fuente=[str(f) for f in payload.get("fuente", [])],
            advertencias=[str(a) for a in payload.get("advertencias", [])],
            bloques=[_parsear_bloque(b) for b in payload["bloques"]],
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"La sección '{id_seccion}' llegó fuera de contrato.") from exc
