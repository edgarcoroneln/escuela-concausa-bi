import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import { driverColors, driverIcons, driverNombres, escuelasEnRiesgo, nivelRiesgo } from "../data/mock.js";

export default function LosSieteCasos() {
  return (
    <PageContainer>
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>Nuestros 7 casos</h1>
          <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>
            Siete escuelas presentan una señal de riesgo. Cada una cuenta una historia distinta.
          </p>
        </div>
        <button
          className="text-sm font-semibold px-4 py-2.5 rounded-full whitespace-nowrap"
          style={{ background: "var(--color-header)", color: "#fff" }}
        >
          Comparar los 7 casos
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {escuelasEnRiesgo.map((e, i) => {
          const color = driverColors[e.driver_dominante] ?? "var(--color-primary)";
          const riesgo = nivelRiesgo(e.indice_riesgo);
          return (
            <Card key={e.cct} hover className="flex flex-col justify-between">
              <div>
                <p className="text-sm font-bold mb-1" style={{ color: "var(--color-ink)" }}>
                  Escuela {String(i + 1).padStart(2, "0")}
                </p>
                <p className="text-xs mb-0.5" style={{ color: "var(--color-ink-faint)" }}>{e.nivel}</p>
                <p className="text-xs mb-0.5" style={{ color: "var(--color-ink-faint)" }}>CCT {e.cct}</p>
                <p className="text-xs mb-4" style={{ color: "var(--color-ink-faint)" }}>{e.municipio}, {e.entidad}</p>

                <div className="flex items-baseline gap-2 mb-1">
                  <span className="text-2xl font-extrabold tabular" style={{ color: riesgo.color }}>
                    {e.indice_riesgo.toFixed(2)}
                  </span>
                  <span className="text-xs font-semibold tabular" style={{ color: "var(--color-ink-faint)" }}>
                    {e.variacion}%
                  </span>
                </div>
                <p className="text-[11px] mb-4" style={{ color: "var(--color-ink-faint)" }}>
                  Índice de riesgo · Variación matrícula
                </p>

                <span
                  className="text-xs font-semibold px-2.5 py-1 rounded-full inline-flex items-center gap-1.5"
                  style={{ background: `${color}1a`, color }}
                >
                  <span>{driverIcons[e.driver_dominante]}</span>
                  {driverNombres[e.driver_dominante]}
                </span>
              </div>

              <Link
                to={`/casos/${e.cct}`}
                className="text-sm font-semibold mt-5 inline-block"
                style={{ color: "var(--color-primary)" }}
              >
                Abrir expediente →
              </Link>
            </Card>
          );
        })}
      </div>
    </PageContainer>
  );
}
