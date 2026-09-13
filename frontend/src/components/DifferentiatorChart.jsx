import Card from "./Card.jsx";
import RiskGauge from "./RiskGauge.jsx";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";

function SchoolPanel({ school }) {
  const color = riskRampColor(school.indiceRiesgo);
  return (
    <div className="flex-1 flex flex-col items-center text-center gap-3 p-5">
      <div>
        <h4 className="text-base font-semibold" style={{ color: "var(--color-ink)" }}>
          {school.nombre}
        </h4>
        <p className="text-xs" style={{ color: "var(--color-ink-faint)" }}>
          {school.cct} · {school.ubicacion}
        </p>
      </div>
      <RiskGauge value={school.indiceRiesgo} color={color} />
      <span
        className="text-xs font-semibold px-3 py-1 rounded-full"
        style={{ background: "var(--color-surface)", border: `2px solid ${DOMINANT_OUTLINE}`, color: "var(--color-ink)" }}
      >
        {school.driver} · {school.driverNombre}
      </span>
      <p className="text-sm leading-snug" style={{ color: "var(--color-ink-soft)" }}>
        {school.recomendacion}
      </p>
    </div>
  );
}

export default function DifferentiatorChart({ data }) {
  return (
    <Card
      title="El diferenciador"
      subtitle="Mismo índice de riesgo, driver dominante y recomendación distintos"
    >
      <div className="flex flex-col md:flex-row items-stretch">
        <SchoolPanel school={data.a} />
        <div className="flex md:flex-col items-center justify-center px-2 py-2">
          <span
            className="text-xs font-bold px-2.5 py-1 rounded-full"
            style={{ background: "var(--color-primary-soft)", color: "var(--color-primary)" }}
          >
            vs
          </span>
        </div>
        <SchoolPanel school={data.b} />
      </div>
    </Card>
  );
}
