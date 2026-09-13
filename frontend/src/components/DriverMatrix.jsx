import * as d3 from "d3";
import { useEffect, useRef, useState } from "react";
import Card from "./Card.jsx";
import { driverIcons, driverNombres } from "../data/mock.js";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";

const DRIVERS = ["D1", "D2", "D3", "D4", "D5", "D6"];

// Heatmap de drivers construido con D3 (no es una tabla HTML con CSS):
// d3.scaleBand para la cuadrícula, una sola rampa monocromática
// (riskRampColor, lib/riskRamp.js -- los mismos --faro-ramp-1..5 de
// index.css) para todas las celdas: claro = menos presión del driver,
// oscuro = más. Antes usaba d3.interpolateRdYlGn (semáforo rojo/verde),
// que Design_Tokens_Stitch.md rechaza explícitamente ("Systematic Risk
// Drivers", igual que el semáforo de nivel de atención) -- corregido aquí,
// primer uso real de este componente (no estaba conectado a ninguna
// pantalla todavía). Un patrón SVG a rayas marca las celdas SIN_DATO (para
// no confundir "falta el dato" con "el driver vale 0").
//
// data: [{ cct, nombre, drivers: { D1: number|null, ..., D6: number|null } }]
//
// atenuarCct (opcional, 12-sep, DevLog comparativa §2): función (cct) =>
// boolean. Cuando se pasa, cada fila/celda cuyo cct evalúe a true baja de
// opacidad -- pensado para sincronizar con el mapa de entidades de
// Panorama.jsx (hover sobre una entidad atenúa las escuelas de las otras).
// Se aplica en un efecto aparte (ver abajo) que solo toca `opacity` sobre
// los nodos ya construidos, para no repetir el fade-in de montaje en cada
// hover del mapa.
export default function DriverMatrix({ data = [], onSelect, atenuarCct }) {
  const svgRef = useRef(null);
  const wrapRef = useRef(null);
  const [width, setWidth] = useState(640);
  const atenuarCctRef = useRef(atenuarCct);

  const rowLabelWidth = 170;
  const rowHeight = 44;
  const headerHeight = 46;
  const height = headerHeight + data.length * rowHeight + 8;

  useEffect(() => {
    atenuarCctRef.current = atenuarCct;
  }, [atenuarCct]);

  useEffect(() => {
    if (!wrapRef.current) return;
    const ro = new ResizeObserver((entries) => {
      const w = entries[0]?.contentRect?.width;
      if (w) setWidth(w);
    });
    ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, []);

  // Efecto de construcción: dibuja la cuadrícula completa (una sola vez por
  // cambio de datos/ancho). Filas y celdas quedan marcadas con data-cct para
  // que el efecto de atenuado (más abajo) solo cambie opacidad sin
  // reconstruir el SVG en cada hover del mapa de entidades.
  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("width", width).attr("height", height).attr("viewBox", `0 0 ${width} ${height}`);

    const defs = svg.append("defs");
    const pattern = defs
      .append("pattern")
      .attr("id", "sinDatoStripes")
      .attr("width", 6)
      .attr("height", 6)
      .attr("patternUnits", "userSpaceOnUse")
      .attr("patternTransform", "rotate(45)");
    pattern.append("rect").attr("width", 6).attr("height", 6).attr("fill", "var(--color-sin-dato-bg)");
    pattern.append("line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 6).attr("stroke", "var(--color-sin-dato)").attr("stroke-width", 2);

    const gridWidth = width - rowLabelWidth;
    const x = d3.scaleBand().domain(DRIVERS).range([rowLabelWidth, rowLabelWidth + gridWidth]).padding(0.08);
    const y = d3.scaleBand().domain(data.map((d) => d.cct)).range([headerHeight, headerHeight + data.length * rowHeight]).padding(0.12);

    // Rampa monocromática: 0 (claro, menos presión) -> 1 (oscuro, más presión)
    const color = (v) => riskRampColor(v);

    // Encabezados de columna: nombre del driver, envuelto a 2 líneas
    const headers = svg
      .append("g")
      .selectAll("g")
      .data(DRIVERS)
      .join("g")
      .attr("transform", (d) => `translate(${x(d) + x.bandwidth() / 2},0)`);

    headers.each(function (d) {
      // Icono del driver (checklist 12-sep, ítem accionable sin dependencia
      // de API) -- mismo emoji que ya se usa en la insignia de driver
      // dominante (LosSieteCasos.jsx) y en DriverBars.jsx, solo que aquí
      // identifica la COLUMNA completa, no una escuela.
      d3.select(this)
        .append("text")
        .attr("text-anchor", "middle")
        .attr("y", 12)
        .attr("font-size", 13)
        .text(driverIcons[d]);

      const words = driverNombres[d].split(" ");
      const lines = words.length > 1 ? [words.slice(0, -1).join(" "), words[words.length - 1]] : [words[0]];
      const text = d3.select(this).append("text").attr("text-anchor", "middle").attr("font-size", 10).attr("font-weight", 600).attr("fill", "var(--color-ink-soft)");
      lines.forEach((line, i) => {
        text.append("tspan").attr("x", 0).attr("y", headerHeight - 22 + i * 12).text(line);
      });
    });

    // Filas: nombre de la escuela (clickeable -> expediente)
    const rows = svg
      .append("g")
      .selectAll("g")
      .data(data)
      .join("g")
      .attr("transform", (d) => `translate(0,${y(d.cct)})`)
      .attr("data-cct", (d) => d.cct);

    rows
      .append("text")
      .attr("x", 0)
      .attr("y", y.bandwidth() / 2 + 4)
      .attr("font-size", 12)
      .attr("font-weight", 600)
      .attr("fill", "var(--color-primary)")
      .style("cursor", onSelect ? "pointer" : "default")
      .text((d) => d.nombre)
      .on("click", (_, d) => onSelect?.(d.cct));

    // Celdas
    const cellGroups = svg
      .append("g")
      .selectAll("g")
      .data(data.flatMap((d) => DRIVERS.map((driver) => ({ cct: d.cct, driver, valor: d.drivers[driver], esDominante: driver === d.dominante }))))
      .join("g")
      .attr("transform", (d) => `translate(${x(d.driver)},${y(d.cct)})`)
      .attr("data-cct", (d) => d.cct);

    cellGroups
      .append("rect")
      .attr("width", x.bandwidth())
      .attr("height", y.bandwidth())
      .attr("rx", 6)
      .attr("fill", (d) => (d.valor == null ? "url(#sinDatoStripes)" : color(d.valor)))
      .attr("stroke", (d) => (d.esDominante ? DOMINANT_OUTLINE : "var(--color-border)"))
      .attr("stroke-width", (d) => (d.esDominante ? 2 : 1))
      .append("title")
      .text((d) =>
        d.valor == null
          ? `${driverNombres[d.driver]} · SIN_DATO`
          : `${driverNombres[d.driver]}: ${d.valor.toFixed(2)}${d.esDominante ? " · Driver dominante" : ""}`
      );

    cellGroups
      .filter((d) => d.valor != null)
      .append("text")
      .attr("x", x.bandwidth() / 2)
      .attr("y", y.bandwidth() / 2 + 4)
      .attr("text-anchor", "middle")
      .attr("font-size", 11)
      .attr("font-weight", 700)
      .attr("fill", (d) => (d.valor > 0.6 ? "#ffffff" : "#0f172a"))
      .text((d) => d.valor.toFixed(2));

    svg.selectAll("g > rect, g > text").attr("opacity", 0).transition().duration(400).attr("opacity", 1);

    // Aplica de inmediato el atenuado vigente (por si ya había una entidad
    // resaltada en el mapa cuando llegaron datos nuevos), sin transición
    // para no pelear con el fade-in de arriba.
    const activo = atenuarCctRef.current;
    if (typeof activo === "function") {
      svg.selectAll("g[data-cct]").attr("opacity", function () {
        return activo(this.getAttribute("data-cct")) ? 0.3 : 1;
      });
    }
  }, [data, width, height, onSelect]);

  // Efecto de atenuado: solo cambia opacidad de las filas/celdas ya
  // construidas cuando cambia atenuarCct (hover del mapa de entidades en
  // Panorama.jsx) -- nunca reconstruye la cuadrícula.
  useEffect(() => {
    d3.select(svgRef.current)
      .selectAll("g[data-cct]")
      .transition()
      .duration(180)
      .attr("opacity", function () {
        return typeof atenuarCct === "function" && atenuarCct(this.getAttribute("data-cct")) ? 0.3 : 1;
      });
  }, [atenuarCct]);

  return (
    <div ref={wrapRef}>
      <svg ref={svgRef} style={{ width: "100%", height: "auto" }} />
      <div className="flex items-center gap-2 mt-3 text-xs" style={{ color: "var(--color-ink-faint)" }}>
        <span>Menos presión</span>
        <div style={{ width: 100, height: 8, borderRadius: 4, background: "linear-gradient(90deg, #eef2f7, #93a5c0, #0f172a)" }} />
        <span>Más presión</span>
        <span className="flex items-center gap-1.5 ml-4">
          <span
            className="inline-block"
            style={{ width: 14, height: 14, borderRadius: 3, background: "#93a5c0", outline: `2px solid ${DOMINANT_OUTLINE}`, outlineOffset: "-1px" }}
          />
          Driver dominante
        </span>
        <span className="flex items-center gap-1.5 ml-4">
          <svg width="14" height="14">
            <defs>
              <pattern id="legendStripes2" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                <rect width="6" height="6" fill="var(--color-sin-dato-bg)" />
                <line x1="0" y1="0" x2="0" y2="6" stroke="var(--color-sin-dato)" strokeWidth="2" />
              </pattern>
            </defs>
            <rect width="14" height="14" rx="3" fill="url(#legendStripes2)" stroke="var(--color-border)" />
          </svg>
          SIN_DATO
        </span>
      </div>
    </div>
  );
}

export function DriverMatrixCard({ title = "Matriz de drivers", subtitle, ...props }) {
  return (
    <Card title={title} subtitle={subtitle}>
      <DriverMatrix {...props} />
    </Card>
  );
}
