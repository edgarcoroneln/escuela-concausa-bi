import * as d3 from "d3";
import { useEffect, useRef } from "react";

// Combinación #2: React + D3 100% a mano (sin librería de charts).
// Cada pieza que Recharts te da gratis (ejes, grid, tooltip, animación de
// entrada) aquí hay que escribirla explícitamente. Cuenta las líneas
// contra BarChartCard.jsx (Recharts) para comparar.
export default function BarD3({ data, xKey, yKey, color = "var(--color-primary)" }) {
  const ref = useRef(null);

  useEffect(() => {
    const width = 420;
    const height = 220;
    const margin = { top: 8, right: 8, bottom: 24, left: 44 };

    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();
    svg.attr("width", width).attr("height", height);

    const x = d3
      .scaleBand()
      .domain(data.map((d) => d[xKey]))
      .range([margin.left, width - margin.right])
      .padding(0.3);

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d[yKey])])
      .nice()
      .range([height - margin.bottom, margin.top]);

    // Eje Y (grid + ticks formateados a millones, a mano)
    svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(
        d3
          .axisLeft(y)
          .ticks(4)
          .tickSize(-(width - margin.left - margin.right))
          .tickFormat((d) => `${(d / 1e6).toFixed(1)}M`)
      )
      .call((g) => g.select(".domain").remove())
      .call((g) => g.selectAll(".tick line").attr("stroke", "var(--color-border)"))
      .call((g) => g.selectAll(".tick text").attr("fill", "var(--color-ink-soft)").attr("font-size", 11));

    // Eje X
    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).tickSize(0))
      .call((g) => g.select(".domain").attr("stroke", "var(--color-border)"))
      .call((g) => g.selectAll("text").attr("fill", "var(--color-ink-soft)").attr("font-size", 11));

    // Barras, con animación de entrada (transition) escrita a mano
    svg
      .append("g")
      .selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", (d) => x(d[xKey]))
      .attr("width", x.bandwidth())
      .attr("y", height - margin.bottom)
      .attr("height", 0)
      .attr("rx", 4)
      .attr("fill", color)
      .transition()
      .duration(500)
      .attr("y", (d) => y(d[yKey]))
      .attr("height", (d) => height - margin.bottom - y(d[yKey]));
  }, [data, xKey, yKey, color]);

  return <svg ref={ref} />;
}
