import { useNavigate } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import { DriverMatrixCard } from "../components/DriverMatrix.jsx";
import { matrizDrivers } from "../data/mock.js";

export default function MatrizDrivers() {
  const navigate = useNavigate();
  return (
    <PageContainer>
      <PageHeader title="Las 7 pistas sobre la mesa" subtitle="Comparativa de los 7 casos en las seis dimensiones del entorno." />
      <DriverMatrixCard
        subtitle="Click en el nombre de la escuela para ver su expediente"
        data={matrizDrivers}
        onSelect={(cct) => navigate(`/casos/${cct}`)}
      />
    </PageContainer>
  );
}
