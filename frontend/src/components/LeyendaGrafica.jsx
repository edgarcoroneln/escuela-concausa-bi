// Bloque fijo de leyenda para cualquier gráfica de la historia (US-641),
// contra 02_Data_Visualization_Spec.md §7.bis: "ninguna gráfica se entrega
// sin su leyenda" y "nunca solo tooltip". Cuatro declaraciones, en el orden
// fijo de la §7.bis.1 (qué se ve / unidad / SIN_DATO aquí / ciclo y
// recorte). El texto de cada pantalla sale literal de la tabla resuelta de
// la §7.bis.2 -- este componente solo le da forma visual, no lo redacta
// (Juan da tratamiento visual, Monserrat es dueña del texto, §7.5).
export default function LeyendaGrafica({ queSeVe, unidad, sinDato, cicloYRecorte }) {
  return (
    <div
      className="mt-3 pt-3 flex flex-col gap-1.5 text-xs"
      style={{ borderTop: "1px solid var(--color-border)", color: "var(--color-ink-faint)" }}
    >
      <p>
        <span className="font-semibold" style={{ color: "var(--color-ink)" }}>Qué se ve: </span>
        {queSeVe}
      </p>
      <p>
        <span className="font-semibold" style={{ color: "var(--color-ink)" }}>Unidad: </span>
        {unidad}
      </p>
      <p>
        <span className="font-semibold" style={{ color: "var(--color-ink)" }}>SIN_DATO aquí: </span>
        {sinDato}
      </p>
      <p>
        <span className="font-semibold" style={{ color: "var(--color-ink)" }}>Ciclo y recorte: </span>
        {cicloYRecorte}
      </p>
    </div>
  );
}
