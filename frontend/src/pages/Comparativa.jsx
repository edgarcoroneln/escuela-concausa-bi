import PageContainer from "../components/PageContainer.jsx";
import EnConstruccion from "../components/EnConstruccion.jsx";

// Pendiente de conectar (revisión de Edgar, PR #302, 11-sep): la evolución
// de matrícula por ciclo necesita una serie histórica por escuela; el
// contrato del API solo expone matricula_total del ciclo actual, sin
// serie temporal. Ver Arquitectura_Frontend_React.md §9.
export default function Comparativa() {
  return (
    <PageContainer>
      <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>
        Pista 1: ¿Qué pasó con la matrícula?
      </h1>
      <p className="text-sm -mt-4" style={{ color: "var(--color-ink-faint)" }}>Evolución de la matrícula en las escuelas en riesgo.</p>
      <EnConstruccion nota="La evolución de matrícula por ciclo necesita una serie histórica por escuela; el API hoy solo expone matricula_total del ciclo actual. Se conecta en cuanto el contrato incluya la serie." />
    </PageContainer>
  );
}
