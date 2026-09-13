import * as d3 from "d3";
import { useEffect, useRef } from "react";
import mexicoStates from "../data/geo/mexico-states.json";

// Silueta real de UNA entidad (mismo geojson de los 32 estados que ya usa
// MapaEntidades.jsx/Login.jsx -- nunca una forma decorativa inventada,
// mismo criterio documentado ahí: "sigue siendo un mapa real, nunca un
// gráfico decorativo con coordenadas inventadas"). Se filtra el feature de
// la entidad pedida y se ajusta la proyección solo a ese polígono (no al
// país completo), con puntos reales encima (lat/lon de EscuelaOut, no
// posiciones inventadas).
//
// 13-sep -- pedido de Diana para el panel "Enclave Georreferenciado" de
// Panorama.jsx: sustituye el diagrama abstracto de nodos + curva del
// mockup (sin respaldo geográfico real, "puede ser solo la silueta del
// estado o municipio") por esta silueta real.
export default function SiluetaEntidad({
  entidadId,
  color = "var(--faro-signal)",
  puntos = [],
  width = 280,
  height = 190,
  ariaLabel,
}) {
  const svgRef = useRef(null);

  useEffect(() => {
    const feature = mexicoStates.features.find((f) => f.properties.id === entidadId);
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("viewBox", `0 0 ${width} ${height}`);
    if (!feature) return;

    const projection = d3.geoMercator().fitExtent(
      [
        [12, 12],
        [width - 12, height - 12],
      ],
      feature
    );
    const path = d3.geoPath(projection);

    svg
      .append("path")
      .attr("d", path(feature))
      .attr("fill", color)
      .attr("fill-opacity", 0.16)
      .attr("stroke", color)
      .attr("stroke-width", 1.4);

    svg
      .append("g")
      .selectAll("circle")
      .data(puntos.filter((p) => typeof p.lat === "number" && typeof p.lon === "number"))
      .join("circle")
      .attr("cx", (d) => projection([d.lon, d.lat])?.[0] ?? -100)
      .attr("cy", (d) => projection([d.lon, d.lat])?.[1] ?? -100)
      .attr("r", 4)
      .attr("fill", color)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.2)
      .append("title")
      .text((d) => d.etiqueta ?? "");
  }, [entidadId, color, puntos, width, height]);

  return <svg ref={svgRef} role="img" aria-label={ariaLabel} style={{ width: "100%", height: "auto" }} />;
}
