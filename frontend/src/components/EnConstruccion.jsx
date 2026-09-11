import Card from "./Card.jsx";

// Placeholder deliberado: la arquitectura (rutas, componentes, API, deploy)
// se decide y valida primero; el contenido de cada pantalla del storytelling
// se llena pantalla por pantalla en la siguiente fase.
export default function EnConstruccion({ nota }) {
  return (
    <Card title="En construcción" subtitle="Arquitectura lista, contenido pendiente">
      <p className="text-sm" style={{ color: "var(--color-ink-soft)" }}>
        {nota ?? "Esta pantalla se llenará con datos reales del API en la siguiente fase."}
      </p>
    </Card>
  );
}
