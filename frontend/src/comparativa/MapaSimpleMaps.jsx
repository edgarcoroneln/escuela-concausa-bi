import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps";
import { driverColors } from "../data/mock.js";
import mexicoStates from "../data/geo/mexico-states.json";

// Combinación #5: mismo mapa que MapaRiesgo.jsx, pero con react-simple-maps
// (envoltura de React sobre d3-geo) en vez de manejar la proyección y el
// <svg> a mano. Sigue siendo D3 por debajo (react-simple-maps usa
// d3-geo/d3-zoom internamente) — la diferencia es cuánto código de
// proyección/zoom/pan escribimos nosotros vs cuánto viene resuelto.
export default function MapaSimpleMaps({ data = [], selectedCct, onSelect }) {
  return (
    <ComposableMap
      projection="geoMercator"
      projectionConfig={{ center: [-102, 23.5], scale: 1350 }}
      width={420}
      height={280}
      style={{ width: "100%", height: "auto" }}
    >
      <Geographies geography={mexicoStates}>
        {({ geographies }) =>
          geographies.map((geo) => (
            <Geography
              key={geo.rsmKey}
              geography={geo}
              fill="var(--color-surface)"
              stroke="var(--color-border)"
              strokeWidth={0.8}
              style={{ default: { outline: "none" }, hover: { outline: "none" }, pressed: { outline: "none" } }}
            />
          ))
        }
      </Geographies>
      {data
        .filter((d) => d.latitud != null && d.longitud != null)
        .map((d) => (
          <Marker key={d.cct} coordinates={[d.longitud, d.latitud]} onClick={() => onSelect?.(d.cct)}>
            <circle
              r={d.cct === selectedCct ? 6.5 : 4.5}
              fill={driverColors[d.driver_dominante] ?? "var(--color-alert)"}
              stroke="#fff"
              strokeWidth={1.2}
              style={{ cursor: onSelect ? "pointer" : "default" }}
            />
          </Marker>
        ))}
    </ComposableMap>
  );
}
