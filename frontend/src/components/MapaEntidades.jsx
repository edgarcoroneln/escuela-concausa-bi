import * as d3 from "d3";
import { useEffect, useRef, useState } from "react";
import mexicoStates from "../data/geo/mexico-states.json";

// Mapa de México (D3 + geojson real de los 32 estados) que resalta las 4
// entidades del alcance de FARO -- extraído el 12-sep de Login.jsx (ahí se
// construyó por primera vez con hover+clic; ver ese archivo para el
// historial completo de las 3 vueltas de esa pantalla) para reutilizarlo en
// más pantallas sin duplicar el SVG ni la lógica de interacción.
//
// Checklist "dar el frontend por 100%" (DevLog comparativa 12-sep, §2/§4):
// "Fondo de mapa decorativo (sin datos) en el hero de P1 y la columna
// lateral de P2, reutilizando MapaEntidadesLogin -- extraerlo a
// components/ primero." Este archivo es exactamente eso: mismo componente,
// ahora con props para poder usarse sin selección (P1, decorativo) o con
// hover reportado al padre (P2, para atenuar DriverMatrix -- ver
// Panorama.jsx).
//
// Sigue siendo un mapa real, nunca un gráfico decorativo con coordenadas
// inventadas (a diferencia del "radar de vigilancia" de los mockups -- ver
// DevLog §0, mismo hallazgo).
export const ENTIDADES_ALCANCE = ["MX-CMX", "MX-MEX", "MX-NLE", "MX-JAL"];

// cveEnt: mismo catálogo INEGI que ya usa el filtro de Explorador.jsx
// (const ENTIDADES, ahí también con comentario de que es SCOPE_ENTIDADES,
// CLAUDE.md §4) -- se repite el mismo valor ya usado y validado contra el
// API en esa pantalla, no se inventa aquí ninguna clave nueva.
export const ENTIDADES_LABEL = [
  { id: "MX-CMX", cveEnt: "09", nombre: "CDMX", color: "var(--faro-entity-cdmx)" },
  { id: "MX-MEX", cveEnt: "15", nombre: "Edomex", color: "var(--faro-entity-edomex)" },
  { id: "MX-NLE", cveEnt: "19", nombre: "Nuevo León", color: "var(--faro-entity-nl)" },
  { id: "MX-JAL", cveEnt: "14", nombre: "Jalisco", color: "var(--faro-entity-jalisco)" },
];
export const ENTIDAD_COLOR = Object.fromEntries(ENTIDADES_LABEL.map((e) => [e.id, e.color]));

// seleccionada/onSeleccionar: opcionales -- sin ellos el mapa solo resalta
// al pasar el cursor (uso decorativo, sin clic, en P1) y no muestra cursor
// de "pointer". onHoverChange: opcional, para que el padre se entere de qué
// entidad está bajo el cursor (uso en P2, para atenuar filas de
// DriverMatrix que no son de esa entidad).
export default function MapaEntidades({
  seleccionada = null,
  onSeleccionar,
  onHoverChange,
  size = 520,
  maxWidth = "28rem",
  ariaLabel = "Mapa de México con Ciudad de México, Estado de México, Nuevo León y Jalisco resaltados",
}) {
  const svgRef = useRef(null);
  const [hovered, setHoveredState] = useState(null);
  const onSeleccionarRef = useRef(onSeleccionar);
  const onHoverChangeRef = useRef(onHoverChange);
  const interactivo = typeof onSeleccionar === "function";

  useEffect(() => {
    onSeleccionarRef.current = onSeleccionar;
  }, [onSeleccionar]);
  useEffect(() => {
    onHoverChangeRef.current = onHoverChange;
  }, [onHoverChange]);

  function actualizarHover(id) {
    setHoveredState(id);
    onHoverChangeRef.current?.(id);
  }

  // Efecto de montaje: construye el mapa una sola vez (proyección, paths,
  // manejadores). No depende de seleccionada/hovered para que los nodos del
  // SVG no se destruyan y recreen en cada hover -- así la transición de CSS
  // de abajo se ve, en vez de "saltar" sin animación.
  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("viewBox", `0 0 ${size} ${size}`);

    const projection = d3.geoMercator().fitSize([size, size], mexicoStates);
    const path = d3.geoPath(projection);

    svg
      .append("g")
      .selectAll("path")
      .data(mexicoStates.features)
      .join("path")
      .attr("d", path)
      .attr("data-id", (d) => d.properties.id)
      .attr("stroke", "rgba(255,255,255,0.18)")
      .attr("stroke-width", 0.6)
      .style("cursor", (d) => (interactivo && ENTIDADES_ALCANCE.includes(d.properties.id) ? "pointer" : "default"))
      .style("transition", "fill-opacity 180ms ease, stroke-width 180ms ease, stroke 180ms ease")
      .on("mouseenter", (event, d) => {
        if (ENTIDADES_ALCANCE.includes(d.properties.id)) actualizarHover(d.properties.id);
      })
      .on("mouseleave", (event, d) => {
        if (ENTIDADES_ALCANCE.includes(d.properties.id)) actualizarHover(null);
      })
      .on("click", (event, d) => {
        if (ENTIDADES_ALCANCE.includes(d.properties.id)) onSeleccionarRef.current?.(d.properties.id);
      })
      .append("title")
      .text((d) => (ENTIDADES_ALCANCE.includes(d.properties.id) ? d.properties.name : ""));
    // Se reconstruye solo si cambia el tamaño (viewBox); "interactivo" ya
    // queda fijo en el manejador de mouseenter/click vía la ref de arriba.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [size]);

  // Efecto de estado: solo actualiza atributos visuales sobre los paths ya
  // creados (opacidad de relleno, grosor/color de borde) cada vez que
  // cambia el hover o la selección.
  useEffect(() => {
    d3.select(svgRef.current)
      .selectAll("path")
      .attr("fill", (d) =>
        ENTIDADES_ALCANCE.includes(d.properties.id) ? ENTIDAD_COLOR[d.properties.id] : "rgba(255,255,255,0.05)"
      )
      .attr("fill-opacity", (d) => {
        const id = d.properties.id;
        if (!ENTIDADES_ALCANCE.includes(id)) return 1;
        if (id === seleccionada) return 1;
        if (id === hovered) return 0.75;
        return 0.4;
      })
      .attr("stroke", (d) => (d.properties.id === seleccionada ? "#ffffff" : "rgba(255,255,255,0.18)"))
      .attr("stroke-width", (d) => (d.properties.id === seleccionada ? 1.6 : 0.6));
  }, [seleccionada, hovered]);

  return (
    <svg
      ref={svgRef}
      role="img"
      aria-label={ariaLabel}
      style={{ width: "100%", height: "auto", maxWidth }}
    />
  );
}
