import * as d3 from "d3";
import { useEffect, useRef } from "react";

// Gauge radial construido directamente con D3 (arc generator + scale),
// no una librería de charts — aquí es donde el proyecto usa D3 "de verdad".
export default function RiskGauge({ value, max = 0.6, alertLine = 0.5, color, size = 132 }) {
  const ref = useRef(null);

  useEffect(() => {
    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();

    const radius = size / 2;
    const thickness = 12;
    const startAngle = -Math.PI * 0.75;
    const endAngle = Math.PI * 0.75;

    const scale = d3.scaleLinear().domain([0, max]).range([startAngle, endAngle]).clamp(true);

    const g = svg.attr("width", size).attr("height", size).append("g").attr("transform", `translate(${radius},${radius})`);

    const track = d3
      .arc()
      .innerRadius(radius - thickness)
      .outerRadius(radius)
      .startAngle(startAngle)
      .endAngle(endAngle);

    g.append("path").attr("d", track).attr("fill", "var(--color-border)");

    const valueArc = d3
      .arc()
      .innerRadius(radius - thickness)
      .outerRadius(radius)
      .startAngle(startAngle)
      .endAngle(scale(value));

    g.append("path").attr("d", valueArc).attr("fill", color);

    // Marca de la línea de alerta (DEC-019)
    const alertAngle = scale(alertLine);
    const markerInner = radius - thickness - 4;
    const markerOuter = radius + 2;
    g.append("line")
      .attr("x1", Math.sin(alertAngle) * markerInner)
      .attr("y1", -Math.cos(alertAngle) * markerInner)
      .attr("x2", Math.sin(alertAngle) * markerOuter)
      .attr("y2", -Math.cos(alertAngle) * markerOuter)
      .attr("stroke", "var(--color-alert)")
      .attr("stroke-width", 2);

    g.append("text")
      .attr("text-anchor", "middle")
      .attr("y", 4)
      .attr("font-size", 26)
      .attr("font-weight", 600)
      .attr("fill", "var(--color-ink)")
      .text(value.toFixed(4));

    g.append("text")
      .attr("text-anchor", "middle")
      .attr("y", 22)
      .attr("font-size", 10)
      .attr("fill", "var(--color-ink-faint)")
      .text("índice de riesgo");
  }, [value, max, alertLine, color, size]);

  return <svg ref={ref} />;
}
