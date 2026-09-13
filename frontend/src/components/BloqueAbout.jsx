import Card from "./Card.jsx";
import MarkdownLite from "./MarkdownLite.jsx";
import MapaScope from "./MapaScope.jsx";
import DiagramaFlujo from "./DiagramaFlujo.jsx";

// Renderizadores de los bloques de "Cómo funciona" (US-601) en la UI nativa.
//
// El contrato es el mismo que consume el shell de Streamlit: un `tipo` por bloque y un renderer
// por tipo. Lo que cambia es el medio — allá cada bloque visual vive en su propio iframe
// (`components.html`), aquí viven en el mismo documento y heredan los tokens del tema.
//
// **Estado de la portación: completa.** Los ocho tipos del contrato se pintan aquí, y ninguno
// necesita una dependencia que el proyecto no tuviera ya.
//
// Los cuatro diagramas E-R que antes llegaban como `mermaid` ahora llegan como `svg` dibujado por
// la API. Se intentó primero con la librería y se revirtió: arrastra `chevrotain` → `lodash-es`
// con dos avisos de severidad **alta**, tanto en la línea 12 como en la 11, más 69 paquetes
// transitivos y 123 MB. Dibujarlos del lado del servidor los deja disponibles para cualquier
// interfaz sin negociar librerías — que es justo lo que hace viable retirar Streamlit (`ADR-012`)
// sin perderlos por el camino.
//
// `mapa` y `diagrama_flujo` se portaron con `d3-geo`/`d3-shape`, que ya eran dependencias.

// --------------------------------------------------------------------------- svg servido

function DiagramaSvg({ codigo, alt }) {
  return (
    <figure className="flex flex-col gap-2">
      <div
        className="overflow-x-auto rounded-xl p-4"
        style={{ background: "#ffffff", border: "1px solid var(--color-border)" }}
        role="img"
        aria-label={alt}
        // Marcado constante generado por nuestra propia API (`_diagrama_arquitectura`), sin
        // entrada de usuario en ningún punto.
        dangerouslySetInnerHTML={{ __html: codigo }}
      />
      <figcaption className="text-xs" style={{ color: "var(--color-ink-faint)" }}>
        {alt}
      </figcaption>
    </figure>
  );
}

// --------------------------------------------------------------------------- barras

function Barras({ items }) {
  const valores = items.map((i) => i.valor).filter((v) => v !== null && v !== undefined);
  const max = valores.length ? Math.max(...valores) : 0;
  return (
    <ul className="flex flex-col gap-3">
      {items.map((item) => {
        const sinDato = item.valor === null || item.valor === undefined;
        return (
          <li key={item.etiqueta} className="flex items-center gap-3">
            <span className="text-xs w-20 shrink-0" style={{ color: "var(--color-ink-soft)" }}>
              {item.etiqueta}
            </span>
            <div className="flex-1 h-3 rounded-full" style={{ background: "var(--color-border)" }}>
              {!sinDato && max > 0 && (
                <div
                  className="h-3 rounded-full"
                  style={{ width: `${(item.valor / max) * 100}%`, background: "var(--color-accent)" }}
                />
              )}
            </div>
            <span
              className="text-xs font-semibold tabular w-28 text-right shrink-0"
              style={{ color: sinDato ? "var(--color-sin-dato)" : "var(--color-ink)" }}
              title={item.nota ?? undefined}
            >
              {sinDato ? "SIN_DATO" : item.valor.toLocaleString("es-MX")}
            </span>
          </li>
        );
      })}
    </ul>
  );
}

// --------------------------------------------------------------------------- despachador

export default function BloqueAbout({ bloque }) {
  switch (bloque.tipo) {
    case "markdown":
      return <MarkdownLite texto={bloque.texto} />;

    case "tabla":
      return (
        <div className="overflow-x-auto rounded-xl" style={{ border: "1px solid var(--color-border)" }}>
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr>
                {bloque.columnas.map((c) => (
                  <th
                    key={c}
                    className="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-left"
                    style={{
                      color: "var(--color-ink-faint)",
                      background: "var(--color-surface-alt)",
                      borderBottom: "1px solid var(--color-border)",
                    }}
                  >
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {bloque.filas.map((fila, i) => (
                <tr key={i} style={{ borderBottom: "1px solid var(--color-border)" }}>
                  {fila.map((celda, j) => (
                    <td
                      key={j}
                      className="px-3 py-2.5 align-top"
                      style={{
                        color: j === 0 ? "var(--color-ink)" : "var(--color-ink-soft)",
                        fontWeight: j === 0 ? 600 : 400,
                      }}
                    >
                      {celda}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );

    case "metricas":
      return (
        <div className="grid gap-3" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
          {bloque.items.map((item) => {
            const sinDato = item.valor === null || item.valor === undefined;
            return (
              <Card key={item.etiqueta}>
                <p className="text-xs mb-1" style={{ color: "var(--color-ink-faint)" }}>
                  {item.etiqueta}
                </p>
                <p
                  className="text-2xl tabular"
                  style={{ color: sinDato ? "var(--color-sin-dato)" : "var(--color-ink)", fontWeight: 600 }}
                >
                  {sinDato ? "SIN_DATO" : Number(item.valor).toLocaleString("es-MX")}
                </p>
                {item.nota && (
                  <p className="text-xs mt-1" style={{ color: "var(--color-ink-faint)" }}>
                    {item.nota}
                  </p>
                )}
              </Card>
            );
          })}
        </div>
      );

    case "svg":
      return <DiagramaSvg codigo={bloque.codigo} alt={bloque.alt} />;

    case "barras":
      return <Barras items={bloque.items} />;

    case "mapa":
      return <MapaScope geojson={bloque.geojson} resaltados={bloque.resaltados} fondo={bloque.fondo} />;

    case "diagrama_flujo":
      return <DiagramaFlujo nodos={bloque.nodos} enlaces={bloque.enlaces} />;

    default:
      // Contrato hacia adelante: un tipo nuevo del lado de la API no tumba la pantalla.
      return (
        <div
          className="rounded-xl p-4 text-sm"
          style={{ background: "var(--color-sin-dato-bg)", color: "var(--color-ink-soft)" }}
        >
          Tipo de bloque no soportado todavía por esta interfaz: <code>{bloque.tipo}</code>.
        </div>
      );
  }
}
