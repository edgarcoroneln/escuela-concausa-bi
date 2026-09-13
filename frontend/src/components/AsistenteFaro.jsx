import { useEffect, useRef, useState } from "react";
import { postAgenteConsultaStream } from "../lib/api.js";

// Nodo flotante "Asistente FARO" (Design_Tokens_Stitch.md, componente
// "Floating Intelligence Node" + 01_UX_Architecture.md §6). Vive montado una
// sola vez en App.jsx -- así el panel y su conversación sobreviven la
// navegación entre pantallas (§6: "no se resetea al cambiar de pantalla"),
// en vez de vivir dentro de cada página.
//
// Consume el cliente SSE ya construido en lib/api.js (postAgenteConsultaStream,
// mergeado a main el 12-sep). El SQL generado NUNCA se muestra en el hilo de
// lectura por defecto (§6, corrige src/frontend/pages/3_Chat.py:85-87): se
// guarda por turno y solo se revela con la acción discreta "Ver la consulta".
//
// Los 3 mensajes de error son literales del spec (§6, diagnóstico Equipo 2) --
// no se inventan variantes. Un error de red/HTTP (servidor caído, 5xx) no
// tiene mensaje propio en el spec porque ese documento solo cubre errores del
// dominio del agente; se le da el mismo tratamiento que "timeout" en vez de
// inventar un cuarto texto no aprobado.
const ERROR_TIMEOUT = "El Asistente FARO está tardando más de lo esperado. Intenta de nuevo.";
const ERROR_SIN_DATOS = "No encontré información para responder eso con los datos disponibles.";
const ERROR_FUERA_DE_ALCANCE = "Esa pregunta está fuera de lo que el Asistente FARO puede consultar hoy.";

const MAX_TURNOS_HISTORIAL = 10;
const MAX_LARGO_TURNO = 500;

// Recorta cada turno al límite de HistorialTurnoIn (src/api/schemas.py) antes
// de mandarlo de regreso al API -- si no, un turno largo revienta el body
// completo con 422 en la siguiente pregunta.
function historialParaApi(mensajes) {
  const turnos = [];
  for (let i = 0; i < mensajes.length - 1; i++) {
    if (mensajes[i].rol === "usuario" && mensajes[i + 1]?.rol === "asistente") {
      turnos.push({
        pregunta: mensajes[i].texto.slice(0, MAX_LARGO_TURNO),
        respuesta: mensajes[i + 1].texto.slice(0, MAX_LARGO_TURNO),
      });
      i++;
    }
  }
  return turnos.slice(-MAX_TURNOS_HISTORIAL);
}

export default function AsistenteFaro({ visible, preguntaInicial, onPreguntaInicialConsumida }) {
  const [abierto, setAbierto] = useState(false);
  const [mensajes, setMensajes] = useState([]);
  const [pregunta, setPregunta] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [verConsultaDeIndice, setVerConsultaDeIndice] = useState(null);
  const listaRef = useRef(null);
  const abortRef = useRef(null);

  useEffect(() => {
    if (listaRef.current) listaRef.current.scrollTop = listaRef.current.scrollHeight;
  }, [mensajes, enviando]);

  // "Pregúntale al Asistente" desde el glosario: precarga la pregunta y abre
  // el panel, pero no la envía sola -- el usuario confirma (§6).
  useEffect(() => {
    if (preguntaInicial) {
      setAbierto(true);
      setPregunta(preguntaInicial);
      onPreguntaInicialConsumida?.();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preguntaInicial]);

  useEffect(() => () => abortRef.current?.abort(), []);

  if (!visible) return null;

  async function enviar(textoForzado) {
    const texto = (textoForzado ?? pregunta).trim();
    if (!texto || enviando) return;
    setPregunta("");
    setEnviando(true);

    const historial = historialParaApi(mensajes);
    const indiceUsuario = mensajes.length;
    setMensajes((m) => [...m, { rol: "usuario", texto }, { rol: "asistente", texto: "", sqlGenerado: null, fueraDeAlcance: false, cargando: true }]);

    const controller = new AbortController();
    abortRef.current = controller;

    const resultado = await postAgenteConsultaStream(texto, {
      historial,
      signal: controller.signal,
      onEvento: (tipo, data) => {
        setMensajes((m) => {
          const copia = [...m];
          const idx = indiceUsuario + 1;
          const actual = copia[idx];
          if (!actual) return m;
          if (tipo === "meta") {
            copia[idx] = { ...actual, sqlGenerado: data.sql_generado ?? null, fueraDeAlcance: !!data.fuera_de_alcance };
          } else if (tipo === "fragmento") {
            copia[idx] = { ...actual, texto: actual.texto + (data.texto ?? ""), cargando: false };
          } else if (tipo === "fin") {
            copia[idx] = { ...actual, cargando: false };
          }
          return copia;
        });
      },
    });

    if (resultado?.error) {
      setMensajes((m) => {
        const copia = [...m];
        const idx = indiceUsuario + 1;
        copia[idx] = { ...copia[idx], texto: ERROR_TIMEOUT, cargando: false, esError: true };
        return copia;
      });
    } else {
      // Si el fragmento acumulado quedó vacío pero el evento `fin` sí llegó,
      // el servidor mandó el "cierre degradado" (fuera_de_alcance / sin
      // datos) -- distinguimos por la bandera de `meta`, no por adivinar.
      setMensajes((m) => {
        const copia = [...m];
        const idx = indiceUsuario + 1;
        const actual = copia[idx];
        if (actual && !actual.texto.trim()) {
          copia[idx] = { ...actual, texto: actual.fueraDeAlcance ? ERROR_FUERA_DE_ALCANCE : ERROR_SIN_DATOS };
        }
        return copia;
      });
    }
    setEnviando(false);
    abortRef.current = null;
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      {abierto && (
        <div
          className="flex flex-col overflow-hidden rounded-xl"
          style={{
            width: "min(26rem, calc(100vw - 3rem))",
            maxHeight: "70vh",
            background: "var(--faro-command-base)",
            border: "1px solid var(--faro-signal-soft)",
            boxShadow: "var(--faro-shadow-asistente)",
          }}
        >
          <div className="flex items-center justify-between px-4 py-2.5" style={{ borderBottom: "1px solid rgba(255,255,255,0.12)" }}>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--faro-signal-soft)" }} />
              <span className="font-mono-dato text-[10px] font-semibold uppercase tracking-wider" style={{ color: "var(--faro-signal-soft)" }}>
                Asistente FARO // en línea
              </span>
            </div>
            <button
              type="button"
              onClick={() => setAbierto(false)}
              className="text-sm leading-none px-1"
              style={{ color: "#ffffff" }}
              aria-label="Cerrar Asistente FARO"
            >
              ×
            </button>
          </div>

          <div ref={listaRef} className="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-3" style={{ minHeight: "12rem" }}>
            {mensajes.length === 0 && (
              <p className="text-sm" style={{ color: "rgba(255,255,255,0.7)" }}>
                Pregunta cómo se calculan los índices, qué significa SIN_DATO, o sobre los datos de las 4 entidades (CDMX, Edomex, NL, Jalisco).
              </p>
            )}
            {mensajes.map((m, i) => (
              <div key={i} className="flex flex-col gap-1" style={{ alignItems: m.rol === "usuario" ? "flex-end" : "flex-start" }}>
                <div
                  className="text-sm px-3 py-2 rounded-lg max-w-[85%]"
                  style={
                    m.rol === "usuario"
                      ? { background: "var(--faro-signal)", color: "#ffffff" }
                      : { background: "rgba(255,255,255,0.08)", color: m.esError ? "#fca5a5" : "#ffffff" }
                  }
                >
                  {m.rol === "asistente" && m.cargando && !m.texto ? "…" : m.texto}
                </div>
                {m.rol === "asistente" && m.sqlGenerado && (
                  <button
                    type="button"
                    className="font-mono-dato text-[10px] underline"
                    style={{ color: "rgba(255,255,255,0.5)" }}
                    onClick={() => setVerConsultaDeIndice(verConsultaDeIndice === i ? null : i)}
                  >
                    {verConsultaDeIndice === i ? "Ocultar la consulta" : "Ver la consulta"}
                  </button>
                )}
                {verConsultaDeIndice === i && m.sqlGenerado && (
                  <pre
                    className="font-mono-dato text-[10px] px-2 py-1.5 rounded max-w-[85%] overflow-x-auto"
                    style={{ background: "rgba(0,0,0,0.35)", color: "rgba(255,255,255,0.8)" }}
                  >
                    {m.sqlGenerado}
                  </pre>
                )}
              </div>
            ))}
          </div>

          <form
            className="flex items-center gap-2 px-3 py-3"
            style={{ borderTop: "1px solid rgba(255,255,255,0.12)" }}
            onSubmit={(e) => {
              e.preventDefault();
              enviar();
            }}
          >
            <input
              type="text"
              value={pregunta}
              onChange={(e) => setPregunta(e.target.value)}
              disabled={enviando}
              placeholder={enviando ? "Transmitiendo…" : "Escribe tu pregunta…"}
              maxLength={500}
              className="flex-1 text-sm px-3 py-2 rounded-md"
              style={{ background: "rgba(255,255,255,0.08)", color: "#ffffff", border: "1px solid rgba(255,255,255,0.15)" }}
            />
            <button
              type="submit"
              disabled={enviando || pregunta.trim().length < 3}
              className="text-xs font-semibold px-3 py-2 rounded-md shrink-0"
              style={{
                background: "var(--faro-signal)",
                color: "#ffffff",
                opacity: enviando || pregunta.trim().length < 3 ? 0.5 : 1,
              }}
            >
              Enviar
            </button>
          </form>
        </div>
      )}

      <button
        type="button"
        onClick={() => setAbierto((v) => !v)}
        className="flex items-center gap-2 px-4 py-2.5 rounded-full"
        style={{
          background: "var(--faro-command-base)",
          color: "#ffffff",
          border: "1px solid var(--faro-signal-soft)",
          boxShadow: "var(--faro-shadow-asistente)",
        }}
      >
        <span className="w-2 h-2 rounded-full" style={{ background: "var(--faro-signal-soft)" }} />
        <span className="text-sm font-semibold">Asistente FARO</span>
      </button>
    </div>
  );
}
