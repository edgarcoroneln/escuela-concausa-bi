"""Cómo funciona FARO (US-601): backend, modelo de datos, capas, cubos y memoria técnica.

**Renderer genérico, no una función por sección.** La página pide el manifest de
`/api/v1/about/secciones` y por cada entrada pide su contenido — nunca sabe de antemano cuántas
secciones hay ni su forma interna, solo sabe pintar los 7 tipos de bloque
(`markdown`/`mermaid`/`tabla`/`metricas`/`mapa`/`barras`/`diagrama_flujo`). Agregar, quitar o
reordenar una sección es un cambio del backend (`src/api/v1/about.py`) únicamente: esta página no
se vuelve a tocar. Ver `PLAN_US225_COMO_FUNCIONA.md` para el porqué (el hotfix corre en paralelo
con cambios de Gold, ADRs y Model Cards de otras células).

**Por qué mapa/barras/diagrama de flujo son D3 vía HTML embebido, no widgets de Streamlit.**
Streamlit se va a dejar de usar pronto (migración a React/Angular). HTML/JS puro embebido con
`components.html` -- igual que ya se hace con el diagrama E-R en mermaid -- es lo único de esta
página que sobrevive esa migración sin reescritura; un `st.dataframe`/tarjetas nativas no.

Sección de **lectura pública**: es metadata del sistema, no dato de escuela, así que no exige
sesión ni rol (a diferencia de `2_Panel_ML.py`/`3_Chat.py`).
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict

import streamlit as st
import streamlit.components.v1 as components

from about_client import (
    AboutNoDisponible,
    BloqueBarras,
    BloqueDesconocido,
    BloqueDiagramaFlujo,
    BloqueMapa,
    BloqueMarkdown,
    BloqueMermaid,
    BloqueMetricas,
    BloqueTabla,
    listar_secciones,
    obtener_seccion,
)
from auth import encabezado

API_BASE_URL = os.environ.get("FARO_API_BASE_URL", "http://localhost:8000").rstrip("/")

#: Altura por defecto de un bloque D3. Los tres bloques D3 usan `viewBox` + `width: 100%`, así
#: que escalan con el ancho del contenedor de Streamlit; solo la altura del iframe es fija.
_ALTO_D3 = 460

#: Cada bloque D3 vive en su propio iframe (`components.html`), documento HTML aparte -- sin esto
#: hereda el modo oscuro del navegador/SO (`prefers-color-scheme`) y el texto oscuro que se
#: escribe más abajo (`fill:#0f172a`) queda invisible sobre un fondo igual de oscuro. Se fija
#: blanco/claro siempre, sin importar el tema del sistema (hallazgo del usuario: "el fondo es
#: negro y las letras son negras" en mapa y cubos).
_ESTILO_CLARO = """
<style>
  :root { color-scheme: light; }
  html, body { background: #ffffff; margin: 0; }
</style>
"""


def _json_para_script(obj) -> str:
    """JSON seguro para incrustar dentro de un `<script>` -- escapa `<` para que un valor que
    contenga literalmente `</script>` no cierre la etiqueta antes de tiempo."""
    return json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")


def _mermaid_html(codigo: str) -> str:
    """Mismo patrón de HTML embebido (`components.html`) que `1_Dashboards.py` usa para el SDK
    de Superset: no depende de que la versión instalada de Streamlit soporte mermaid nativo."""
    return f"""
    {_ESTILO_CLARO}
    <pre class="mermaid">{codigo}</pre>
    <script src="https://unpkg.com/mermaid@10/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{ startOnLoad: true, theme: "default" }});</script>
    """


def _mapa_html(bloque: BloqueMapa) -> str:
    """Mapa D3 (`d3.geoMercator` + `d3.geoPath`, sin librería de mapas). `fondo` (si viene) es la
    silueta nacional simplificada, gris, detrás de los municipios de los 4 estados resaltados --
    pedido explícito del usuario tras ver el mapa sin contexto del resto del país. La proyección
    encuadra el `fondo` cuando existe (así los 4 estados se ven en su posición real dentro de
    México), o los municipios solos si no."""
    geojson_js = _json_para_script(bloque.geojson)
    fondo_js = _json_para_script(bloque.fondo) if bloque.fondo else "null"
    resaltados_js = _json_para_script([asdict(r) for r in bloque.resaltados])
    return f"""
    {_ESTILO_CLARO}
    <div id="mapa" style="width:100%"></div>
    <script src="https://unpkg.com/d3@7/dist/d3.min.js"></script>
    <script>
      const geojson = {geojson_js};
      const fondo = {fondo_js};
      const resaltados = {resaltados_js};
      const colorPorEntidad = Object.fromEntries(resaltados.map(r => [r.cve_ent, r.color]));
      const nombrePorEntidad = Object.fromEntries(resaltados.map(r => [r.cve_ent, r.nombre]));

      const ancho = document.getElementById("mapa").clientWidth || 760;
      const alto = {_ALTO_D3 - 60};
      const svg = d3.select("#mapa").append("svg")
        .attr("viewBox", `0 0 ${{ancho}} ${{alto}}`)
        .attr("width", "100%").attr("height", alto);

      const proyeccion = d3.geoMercator().fitSize([ancho, alto], fondo || geojson);
      const path = d3.geoPath(proyeccion);

      if (fondo) {{
        svg.append("g").selectAll("path")
          .data(fondo.features)
          .join("path")
            .attr("d", path)
            .attr("fill", "#e2e8f0")
            .attr("stroke", "#cbd5e1").attr("stroke-width", 0.6)
          .append("title").text("México (silueta simplificada, decorativa)");
      }}

      svg.append("g").selectAll("path")
        .data(geojson.features)
        .join("path")
          .attr("d", path)
          .attr("fill", d => colorPorEntidad[d.properties.cve_ent] || "#94a3b8")
          .attr("stroke", "#fff").attr("stroke-width", 0.4)
        .append("title")
          .text(d => `${{d.properties.nombre_municipio}} · ${{nombrePorEntidad[d.properties.cve_ent] || d.properties.nombre_entidad}}`);

      const leyenda = svg.append("g").attr("transform", `translate(12,12)`);
      const filasLeyenda = fondo ? [{{nombre: "Resto de México", color: "#e2e8f0"}}, ...resaltados] : resaltados;
      filasLeyenda.forEach((r, i) => {{
        const fila = leyenda.append("g").attr("transform", `translate(0,${{i * 18}})`);
        fila.append("rect").attr("width", 12).attr("height", 12)
          .attr("fill", r.color).attr("stroke", "#cbd5e1").attr("stroke-width", 0.5);
        fila.append("text").attr("x", 18).attr("y", 10).attr("font-size", 12)
          .attr("font-family", "sans-serif").attr("fill", "#0f172a").text(r.nombre);
      }});
    </script>
    """


def _barras_html(bloque: BloqueBarras) -> str:
    """Barras horizontales D3, una fila por capa (bronze/silver/gold). Reemplaza al icicle
    original (US-601, retroalimentación del usuario): con datos tan dispares -- gold ~6x más
    grande que silver -- el icicle repartía el ancho por proporción y silver casi desaparecía.
    Aquí cada capa tiene su propia fila de altura fija, siempre legible."""
    items_js = _json_para_script([asdict(i) for i in bloque.items])
    colores_js = _json_para_script(["#B08968", "#8D99AE", "#D4AF37"])  # bronce, plata, oro
    alto_fila = 56
    alto = len(bloque.items) * alto_fila + 20
    return f"""
    {_ESTILO_CLARO}
    <div id="barras" style="width:100%"></div>
    <script src="https://unpkg.com/d3@7/dist/d3.min.js"></script>
    <script>
      const items = {items_js};
      const colores = {colores_js};
      const altoFila = {alto_fila};
      const ancho = document.getElementById("barras").clientWidth || 760;
      const alto = {alto};
      const margenEtiqueta = 90;
      const margenValor = 90;
      const anchoBarraMax = ancho - margenEtiqueta - margenValor;

      const maxValor = Math.max(1, ...items.filter(d => d.valor !== null).map(d => d.valor));

      const svg = d3.select("#barras").append("svg")
        .attr("viewBox", `0 0 ${{ancho}} ${{alto}}`)
        .attr("width", "100%").attr("height", alto);

      const fila = svg.selectAll("g")
        .data(items)
        .join("g")
          .attr("transform", (d, i) => `translate(0,${{i * altoFila}})`);

      fila.append("text")
        .attr("x", 0).attr("y", altoFila / 2 + 5)
        .attr("font-size", 14).attr("font-family", "sans-serif").attr("font-weight", 600)
        .attr("fill", "#0f172a")
        .text(d => d.etiqueta);

      fila.each(function (d, i) {{
        const g = d3.select(this);
        if (d.valor === null) {{
          g.append("rect")
            .attr("x", margenEtiqueta).attr("y", altoFila / 2 - 12)
            .attr("width", 120).attr("height", 24)
            .attr("fill", "none").attr("stroke", "#94a3b8").attr("stroke-width", 1.5)
            .attr("stroke-dasharray", "4,3");
          g.append("text")
            .attr("x", margenEtiqueta + 60).attr("y", altoFila / 2 + 5)
            .attr("text-anchor", "middle")
            .attr("font-size", 12).attr("font-family", "sans-serif").attr("fill", "#64748b")
            .text("SIN_DATO")
            .append("title").text(d.nota || "Sin materializar todavía.");
          return;
        }}
        const anchoBarra = Math.max(2, (d.valor / maxValor) * anchoBarraMax);
        g.append("rect")
          .attr("x", margenEtiqueta).attr("y", altoFila / 2 - 14)
          .attr("width", anchoBarra).attr("height", 28)
          .attr("rx", 3)
          .attr("fill", colores[i % colores.length]);
        g.append("text")
          .attr("x", margenEtiqueta + anchoBarra + 8).attr("y", altoFila / 2 + 5)
          .attr("font-size", 13).attr("font-family", "sans-serif").attr("fill", "#0f172a")
          .text(Math.round(d.valor).toLocaleString());
      }});
    </script>
    """


def _flujo_html(bloque: BloqueDiagramaFlujo) -> str:
    """Diagrama de 3 columnas con curvas (D3, sin plugin de Sankey): tablas fuente → cubos →
    dashboards. Resalta al pasar el mouse los enlaces conectados a un nodo."""
    nodos_js = _json_para_script([asdict(n) for n in bloque.nodos])
    enlaces_js = _json_para_script([asdict(e) for e in bloque.enlaces])
    return f"""
    {_ESTILO_CLARO}
    <div id="flujo" style="width:100%"></div>
    <script src="https://unpkg.com/d3@7/dist/d3.min.js"></script>
    <script>
      const nodos = {nodos_js};
      const enlaces = {enlaces_js};
      const ancho = document.getElementById("flujo").clientWidth || 900;
      const porColumna = [0, 1, 2].map(c => nodos.filter(n => n.columna === c));
      const filasMax = Math.max(...porColumna.map(c => c.length), 1);
      const alto = Math.max({_ALTO_D3}, filasMax * 26);

      const xColumna = [60, ancho / 2, ancho - 60];
      const pos = {{}};
      porColumna.forEach((col, c) => {{
        const paso = alto / (col.length + 1);
        col.forEach((n, i) => {{ pos[n.id] = {{x: xColumna[c], y: paso * (i + 1)}}; }});
      }});

      const svg = d3.select("#flujo").append("svg")
        .attr("viewBox", `0 0 ${{ancho}} ${{alto}}`)
        .attr("width", "100%").attr("height", alto);

      const enlace = d3.linkHorizontal()
        .source(e => [pos[e.origen].x + 4, pos[e.origen].y])
        .target(e => [pos[e.destino].x - 4, pos[e.destino].y]);

      const rutas = svg.append("g").selectAll("path")
        .data(enlaces)
        .join("path")
          .attr("d", enlace)
          .attr("fill", "none")
          .attr("stroke", "#94a3b8")
          .attr("stroke-width", 1.2)
          .attr("opacity", 0.45);

      const nodo = svg.append("g").selectAll("g")
        .data(nodos)
        .join("g")
          .attr("transform", d => `translate(${{pos[d.id].x}},${{pos[d.id].y}})`)
          .style("cursor", "pointer")
          .on("mouseenter", (_ev, d) => {{
            rutas.attr("opacity", e => (e.origen === d.id || e.destino === d.id) ? 0.9 : 0.08);
          }})
          .on("mouseleave", () => rutas.attr("opacity", 0.45));

      nodo.append("circle").attr("r", 5)
        .attr("fill", d => d.columna === 0 ? "#4C72B0" : d.columna === 1 ? "#D4AF37" : "#55A868");

      nodo.append("text")
        .attr("x", d => d.columna === 2 ? -9 : 9)
        .attr("y", 4)
        .attr("text-anchor", d => d.columna === 2 ? "end" : "start")
        .attr("font-size", 10.5).attr("font-family", "sans-serif")
        .attr("fill", "#0f172a")
        .text(d => d.etiqueta)
        .append("title").text(d => d.etiqueta);

      nodo.select("circle").append("title").text(d => d.etiqueta);
    </script>
    """


def _render_bloque(bloque) -> None:
    if isinstance(bloque, BloqueMarkdown):
        st.markdown(bloque.texto)
    elif isinstance(bloque, BloqueTabla):
        filas = {
            columna: [fila[i] for fila in bloque.filas]
            for i, columna in enumerate(bloque.columnas)
        }
        st.table(filas)
    elif isinstance(bloque, BloqueMetricas):
        if not bloque.items:
            return
        columnas = st.columns(len(bloque.items))
        for columna, item in zip(columnas, bloque.items):
            with columna:
                st.metric(
                    item.etiqueta,
                    item.valor if item.valor is not None else "SIN_DATO",
                    help=item.nota,
                )
    elif isinstance(bloque, BloqueMermaid):
        components.html(_mermaid_html(bloque.codigo), height=420, scrolling=True)
    elif isinstance(bloque, BloqueMapa):
        components.html(_mapa_html(bloque), height=_ALTO_D3, scrolling=False)
    elif isinstance(bloque, BloqueBarras):
        alto_barras = len(bloque.items) * 56 + 40
        components.html(_barras_html(bloque), height=alto_barras, scrolling=False)
    elif isinstance(bloque, BloqueDiagramaFlujo):
        # Alto variable: un diagrama con muchos nodos por columna necesita más alto que
        # `_ALTO_D3` para no amontonar etiquetas -- se calcula igual que dentro del script.
        filas_max = max((len([n for n in bloque.nodos if n.columna == c]) for c in range(3)), default=1)
        alto = max(_ALTO_D3, filas_max * 26) + 20
        components.html(_flujo_html(bloque), height=alto, scrolling=True)
    elif isinstance(bloque, BloqueDesconocido):
        # Contrato hacia adelante (US-601): un tipo de bloque nuevo no tumba la página, solo
        # se avisa que esta sección tiene contenido que este cliente todavía no sabe pintar.
        st.warning(f"Tipo de bloque no soportado todavía por esta página: `{bloque.tipo}`.")


def _render_seccion(id_seccion: str) -> None:
    try:
        seccion = obtener_seccion(API_BASE_URL, id_seccion)
    except LookupError as exc:
        st.warning(str(exc))
        return
    except AboutNoDisponible as exc:
        st.warning(f"Esta sección no está disponible ahora mismo: {exc}")
        return
    except ValueError as exc:
        st.warning(f"Esta sección llegó fuera de contrato: {exc}")
        return

    for advertencia in seccion.advertencias:
        st.info(advertencia)

    for bloque in seccion.bloques:
        _render_bloque(bloque)

    if seccion.fuente:
        st.caption("Fuente: " + " · ".join(seccion.fuente))


def render() -> None:
    st.title("Cómo funciona FARO")
    st.caption(
        "Arquitectura del backend, modelo de datos, capas bronze/silver/gold, cubos de Gold, "
        "memoria técnica, decisiones de arquitectura y modelos de ML. Sección pública."
    )
    encabezado()  # solo pinta el estado de sesión; esta página no exige rol

    try:
        secciones = listar_secciones(API_BASE_URL)
    except AboutNoDisponible as exc:
        st.error(f"No se pudo cargar el índice de secciones: {exc}")
        return
    except ValueError as exc:
        st.error(f"El manifest de secciones llegó fuera de contrato: {exc}")
        return

    if not secciones:
        st.info("Todavía no hay secciones publicadas.")
        return

    pestañas = st.tabs([s.titulo for s in secciones])
    for pestaña, resumen in zip(pestañas, secciones):
        with pestaña:
            _render_seccion(resumen.id)


render()
