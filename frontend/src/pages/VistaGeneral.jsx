import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import KpiCard from "../components/KpiCard.jsx";
import DifferentiatorChart from "../components/DifferentiatorChart.jsx";
import BarChartCard from "../components/BarChartCard.jsx";
import DonutChartCard from "../components/DonutChartCard.jsx";
import { MapaRiesgoCard } from "../components/MapaRiesgo.jsx";
import { escuelasPorNivel, escuelasEnRiesgo, kpis, matriculaPorCiclo, parDiferenciador } from "../data/mock.js";

export default function VistaGeneral() {
  return (
    <PageContainer>
      <PageHeader title="Panorama general" subtitle="Una visión rápida de la situación de las 7 escuelas en riesgo." />

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((k) => (
          <KpiCard key={k.label} {...k} tone={k.label.includes("riesgo alto") ? "alert" : "default"} />
        ))}
      </section>

      <DifferentiatorChart data={parDiferenciador} />

      <MapaRiesgoCard subtitle="Ubicación de las 7 escuelas" data={escuelasEnRiesgo} />

      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <BarChartCard
          title="Matrícula por ciclo"
          subtitle="Alumnado inscrito, últimos 3 ciclos"
          data={matriculaPorCiclo}
          xKey="ciclo"
          yKey="matricula"
        />
        <DonutChartCard
          title="Distribución por nivel educativo"
          subtitle="Universo cubierto"
          data={escuelasPorNivel}
          nameKey="nombre"
          valueKey="valor"
        />
      </section>
    </PageContainer>
  );
}
