// Cliente del API real de FARO (contrato: api/openapi.v1.json).
// Base URL configurable por env var de Vite: VITE_API_BASE_URL
//   - local:  NO se define -> "" (rutas relativas; server.proxy de Vite las
//             manda a localhost:8000, ver vite.config.js)
//   - prod:   se sirve en el MISMO origen vía proxy nginx (ADR-012, Luis) ->
//             VITE_API_BASE_URL vacío en .env.production
//
// Todas las funciones devuelven { data, error }. Nunca lanzan (throw) para que
// la página decida cómo mostrar el error.
//
// OJO -- corregido 10-sep (revisión de Edgar, PR #302): antes este comentario
// decía que las páginas podían caer a mock data en error para "no romper la
// demo". Eso es justo el patrón que se pidió eliminar: un error real de red
// NUNCA debe disfrazarse de dato de ejemplo en silencio. El único mock
// permitido es el modo demo explícito de ./demoMode.js (VITE_USE_MOCK=true).
// Ver useApiResource.js para el patrón de carga recomendado.

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

// Origen absoluto del API -- SOLO para el link de "Iniciar sesion" (US-405,
// ADR-012). El boton no puede pasar por el proxy /api/* de este frontend: la
// cookie anti-CSRF `faro_oauth_state` se tiene que fijar en el origen del API,
// no en el del frontend, o Google regresa a un origen que nunca la fijo y el
// callback responde 401. Variable separada de VITE_API_BASE_URL a proposito --
// esa se queda vacia (rutas relativas via proxy) y esta va con URL absoluta;
// compartir una sola variable para las dos rompe alguna de las dos.
//   - local:  VITE_API_ORIGIN=http://localhost:8000
//   - prod:   VITE_API_ORIGIN=https://<host real de faro-api> (coordinar con Christian/Luis --
//             ese mismo valor, sin / final, es el que Christian valida contra FRONTEND_REDIRECT_URIS)
const API_ORIGIN = import.meta.env.VITE_API_ORIGIN ?? "";

async function request(path, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
      credentials: "same-origin", // mismo origen vía proxy nginx (ADR-012); la cookie httpOnly viaja sola
      ...options,
    });
    if (!res.ok) {
      return { data: null, error: `${res.status} ${res.statusText}` };
    }
    return { data: await res.json(), error: null };
  } catch (err) {
    return { data: null, error: err.message ?? "network_error" };
  }
}

// --- Version / salud (públicos, sin login -- DEC-023/DEC-026, US-621) ---
// `cortes_atencion` ({ alta, media, ancla_calibracion }) es la fuente de verdad de los
// umbrales de nivel de atención. NUNCA se escriben 0.50/0.30 a mano en el frontend --
// eso es justo el patrón que causó BUG-058 (mismo error, con el diccionario de
// entidades). Ver nivelRiesgo() en data/mock.js y lib/cortesAtencion.js.
export const getVersion = () => request("/api/v1/version");

// --- KPIs y catálogos ---
export const getKpis = () => request("/api/v1/kpis");
export const getEscuelas = (params = {}) =>
  request(`/api/v1/escuelas?${new URLSearchParams(params)}`);
export const getEscuela = (cct) => request(`/api/v1/escuelas/${cct}`);

// "Los 7 casos" -- escuelas en riesgo. El endpoint NO admite un filtro
// indice_riesgo_min (revisión de Edgar en PR #302, 10-sep): el contrato
// disponible es ordenar. Se pide el catálogo ordenado desc por indice_riesgo
// y se valida/recorta contra el conteo real de KpisOut.escuelas_en_riesgo.
//
// Fix 11-sep (segunda revisión de Edgar, PR #302): la versión anterior
// desenvolvía el sobre de paginación pero devolvía data.items completo sin
// aplicar la línea de alerta ni el recorte que este mismo comentario ya
// prometía -- "Los 7 casos" podía mostrar escuelas fuera del umbral, más de
// siete registros, y tronaba en LosSieteCasos.jsx (`e.indice_riesgo.toFixed(2)`)
// si entraba un registro con indice_riesgo: null. Ahora:
//   1. descarta indice_riesgo no numérico (nunca truena .toFixed() en quien
//      consume esto);
//   2. aplica la línea de alerta real leída de GET /api/v1/version
//      (cortes_atencion.alta, DEC-023/DEC-026 -- ya NO un número fijo aquí,
//      ver hallazgo de Diana 12-sep: escribir 0.50/0.30 a mano en el
//      frontend es el mismo patrón que causó BUG-058);
//   3. recorta al conteo oficial de KpisOut.escuelas_en_riesgo -- ese número
//      es la fuente de verdad del backend, no "los que alcancen el umbral
//      en esta página".
//
// Coordenadas (US-621, 11-sep): EscuelaOut ya trae latitud/longitud en el
// listado -- ver comentario en schemas.py -- así que el mapa de las 7
// escuelas ya no necesita una llamada por escuela.
export const getEscuelasEnRiesgo = async (size = 50) => {
  // El endpoint de lista devuelve un sobre de paginación (Page[EscuelaOut]:
  // { items, total, page, size }), no un arreglo -- bug encontrado 11-sep en
  // pruebas de "Los 7 casos" (la página se quedaba en blanco sin error
  // porque escuelas.length de un objeto es undefined). Se desenvuelve aquí
  // para que el resto del código siga tratando el resultado como arreglo.
  const [escuelasRes, kpisRes, versionRes] = await Promise.all([
    request(
      `/api/v1/escuelas?${new URLSearchParams({ order_by: "indice_riesgo", order: "desc", size: String(size) })}`
    ),
    request("/api/v1/kpis"),
    getVersion(),
  ]);
  if (escuelasRes.error) return { data: null, error: escuelasRes.error };
  if (kpisRes.error) return { data: null, error: kpisRes.error };
  if (versionRes.error) return { data: null, error: versionRes.error };

  const lineaAlerta = versionRes.data.cortes_atencion?.alta;
  if (typeof lineaAlerta !== "number") {
    // /version todavia sin cortes_atencion (API vieja) -- no se inventa un
    // 0.50 aqui, se reporta el error tal cual para que la pantalla lo muestre.
    return { data: null, error: "cortes_atencion_no_disponible" };
  }

  const enRiesgo = escuelasRes.data.items.filter(
    (e) => typeof e.indice_riesgo === "number" && e.indice_riesgo >= lineaAlerta
  );
  return { data: enRiesgo.slice(0, kpisRes.data.escuelas_en_riesgo), error: null };
};

// Pantalla 2 (Panorama, US-641): la matriz de drivers necesita d1..d6 de
// cada escuela en riesgo, y esos campos SOLO vienen en EscuelaDetalleOut
// (GET /escuelas/{cct}, uno a la vez) -- el listado de arriba no los trae.
// Esto es exactamente el costo que 01_UX_Architecture.md §8 documenta como
// esperado para revelar el panorama ("2 del conjunto + 1 por escuela"), no
// un problema a resolver -- mismo gap que dejó pages/MatrizDrivers.jsx sin
// conectar (revisión de Edgar, PR #302), ahora aceptado explícitamente por
// el spec de UX/UI.
export const getPanoramaEscuelas = async () => {
  const base = await getEscuelasEnRiesgo();
  if (base.error) return { data: null, error: base.error };
  const detalles = await Promise.all(base.data.map((e) => getEscuela(e.cct)));
  const fallo = detalles.find((d) => d.error);
  if (fallo) return { data: null, error: fallo.error };
  return { data: base.data.map((e, i) => ({ ...e, ...detalles[i].data })), error: null };
};

export const getMunicipios = (params = {}) =>
  request(`/api/v1/municipios?${new URLSearchParams(params)}`);
export const getMunicipio = (cveMun) => request(`/api/v1/municipios/${cveMun}`);

// Nombre real de municipio/entidad para pantallas que hoy solo tienen cve_mun
// por escuela (MapaCasos.jsx, ComparacionTerritorial.jsx -- checklist §4,
// "Municipio y entidad por nombre real"). EscuelaOut nunca trajo el nombre,
// solo el código; GET /municipios/{cve_mun} sí lo expone desde el 11-sep
// (US-621, MunicipioOut en schemas.py) pero nadie lo había probado desde
// ninguna pantalla -- probado y confirmado real el 12-sep (BUG-077, 317/317
// municipios con nombre_entidad). Una llamada por municipio ÚNICO, no por
// escuela: las escuelas en riesgo suelen repetir municipio, así que
// deduplicar cve_mun antes de llamar evita llamadas redundantes.
export const getMunicipiosPorClaves = async (cveMuns) => {
  const unicas = [...new Set(cveMuns)];
  const resultados = await Promise.all(unicas.map((cve) => getMunicipio(cve)));
  const fallo = resultados.find((r) => r.error);
  if (fallo) return { data: null, error: fallo.error };
  const porClave = {};
  unicas.forEach((cve, i) => {
    porClave[cve] = resultados[i].data;
  });
  return { data: porClave, error: null };
};

// Pantalla "¿Es un caso aislado?" (ComparacionTerritorial): las escuelas en
// riesgo con el nombre real de su municipio/entidad, para comparar sin
// pintar códigos INEGI. Compone getEscuelasEnRiesgo + getMunicipiosPorClaves
// -- mismo estilo de composición que getPanoramaEscuelas, arriba.
export const getComparacionTerritorial = async () => {
  const base = await getEscuelasEnRiesgo();
  if (base.error) return { data: null, error: base.error };
  const municipios = await getMunicipiosPorClaves(base.data.map((e) => e.cve_mun));
  if (municipios.error) return { data: null, error: municipios.error };
  const escuelas = base.data.map((e) => ({
    ...e,
    nombre_municipio: municipios.data[e.cve_mun]?.nombre_municipio ?? null,
    nombre_entidad: municipios.data[e.cve_mun]?.nombre_entidad ?? null,
  }));
  return { data: escuelas, error: null };
};

// --- Predicciones / ML ---
export const getPrediccion = (cct) => request(`/api/v1/predicciones/${cct}`);
export const getPrediccionExplicacion = (cct) =>
  request(`/api/v1/predicciones/${cct}/explicacion`);
export const postPrediccionesBatch = (ccts) =>
  request("/api/v1/predicciones/batch", { method: "POST", body: JSON.stringify({ ccts }) });

// --- Agente (chat) ---
// `historial`: turnos previos del chat (pregunta del usuario + respuesta del agente),
// del mas antiguo al mas reciente, max. MAX_TURNOS_HISTORIAL turnos (10, ver
// src/api/schemas.py). Opcional y retrocompatible -- un arreglo vacio (default) se
// comporta igual que antes de este cambio. Contrato exacto y ejemplos:
// tests/test_agente_historial.py.
//
// OJO -- pendiente de acuerdo con backend (Andres/Karla, 11-sep): si una `respuesta`
// de un turno pasa de 500 caracteres, el contrato la rechaza con 422 al reenviarla.
// La decision es que trunque el API (en redactar_respuesta_con_llm, src/agente/llm.py),
// no este cliente -- no se agrega recorte aqui hasta que ese cambio este en main.
//
// Quien construya el estado del chat (turnos) debe pasar `historial` ya armado como
// lista de { pregunta, respuesta }; esta funcion solo lo reenvia tal cual.
export const postAgenteConsulta = (pregunta, historial = []) =>
  request("/api/v1/agente/consulta", {
    method: "POST",
    body: JSON.stringify({ pregunta, historial }),
  });

// --- Agente (chat), streaming SSE (US-305 Fase 3) ---
// Contrato: API_Specification.md §3.5 v1.3 (Christian, 11-sep). Ya mergeado
// a main (12-sep) -- src/api/v1/agente.py registra "/consulta/stream".
//
// EventSource no sirve aqui -- el endpoint es POST y EventSource solo hace
// GET (nota de Christian). Se lee el cuerpo con fetch() + ReadableStream,
// mismo patron de sesion por cookie que request() (credentials: "same-origin").
//
// Mismo cuerpo que postAgenteConsulta (pregunta, historial, + contexto
// opcional, ver bloque de arriba). Siempre llegan los 3 eventos, tambien si
// algo falla a medio camino -- el backend convierte el fallo en un
// `fragmento` con mensaje generico y manda `fin` igual, asi que el cliente
// nunca se queda esperando:
//   - "meta"      (una vez, al inicio): { sql_generado, fuera_de_alcance }
//   - "fragmento" (una o mas veces):    { texto } -- concatenados en orden forman la respuesta
//   - "fin"       (una vez, al final):  {}
//
// onEvento(tipo, data) se llama por cada evento segun llega, para que quien
// consuma esto pueda ir pintando la burbuja del chat en vivo y cerrarla al
// recibir "fin". El `texto` de cada fragmento se debe pintar como texto
// plano, nunca como HTML (nota de Christian) -- esa decision es de quien
// consuma esto, este cliente no sanea ni interpreta el texto.
export async function postAgenteConsultaStream(pregunta, { historial = [], contexto = null, onEvento, signal } = {}) {
  let res;
  try {
    res = await fetch(`${BASE_URL}/api/v1/agente/consulta/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ pregunta, historial, ...(contexto ? { contexto } : {}) }),
      signal,
    });
  } catch (err) {
    return { error: err.message ?? "network_error" };
  }

  if (!res.ok || !res.body) {
    return { error: `${res.status} ${res.statusText}` };
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  // Parser minimo de SSE: bloques separados por linea en blanco, cada uno con
  // "event: <tipo>" + "data: <json>". No hace falta una libreria -- el
  // contrato (API_Specification.md §3.5) es simple y fijo.
  const procesarBuffer = () => {
    const bloques = buffer.split("\n\n");
    buffer = bloques.pop() ?? ""; // el ultimo bloque puede venir incompleto todavia
    for (const bloque of bloques) {
      if (!bloque.trim()) continue;
      let tipo = "message";
      let dataRaw = "";
      for (const linea of bloque.split("\n")) {
        if (linea.startsWith("event:")) tipo = linea.slice(6).trim();
        else if (linea.startsWith("data:")) dataRaw += linea.slice(5).trim();
      }
      let data = {};
      try {
        data = dataRaw ? JSON.parse(dataRaw) : {};
      } catch {
        continue; // evento puntual malformado -- no debe tronar la UI
      }
      onEvento?.(tipo, data);
    }
  };

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      procesarBuffer();
    }
  } catch (err) {
    // Conexion cortada a medias: el contrato promete que "fin" siempre llega,
    // pero si la conexion se cae antes de que llegue, este cliente avisa
    // "fin" igual para que la UI no se quede esperando para siempre.
    onEvento?.("fin", {});
    return { error: err.message ?? "stream_error" };
  }

  return { error: null };
}

// --- Auth (US-402, US-405, C4, ADR-012) ---
export const getAuthMe = () => request("/api/v1/auth/me");

// Arranca el flujo de login (US-405). URL absoluta a proposito -- ver
// comentario de API_ORIGIN arriba: se lee en el momento del click, no al
// cargar el modulo, para que siempre use el origen real del tab (relevante
// si algun dia el front vive en mas de un origen valido).
export const getAuthLoginUrl = () =>
  `${API_ORIGIN}/api/v1/auth/login?redirect=${encodeURIComponent(window.location.origin)}`;

// Canje del codigo de un solo uso por la sesion, modo cookie (US-405,
// ADR-010, ADR-012). Ruta RELATIVA a proposito -- a diferencia del login de
// arriba, esta llamada SI va por el proxy same-origin de este frontend
// (via request(), que ya manda credentials: "same-origin"), porque la
// cookie httpOnly de sesion se tiene que fijar en el origen del frontend,
// no en el del API. Nunca toca JWT: la respuesta es SesionOut (solo
// expira_en), nunca TokenPair -- ver src/api/schemas.py.
export const postAuthExchange = (code) =>
  request("/api/v1/auth/exchange?sesion=cookie", {
    method: "POST",
    body: JSON.stringify({ code }),
  });

// Cierre de sesion: el frontend no guarda ni refresca tokens -- solo pide
// logout y la cookie httpOnly la borra el API.
export const postAuthLogout = () => request("/api/v1/auth/logout", { method: "POST" });

export const API_BASE_URL = BASE_URL;
