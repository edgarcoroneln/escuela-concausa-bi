import * as Plot from "@observablehq/plot";
import { useEffect, useRef } from "react";

// Combinación #3: React + Observable Plot (construido por el mismo autor de
// D3, encima de d3-scale/d3-shape). Declarativo como Recharts, pero "más
// D3" en su linaje. Plot.plot() genera un nodo DOM que insertamos a mano.
export default function BarPlot({ data, xKey, yKey, color = "#2b5aa8" }) {
  const ref = useRef(null);

  useEffect(() => {
    const plot = Plot.plot({
      width: 420,
      height: 220,
      marginLeft: 48,
      style: { fontFamily: "var(--font-sans)", fontSize: 11 },
      y: { grid: true, tickFormat: (d) => `${(d / 1e6).toFixed(1)}M`, label: null },
      x: { label: null },
      marks: [
        Plot.barY(data, { x: xKey, y: yKey, fill: color, rx: 4 }),
        Plot.ruleY([0]),
      ],
    });
    ref.current.innerHTML = "";
    ref.current.append(plot);
    return () => plot.remove();
  }, [data, xKey, yKey, color]);

  return <div ref={ref} />;
}
