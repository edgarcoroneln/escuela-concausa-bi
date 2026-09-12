// Renderizador del subconjunto de Markdown que realmente usan los bloques de "Cómo funciona".
//
// **Por qué no una librería.** Se midió el contenido real que sirve la API en las 6 secciones:
// código en línea (53 usos), negritas (26), encabezados `###` (5) y una lista numerada. Nada de
// enlaces, imágenes, tablas ni HTML embebido — las tablas son su propio tipo de bloque. Traer un
// parser completo (y su superficie de HTML arbitrario) para eso sería más riesgo que beneficio.
//
// **Consecuencia declarada:** si alguien escribe Markdown fuera de ese subconjunto en un bloque,
// aquí se verá literal, no roto. Es el modo de falla que se prefirió: texto de más antes que
// contenido desaparecido en silencio.

const CODIGO_O_NEGRITA = /(`[^`]+`|\*\*[^*]+\*\*)/g;

function conFormatoEnLinea(texto, claveBase) {
  return texto.split(CODIGO_O_NEGRITA).map((parte, i) => {
    const clave = `${claveBase}-${i}`;
    if (parte.startsWith("`") && parte.endsWith("`") && parte.length > 1) {
      return (
        <code
          key={clave}
          className="px-1 py-0.5 rounded text-[0.85em]"
          style={{
            fontFamily: "var(--font-mono, ui-monospace, monospace)",
            background: "var(--color-surface-alt)",
            border: "1px solid var(--color-border)",
            color: "var(--color-ink-soft)",
          }}
        >
          {parte.slice(1, -1)}
        </code>
      );
    }
    if (parte.startsWith("**") && parte.endsWith("**") && parte.length > 3) {
      return (
        <strong key={clave} style={{ color: "var(--color-ink)", fontWeight: 600 }}>
          {parte.slice(2, -2)}
        </strong>
      );
    }
    return <span key={clave}>{parte}</span>;
  });
}

export default function MarkdownLite({ texto }) {
  const lineas = texto.split("\n");
  const nodos = [];
  let parrafo = [];
  let lista = [];

  const cerrarParrafo = () => {
    if (!parrafo.length) return;
    const contenido = parrafo.join(" ");
    nodos.push(
      <p key={`p-${nodos.length}`} className="text-sm leading-relaxed" style={{ color: "var(--color-ink-soft)" }}>
        {conFormatoEnLinea(contenido, `p${nodos.length}`)}
      </p>,
    );
    parrafo = [];
  };

  const cerrarLista = () => {
    if (!lista.length) return;
    const items = lista;
    nodos.push(
      <ol key={`ol-${nodos.length}`} className="flex flex-col gap-2 pl-1">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2.5 text-sm leading-relaxed" style={{ color: "var(--color-ink-soft)" }}>
            <span
              className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold"
              style={{ background: "var(--color-primary-soft)", color: "var(--color-primary)" }}
            >
              {i + 1}
            </span>
            <span>{conFormatoEnLinea(item, `li${nodos.length}-${i}`)}</span>
          </li>
        ))}
      </ol>,
    );
    lista = [];
  };

  for (const linea of lineas) {
    const limpia = linea.trim();
    if (!limpia) {
      cerrarParrafo();
      cerrarLista();
      continue;
    }
    const encabezado = limpia.match(/^(#{2,4})\s+(.*)$/);
    if (encabezado) {
      cerrarParrafo();
      cerrarLista();
      nodos.push(
        <h3
          key={`h-${nodos.length}`}
          className="text-base mt-1"
          style={{ color: "var(--color-ink)", fontWeight: 600, fontFamily: "var(--font-display)" }}
        >
          {conFormatoEnLinea(encabezado[2], `h${nodos.length}`)}
        </h3>,
      );
      continue;
    }
    const numerada = limpia.match(/^\d+\.\s+(.*)$/);
    if (numerada) {
      cerrarParrafo();
      lista.push(numerada[1]);
      continue;
    }
    cerrarLista();
    parrafo.push(limpia);
  }
  cerrarParrafo();
  cerrarLista();

  return <div className="flex flex-col gap-3">{nodos}</div>;
}
