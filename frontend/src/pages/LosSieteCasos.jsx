import { Link } from "react-router-dom";
import { useState } from "react";
import PageContainer from "../components/PageContainer.jsx";
import Card from "../components/Card.jsx";
import DemoBadge from "../components/DemoBadge.jsx";
import DriverBars from "../components/DriverBars.jsx";
import { IconTrendingUp } from "../components/Icons.jsx";
import { ENTIDADES_LABEL } from "../components/MapaEntidades.jsx";
import MapaPin from "../components/MapaPin.jsx";
import { driverNombres, nivelRiesgo, panoramaMock } from "../data/mock.js";
import { riskRampColor, DOMINANT_OUTLINE } from "../lib/riskRamp.js";
import { getConclusionEscuelas } from "../lib/api.js";
import { useApiResource } from "../lib/useApiResource.js";
import { useCortesAtencion } from "../lib/cortesAtencion.js";
import { valorOrientado } from "../lib/driverOrientacion.js";
import { FASES } from "../lib/navFases.js";

// Pantalla 3 -- Selección de Caso (pase de fidelidad 13-sep contra
// mockups/03_Seleccion_Caso.png + .html -- confirmado que SÍ es esta
// pantalla: el propio mockup resalta "03 Selección de Caso" en su menú y
// su barra superior dice "FASE_03").
//
// 13-sep, SEGUNDA RONDA -- Diana pidió, con 2 imágenes nuevas (screenshot
// completo del mockup + el recorte de la barra de protocolo/banner),
// fidelidad prácticamente literal: "no le cambies nada... textos,
// imagenes, colores, iconos, recuadros, tamaños, y todo", incluida la
// separación exacta entre bloques de caso, todos los textos de la barra
// superior/banner, y el mismo color de acento que usa el mockup para
// resaltar el caso seleccionado. Se revisa cada elemento del primer pase
// (comentario largo más abajo) contra esta nueva exigencia:
//
//   - Colores/tipografía: se pasa toda la pantalla a los tokens oficiales
//     (--faro-*, clases text-label-*/title-md/headline-sm ya usadas en el
//     resto del proyecto) y el acento de selección deja de usar
//     --color-primary (negro/slate, lo que traía el primer pase) para usar
//     --faro-signal (cian #0284c7) -- ES el mismo tono que el mockup usa
//     para su anillo/barra de selección ("secondary", #006398 en su propia
//     paleta de Stitch): el primer pase eligió mal el token y Diana lo
//     notó. Ahora el borde 2px, la barra lateral gruesa, el chip
//     "SELECCIONADO PARA EXPEDIENTE", el número de fila y el ÍNDICE de la
//     fila activa comparten ese mismo acento, igual que el mockup.
//   - El acento ámbar del driver dominante (DOMINANT_OUTLINE) se usa ahora
//     TAMBIÉN como color de texto del badge "VECTOR DOMINANTE" de cada
//     fila (antes solo era contorno) -- así lo pinta el mockup en las 7
//     filas. Esto no reabre el debate de "color por driver" que
//     Design_Tokens_Stitch.md rechaza: el ámbar es siempre el MISMO tono
//     sin importar cuál de los 6 drivers sea el dominante -- señala
//     "estado de dominancia", no identifica una categoría. El desglose de
//     vectores del panel inspector (DriverBars.jsx) NO se toca: es un
//     componente compartido con la Pantalla 4 y ese ajuste de color no fue
//     parte de este pedido.
//   - Barra de filtros ("Filtrar por: Entidad ... / Nivel de Riesgo ... /
//     Reestablecer") y "ORDEN: ÍNDICE COMPUESTO DESCENDENTE": se restauran
//     tal cual el mockup, pero con el mismo criterio de dato real que ya
//     usa "Enclave Georreferenciado" en Panorama.jsx -- el chip de entidad
//     muestra la entidad real con más casos de este conjunto (y su conteo
//     real), y el chip de nivel de riesgo dice "▲ Alta" solo cuando eso es
//     cierto para las 7 (si no, dice "mixto"). "Reestablecer" queda igual
//     que en el propio mockup: un span decorativo sin onClick, no un botón
//     funcional (P3 no implementa filtros reales, 02_Data_Visualization_
//     Spec.md línea 95: "reutiliza los mismos datos ya cargados en la
//     P2", sin llamada nueva).
//   - "Muestra diagnóstica: Activa" por fila SÍ se restaura -- es una
//     etiqueta fija y universal (verdadera para cualquier fila real de
//     esta lista, no un dato inventado por escuela).
//   - "GEO_LOCK: ACTIVO" / "PERÍMETRO 250M" en el panel de georreferencia
//     SÍ se restauran -- son literalmente el mismo tipo de rótulo de
//     estado de sistema, decorativo y fijo, que ya usa el resto del
//     producto ("TELEMETRÍA // EN VIVO", "SISTEMA SENSOR SOCIAL"): no
//     insinúan un dato específico por escuela, así que no violan la regla
//     de "nunca inventar" -- son parte de la identidad visual del
//     protocolo, igual en cualquier caso.
//   - Lo que SIGUE sin poder mostrarse tal cual, porque no hay campo real
//     detrás (mismo criterio "nunca inventar", CLAUDE.md §4):
//       · "Sub-red Poniente" / "Zona Escolar Urbana 12" / "Cuadrante Valle
//         Sur" / "Zona 04 · Perímetro Céntrico": subzonas administrativas
//         por escuela que ni EscuelaOut ni EscuelaDetalleOut traen
//         (confirmado en src/api/schemas.py) -- inventar un nombre de zona
//         junto al nombre real de una escuela real sería atribuirle una
//         ubicación administrativa falsa a una institución concreta. Se
//         omiten.
//       · "Cluster Prioritario: Edomex Norte-Valle Central" (barra
//         superior, imagen 2): SÍ existe un campo real con ese nombre --
//         `PrediccionOut.cluster` (src/api/schemas.py) -- pero es un
//         ENTERO de un modelo de clustering (ML-03/US-321, Estefany
//         Hernández) que **todavía no existe**: el propio schema lo deja
//         `None` a propósito ("sin productor, cluster es None", BUG-010) y
//         getConclusionEscuelas() ni siquiera lo pide todavía. No es lo
//         mismo que "la entidad con más casos" (eso ya se muestra, real,
//         en el chip de filtro de arriba) -- serían dos conceptos
//         distintos, y ponerle "Cluster Prioritario" a un cálculo que no
//         es el cluster real confundiría el término. Se omite el segmento
//         completo de la barra superior en vez de rellenarlo con un
//         número o nombre que no le corresponde. Vale la pena avisarle al
//         equipo (Estefany/ML-03) que este es justo el elemento de UX que
//         falta por construir del lado de datos.
//       · El icono decorativo "insights" del pie de la lista (mockup) no
//         se agrega: no se tiene la certeza del trazo SVG exacto de ese
//         glifo de Material Symbols y un path inventado se vería peor que
//         omitirlo -- se deja el texto sin icono, igual que ya estaba.
//   - "Lat/Lon" del panel inspector: el mockup literalmente dice "Lon:
//     99.6569° W" (inglés) -- se mantiene "O" (Oeste) en español, como el
//     resto de la pantalla, en vez de copiar ese error de idioma del
//     propio mockup de Stitch.
//
// El resto de las decisiones del primer pase (nota diagnóstica calculada
// en vivo sin la marca "Asistente FARO", caso activo por defecto = primero
// del arreglo real, fuente de datos getConclusionEscuelas) NO cambia --
// Diana no las tocó en este segundo pedido.
//
// 13-sep, TERCERA RONDA -- Diana revisó el render y pidió 3 ajustes más,
// con 4 imágenes (2 de su propio render, 2 recortes del mockup original):
//   1) La tarjeta "Nota diagnóstica" (de-brandeada en el primer pase, por
//      no confundirla con el chat real "Asistente FARO" ya montado en
//      App.jsx) se reemplaza por el encabezado tal cual lo pinta el
//      mockup: "ASISTENTE FARO // NOTA DIAGNÓSTICA" + etiqueta "Auditoría
//      activa" a la derecha. Diana decide aquí que sí quiere esa
//      literalidad -- la nota de la tensión queda documentada, pero la
//      decisión de diseño es suya. El CONTENIDO sigue siendo el calculado
//      en vivo de notaDiagnostica() (nunca la oración fija del mockup con
//      "Mixcoac"/0.47/0.06 de ejemplo) -- eso no cambió, solo el rótulo.
//   2) Se quita por completo el bloque kicker/título/subtítulo
//      ("Pantalla 03 · Selección de caso" / "Los casos que requieren
//      atención" / "N escuelas presentan..."): no es parte del mockup de
//      Stitch (esa pantalla no tiene ese encabezado, es un patrón que se
//      arrastró del primer armado de la pantalla) y quedaba redundante
//      con la barra de protocolo de arriba -- mismo criterio que el punto
//      1 de la segunda ronda de Panorama.jsx. El DemoBadge y el enlace
//      "← Volver al panorama" se reubican dentro de esa misma barra de
//      protocolo para no perder ninguna de las dos funciones.
//   3) La barra inferior "N escuelas identificadas..." + la tarjeta
//      LeyendaGrafica (Qué se ve/Unidad/SIN_DATO aquí/Ciclo y recorte) se
//      quitan enteras -- se reemplazan por una sola barra de cierre con el
//      formato y el texto del pie del mockup ("SISTEMA SENSOR SOCIAL //
//      FARO-V2.4"), sin la leyenda extendida (esa leyenda no existe en el
//      mockup de esta pantalla; era un añadido del primer pase).
//   4) Ningún icono nuevo en ninguno de los dos elementos de arriba: el
//      mockup dibuja un ícono "psychology" junto a NOTA DIAGNÓSTICA y un
//      ícono "insights" en el pie, pero Diana pidió quitarlos -- quedan
//      solo como texto, sin glifo.
//
// 13-sep, CUARTA RONDA -- 4 pedidos más, sin imágenes nuevas:
//   1) Se quita el enlace "← Volver al panorama" de la barra de protocolo
//      (reubicado ahí en la tercera ronda) -- ya no queda ningún enlace de
//      regreso en esta pantalla. El Sidebar sigue siendo la vía real para
//      navegar entre fases.
//   2) Los 2 breakpoints que decidían "lista + inspector en columnas" vs.
//      "todo apilado" bajan de `xl` (1280px) a `lg` (1024px): con `xl`, una
//      ventana no maximizada en una pantalla normal (~1366px de ancho de
//      *viewport*, no de pantalla) ya apilaba el inspector debajo de la
//      lista aunque hubiera espacio de sobra. `lg` reacciona antes y deja
//      más rango de anchos de ventana usando el layout de 2 columnas.
//   3) TODOS los iconos SVG de Icons.jsx se quitan de este archivo: el de
//      "info" del banner, el de "location_on" de georreferencia, y las 2
//      flechas ("Saltar directo a Conclusión Global" / "Abrir expediente
//      completo"). También se quita el emoji por driver (🚨, 🏘️, etc.) del
//      badge "VECTOR DOMINANTE" de cada fila. Import de Icons.jsx eliminado
//      del todo -- ya no se usa nada de ahí en este archivo.
//      OJO -- lo único que NO se quitó: el ▲/■/● de "ATENCIÓN" (nivelRiesgo,
//      lib/mock.js). Ese no es un icono decorativo de Material Symbols: es
//      el requisito de diseño S3/DEC-023 ("nivel de atención sin color
//      propio -- ícono + texto únicamente, nunca semáforo"), la alternativa
//      es exactamente el semáforo rojo/ámbar/verde que el propio doc de
//      identidad rechaza. Si de verdad quieres que también desaparezca,
//      dímelo y lo quito, pero entonces el nivel de atención quedaría solo
//      como texto ("alta"/"media"/"baja").
//   4) Recuadros más grandes/anchos: padding de cada fila de caso subió de
//      --faro-space-md (12px) a --faro-space-lg (24px); la pista de índice
//      pasó de 88px a 120px de ancho; el badge "VECTOR DOMINANTE" de
//      min-w-[7.5rem] a min-w-[9.5rem]; las barras de filtros/banner/cierre
//      de p-3/p-4 a p-5; y el panel inspector de la derecha de 26rem (el
//      ancho documentado en Design_Tokens_Stitch.md para ese panel) a
//      32rem -- ese es el único valor que ya no coincide con el token
//      documentado, avisado aquí por si prefieres mantenerlo en 26rem.
//
// 13-sep, QUINTA RONDA -- 2 pedidos más:
//   1) Se agrega de vuelta el icono decorativo del pie de la lista de
//      casos (figura adjunta), justo debajo de la última fila -- ya vivía
//      ahí (la barra "N escuelas identificadas..." + "SISTEMA SENSOR
//      SOCIAL // FARO-V2.4"), solo le faltaba el icono. Es un dibujo
//      propio (IconTrendingUp, components/Icons.jsx), no el glifo exacto
//      de Material Symbols "insights" -- mismo motivo que la ronda
//      anterior: sin certeza del trazo oficial, mejor un equivalente
//      honesto que uno adivinado.
//   2) "Desglose preliminar de vectores" (panel inspector): se quita el
//      emoji por driver y se agrega el id (D1..D6) en su lugar, como ya
//      hace el propio mockup ("D1 Pobreza y Rezago Social"). Este cambio
//      vive en components/DriverBars.jsx, COMPARTIDO con la Pantalla 4
//      (Expediente de Escuela) -- se avisa aquí porque también se ve ahí,
//      no solo en esta pantalla.
export default function LosSieteCasos() {
  const { status, data, error } = useApiResource(getConclusionEscuelas, { mock: panoramaMock });
  const { status: cortesStatus, cortes, error: cortesError } = useCortesAtencion();
  const esReal = status === "ok";
  const escuelas = status === "ok" || status === "demo" ? data : [];
  const n = escuelas.length;

  const [selectedCct, setSelectedCct] = useState(null);
  const activo = (selectedCct ? escuelas.find((e) => e.cct === selectedCct) : null) ?? escuelas[0] ?? null;

  // Entidad real desde cve_mun (INEGI "EEMMM") -- mismo helper que
  // Panorama.jsx; en modo demo el mock no trae cve_mun, se resuelve por
  // nombre de entidad contra ENTIDADES_LABEL.
  const cveEntDeEscuela = (e) => {
    if (typeof e.cve_mun === "string") return e.cve_mun.slice(0, 2);
    const porNombre = ENTIDADES_LABEL.find((ent) => ent.nombre.toLowerCase() === (e.entidad ?? "").toLowerCase());
    return porNombre ? porNombre.cveEnt : null;
  };
  const entidadDeEscuela = (e) => {
    if (!e) return null;
    if (esReal) {
      const cveEnt = cveEntDeEscuela(e);
      return cveEnt ? ENTIDADES_LABEL.find((ent) => ent.cveEnt === cveEnt)?.nombre ?? null : null;
    }
    return e.entidad ?? null;
  };
  const municipioDeEscuela = (e) => (e ? (esReal ? e.nombre_municipio ?? null : e.municipio ?? null) : null);
  const lugarDeEscuela = (e) => [municipioDeEscuela(e), entidadDeEscuela(e)].filter(Boolean).join(", ");

  // FIX (2026-09-13, pedido de Diana -- "arreglar el mapa sin quitarlo"): mismo
  // cveEntDeEscuela(e) de arriba, contra el mismo catalogo ENTIDADES_LABEL, para
  // obtener {id, color} y poder dibujar el mapa real de MapaPin.jsx en vez del
  // radar decorativo.
  const entidadInfoDeEscuela = (e) => {
    if (!e) return null;
    const cveEnt = cveEntDeEscuela(e);
    return cveEnt ? ENTIDADES_LABEL.find((ent) => ent.cveEnt === cveEnt) ?? null : null;
  };

  // Chip de filtro "Entidad: ..." (decorativo, igual que en el mockup --
  // ver comentario de arriba): entidad real con más de las N escuelas de
  // este conjunto, y su conteo real. Mismo cálculo que "Enclave
  // Georreferenciado" de Panorama.jsx, aplicado aquí sobre estas 7.
  const conteoPorEntidad = {};
  for (const e of escuelas) {
    const cveEnt = cveEntDeEscuela(e);
    if (!cveEnt) continue;
    conteoPorEntidad[cveEnt] = (conteoPorEntidad[cveEnt] ?? 0) + 1;
  }
  const cveEntTop = Object.entries(conteoPorEntidad).sort((a, b) => b[1] - a[1])[0]?.[0] ?? null;
  const entidadTop = cveEntTop ? ENTIDADES_LABEL.find((e) => e.cveEnt === cveEntTop) : null;
  const conteoEntidadTop = cveEntTop ? conteoPorEntidad[cveEntTop] : null;

  // "Nivel de Riesgo: ▲ Alta" del chip de filtro solo se afirma si es
  // literalmente cierto para las N escuelas de este conjunto -- nunca un
  // texto fijo como en el mockup.
  const nivelesDeAtencion = cortes ? escuelas.map((e) => nivelRiesgo(e.indice_riesgo, cortes).label) : [];
  const todasAlta = nivelesDeAtencion.length > 0 && nivelesDeAtencion.every((l) => l === "Alta");

  // Nota diagnóstica calculada del propio conjunto de drivers de la
  // escuela activa: su driver dominante contra su driver de menor valor
  // (ambos reales, d1..d6 de EscuelaDetalleOut) -- nunca la oración fija
  // del mockup.
  const notaDiagnostica = (e) => {
    if (!e || !e.driver_dominante) return null;
    // FIX (2026-09-13, US-651, hallazgo de Marina García + su IA): D3/D4
    // llegan crudos (alto = buen servicio) -- sin orientar, esta nota podía
    // decir "mayor presión en Conectividad (1.00)" para una escuela con
    // conectividad completa, justo lo contrario. Ver lib/driverOrientacion.js.
    const drivers = {
      D1: e.d1,
      D2: e.d2,
      D3: valorOrientado("D3", e.d3),
      D4: valorOrientado("D4", e.d4),
      D5: e.d5,
      D6: e.d6,
    };
    const valorDominante = drivers[e.driver_dominante];
    if (typeof valorDominante !== "number") return null;
    const otros = Object.entries(drivers).filter(([code, v]) => code !== e.driver_dominante && typeof v === "number");
    const nombreDom = driverNombres[e.driver_dominante];
    if (!otros.length) {
      return `El plantel ${e.nombre} registra su mayor presión en ${nombreDom} (${valorDominante.toFixed(2)}); los demás drivers no tienen dato todavía.`;
    }
    const [codeMin, valMin] = otros.sort((a, b) => a[1] - b[1])[0];
    return `El plantel ${e.nombre} registra su mayor presión en ${nombreDom} (${valorDominante.toFixed(2)}), frente a ${driverNombres[codeMin].toLowerCase()} (${valMin.toFixed(2)}), su valor más bajo entre los drivers observados.`;
  };

  return (
    <PageContainer>
      {/* FIX (2026-09-13, US-651, obs. 8, Marina García + su IA): "AUDITORÍA
          TERRITORIAL DE RIESGO" pasa a la etiqueta real de esta fase ("Selección de
          Caso"), tomada de FASES (lib/navFases.js) -- misma nomenclatura que la barra
          lateral y el resto de pantallas del flujo. */}
      <div
        className="rounded-xl px-4 py-3 flex items-center justify-between flex-wrap gap-3"
        style={{ background: "var(--faro-canvas-container)", border: "1px solid var(--faro-hairline)" }}
      >
        <div className="flex items-center gap-3 flex-wrap">
          <span
            className="text-label-micro-mono font-semibold px-2 py-1 rounded"
            style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
          >
            FASE_{FASES.find((f) => f.to === "/casos").n}
          </span>
          <span className="text-label-micro-mono uppercase" style={{ color: "var(--color-ink-faint)" }}>
            {FASES.find((f) => f.to === "/casos").label}
          </span>
        </div>
        <div className="flex items-center gap-3 flex-wrap text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
          <span>
            CASOS DETECTADOS: <strong style={{ color: "var(--color-ink)" }}>{String(n).padStart(2, "0")} UNIDADES</strong>
          </span>
          <span>/</span>
          <span>
            SELECCIÓN ACTIVA:{" "}
            <span
              className="px-2 py-0.5 rounded font-semibold"
              style={{ background: "rgba(2, 132, 199, 0.1)", color: "var(--faro-signal)" }}
            >
              {activo?.cct ?? "—"}
            </span>
          </span>
          {status === "demo" && <DemoBadge />}
        </div>
      </div>

      {/* ---- Banner de protocolo (imagen 2: icono + "Protocolo de Auditoría
          Selectiva Flexible" + chip "MODO_EXPEDITO", texto literal) ---- */}
      <div
        className="p-5 rounded-xl shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative overflow-hidden"
        style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)" }}
      >
        <div className="absolute left-0 top-0 bottom-0 w-1" style={{ background: "var(--faro-signal)" }} aria-hidden="true" />
        <div className="flex flex-col gap-1 pl-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-title-md" style={{ color: "var(--color-ink)" }}>Protocolo de Auditoría Selectiva Flexible</span>
            <span
              className="text-label-micro-mono px-2 py-0.5 rounded"
              style={{ background: "var(--faro-canvas-container)", color: "var(--color-ink-faint)" }}
            >
              MODO_EXPEDITO
            </span>
          </div>
          <p className="text-body-sm max-w-3xl" style={{ color: "var(--color-ink-faint)" }}>
            El protocolo analítico permite examinar <strong style={{ color: "var(--color-ink)" }}>un único plantel representativo</strong> para
            activar la síntesis diagnóstica. No es indispensable auditar los {n || 7} expedientes de forma consecutiva antes de emitir la resolución
            técnica integral.
          </p>
        </div>
        <Link
          to="/conclusion"
          className="text-label-ui inline-flex items-center px-4 py-2 rounded-lg shrink-0 self-start lg:self-center shadow-sm"
          style={{ background: "var(--faro-canvas-container)", color: "var(--color-ink)" }}
        >
          Saltar directo a Conclusión Global
        </Link>
      </div>

      {status === "loading" && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>Cargando escuelas…</p>
      )}
      {status === "error" && (
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No se pudieron cargar las escuelas del API ({error}).
        </p>
      )}
      {(status === "ok" || status === "demo") && cortesStatus !== "loading" && !cortes && (
        <p className="text-sm" style={{ color: "var(--color-risk-high)" }}>
          No fue posible cargar los cortes de atención desde /version{cortesStatus === "error" && cortesError ? ` (${cortesError})` : ""}. Intenta de nuevo más tarde.
        </p>
      )}

      {escuelas.length > 0 && cortes && activo && (
        <div className="flex flex-col lg:flex-row gap-5 items-start">
          {/* ---- Panel central: filtros + lista de casos (fila por escuela) ---- */}
          <div className="flex-1 w-full min-w-0 flex flex-col gap-3">
            {/* Barra de filtros -- decorativa, igual que en el propio mockup
                (sin onClick / sin recorte real del conjunto): P3 reutiliza los
                mismos datos ya cargados en P2, sin filtros reales todavía
                (02_Data_Visualization_Spec.md línea 95). Valores mostrados
                SÍ son reales (entidad con más casos y su conteo). */}
            <div
              className="p-5 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-2"
              style={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", boxShadow: "var(--shadow-card)" }}
            >
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--color-ink-faint)" }}>
                  Filtrar por:
                </span>
                {entidadTop && (
                  <span
                    className="text-label-micro-mono px-2 py-0.5 rounded-lg"
                    style={{ background: "var(--faro-canvas-container)", color: "var(--color-ink)" }}
                  >
                    Entidad: {entidadTop.nombre} ({conteoEntidadTop})
                  </span>
                )}
                {nivelesDeAtencion.length > 0 && (
                  <span
                    className="text-label-micro-mono px-2 py-0.5 rounded-lg"
                    style={{ background: "var(--faro-canvas-container)", color: "var(--color-ink)" }}
                  >
                    Nivel de Riesgo: {todasAlta ? "▲ Alta" : "mixto"}
                  </span>
                )}
                <span className="text-label-micro-mono cursor-default" style={{ color: "var(--faro-signal)" }}>
                  Reestablecer
                </span>
              </div>
              <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>
                ORDEN: <span className="font-semibold uppercase" style={{ color: "var(--color-ink)" }}>Índice compuesto descendente</span>
              </span>
            </div>

            <div className="flex flex-col" style={{ gap: "var(--faro-space-sm)" }}>
              {escuelas.map((e, i) => {
                const color = riskRampColor(e.indice_riesgo);
                const riesgo = nivelRiesgo(e.indice_riesgo, cortes);
                const seleccionada = activo.cct === e.cct;
                const lugar = lugarDeEscuela(e);
                return (
                  <div
                    key={e.cct}
                    role="button"
                    tabIndex={0}
                    onClick={() => setSelectedCct(e.cct)}
                    onKeyDown={(ev) => {
                      if (ev.key === "Enter" || ev.key === " ") {
                        ev.preventDefault();
                        setSelectedCct(e.cct);
                      }
                    }}
                    className="group relative aparicion-escalonada cursor-pointer overflow-hidden"
                    style={{
                      "--delay": `${i * 40}ms`,
                      padding: "var(--faro-space-lg)",
                      background: "var(--color-surface)",
                      border: seleccionada ? "2px solid var(--faro-signal)" : "1px solid var(--color-border)",
                      boxShadow: "var(--shadow-card)",
                      borderRadius: "var(--radius-card)",
                    }}
                  >
                    {seleccionada && (
                      <div
                        className="absolute left-0 top-0 bottom-0"
                        style={{ width: 4, background: "var(--faro-signal)" }}
                        aria-hidden="true"
                      />
                    )}
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3" style={{ paddingLeft: seleccionada ? 8 : 0 }}>
                      <div className="flex items-start gap-3 min-w-0">
                        <span
                          className="text-label-data-mono shrink-0 mt-0.5"
                          style={{ color: seleccionada ? "var(--faro-signal)" : "var(--color-ink-faint)", fontWeight: seleccionada ? 700 : 400 }}
                        >
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        <div className="flex flex-col min-w-0 gap-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <h3
                              className="text-title-md truncate group-hover:text-[color:var(--faro-signal)]"
                              style={{ color: seleccionada ? "var(--faro-signal)" : "var(--color-ink)", fontWeight: seleccionada ? 700 : 600 }}
                            >
                              {e.nombre}
                            </h3>
                            <span
                              className="text-label-data-mono px-2 py-0.5 rounded font-semibold"
                              style={
                                seleccionada
                                  ? { background: "var(--faro-signal)", color: "#ffffff" }
                                  : { background: "var(--color-surface-alt, #f4f4f5)", color: "var(--color-ink)" }
                              }
                            >
                              {e.cct}
                            </span>
                            <span
                              className="text-label-micro-mono px-2 py-0.5 rounded"
                              style={{ background: "var(--color-surface-alt, #f4f4f5)", color: "var(--color-ink-faint)" }}
                            >
                              {e.nivel}
                            </span>
                            {seleccionada && (
                              <span
                                className="inline-flex items-center gap-1 text-label-micro-mono font-semibold px-2 py-0.5 rounded"
                                style={{ background: "rgba(2, 132, 199, 0.12)", color: "var(--faro-signal)" }}
                              >
                                <span
                                  className="w-1.5 h-1.5 rounded-full"
                                  style={{ background: "var(--faro-signal)" }}
                                  aria-hidden="true"
                                />
                                SELECCIONADO PARA EXPEDIENTE
                              </span>
                            )}
                          </div>
                          <p className="text-label-micro-mono" style={{ color: seleccionada ? "var(--color-ink)" : "var(--color-ink-faint)" }}>
                            {lugar || "Municipio y entidad sin dato"}
                            {seleccionada && " • Expediente listo para inspección focalizada"}
                            {!seleccionada && " • Muestra diagnóstica: Activa"}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 shrink-0 pt-2 lg:pt-0 flex-wrap">
                        <div className="flex flex-col items-end gap-0.5">
                          <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>ATENCIÓN</span>
                          <span className="text-label-data-mono font-bold" style={{ color: "var(--color-ink)" }}>
                            {riesgo.icon} {riesgo.label.toLowerCase()}
                          </span>
                        </div>
                        <div className="flex flex-col items-end gap-0.5">
                          <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>ÍNDICE</span>
                          <span
                            className="text-label-data-mono font-bold"
                            style={{ color: seleccionada ? "var(--faro-signal)" : "var(--color-ink)" }}
                          >
                            {e.indice_riesgo.toFixed(3)}
                          </span>
                        </div>
                        <div
                          className="relative rounded-full overflow-hidden shrink-0"
                          style={{ width: 120, height: 8, background: "var(--color-surface-alt, #f4f4f5)" }}
                          title={`Línea de alerta: ${cortes.alta.toFixed(2)}`}
                        >
                          <div
                            className="h-full rounded-full"
                            style={{ width: `${Math.max(0, Math.min(1, e.indice_riesgo / (cortes.ancla_calibracion ?? 0.6))) * 100}%`, background: color }}
                          />
                          <div
                            className="absolute top-0 bottom-0"
                            style={{
                              left: `${Math.max(0, Math.min(1, cortes.alta / (cortes.ancla_calibracion ?? 0.6))) * 100}%`,
                              width: 2,
                              background: "var(--color-risk-high)",
                            }}
                          />
                        </div>
                        <div
                          className="px-3 py-2 rounded-lg flex flex-col items-end min-w-[9.5rem]"
                          style={{ background: "var(--color-surface-alt, #f4f4f5)", border: `1.5px solid ${DOMINANT_OUTLINE}` }}
                        >
                          <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>VECTOR DOMINANTE</span>
                          <span className="text-label-ui font-bold" style={{ color: DOMINANT_OUTLINE }}>
                            {driverNombres[e.driver_dominante]}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div
              className="p-5 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              style={{ background: "var(--faro-canvas-container)" }}
            >
              <div className="flex items-center gap-3">
                <IconTrendingUp size={20} style={{ color: "var(--faro-signal)" }} />
                <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>
                  {n} {n === 1 ? "escuela identificada" : "escuelas identificadas"} con nivel de atención alta. Caso representativo seleccionado:{" "}
                  <span className="font-semibold" style={{ color: "var(--color-ink)" }}>{activo.nombre}</span>
                  {activo.nivel ? ` (${activo.nivel}${lugarDeEscuela(activo) ? `, ${lugarDeEscuela(activo)}` : ""})` : ""}.
                </p>
              </div>
              <span className="text-label-micro-mono shrink-0" style={{ color: "var(--color-ink-faint)" }}>
                SISTEMA SENSOR SOCIAL // FARO-V2.4
              </span>
            </div>
          </div>

          {/* ---- Panel inspector: caso seleccionado ---- */}
          <aside className="w-full lg:w-[32rem] shrink-0 flex flex-col gap-4 lg:sticky lg:top-24">
            <Card>
              <div className="flex items-start justify-between gap-3 pb-3 mb-3" style={{ borderBottom: "1px solid var(--color-border)" }}>
                <div className="flex flex-col gap-1 min-w-0">
                  <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--faro-signal)" }}>
                    Previsualización de caso
                  </span>
                  <h2 className="text-headline-sm truncate" style={{ color: "var(--color-ink)" }}>{activo.nombre}</h2>
                  <p className="text-label-data-mono" style={{ color: "var(--color-ink-faint)" }}>
                    <span className="font-bold" style={{ color: "var(--color-ink)" }}>{activo.cct}</span> · {activo.nivel}
                    {lugarDeEscuela(activo) ? ` · ${lugarDeEscuela(activo)}` : ""}
                  </p>
                </div>
                <span
                  className="text-label-micro-mono font-semibold px-2 py-1 rounded shrink-0"
                  style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
                >
                  CASO_ACTIVO
                </span>
              </div>

              {typeof activo.latitud === "number" && typeof activo.longitud === "number" && (
                <div className="mb-4 flex flex-col gap-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--color-ink-faint)" }}>
                      Georreferencia Perimetral
                    </span>
                    {municipioDeEscuela(activo) && (
                      <span className="text-label-micro-mono font-semibold" style={{ color: "var(--faro-signal)" }}>
                        {municipioDeEscuela(activo).toUpperCase()}
                      </span>
                    )}
                  </div>
                  <div
                    className="rounded-lg relative flex flex-col justify-between p-2 overflow-hidden"
                    style={{ background: "var(--color-surface-alt, #f4f4f5)", border: "1px solid var(--color-border)", height: "9rem" }}
                  >
                    {/* FIX (2026-09-13, US-651, obs. 7, Marina García + su IA): se quitaron
                        "GEO_LOCK: ACTIVO" y "PERÍMETRO 250M" -- ninguna de las dos era una
                        medida real de esta escuela, eran etiquetas fijas de encuadre (mismo
                        hallazgo que "Radio de Vigilancia: 1,500m" en ExpedienteEscuela.jsx).
                        FIX (2026-09-13, pedido de Diana -- "arreglar el mapa sin quitarlo"):
                        el círculo concéntrico puramente decorativo que quedó en su lugar se
                        reemplazó primero por SiluetaEntidad.jsx y despues, a pedido de Diana,
                        por MapaPin.jsx: mapa de la república COMPLETA con la entidad
                        resaltada y un PIN real (mismo trazo que IconLocationOn, Icons.jsx) en
                        las coordenadas reales de ESTA escuela, sin depender de ningún servicio
                        externo. El Lat/Lon de abajo sigue siendo un dato real, se conserva
                        encima. */}
                    {entidadInfoDeEscuela(activo) && (
                      <div className="absolute inset-0">
                        <MapaPin
                          puntos={[
                            {
                              lat: activo.latitud,
                              lon: activo.longitud,
                              entidadId: entidadInfoDeEscuela(activo).id,
                              color: entidadInfoDeEscuela(activo).color,
                              etiqueta: activo.nombre ?? "Esta escuela",
                            },
                          ]}
                          ariaLabel={`Ubicación real de ${activo.nombre ?? "la escuela"} dentro de ${entidadInfoDeEscuela(activo).nombre}`}
                        />
                      </div>
                    )}
                    {/* FIX (2026-09-13, pedido de Diana -- "quita esa línea negra que dice
                        latitud y lon"): se quita la barra Lat/Lon -- el pin del mapa de arriba
                        ya señala la ubicación real de la escuela, el texto quedaba redundante.
                        El dato real sigue disponible al pasar el cursor sobre el pin (title del
                        <path>, ver MapaPin.jsx) para quien lo necesite. */}
                  </div>
                </div>
              )}

              <div className="flex flex-col gap-2 mb-4">
                <div className="flex items-center justify-between">
                  <span className="text-label-micro-mono uppercase font-semibold" style={{ color: "var(--color-ink-faint)" }}>
                    Desglose preliminar de vectores
                  </span>
                  <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>Escala 0.0–1.0</span>
                </div>
                {/* FIX (2026-09-13, US-651): DriverBars espera valores YA orientados
                    (igual que Explorador.jsx) -- pasar los crudos pintaba D4=1.00
                    (conectividad completa) como barra de presión máxima. */}
                <DriverBars
                  drivers={{
                    D1: activo.d1,
                    D2: activo.d2,
                    D3: valorOrientado("D3", activo.d3),
                    D4: valorOrientado("D4", activo.d4),
                    D5: activo.d5,
                    D6: activo.d6,
                  }}
                  driverDominante={activo.driver_dominante}
                />
              </div>

              <Link
                to={`/escuela/${activo.cct}`}
                className="w-full py-2.5 px-4 rounded-lg flex items-center justify-center text-body-sm font-semibold"
                style={{ background: "var(--faro-command-base)", color: "#ffffff" }}
              >
                Abrir expediente completo
              </Link>
              <p className="text-center text-label-micro-mono mt-2" style={{ color: "var(--color-ink-faint)" }}>
                FARO EXPEDIENTES // CCT {activo.cct}
              </p>
            </Card>

            {notaDiagnostica(activo) && (
              <Card>
                <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
                  <span className="text-label-micro-mono font-semibold uppercase" style={{ color: "var(--faro-signal)" }}>
                    Asistente FARO // Nota diagnóstica
                  </span>
                  <span className="text-label-micro-mono" style={{ color: "var(--color-ink-faint)" }}>Auditoría activa</span>
                </div>
                <p className="text-body-sm" style={{ color: "var(--color-ink-faint)" }}>{notaDiagnostica(activo)}</p>
              </Card>
            )}
          </aside>
        </div>
      )}
    </PageContainer>
  );
}
