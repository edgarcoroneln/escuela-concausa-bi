import PageContainer from "../components/PageContainer.jsx";
import RankingList from "../components/RankingList.jsx";
import { rankingMunicipios } from "../data/mock.js";

export default function ComparacionTerritorial() {
  return (
    <PageContainer>
      <h1 className="text-2xl" style={{ color: "var(--color-ink)", fontWeight: 700 }}>¿Es un caso aislado?</h1>
      <p className="text-sm -mt-4" style={{ color: "var(--color-ink-faint)" }}>
        Compara cada escuela con su municipio, nivel educativo y escuelas similares.
      </p>
      <RankingList
        title="Ranking municipal por número de escuelas"
        subtitle="Municipios con mayor número de escuelas en el universo cubierto"
        data={rankingMunicipios}
        labelKey="municipio"
        sublabelKey="entidad"
        valueKey="escuelas"
      />
    </PageContainer>
  );
}
