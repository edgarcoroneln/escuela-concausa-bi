import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import EnConstruccion from "../components/EnConstruccion.jsx";

// Pendiente de conectar (revisión de Edgar, PR #302, 11-sep): la matriz
// necesita los 6 drivers (d1..d6) de las 7 escuelas a la vez, pero esos
// campos solo vienen en EscuelaDetalleOut (GET /escuelas/{cct}, una
// escuela a la vez) -- la lista paginada que usa "Los 7 casos" no los
// trae. Conectarla hoy implicaría 7 llamadas individuales; se deja en
// construcción hasta decidir si vale la pena ese patrón o si conviene
// pedir un endpoint de lote (postPrediccionesBatch en lib/api.js es el
// precedente de lote que ya existe para predicciones).
export default function MatrizDrivers() {
  return (
    <PageContainer>
      <PageHeader title="Las seis pistas, caso por caso" subtitle="Comparativa de los casos en las seis dimensiones del entorno." />
      <EnConstruccion nota="La matriz necesita los 6 drivers de las escuelas en riesgo a la vez; hoy eso requiere una llamada por escuela (no hay endpoint de lote para el detalle). Se conecta cuando se resuelva ese patrón." />
    </PageContainer>
  );
}
