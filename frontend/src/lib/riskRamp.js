import { scaleLinear } from "d3";

// Rampa secuencial de magnitud (03_Visual_Identity.md S3): un solo tono, 5
// pasos, para cualquier valor 0->1 (indice de riesgo, presion de un driver,
// o una frecuencia ya normalizada). El color NUNCA identifica una
// categoria/driver -- ese concepto quedo rechazado explicitamente
// (Design_Tokens_Stitch.md, "Systematic Risk Drivers"; tambien "Calibrated
// Risk Tiers" para el semaforo por nivel). Duplica los valores de
// --faro-ramp-1..5 de index.css: D3/SVG necesita hex crudo para interpolar,
// no puede leer variables CSS custom properties directamente.
const RAMP_STOPS = ["#eef2f7", "#c7d2e0", "#93a5c0", "#56698c", "#0f172a"];

const rampScale = scaleLinear().domain([0, 0.25, 0.5, 0.75, 1]).range(RAMP_STOPS).clamp(true);

/** Color de la rampa para un valor 0->1. null/undefined => gris de contexto (SIN_DATO). */
export function riskRampColor(value) {
  if (value == null || Number.isNaN(value)) return "var(--color-sin-dato)";
  return rampScale(value);
}

// Acento del driver dominante (S3): SOLO como contorno, nunca como relleno.
export const DOMINANT_OUTLINE = "#b45309";

// Nivel de atencion (S3): "sin color propio -- icono + texto unicamente".
// Iconos fijos, un solo tono de tinta (var(--color-ink)), nunca semaforo.
export const NIVEL_ICONOS = { Alta: "▲", Media: "■", Baja: "●" };
