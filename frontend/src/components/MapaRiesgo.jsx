import * as d3 from "d3";
import { useEffect, useRef, useState } from "react";
import Card from "./Card.jsx";
import { riskRampColor } from "../lib/riskRamp.js";
import mexicoStates from "../data/geo/mexico-states.json";

// Mapa real de México con D3 (d3-geo, proyección Mercator ajustada al bbox del
// geojson) + geojson de estados (fuente: github.com/angelnmara/geojson).
// Los "casos" se ubican por latitud/longitud reales que trae el API
// (EscuelaDetalleOut.latitud / .longitud) — no son coordenadas de pantalla.
//
// data: [{ cct, nombre, latitud, longitud, indice_riesgo, driver_dominante }]
export default function MapaRiesgo({ data = [], selectedCct, onSelect, height = 460 }) {
  const svgRef = useRef(null);
  const wrapRef = useRef(null);
  const [width, setWidth] = useState(720);

  useEffect(() => {
    if (!wrapRef.current) return;
    const ro = new ResizeObserver((entries) => {
      const w = entries[0]?.contentRect?.width;
      if (w) setWidth(w);
    });
    ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("width", width).attr("height", height).attr("viewBox", `0 0 ${width} ${height}`);

    const projection = d3.geoMercator().fitSize([width, height], mexicoStates);
    const path = d3.geoPath(projection);

    const g = svg.append("g");

    g.append("g")
      .selectAll("path")
      .data(mexicoStates.features)
      .join("path")
      .attr("d", path)
      .attr("fill", "var(--color-surface)")
      .attr("stroke", "var(--color-border)")
      .attr("stroke-width", 0.8);

    const marks = g
      .append("g")
      .selectAll("g")
      .data(data.filter((d) => d.latitud != null && d.longitud != null))
      .join("g")
      .attr("transform", (d) => {
        const p = projection([d.longitud, d.latitud]);
        return p ? `translate(${p[0]},${p[1]})` : "translate(-9999,-9999)";
      })
      .style("cursor", "pointer")
      .on("click", (_, d) => onSelect?.(d.cct));

    marks
      .append("circle")
      .attr("r", (d) => (d.cct === selectedCct ? 9 : 6.5))
      .attr("fill", (d) => riskRampColor(d.indice_riesgo))
      .attr("stroke", "#fff")
      .attr("stroke-width", (d) => (d.cct === selectedCct ? 2.5 : 1.5))
      .attr("opacity", 0.9);

    marks
      .append("text")
      .attr("y", -12)
      .attr("text-anchor", "middle")
      .attr("font-size", 10)
      .attr("font-weight", 600)
      .attr("fill", "var(--color-ink)")
      .text((d) => (d.cct === selectedCct ? d.nombre : ""));
  }, [data, width, height, selectedCct, onSelect]);

  return (
    <div ref={wrapRef}>
      <svg ref={svgRef} style={{ width: "100%", height: "auto" }} />
    </div>
  );
}

export function MapaRiesgoCard({ title = "Mapa de los casos", subtitle, ...props }) {
  return (
    <Card title={title} subtitle={subtitle}>
      <MapaRiesgo {...props} />
    </Card>
  );
}
