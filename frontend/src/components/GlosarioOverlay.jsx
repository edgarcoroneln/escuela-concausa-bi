import { useCortesAtencion } from "../lib/cortesAtencion.js";

// Overlay de glosario, disponible "en todas las pantallas posteriores al
// login" (01_UX_Architecture.md §1). Los cortes de nivel de atención se leen
// de GET /api/v1/version (useCortesAtencion) -- nunca se escriben 0.50/0.30 a
// mano aquí tampoco, mismo criterio que nivelRiesgo() en data/mock.js.
//
// CORRECCIÓN 12-sep (auditoría mockups vs código, Equipo 3): faltaban 3 de
// los 8 términos que 02_Data_Visualization_Spec.md §1.2 exige textualmente
// ("Texto de datos que las gráficas necesitan que el glosario diga") --
// "Driver", "Recomendación" y la distinción "Nivel de atención ≠ prioridad"
// (esta última, además, es justo la aclaración que evita la confusión de
// BUG-063 entre el nivel de atención del front y la columna `prioridad` de
// Gold/Superset). También se completó "Índice de riesgo" con las anclas de
// calibración que el §1.2 pide explícitas. "Completitud de evidencia" se
// deja con su nombre ya usado en el resto del producto (LeyendaGrafica.jsx),
// aunque el spec la llama "Evidencia disponible" -- mismo concepto, un solo
// nombre para no tener dos etiquetas de lo mismo en la misma app.
const TERMINOS_BASE = [
  {
    termino: "SIN_DATO",
    definicion:
      "Marca que un driver o escuela no tiene una señal registrada para el ciclo consultado. No es un cero: tratarlo como cero subestimaría el riesgo, así que se muestra explícito, nunca en blanco.",
    pregunta: "¿Qué significa SIN_DATO?",
  },
  {
    termino: "Driver dominante",
    definicion:
      "El driver (de los 6 ejes de análisis) con mayor peso en el índice de riesgo de una escuela. Determina qué recomendación se le asocia.",
    pregunta: "¿Qué es el driver dominante?",
  },
  {
    termino: "Recomendación",
    definicion:
      "La acción asociada al driver dominante. Hay una por driver; dos escuelas con el mismo riesgo pueden recibir recomendaciones distintas.",
    pregunta: "¿Cómo se elige la recomendación de una escuela?",
  },
  {
    termino: "Completitud de evidencia",
    definicion:
      "Qué proporción de los 6 drivers tiene dato real (no SIN_DATO) para una escuela. Una completitud baja se comunica como evidencia incompleta, nunca como ausencia del problema.",
    pregunta: "¿Qué es la completitud de evidencia?",
  },
];

export default function GlosarioOverlay({ abierto, onCerrar, onPreguntar }) {
  const { cortes } = useCortesAtencion();

  if (!abierto) return null;

  const indiceDefinicion = cortes
    ? `Un número entre 0 y 1 que traduce la variación de matrícula que el modelo (ML-01) proyecta para la escuela en el próximo ciclo. ${cortes.media} corresponde a una escuela que conserva su matrícula y ${cortes.ancla_calibracion ?? 0.6} a una que perdería 5 %. FARO pone la línea de alerta en ${cortes.alta}, que equivale a perder alrededor de 3.4 %. No dice cuántos alumnos perdió la escuela.`
    : "Valor entre 0 y 1 que resume la propensión al abandono escolar de una escuela, calculado por el modelo (ML-01) a partir de sus 6 drivers.";

  const nivelDefinicion = cortes
    ? `Etiqueta (alta, media o baja) que resume qué tanta atención requiere una escuela, según su índice de riesgo: alta ≥ ${cortes.alta}, media ≥ ${cortes.media}, baja por debajo de ${cortes.media}. Nunca se deriva del campo "prioridad" (DEC-023, DEC-026).`
    : "Etiqueta (alta, media o baja) que resume qué tanta atención requiere una escuela, según su índice de riesgo. Nunca se deriva del campo \"prioridad\" (DEC-023, DEC-026).";

  const nivelVsPrioridadDefinicion = cortes
    ? `Superset (DB-09) muestra una columna llamada "prioridad" que viene de Gold y usa otro corte: solo llama alta a partir de ${cortes.ancla_calibracion ?? 0.6}. Como ninguna escuela de esta historia llega a ese valor, ahí aparecen como "media". Las dos lecturas son correctas según su propia definición; FARO usa siempre el nivel de atención y nunca le dice "prioridad" a esa etiqueta.`
    : `Superset (DB-09) muestra una columna llamada "prioridad" que usa otro corte distinto al nivel de atención de FARO. Las dos lecturas son correctas según su propia definición; FARO usa siempre el nivel de atención y nunca le dice "prioridad" a esa etiqueta.`;

  const terminos = [
    TERMINOS_BASE[0],
    { termino: "Índice de riesgo", definicion: indiceDefinicion, pregunta: "¿Cómo se calcula el índice de riesgo?" },
    { termino: "Nivel de atención", definicion: nivelDefinicion, pregunta: "¿Cómo se calcula el nivel de atención?" },
    { termino: "Nivel de atención ≠ \"prioridad\"", definicion: nivelVsPrioridadDefinicion, pregunta: "¿Por qué Superset a veces dice otra cosa distinta al nivel de atención?" },
    {
      termino: "Driver",
      definicion:
        "Cada una de las seis pistas del entorno que FARO revisa: pobreza y rezago, inseguridad, infraestructura escolar, conectividad, estrés hídrico y calidad del aire.",
      pregunta: "¿Qué es un driver?",
    },
    ...TERMINOS_BASE.slice(1),
  ];

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center p-4"
      style={{ background: "rgba(15, 23, 42, 0.5)" }}
      onClick={onCerrar}
    >
      <div
        className="w-full rounded-xl p-6 flex flex-col gap-4 max-h-[85vh] overflow-y-auto"
        style={{ maxWidth: "36rem", background: "var(--color-surface)", boxShadow: "var(--faro-shadow-modal)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg" style={{ color: "var(--color-ink)" }}>Glosario metodológico</h2>
          <button type="button" onClick={onCerrar} className="text-xl leading-none" style={{ color: "var(--faro-context-gray)" }} aria-label="Cerrar glosario">
            ×
          </button>
        </div>
        <div className="flex flex-col gap-3">
          {terminos.map((t) => (
            <div key={t.termino} className="p-3 rounded-lg" style={{ background: "var(--color-surface-alt)" }}>
              <p className="text-sm font-semibold" style={{ color: "var(--color-ink)" }}>{t.termino}</p>
              <p className="text-sm mt-1" style={{ color: "var(--color-ink-faint)" }}>{t.definicion}</p>
              {onPreguntar && (
                <button
                  type="button"
                  className="text-xs mt-2 underline"
                  style={{ color: "var(--faro-signal)" }}
                  onClick={() => {
                    onPreguntar(t.pregunta);
                    onCerrar();
                  }}
                >
                  Pregúntale al Asistente
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
