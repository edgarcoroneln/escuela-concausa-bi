import * as d3 from "d3";
import { useEffect, useRef } from "react";
import mexicoStates from "../data/geo/mexico-states.json";

// Mapa de la república completa (mismo geojson real de 32 estados que ya usan
// MapaEntidades.jsx/SiluetaEntidad.jsx -- nunca un mapa decorativo inventado)
// con la entidad de la escuela resaltada en su color de marca y un PIN real en
// las coordenadas exactas de esa escuela (EscuelaOut.latitud/longitud, nunca
// una posición inventada ni el centro del estado).
//
// FIX (2026-09-13, pedido de Diana sobre ExpedienteEscuela.jsx/LosSieteCasos.jsx
// -- "un mapa de la república ajustado al tamaño del recuadro... con un pin de
// la entidad"): reemplaza a SiluetaEntidad.jsx en esos dos recuadros. Con el
// país completo visible, un punto simple (el que usa SiluetaEntidad.jsx) queda
// casi invisible -- se usa en cambio el mismo glifo "location_on" que ya usa el
// proyecto en Icons.jsx (IconLocationOn), dibujado a mano con <path> sobre el
// propio SVG del mapa (mismo trazo oficial de Material Symbols, no una forma
// inventada), para que la ubicación se lea de un vistazo.
//
// Se dibuja siempre a tamaño de contenedor (width/height: 100%) -- pensado
// para los recuadros de tamaño fijo de ExpedienteEscuela.jsx/LosSieteCasos.jsx,
// no para un layout de alto libre como el de Panorama.jsx (que sigue usando
// SiluetaEntidad.jsx sin cambios).
const PIN_PATH =
  "M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 294q122-112 181-203.5T720-552q0-109-69.5-178.5T480-800q-101 0-170.5 69.5T240-552q0 71 59 162.5T480-186Zm0 106Q319-217 239.5-334.5T160-552q0-150 96.5-239T480-880q127 0 223.5 89T800-552q0 100-79.5 217.5T480-80Zm0-480Z";

// El pin vive en el espacio de coordenadas 0..960 / -960..0 de Material
// Symbols (mismo que usa SymbolIcon en Icons.jsx). La punta del glifo cae en
// (480,-80): la traslación de abajo la manda al origen antes de reescalar y
// reubicar en el punto real del mapa, para que sea la PUNTA -- no el centro
// del glifo -- la que señale la coordenada exacta.
const PIN_ESCALA = 0.032;

export default function MapaPin({ entidadId, color = "var(--faro-signal)", lat, lon, etiqueta, ariaLabel }) {
  const svgRef = useRef(null);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const tamano = 320;
    svg.attr("viewBox", `0 0 ${tamano} ${tamano}`);

    const projection = d3.geoMercator().fitSize([tamano, tamano], mexicoStates);
    // FIX (2026-09-13, pedido de Diana -- "centra más el mapa"): fitSize centra el
    // PAÍS completo en el recuadro, pero lo que importa aquí es la escuela, no
    // México como silueta -- si la escuela cae lejos del centro geométrico del
    // país (p.ej. Nuevo León, al norte), el pin terminaba pegado a una orilla.
    // Se conserva la escala de fitSize (mismo nivel de detalle/contexto) pero se
    // recentra la proyección para que el punto real de la escuela quede en el
    // centro exacto del recuadro -- por eso va antes de crear `path`, que ya usa
    // la proyección final.
    if (typeof lat === "number" && typeof lon === "number") {
      projection.center([lon, lat]).translate([tamano / 2, tamano / 2]);
    }
    const path = d3.geoPath(projection);

    svg
      .append("g")
      .selectAll("path")
      .data(mexicoStates.features)
      .join("path")
      .attr("d", path)
      .attr("fill", (d) => (d.properties.id === entidadId ? color : "#e2e8f0"))
      .attr("fill-opacity", (d) => (d.properties.id === entidadId ? 0.35 : 1))
      .attr("stroke", (d) => (d.properties.id === entidadId ? color : "#cbd5e1"))
      .attr("stroke-width", (d) => (d.properties.id === entidadId ? 1.4 : 0.5))
      .append("title")
      .text((d) => d.properties.name);

    if (typeof lat === "number" && typeof lon === "number") {
      const proyectado = projection([lon, lat]);
      const px = proyectado?.[0];
      const py = proyectado?.[1];
      if (typeof px === "number" && typeof py === "number") {
        const pin = svg.append("g").attr("transform", `translate(${px},${py}) scale(${PIN_ESCALA}) translate(-480,80)`);
        pin
          .append("path")
          .attr("d", PIN_PATH)
          .attr("fill", color)
          .attr("stroke", "#ffffff")
          .attr("stroke-width", 18)
          .attr("paint-order", "stroke")
          .append("title")
          .text(etiqueta ?? "");
      }
    }
  }, [entidadId, color, lat, lon, etiqueta]);

  return <svg ref={svgRef} role="img" aria-label={ariaLabel} style={{ width: "100%", height: "100%" }} />;
}
