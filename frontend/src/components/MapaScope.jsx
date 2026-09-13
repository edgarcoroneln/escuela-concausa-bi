import { useEffect, useRef } from "react";
import { geoMercator, geoPath } from "d3-geo";
import { select } from "d3-selection";
import { zoom as d3zoom } from "d3-zoom";

// Mapa del bloque `mapa` de "Cómo funciona" (US-601), portado del renderer de D3 que vivía
// dentro del shell de Streamlit.
//
// Sin librería de mapas: `geoMercator` + `geoPath` sobre el GeoJSON que sirve la propia API.
// `d3-geo` y `d3` ya eran dependencias del proyecto (los usa el mapa de riesgo), así que este
// bloque no agrega ninguna.
//
// El color es CATEGÓRICO, un tono por entidad — no una escala de valor. El gris del fondo no es
// `SIN_DATO`: es el resto de México como contexto geográfico, fuera del alcance del proyecto.
//
// La leyenda vive fuera del grupo que recibe el zoom, para que no se encoja ni se desplace al
// hacer pan — mismo criterio que el original.

export default function MapaScope({ geojson, resaltados, fondo, alto = 400 }) {
  const contenedor = useRef(null);

  useEffect(() => {
    const nodo = contenedor.current;
    if (!nodo) return undefined;
    nodo.replaceChildren();

    const ancho = nodo.clientWidth || 760;
    const colorPorEntidad = Object.fromEntries(resaltados.map((r) => [r.cve_ent, r.color]));
    const nombrePorEntidad = Object.fromEntries(resaltados.map((r) => [r.cve_ent, r.nombre]));

    const svg = select(nodo)
      .append("svg")
      .attr("viewBox", `0 0 ${ancho} ${alto}`)
      .attr("width", "100%")
      .attr("height", alto);

    const proyeccion = geoMercator().fitSize([ancho, alto], fondo || geojson);
    const path = geoPath(proyeccion);
    const capa = svg.append("g");

    if (fondo) {
      capa
        .append("g")
        .selectAll("path")
        .data(fondo.features)
        .join("path")
        .attr("d", path)
        .attr("fill", "#e2e8f0")
        .attr("stroke", "#cbd5e1")
        .attr("stroke-width", 0.6)
        .append("title")
        .text("México (silueta simplificada, decorativa)");
    }

    capa
      .append("g")
      .selectAll("path")
      .data(geojson.features)
      .join("path")
      .attr("d", path)
      .attr("fill", (d) => colorPorEntidad[d.properties.cve_ent] || "#94a3b8")
      .attr("stroke", "#fff")
      .attr("stroke-width", 0.4)
      .append("title")
      .text(
        (d) =>
          `${d.properties.nombre_municipio} · ${
            nombrePorEntidad[d.properties.cve_ent] || d.properties.nombre_entidad
          }`,
      );

    const leyenda = svg.append("g").attr("transform", "translate(12,12)");
    const filas = fondo ? [{ nombre: "Resto de México", color: "#e2e8f0" }, ...resaltados] : resaltados;
    filas.forEach((r, i) => {
      const fila = leyenda.append("g").attr("transform", `translate(0,${i * 18})`);
      fila
        .append("rect")
        .attr("width", 12)
        .attr("height", 12)
        .attr("fill", r.color)
        .attr("stroke", "#cbd5e1")
        .attr("stroke-width", 0.5);
      fila
        .append("text")
        .attr("x", 18)
        .attr("y", 10)
        .attr("font-size", 12)
        .attr("font-family", "var(--font-sans)")
        .attr("fill", "#0f172a")
        .text(r.nombre);
    });

    const comportamiento = d3zoom()
      .scaleExtent([1, 8])
      .translateExtent([
        [-ancho * 0.2, -alto * 0.2],
        [ancho * 1.2, alto * 1.2],
      ])
      .on("start", () => {
        nodo.style.cursor = "grabbing";
      })
      .on("zoom", (evento) => capa.attr("transform", evento.transform))
      .on("end", () => {
        nodo.style.cursor = "grab";
      });
    svg.call(comportamiento);

    return () => nodo.replaceChildren();
  }, [geojson, resaltados, fondo, alto]);

  return (
    <div className="flex flex-col gap-1.5">
      <div
        ref={contenedor}
        className="rounded-xl overflow-hidden"
        style={{ background: "#ffffff", border: "1px solid var(--color-border)", cursor: "grab" }}
      />
      <p className="text-xs" style={{ color: "var(--color-ink-faint)" }}>
        Rueda del mouse para acercar o alejar · arrastra para mover el mapa. Un color por entidad;
        no es una escala de valor. El gris de fondo es el resto de México, no <code>SIN_DATO</code>.
      </p>
    </div>
  );
}
