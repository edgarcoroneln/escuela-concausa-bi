import { useEffect, useState } from "react";
import { driverIcons, driverNombres } from "../data/mock.js";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";

const DRIVERS = ["D1", "D2", "D3", "D4", "D5", "D6"];

// Barra individual con animación de relleno (checklist 12-sep, item
// accionable sin dependencia de API): arranca en 0% y, ya montada, transita
// en CSS hasta su ancho real -- mismo patrón "crece desde 0" que el arco de
// RiskGauge.jsx, aquí con CSS puro (no hace falta D3 para una barra).
function Barra({ valor, color }) {
  const [ancho, setAncho] = useState(0);
  const anchoFinal = Math.max(valor, 0.03) * 100;

  useEffect(() => {
    const id = requestAnimationFrame(() => setAncho(anchoFinal));
    return () => cancelAnimationFrame(id);
  }, [anchoFinal]);

  return (
    <div
      className="h-full rounded-full"
      style={{
        width: `${ancho}%`,
        background: color,
        transition: "width 650ms cubic-bezier(0.4, 0, 0.2, 1)",
      }}
    />
  );
}

// Gráfica comparativa de los 6 drivers de UNA escuela (Pantalla 4, §4 y
// §7.bis.2 "P4 · Comparativa de los 6 drivers"). CSS/SVG plano, sin D3 --
// a diferencia de DriverMatrix.jsx (que sí necesita D3 para su cuadrícula
// de muchas escuelas), aquí es una sola fila de 6 barras y una tabla
// HTML+CSS lo resuelve entero. Misma rampa monocromática (riskRampColor)
// que el resto del producto: el color nunca identifica un driver, mide
// presión.
//
// SIN_DATO se dibuja como "pista rayada de punta a punta" (§7.bis.2), no
// como una barra en 0 -- un valor real de 0 se vería igual a "no hay dato"
// si no se distinguieran.
export default function DriverBars({ drivers, driverDominante }) {
  return (
    <div className="flex flex-col gap-3">
      {DRIVERS.map((code) => {
        const valor = drivers[code];
        const sinDato = valor === null || valor === undefined;
        const esDominante = code === driverDominante;
        return (
          <div key={code} className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 shrink-0" style={{ width: "11rem" }}>
              <span>{driverIcons[code]}</span>
              <span className="text-xs font-medium" style={{ color: "var(--color-ink)" }}>
                {driverNombres[code]}
              </span>
              {esDominante && (
                <span title="Driver dominante" style={{ color: DOMINANT_OUTLINE }}>▲</span>
              )}
            </div>
            <div
              className="flex-1 rounded-full overflow-hidden relative"
              style={{
                height: 14,
                background: sinDato
                  ? "repeating-linear-gradient(45deg, var(--color-sin-dato-bg), var(--color-sin-dato-bg) 4px, var(--color-border) 4px, var(--color-border) 8px)"
                  : "var(--color-surface-alt, #f4f4f5)",
                border: esDominante ? `2px solid ${DOMINANT_OUTLINE}` : "1px solid var(--color-border)",
              }}
              title={sinDato ? `${driverNombres[code]}: SIN_DATO` : `${driverNombres[code]}: ${valor.toFixed(2)}`}
            >
              {!sinDato && <Barra valor={valor} color={riskRampColor(valor)} />}
            </div>
            <span
              className="text-xs font-semibold tabular shrink-0"
              style={{ width: "3.5rem", textAlign: "right", color: sinDato ? "var(--color-ink-faint)" : "var(--color-ink)" }}
            >
              {sinDato ? "SIN_DATO" : valor.toFixed(2)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
