import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import EnConstruccion from "../components/EnConstruccion.jsx";

// Pendiente de conectar (revisión de Edgar, PR #302, 11-sep): el mapa
// depende de latitud/longitud y del nombre de municipio/entidad por
// escuela. EscuelaOut/EscuelaDetalleOut no traen esos dos últimos todavía
// (solo cve_mun, código sin nombre) -- ver el gap de contrato documentado
// en lib/api.js (getEscuelasEnRiesgo) y en Arquitectura_Frontend_React.md
// §9. Se deja "en construcción" en vez de mostrar datos de ejemplo sin
// rotular mientras el contrato no los exponga.
export default function MapaCasos() {
  return (
    <PageContainer>
      <PageHeader title="¿Dónde están ocurriendo los casos?" subtitle="Explora la ubicación de las 7 escuelas y su contexto territorial." />
      <EnConstruccion nota="El mapa necesita latitud/longitud y el nombre de municipio/entidad por escuela -- el contrato del API todavía no los expone (solo cve_mun). Se conecta en cuanto estén disponibles." />
    </PageContainer>
  );
}
