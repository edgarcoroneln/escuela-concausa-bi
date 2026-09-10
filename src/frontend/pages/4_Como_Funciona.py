"""Cómo funciona FARO (US-601): backend, modelo de datos, capas, cubos y memoria técnica.

**Renderer genérico, no una función por sección.** La página pide el manifest de
`/api/v1/about/secciones` y por cada entrada pide su contenido — nunca sabe de antemano cuántas
secciones hay ni su forma interna, solo sabe pintar los 7 tipos de bloque
(`markdown`/`mermaid`/`tabla`/`metricas`/`mapa`/`barras`/`diagrama_flujo`). Agregar, quitar o
reordenar una sección es un cambio del backend (`src/api/v1/about.py`) únicamente: esta página no
se vuelve a tocar. Ver `vault/03_Architecture/Bosquejo_Componentes_US601.md` para el porqué (corre
en paralelo con cambios de Gold, ADRs y Model Cards de otras células).

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

#: Los 4 E-R (mermaid) NO miden lo mismo: medido en vivo con Playwright, Bronze renderiza a ~110px
#: de alto natural, Silver a ~260px, Gold (el más grande) necesita bastante más. `components.html`
#: no tiene mecanismo de auto-resize (se probó `postMessage({type:"streamlit:setFrameHeight"})`:
#: Streamlit lo ignora fuera de un custom component registrado), así que cada `BloqueMermaid`
#: trae su propio `alto` sugerido (`src/api/v1/about.py`, medido igual que estos por Playwright)
#: en vez de forzar uno solo para los 4 -- un alto compartido o dejaba espacio muerto bajo
#: Bronze/Silver, o encogía a Gold hasta volverlo ilegible sin zoom. Este es solo el default
#: para un bloque que no traiga `alto` (retrocompatibilidad).
_ALTO_MERMAID_DEFECTO = 380

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


def _mermaid_html(codigo: str, alto: int) -> str:
    """Mismo patrón de HTML embebido (`components.html`) que `1_Dashboards.py` usa para el SDK
    de Superset: no depende de que la versión instalada de Streamlit soporte mermaid nativo.

    Con pan/zoom (hallazgo del usuario: el E-R de Gold "tiene mucho zoom y sale incompleto").
    `useMaxWidth: false` hace que mermaid renderice el diagrama a su tamaño natural completo en
    vez de encogerlo para caber en el ancho del iframe. El zoom no se aplica sobre la `<svg>` de
    mermaid directamente (su estructura interna no es contrato nuestro) sino sobre el `<div>` que
    la envuelve, vía `transform` CSS. Al cargar, se calcula una escala inicial que ajusta el
    diagrama completo al viewport, para no arrancar mostrando solo una esquina.

    **Bug real diagnosticado con Playwright, no adivinado (causa de "no se visualizan los E-R"):**
    `st.tabs` monta el contenido de las 7 secciones de una vez; las pestañas que no están activas
    quedan en `display:none`. Mientras un iframe vive dentro de un `display:none`, su documento
    interno tiene `clientWidth/clientHeight = 0` -- confirmado inyectando JS en los iframes reales
    de la página. `mermaid.run()` corre de inmediato al cargar, sin esperar a que su pestaña esté
    visible, y calcula el enrutado de las relaciones contra ese viewport de tamaño cero: produce
    rutas SVG degeneradas y `mermaid` truena internamente (`getPointAtLength` sobre un `<path>`
    vacío). `mermaid.run()` **no rechaza la promesa** en ese caso -- atrapa la excepción y renderiza
    su propio ícono de "Syntax error in text" como si fuera un resultado normal, por eso no bastaba
    con un `.catch()`, y **reintentar sin más tampoco alcanza**: una vez que ya corrió sobre el
    documento vacío, repetir en el mismo instante repite el mismo resultado. Confirmado con el
    mismo texto exacto: falla siempre mientras la pestaña está oculta, funciona siempre en cuanto
    se mide `clientWidth > 0`. El fix real es esperar visibilidad (`requestAnimationFrame`, que el
    navegador pausa mientras el iframe está oculto y retoma solo, por diseño) antes del primer
    `mermaid.run()`; el reintento por contenido queda como red de seguridad adicional, no como el
    fix. El texto original se guarda en JS (no se re-lee del DOM) porque `mermaid.run()` reemplaza
    el contenido del `<pre>` con el SVG -- de error o no -- y `mermaid` no vuelve a procesar un
    elemento ya marcado `data-processed` sin que se le devuelva el texto y se le quite esa marca
    primero."""
    codigo_js = _json_para_script(codigo)
    return f"""
    {_ESTILO_CLARO}
    <div id="er-viewport" style="width:100%; height:{alto - 30}px; overflow:hidden;
                                  cursor:grab; border:1px solid #e2e8f0; border-radius:4px;">
      <div id="er-lienzo" style="transform-origin:0 0; width:fit-content;">
        <pre class="mermaid" id="er-diagrama"></pre>
      </div>
    </div>
    <p style="font-size:12px; color:#64748b; font-family:sans-serif; margin:6px 2px 0;">
      Rueda del mouse para acercar/alejar · arrastra para mover el diagrama.
    </p>
    <script src="https://unpkg.com/mermaid@10/dist/mermaid.min.js"></script>
    <script src="https://unpkg.com/d3@7/dist/d3.min.js"></script>
    <script>
      const codigoFuente = {codigo_js};
      const elemento = document.getElementById("er-diagrama");

      mermaid.initialize({{
        startOnLoad: false, theme: "default",
        er: {{ useMaxWidth: false }}, flowchart: {{ useMaxWidth: false }}
      }});

      // El navegador pausa requestAnimationFrame mientras esta pestaña de Streamlit está
      // display:none y lo retoma solo al mostrarla -- por eso alcanza con esperar aquí, sin
      // observar el DOM del padre (cross-origin-ish, esta página vive en su propio srcdoc).
      function esperarVisible() {{
        return new Promise((resolve) => {{
          (function chequear() {{
            if (document.documentElement.clientWidth > 0) resolve();
            else requestAnimationFrame(chequear);
          }})();
        }});
      }}

      async function intentarRenderizar(intento) {{
        elemento.removeAttribute("data-processed");
        elemento.textContent = codigoFuente;
        await mermaid.run({{ querySelector: "#er-diagrama" }});
        const fallo = document.getElementById("er-viewport").textContent.includes("Syntax error");
        if (fallo && intento < 3) {{
          await esperarVisible();
          await new Promise(r => setTimeout(r, 300 * intento));
          return intentarRenderizar(intento + 1);
        }}
      }}

      esperarVisible().then(() => intentarRenderizar(1)).then(() => {{
        const viewport = document.getElementById("er-viewport");
        const lienzo = d3.select("#er-lienzo");

        const zoom = d3.zoom()
          .scaleExtent([0.3, 4])
          .on("start", () => {{ viewport.style.cursor = "grabbing"; }})
          .on("zoom", (event) => {{
            lienzo.style("transform",
              `translate(${{event.transform.x}}px, ${{event.transform.y}}px) scale(${{event.transform.k}})`);
          }})
          .on("end", () => {{ viewport.style.cursor = "grab"; }});
        d3.select(viewport).call(zoom);

        const svg = viewport.querySelector("svg");
        if (svg) {{
          const caja = svg.getBoundingClientRect();
          const anchoDiagrama = caja.width || 800;
          const altoDiagrama = caja.height || 400;
          const escalaInicial = Math.min(
            1,
            (viewport.clientWidth - 24) / anchoDiagrama,
            (viewport.clientHeight - 24) / altoDiagrama
          ) || 1;
          const transformInicial = d3.zoomIdentity.translate(12, 12).scale(escalaInicial);
          d3.select(viewport).call(zoom.transform, transformInicial);
        }}
      }});
    </script>
    """


def _mapa_html(bloque: BloqueMapa) -> str:
    """Mapa D3 (`d3.geoMercator` + `d3.geoPath`, sin librería de mapas). `fondo` (si viene) es la
    silueta nacional simplificada, gris, detrás de los municipios de los 4 estados resaltados --
    pedido explícito del usuario tras ver el mapa sin contexto del resto del país. La proyección
    encuadra el `fondo` cuando existe (así los 4 estados se ven en su posición real dentro de
    México), o los municipios solos si no.

    Con pan/zoom (hallazgo del usuario: el mapa era estático). `d3.zoom()` se aplica sobre un
    único `<g id="capa">` que envuelve fondo + municipios; la leyenda vive **fuera** de ese grupo
    (se agrega después, directo sobre el `svg`) para que no se mueva ni encoja con el zoom."""
    geojson_js = _json_para_script(bloque.geojson)
    fondo_js = _json_para_script(bloque.fondo) if bloque.fondo else "null"
    resaltados_js = _json_para_script([asdict(r) for r in bloque.resaltados])
    return f"""
    {_ESTILO_CLARO}
    <div id="mapa" style="width:100%; cursor:grab;"></div>
    <p style="font-size:12px; color:#64748b; font-family:sans-serif; margin:6px 2px 0;">
      Rueda del mouse para acercar/alejar · arrastra para mover el mapa.
    </p>
    <script src="https://unpkg.com/d3@7/dist/d3.min.js"></script>
    <script>
      const geojson = {geojson_js};
      const fondo = {fondo_js};
      const resaltados = {resaltados_js};
      const colorPorEntidad = Object.fromEntries(resaltados.map(r => [r.cve_ent, r.color]));
      const nombrePorEntidad = Object.fromEntries(resaltados.map(r => [r.cve_ent, r.nombre]));

      const contenedor = document.getElementById("mapa");
      const ancho = contenedor.clientWidth || 760;
      const alto = {_ALTO_D3 - 60};
      const svg = d3.select("#mapa").append("svg")
        .attr("viewBox", `0 0 ${{ancho}} ${{alto}}`)
        .attr("width", "100%").attr("height", alto);

      const proyeccion = d3.geoMercator().fitSize([ancho, alto], fondo || geojson);
      const path = d3.geoPath(proyeccion);

      const capa = svg.append("g");

      if (fondo) {{
        capa.append("g").selectAll("path")
          .data(fondo.features)
          .join("path")
            .attr("d", path)
            .attr("fill", "#e2e8f0")
            .attr("stroke", "#cbd5e1").attr("stroke-width", 0.6)
          .append("title").text("México (silueta simplificada, decorativa)");
      }}

      capa.append("g").selectAll("path")
        .data(geojson.features)
        .join("path")
          .attr("d", path)
          .attr("fill", d => colorPorEntidad[d.properties.cve_ent] || "#94a3b8")
          .attr("stroke", "#fff").attr("stroke-width", 0.4)
        .append("title")
          .text(d => `${{d.properties.nombre_municipio}} · ${{nombrePorEntidad[d.properties.cve_ent] || d.properties.nombre_entidad}}`);

      // Leyenda fuera de `capa`: no forma parte del zoom, se queda fija en la esquina.
      const leyenda = svg.append("g").attr("transform", `translate(12,12)`);
      const filasLeyenda = fondo ? [{{nombre: "Resto de México", color: "#e2e8f0"}}, ...resaltados] : resaltados;
      filasLeyenda.forEach((r, i) => {{
        const fila = leyenda.append("g").attr("transform", `translate(0,${{i * 18}})`);
        fila.append("rect").attr("width", 12).attr("height", 12)
          .attr("fill", r.color).attr("stroke", "#cbd5e1").attr("stroke-width", 0.5);
        fila.append("text").attr("x", 18).attr("y", 10).attr("font-size", 12)
          .attr("font-family", "sans-serif").attr("fill", "#0f172a").text(r.nombre);
      }});

      const zoom = d3.zoom()
        .scaleExtent([1, 8])
        .translateExtent([[-ancho * 0.2, -alto * 0.2], [ancho * 1.2, alto * 1.2]])
        .on("start", () => {{ contenedor.style.cursor = "grabbing"; }})
        .on("zoom", (event) => {{ capa.attr("transform", event.transform); }})
        .on("end", () => {{ contenedor.style.cursor = "grab"; }});
      svg.call(zoom);
    </script>
    """


def _barras_html(bloque: BloqueBarras) -> str:
    """Barras horizontales D3, una fila por capa (bronze/silver/gold). Reemplaza al icicle
    original (US-601, retroalimentación del usuario): con datos tan dispares -- gold ~6x más
    grande que silver -- el icicle repartía el ancho por proporción y silver casi desaparecía.
    Aquí cada capa tiene su propia fila de altura fija, siempre legible.

    **Bug real corregido (hallazgo del usuario: "se sale de la pantalla los datos gold"):** el
    ancho se media con `clientWidth` en el instante en que el script corre -- que es al cargar la
    página, sin esperar a que su pestaña de Streamlit esté visible (`st.tabs` monta las 7
    secciones de una vez; las que no están activas quedan en `display:none`, y ahí `clientWidth`
    mide `0`). El `|| 760` cubría ese caso con un ancho fijo supuesto, pero si el contenedor real
    (una vez visible) resulta más angosto que 760, la barra de Gold -- la que llega más cerca del
    borde derecho, al ser el valor máximo -- deja menos margen del que el layout asumió. Mismo
    fix que ya se aplicó al E-R: no medir mientras está oculto, esperar a que el layout sea real.
    Además se amplía el margen reservado para la etiqueta de valor, para que nunca quede pegada
    al borde aunque el ancho real sea justo."""
    items_js = _json_para_script([asdict(i) for i in bloque.items])
    colores_js = _json_para_script(["#B08968", "#8D99AE", "#D4AF37"])  # bronce, plata, oro
    alto_fila = 56
    alto = len(bloque.items) * alto_fila + 20
    return f"""
    {_ESTILO_CLARO}
    <div id="barras" style="width:100%"></div>
    <script src="https://unpkg.com/d3@7/dist/d3.min.js"></script>
    <script>
      function esperarVisible() {{
        return new Promise((resolve) => {{
          (function chequear() {{
            if (document.getElementById("barras").clientWidth > 0) resolve();
            else requestAnimationFrame(chequear);
          }})();
        }});
      }}

      esperarVisible().then(dibujar);

      function dibujar() {{
      const items = {items_js};
      const colores = {colores_js};
      const altoFila = {alto_fila};
      const ancho = document.getElementById("barras").clientWidth;
      const alto = {alto};
      const margenEtiqueta = 90;
      // Un poco más del mínimo indispensable para "3,297": nunca queda pegada al borde.
      const margenValor = 110;
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
      }}
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
        # scrolling=False: el pan/zoom lo maneja el propio bloque (`#er-viewport`, overflow
        # hidden); un scrollbar de iframe encima sería un segundo mecanismo de mover el
        # contenido, confuso junto con arrastrar para pan.
        alto = bloque.alto or _ALTO_MERMAID_DEFECTO
        components.html(_mermaid_html(bloque.codigo, alto), height=alto, scrolling=False)
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
