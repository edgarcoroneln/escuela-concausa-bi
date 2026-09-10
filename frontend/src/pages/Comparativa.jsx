import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import BarChartCard from "../components/BarChartCard.jsx";
import { matriculaPorCiclo } from "../data/mock.js";

export default function Comparativa() {
  return (
    <PageContainer>
      <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>
        Pista 1: ¿Qué pasó con la matrícula?
      </h1>
      <p className="text-sm -mt-4" style={{ color: "var(--color-ink-faint)" }}>Evolución de la matrícula en las 7 escuelas en riesgo.</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <BarChartCard
            title="Matrícula por ciclo escolar"
            subtitle="Siguiente fase: desglose por cada una de las 7 escuelas"
            data={matriculaPorCiclo}
            xKey="ciclo"
            yKey="matricula"
          />
        </div>
        <Card style={{ background: "var(--color-primary-soft)" }} className="flex flex-col gap-2">
          <span className="text-xs font-semibold" style={{ color: "var(--color-primary)" }}>ℹ️ Hallazgo</span>
          <p className="text-sm font-semibold" style={{ color: "var(--color-ink)" }}>
            6 de las 7 escuelas presentan una caída de matrícula en el último ciclo analizado.
          </p>
          <p className="text-xs" style={{ color: "var(--color-ink-soft)" }}>
            La caída nos dice dónde investigar, pero aún no nos dice por qué está ocurriendo.
          </p>
        </Card>
      </div>
    </PageContainer>
  );
}
