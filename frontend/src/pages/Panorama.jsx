import { useState } from "react";
import { Link } from "react-router-dom";
import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import DriverMatrix from "../components/DriverMatrix.jsx";
import Card from "../components/Card.jsx";
import LeyendaGrafica from "../components/LeyendaGrafica.jsx";
import MapaEntidades, { ENTIDADES_LABEL } from "../components/MapaEntidades.jsx";
import { getPanoramaEscuelas, getKpis } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { panoramaMock, kpisMockParaComparacion2Ciclos } from "../data/mock.js";

// Pantalla 2 -- Panorama de riesgo (rediseño Fase 2, US-641). Contra
// 01_UX_Architecture.md §2 "Pantalla 2": esta es la ÚNICA pantalla que
// revela el conteo de casos (P1 nunca lo hace, ver Home.jsx) y la ÚNICA
// donde se muestra la matrícula general de los casos "dentro de la
// historia" (VistaGeneral.jsx la muestra también, pero es la vista
// heredada, no la narrativa guiada).
//
// N siempre sale de datos reales (nunca escrito a mano): es el mismo
// arreglo que dibuja la matrix, ya recortado por getEscuelasEnRiesgo() al
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
//
// CORRECCIÓN 12-sep (DevLog comparativa, checklist §2/§4): el mockup reserva
// una tarjeta lateral completa para el mini-mapa de "radar" con datos
// inventados (ver DevLog §0). Ese hueco se llena aquí con el mapa real de
// las 4 entidades (components/MapaEntidades.jsx) y, a diferencia de P1
// (decorativo), aquí sí es interactivo: al pasar el cursor por una entidad
// se atenúan las filas de DriverMatrix que no son de esa entidad. La
// entidad de cada escuela no es un dato nuevo: se deriva de `cve_mun`
// (formato INEGI "EEMMM", los mismos 2 dígitos de entidad que ya expone
// `MunicipioOut.cve_ent` en src/api/schemas.py), no se inventa ni se llama
// a un endpoint adicional.
export default function Panorama() {
  const { status, data, error } = useApiResource(getPanoramaEscuelas, { mock: panoramaMock });
  const escuelas = status === "ok" || status === "demo" ? data : [];
  const n = escuelas.length;
  const matriculaTotal = escuelas.reduce((acc, e) => acc + (e.matricula_total ?? 0), 0);

  // Agregados del alcance completo (4 entidades), no solo de las escuelas en
  // riesgo -- 02_Data_Visualization_Spec.md fila "P2 -- Panorama" pide
  // variacion_matricula e indice_completitud_drivers de KpisOut, y la fila de
  // reconciliación de variación de matrícula ("Caída de matrícula de una
  // escuela concreta") resuelve explícito: "Sólo la variación agregada, en la
  // P2". Llamada independiente de getPanoramaEscuelas() -- si falla, la
  // pantalla sigue mostrando el resto (no bloquea el panorama por un
  // agregado adicional).
  const { status: kpisStatus, data: kpisData } = useApiResource(getKpis, {
    mock: kpisMockParaComparacion2Ciclos,
  });
  const kpis = kpisStatus === "ok" || kpisStatus === "demo" ? kpisData : null;

  const matrizData = escuelas.map((e) => ({
    cct: e.cct,
    nombre: e.nombre,
    // Primeros 2 dígitos de cve_mun (INEGI: entidad + municipio) -- mismo
    // criterio que MunicipioOut.cve_ent/cve_mun, no un dato inventado.
    cveEnt: typeof e.cve_mun === "string" ? e.cve_mun.slice(0, 2) : null,
    drivers: { D1: e.d1, D2: e.d2, D3: e.d3, D4: e.d4, D5: e.d5, D6: e.d6 },
    // Driver dominante ya resuelto por el backend/mock -- se usa para dibujar
    // el contorno ambar (03_Visual_Identity.md S3), mismo patron que ya
    // implementa DriverBars.jsx en el Expediente (Pantalla 4). Antes no se
    // pasaba: hallazgo de la revision visual del 13-sep contra los mockups.
    dominante: e.driver_dominante,
  }));

  const [entidadHover, setEntidadHover] = useState(null);
  const cveEntActiva = entidadHover ? ENTIDADES_LABEL.find((e) => e.id === entidadHover)?.cveEnt ?? null : null;
  const ccsEnEntidadActiva = cveEntActiva
    ? new Set(matrizData.filter((d) => d.cveEnt === cveEntActiva).map((d) => d.cct))
    : null;
  const atenuarCct = ccsEnEntidadActiva ? (cct) => !ccsEnEntidadActiva.has(cct) : undefined;

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
            {kpis && typeof kpis.variacion_matricula === "number" && typeof kpis.indice_completitud_drivers === "number" && (
              <p className="text-sm mt-1" style={{ color: "rgba(255,255,255,0.7)" }}>
                Matrícula del alcance completo (4 entidades) vs. el ciclo anterior: {(kpis.variacion_matricula * 100).toFixed(1)}%.
                Completitud promedio de los 6 drivers: {(kpis.indice_completitud_drivers * 100).toFixed(0)}%.
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-[1fr_240px] gap-4 items-start">
            <Card
              title="Comparativa de los 6 drivers"
              subtitle="Cada fila es una escuela; cada columna, una de las 6 líneas de evidencia. Claro = menos presión, oscuro = más."
            >
              <DriverMatrix data={matrizData} atenuarCct={atenuarCct} />
              {/* Leyenda obligatoria (02_Data_Visualization_Spec.md §7.bis.2, fila "P2 · Matriz de
                  casos") -- además del degradado propio de DriverMatrix, el bloque de 4 declaraciones
                  que pide la §7.bis.1. */}
              <LeyendaGrafica
                queSeVe="Una fila por escuela en riesgo y una columna por pista del entorno. El tono de la celda dice cuánta presión ejerce esa pista sobre esa escuela; el recuadro con ▲ marca la que más destaca."
                unidad="Posición relativa de 0 a 1 frente al resto de escuelas observadas, no porcentaje: 0 es la menor presión observada y 1 la mayor."
                sinDato="Celda rayada: esa pista no se pudo verificar para esa escuela. No es un cero ni quiere decir que no haya problema."
                cicloYRecorte={`Ciclo más reciente materializado. Las ${n} escuelas que cruzan la línea de alerta, de las escuelas del alcance (CDMX, Estado de México, Nuevo León y Jalisco).`}
              />
            </Card>

            <Card
              title="Entidades del alcance"
              subtitle="Pasa el cursor sobre una entidad para resaltar solo sus escuelas en la matriz."
            >
              <div className="flex justify-center">
                <MapaEntidades
                  size={240}
                  maxWidth="12rem"
                  onHoverChange={setEntidadHover}
                  ariaLabel="Mapa de México con las 4 entidades del alcance de FARO; pasa el cursor sobre una para resaltar solo sus escuelas en la matriz de drivers"
                />
              </div>
            </Card>
          </div>

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
