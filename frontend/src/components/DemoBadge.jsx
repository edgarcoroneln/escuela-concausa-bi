// Etiqueta visible para cualquier dato de ejemplo que se muestre en pantalla
// (revisión de Edgar, PR #302, 10-sep) -- nunca debe verse en producción.
// Úsala junto a cualquier bloque que siga usando src/data/mock.js mientras
// su endpoint real no exista o no esté conectado.
export default function DemoBadge({ children = "Datos de ejemplo -- no conectado al API real" }) {
  return (
    <span
      className="text-[11px] font-semibold px-2.5 py-1 rounded-full inline-flex items-center gap-1.5"
      style={{ background: "#f5a62333", color: "#8a5a00" }}
      title="Modo demo. Ver frontend/src/lib/demoMode.js"
    >
      🧪 {children}
    </span>
  );
}
