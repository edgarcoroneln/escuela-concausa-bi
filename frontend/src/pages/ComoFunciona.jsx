import { useEffect, useState } from "react";
import PageContainer from "../components/PageContainer.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Card from "../components/Card.jsx";
import BloqueAbout from "../components/BloqueAbout.jsx";
import { getSeccion, getSecciones } from "../lib/about.js";

// "Cómo funciona" (US-601) en la interfaz nativa.
//
// La pantalla no sabe qué secciones existen ni qué traen: pide el manifest y pinta lo que venga.
// Agregar, quitar o reordenar una sección del lado de la API no obliga a tocar este archivo —
// que es exactamente lo que el contrato de bloques buscaba cuando se diseñó para Streamlit.
//
// Rutas públicas: no exige sesión.

export default function ComoFunciona() {
  const [secciones, setSecciones] = useState(null);
  const [errorManifest, setErrorManifest] = useState(null);
  const [activa, setActiva] = useState(null);
  const [contenido, setContenido] = useState(null);
  const [errorSeccion, setErrorSeccion] = useState(null);

  // `cargando` se DERIVA en vez de guardarse: es cierto exactamente mientras lo que hay en
  // pantalla no corresponde a la sección elegida. Guardarlo obligaba a un `setState` síncrono
  // dentro del efecto (y a mantener dos fuentes de verdad en sincronía).
  const cargando = Boolean(activa) && !errorSeccion && contenido?.id !== activa;

  useEffect(() => {
    let cancelado = false;
    getSecciones().then(({ data, error }) => {
      if (cancelado) return;
      if (error) {
        setErrorManifest(error);
        return;
      }
      const ordenadas = [...data].sort((a, b) => a.orden - b.orden);
      setSecciones(ordenadas);
      setActiva(ordenadas[0]?.id ?? null);
    });
    return () => {
      cancelado = true;
    };
  }, []);

  useEffect(() => {
    if (!activa) return undefined;
    let cancelado = false;
    getSeccion(activa).then(({ data, error }) => {
      if (cancelado) return;
      if (error) {
        setErrorSeccion(error);
        setContenido(null);
        return;
      }
      setErrorSeccion(null);
      setContenido(data);
    });
    return () => {
      cancelado = true;
    };
  }, [activa]);

  if (errorManifest) {
    return (
      <PageContainer>
        <PageHeader kicker="Cómo funciona" title="Cómo funciona FARO" />
        <Card>
          <p className="text-sm" style={{ color: "var(--color-alert)" }}>
            No se pudo leer el índice de secciones: {errorManifest}. El API responde en
            <code> /api/v1/about/secciones</code>; si estás en local, revisa que esté levantado.
          </p>
        </Card>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        kicker="Cómo funciona"
        title="Cómo funciona FARO"
        subtitle="De ocho fuentes públicas a una página: componentes, modelo de datos, capas, cubos, decisiones y modelos."
      />

      {/* Navegación entre secciones. El manifest manda el orden; esta pantalla no lo fija. */}
      <nav className="flex flex-wrap gap-2" aria-label="Secciones">
        {(secciones ?? []).map((s) => {
          const esActiva = s.id === activa;
          return (
            <button
              key={s.id}
              type="button"
              onClick={() => setActiva(s.id)}
              aria-current={esActiva ? "page" : undefined}
              className="text-sm px-3.5 py-1.5 rounded-full transition-colors"
              style={{
                background: esActiva ? "var(--color-primary)" : "var(--color-surface)",
                color: esActiva ? "#ffffff" : "var(--color-ink-soft)",
                border: `1px solid ${esActiva ? "var(--color-primary)" : "var(--color-border)"}`,
                fontWeight: esActiva ? 600 : 500,
              }}
            >
              {s.titulo}
            </button>
          );
        })}
      </nav>

      {cargando && (
        <p className="text-sm" style={{ color: "var(--color-ink-faint)" }}>
          Cargando sección…
        </p>
      )}

      {errorSeccion && (
        <Card>
          <p className="text-sm" style={{ color: "var(--color-alert)" }}>
            No se pudo cargar la sección: {errorSeccion}
          </p>
        </Card>
      )}

      {contenido && !cargando && (
        <article className="flex flex-col gap-5">
          {/* Advertencias del sobre: si la API declara una, va antes del contenido. */}
          {contenido.advertencias?.length > 0 && (
            <div
              className="rounded-xl p-4 flex flex-col gap-1"
              style={{ background: "var(--color-alert-soft)", border: "1px solid var(--color-alert)" }}
            >
              {contenido.advertencias.map((a, i) => (
                <p key={i} className="text-sm" style={{ color: "var(--color-alert)" }}>
                  {a}
                </p>
              ))}
            </div>
          )}

          {contenido.bloques.map((bloque, i) => (
            <BloqueAbout key={`${contenido.id}-${i}`} bloque={bloque} />
          ))}

          {/* Procedencia: cada sección declara de dónde salió su contenido. Se muestra porque es
              lo que permite notar que el original cambió y esta copia quedó atrás. */}
          {contenido.fuente?.length > 0 && (
            <footer
              className="pt-4 mt-2 flex flex-col gap-1.5"
              style={{ borderTop: "1px solid var(--color-border)" }}
            >
              <p
                className="text-xs font-semibold uppercase tracking-wide"
                style={{ color: "var(--color-ink-faint)" }}
              >
                Fuentes de esta sección
              </p>
              <ul className="flex flex-col gap-0.5">
                {contenido.fuente.map((f) => (
                  <li key={f} className="text-xs" style={{ color: "var(--color-ink-faint)" }}>
                    {f}
                  </li>
                ))}
              </ul>
            </footer>
          )}
        </article>
      )}
    </PageContainer>
  );
}
