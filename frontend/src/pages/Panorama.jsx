import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import DriverMatrix from "../components/DriverMatrix.jsx";
import Card from "../components/Card.jsx";
import { getPanoramaEscuelas } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { panoramaMock } from "../data/mock.js";

// Pantalla 2 -- Panorama de riesgo (rediseño Fase 2, US-641). Contra
// 01_UX_Architecture.md §2 "Pantalla 2": esta es la ÚNICA pantalla que
// revela el conteo de casos (P1 nunca lo hace, ver Home.jsx) y la ÚNICA
// donde se muestra la matrícula general de los casos "dentro de la
// historia" (VistaGeneral.jsx la muestra también, pero es la vista
// heredada, no la narrativa guiada).
//
// N siempre sale de datos reales (nunca escrito a mano): es el mismo
// arreglo que dibuja la matriz, ya recortado por getEscuelasEnRiesgo() al
// conteo oficial de KpisOut.escuelas_en_riesgo (DEC-024).
//
// Primer uso real de DriverMatrix.jsx (antes solo vivía en MatrizDrivers.jsx
// "en construcción", nunca conectada) -- el costo de "N+2 llamadas" que ese
// comentario dudaba en pagar es exactamente el que el propio spec de UX/UI
// documenta como esperado en §8 para revelar el panorama.
//
// Filtros de §3 ("solo atenúan filas, nunca recortan el conjunto, sin
// llamada nueva al API") NO se implementaron en esta entrega -- deferido a
// propósito, ver DevLog de esta fecha.
export default function Panorama() {
  const { status, data, error } = useApiResource(getPanoramaEscuelas, { mock: panoramaMock });
  const escuelas = status === "ok" || status === "demo" ? data : [];
  const n = escuelas.length;
  const matriculaTotal = escuelas.reduce((acc, e) => acc + (e.matricula_total ?? 0), 0);

  const matrizData = escuelas.map((e) => ({
    cct: e.cct,
    nombre: e.nombre,
    drivers: { D1: e.d1, D2: e.d2, D3: e.d3, D4: e.d4, D5: e.d5, D6: e.d6 },
  }));

  return (
    <PageContainer>
      <div className="flex items-start justify-between flex-wrap gap-4">
        <PageHeader
          kicker="Pantalla 02 · Panorama"
          title="El panorama de riesgo"
          subtitle="Todas las escuelas en riesgo comparten una señal, pero cada una vive una situación distinta."
        />
        {status === "demo" && <DemoBadge />}
      </div>

      {status === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando el panorama…</p>
      )}
      {status === "error" && (
        // Literal del spec (§2, "Pantalla 2", Estados): sin detalle interno,
        // a diferencia de otras pantallas que sí muestran el error crudo.
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No pudimos cargar el panorama, intenta de nuevo.
        </p>
      )}

      {(status === "ok" || status === "demo") && (
        <>
          <div
            className="rounded-2xl p-6"
            style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
          >
            <p className="text-2xl leading-snug" style={{ fontWeight: 700, maxWidth: "36ch" }}>
              {n} {n === 1 ? "escuela está" : "escuelas están"} en riesgo. Tenemos {n} {n === 1 ? "caso" : "casos"} por investigar.
            </p>
            <p className="text-sm mt-3" style={{ color: "rgba(255,255,255,0.7)" }}>
              Entre las {n === 1 ? "1 escuela" : `${n} escuelas`} suman {matriculaTotal.toLocaleString("es-MX")} alumnos matriculados.
            </p>
          </div>

          <Card
            title="Comparativa de los 6 drivers"
            subtitle="Cada fila es una escuela; cada columna, una de las 6 líneas de evidencia. Claro = menos presión, oscuro = más."
          >
            <DriverMatrix data={matrizData} />
          </Card>

          <div className="flex justify-end">
            <Link
              to="/casos"
              className="inline-block text-sm font-semibold px-5 py-3 rounded-full"
              style={{ background: "var(--color-primary)", color: "#ffffff" }}
            >
              Elegir un caso →
            </Link>
          </div>
        </>
      )}
    </PageContainer>
  );
}
