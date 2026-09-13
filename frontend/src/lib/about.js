// Cliente de la sección "Cómo funciona" (US-601). Mismo contrato que consume el shell de
// Streamlit (`src/frontend/about_client.py`): un manifest y un sobre genérico de bloques.
//
// Rutas públicas: no exigen sesión (el router se registra fuera de `AUTH_LECTURA_PUBLICA`),
// así que esta pantalla funciona sin iniciar sesión, igual que en Streamlit.
//
// Devuelven { data, error } y nunca lanzan, como el resto de `lib/api.js`.

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

async function pedir(ruta) {
  try {
    const res = await fetch(`${BASE_URL}${ruta}`, {
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
    });
    if (!res.ok) return { data: null, error: `${res.status} ${res.statusText}` };
    return { data: await res.json(), error: null };
  } catch (err) {
    return { data: null, error: err.message ?? "network_error" };
  }
}

export const getSecciones = () => pedir("/api/v1/about/secciones");
export const getSeccion = (id) => pedir(`/api/v1/about/secciones/${id}`);

//: Los tipos que esta pantalla sabe pintar. Están los ocho del contrato: `mermaid` es el único
//: que no se dibuja, y a propósito — ninguna sección lo emite desde que los cuatro E-R pasaron a
//: `svg` (ver el encabezado de `BloqueAbout.jsx`). Si volviera a aparecer, cae en el bloque de
//: "tipo no soportado" y avisa en su propio espacio, sin tumbar la página.
export const TIPOS_RENDERIZADOS = new Set([
  "markdown",
  "tabla",
  "metricas",
  "svg",
  "barras",
  "mapa",
  "diagrama_flujo",
]);
