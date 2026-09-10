import { useState } from "react";
import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Card from "../components/Card.jsx";
import MapaRiesgo from "../components/MapaRiesgo.jsx";
import { escuelasEnRiesgo } from "../data/mock.js";

export default function MapaCasos() {
  const [selected, setSelected] = useState(escuelasEnRiesgo[0].cct);
  const escuela = escuelasEnRiesgo.find((e) => e.cct === selected);

  return (
    <PageContainer>
      <PageHeader title="¿Dónde están ocurriendo los casos?" subtitle="Explora la ubicación de las 7 escuelas y su contexto territorial." />
      <Card>
        <select
          className="text-sm mb-4 px-3 py-2 rounded-lg"
          style={{ border: "1px solid var(--color-border)", background: "var(--color-surface)" }}
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
        >
          {escuelasEnRiesgo.map((e) => (
            <option key={e.cct} value={e.cct}>
              {e.nombre}
            </option>
          ))}
        </select>
        <MapaRiesgo data={escuelasEnRiesgo} selectedCct={selected} onSelect={setSelected} height={480} />
        {escuela && (
          <p className="text-sm mt-3" style={{ color: "var(--color-ink-soft)" }}>
            <strong style={{ color: "var(--color-ink)" }}>{escuela.nombre}</strong> · {escuela.cct} · índice de riesgo {escuela.indice_riesgo.toFixed(4)}
          </p>
        )}
        <p className="text-xs mt-4" style={{ color: "var(--color-ink-faint)" }}>
          7 escuelas en {new Set(escuelasEnRiesgo.map((e) => e.municipio)).size} municipios y {new Set(escuelasEnRiesgo.map((e) => e.entidad)).size} entidades
        </p>
      </Card>
    </PageContainer>
  );
}
