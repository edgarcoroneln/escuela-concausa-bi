import PageContainer from "../components/PageContainer.jsx";
import EnConstruccion from "../components/EnConstruccion.jsx";

// Pendiente de conectar (revisión de Edgar, PR #302, 11-sep): el ranking
// municipal necesita el nombre del municipio/entidad por escuela; el
// contrato del API solo expone cve_mun (código), no el nombre. Ver el gap
// de contrato documentado en lib/api.js (getEscuelasEnRiesgo) y en
// Arquitectura_Frontend_React.md §9.
export default function ComparacionTerritorial() {
  return (
    <PageContainer>
      <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>¿Es un caso aislado?</h1>
      <p className="text-sm -mt-4" style={{ color: "var(--color-ink-faint)" }}>
        Compara cada escuela con su municipio, nivel educativo y escuelas similares.
      </p>
      <EnConstruccion nota="El ranking municipal necesita el nombre del municipio/entidad por escuela -- el API hoy solo expone el código cve_mun. Se conecta en cuanto el contrato incluya el nombre." />
    </PageContainer>
  );
}
