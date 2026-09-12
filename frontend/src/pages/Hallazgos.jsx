import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import { driverIcons, driverNombres } from "../data/mock.js";
import { riskRampColor } from "../lib/riskRamp.js";

const HALLAZGOS = [
  "Todas están en riesgo, pero no todas enfrentan el mismo problema.",
  "La conectividad es el driver dominante más frecuente entre los casos.",
  "Los casos se distribuyen en 6 municipios y 5 entidades.",
  "En 2 escuelas la cobertura de calidad del aire es insuficiente (SIN_DATO).",
  "Los contextos territoriales son clave para entender cada caso.",
];

const DISTRIBUCION = [
  { driver: "D4", n: 2 },
  { driver: "D2", n: 1 },
  { driver: "D3", n: 1 },
  { driver: "D1", n: 1 },
  { driver: "D5", n: 1 },
  { driver: "D6", n: 1 },
];

export default function Hallazgos() {
  const max = Math.max(...DISTRIBUCION.map((d) => d.n));
  return (
    <PageContainer>
      <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>Cada escuela, su historia</h1>
      <p className="text-sm -mt-4" style={{ color: "var(--color-ink-faint)" }}>Principales hallazgos de la investigación.</p>
      <div className="-mt-2"><DemoBadge /></div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="Distribución de driver dominante">
          <ul className="flex flex-col gap-3">
            {DISTRIBUCION.map((d) => (
              <li key={d.driver} className="flex items-center gap-3">
                <span className="text-xs w-32 flex items-center gap-1.5" style={{ color: "var(--color-ink-soft)" }}>
                  {driverIcons[d.driver]} {driverNombres[d.driver]}
                </span>
                <div className="flex-1 h-2.5 rounded-full" style={{ background: "var(--color-border)" }}>
                  <div className="h-2.5 rounded-full" style={{ width: `${(d.n / max) * 100}%`, background: riskRampColor(d.n / max) }} />
                </div>
                <span className="text-xs font-semibold tabular w-4 text-right" style={{ color: "var(--color-ink)" }}>{d.n}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Lo que aprendimos">
          <ol className="flex flex-col gap-3">
            {HALLAZGOS.map((h, i) => (
              <li key={i} className="flex gap-3 text-sm" style={{ color: "var(--color-ink-soft)" }}>
                <span
                  className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold"
                  style={{ background: "var(--color-primary-soft)", color: "var(--color-primary)" }}
                >
                  {i + 1}
                </span>
                {h}
              </li>
            ))}
          </ol>
        </Card>
      </div>
    </PageContainer>
  );
}
