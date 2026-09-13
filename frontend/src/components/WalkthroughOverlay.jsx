// Walkthrough de la Pantalla 1, texto literal de 01_UX_Architecture.md §4.
// Se superpone a P1, no navega ni la reemplaza -- el botón "Empezar" solo
// cierra el overlay.
const PASOS = [
  "Bienvenido a FARO. Vamos a investigar juntos qué está pasando con la matrícula escolar.",
  "La matrícula nos dio la primera pista. Ahora vamos a revisar la evidencia detrás de cada caso.",
  "En cualquier momento puedes preguntarle al Asistente FARO —el botón flotante— sobre los datos de FARO.",
];

export default function WalkthroughOverlay({ abierto, onCerrar }) {
  if (!abierto) return null;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center p-4"
      style={{ background: "rgba(15, 23, 42, 0.5)" }}
      onClick={onCerrar}
    >
      <div
        className="w-full rounded-xl p-6 flex flex-col gap-4"
        style={{ maxWidth: "28rem", background: "var(--color-surface)", boxShadow: "var(--faro-shadow-modal)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <span className="font-mono-dato text-[10px] uppercase font-semibold tracking-wider" style={{ color: "var(--faro-signal)" }}>
          Guía rápida
        </span>
        <div className="flex flex-col gap-3">
          {PASOS.map((paso, i) => (
            <p key={i} className="text-sm leading-relaxed" style={{ color: "var(--color-ink)" }}>
              {paso}
            </p>
          ))}
        </div>
        <div className="flex justify-end pt-1">
          <button
            type="button"
            onClick={onCerrar}
            className="text-sm font-semibold px-4 py-2 rounded-md"
            style={{ background: "var(--color-primary)", color: "#ffffff" }}
          >
            Empezar
          </button>
        </div>
      </div>
    </div>
  );
}
