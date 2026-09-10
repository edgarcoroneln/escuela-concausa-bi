import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import BarChartCard from "../components/BarChartCard.jsx";
import MapaRiesgo from "../components/MapaRiesgo.jsx";
import BarD3 from "../comparativa/BarD3.jsx";
import BarPlot from "../comparativa/BarPlot.jsx";
import MapaSimpleMaps from "../comparativa/MapaSimpleMaps.jsx";
import { escuelasEnRiesgo, matriculaPorCiclo } from "../data/mock.js";

// Página de comparación técnica, NO parte del storytelling para el Dr.
// Construye la MISMA pieza (la gráfica de matrícula) con 3 enfoques
// distintos, y el MISMO mapa con 2 enfoques distintos, para decidir con
// evidencia en vez de solo teoría. Ruta directa: /comparativa-stacks
// (no está en el nav principal a propósito).
export default function ComparativaStacks() {
  return (
    <PageContainer>
      <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>
        Comparación de combinaciones de herramientas
      </h1>
      <p className="text-sm -mt-4 max-w-2xl" style={{ color: "var(--color-ink-faint)" }}>
        Misma gráfica de matrícula construida 3 formas distintas, y el mismo mapa construido 2 formas distintas.
        Página de trabajo interna — no forma parte de la demo.
      </p>

      <h2 className="text-lg mt-4" style={{ color: "var(--color-ink)", fontWeight: 700 }}>
        Gráfica de matrícula: 3 formas
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <BarChartCard data={matriculaPorCiclo} xKey="ciclo" yKey="matricula" title="#1 — Recharts" subtitle="Ya en producción en la app" />
        <Card title="#2 — D3 100% a mano" subtitle="Sin librería de charts">
          <BarD3 data={matriculaPorCiclo} xKey="ciclo" yKey="matricula" />
        </Card>
        <Card title="#3 — Observable Plot" subtitle="Construido por el autor de D3">
          <BarPlot data={matriculaPorCiclo} xKey="ciclo" yKey="matricula" />
        </Card>
      </div>

      <h2 className="text-lg mt-4" style={{ color: "var(--color-ink)", fontWeight: 700 }}>
        Mapa de los casos: 2 formas
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="#1 — D3-geo a mano" subtitle="MapaRiesgo.jsx, ya en producción">
          <MapaRiesgo data={escuelasEnRiesgo} height={280} />
        </Card>
        <Card title="#5 — react-simple-maps" subtitle="Envoltura de React sobre d3-geo">
          <MapaSimpleMaps data={escuelasEnRiesgo} />
        </Card>
      </div>
    </PageContainer>
  );
}
