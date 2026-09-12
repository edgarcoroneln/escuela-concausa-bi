import { useEffect, useRef } from "react";
import { select } from "d3-selection";
import { linkHorizontal } from "d3-shape";

// Diagrama de 3 columnas del bloque `diagrama_flujo` (US-601): tablas fuente → cubos →
// dashboards. Portado del renderer de D3 del shell de Streamlit.
//
// Sin plugin de Sankey: `linkHorizontal` basta y evita otra dependencia. `d3-shape` y
// `d3-selection` ya venían con `d3`, que el proyecto usa desde antes.
//
// Al pasar el mouse por un nodo se resaltan sus enlaces y se apagan los demás: con ~30 nodos y
// más enlaces, sin eso el diagrama se lee como una maraña.

const COLOR_COLUMNA = ["#4C72B0", "#D4AF37", "#55A868"];

export default function DiagramaFlujo({ nodos, enlaces, altoMinimo = 460 }) {
  const contenedor = useRef(null);

  useEffect(() => {
    const nodo = contenedor.current;
    if (!nodo) return undefined;
    nodo.replaceChildren();

    const ancho = nodo.clientWidth || 900;
    const porColumna = [0, 1, 2].map((c) => nodos.filter((n) => n.columna === c));
    const filasMax = Math.max(...porColumna.map((c) => c.length), 1);
    const alto = Math.max(altoMinimo, filasMax * 26);

    const xColumna = [60, ancho / 2, ancho - 60];
    const pos = {};
    porColumna.forEach((columna, c) => {
      const paso = alto / (columna.length + 1);
      columna.forEach((n, i) => {
        pos[n.id] = { x: xColumna[c], y: paso * (i + 1) };
      });
    });

    const svg = select(nodo)
      .append("svg")
      .attr("viewBox", `0 0 ${ancho} ${alto}`)
      .attr("width", "100%")
      .attr("height", alto);

    const enlace = linkHorizontal()
      .source((e) => [pos[e.origen].x + 4, pos[e.origen].y])
      .target((e) => [pos[e.destino].x - 4, pos[e.destino].y]);

    const rutas = svg
      .append("g")
      .selectAll("path")
      .data(enlaces)
      .join("path")
      .attr("d", enlace)
      .attr("fill", "none")
      .attr("stroke", "#94a3b8")
      .attr("stroke-width", 1.2)
      .attr("opacity", 0.45);

    const grupo = svg
      .append("g")
      .selectAll("g")
      .data(nodos)
      .join("g")
      .attr("transform", (d) => `translate(${pos[d.id].x},${pos[d.id].y})`)
      .style("cursor", "pointer")
      .on("mouseenter", (_ev, d) =>
        rutas.attr("opacity", (e) => (e.origen === d.id || e.destino === d.id ? 0.9 : 0.08)),
      )
      .on("mouseleave", () => rutas.attr("opacity", 0.45));

    grupo
      .append("circle")
      .attr("r", 5)
      .attr("fill", (d) => COLOR_COLUMNA[d.columna] ?? "#94a3b8");

    grupo
      .append("text")
      .attr("x", (d) => (d.columna === 2 ? -9 : 9))
      .attr("y", 4)
      .attr("text-anchor", (d) => (d.columna === 2 ? "end" : "start"))
      .attr("font-size", 10.5)
      .attr("font-family", "var(--font-sans)")
      .attr("fill", "#0f172a")
      .text((d) => d.etiqueta)
      .append("title")
      .text((d) => d.etiqueta);

    return () => nodo.replaceChildren();
  }, [nodos, enlaces, altoMinimo]);

  return (
    <div className="flex flex-col gap-1.5">
      <div
        ref={contenedor}
        className="rounded-xl overflow-x-auto"
        style={{ background: "#ffffff", border: "1px solid var(--color-border)" }}
      />
      <p className="text-xs" style={{ color: "var(--color-ink-faint)" }}>
        Pasa el mouse por un nodo para resaltar solo sus conexiones.
      </p>
    </div>
  );
}
