import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Header from "./components/Header.jsx";
import AsistenteFaro from "./components/AsistenteFaro.jsx";
import Login from "./pages/Login.jsx";
import { SessionProvider, useSession } from "./lib/session.jsx";
import { isDemoMode } from "./lib/demoMode.js";

// Layout raiz (Fase 2 del rediseño, US-641): barra lateral fija +
// cabecera fija + <Outlet/>, con el Asistente FARO flotante montado una
// sola vez aqui para que su conversacion sobreviva la navegacion entre
// pantallas (01_UX_Architecture.md §6). Antes era un unico Topbar plano
// (Fase 1) -- ver Sidebar.jsx y Header.jsx para el porque del cambio.
//
// CORRECCIÓN 12-sep (auditoría mockups vs código, US-621 "Mockup 0 --
// Login"): hasta esta entrega, este layout montaba el shell completo sin
// importar la sesión -- "anonimo" no tenía pantalla propia, cada página
// fallaba por su cuenta con "sin sesión iniciada" (el error que Diana venía
// viendo en Panorama). Ahora, sin sesión, se muestra Login.jsx a pantalla
// completa -- sin Sidebar/Header/Asistente -- igual que el Mockup 0. En
// "loading" no se muestra ninguno de los dos para no parpadear entre Login
// y el shell mientras se resuelve GET /auth/me.
//
// `onPreguntar` viaja a cada pagina via el contexto del Outlet (useOutletContext)
// para que el glosario de cualquier pantalla pueda precargar una pregunta en
// el Asistente sin que este dependa de vivir dentro de esa pagina.
//: Rutas que se ven sin sesión, con el mismo chrome que el resto.
//:
//: **Por qué existe esta lista.** `about` (US-601) está declarado **público siempre** del lado
//: del API, y a propósito: `src/api/v1/__init__.py` lo justifica en que es metadata del sistema
//: —arquitectura, modelo de datos, stack—, no dato de escuela, así que no debe ocultarse cuando
//: C4 endurezca la lectura de Gold. Sin esta lista, la compuerta de abajo contradecía esa
//: decisión: el API servía la sección a cualquiera y la interfaz pedía login para verla.
//:
//: Se mantiene como lista explícita, no como un flag por pantalla: que una ruta sea pública es
//: una decisión de producto y conviene que se lea de un vistazo, en un solo lugar.
const RUTAS_PUBLICAS = ["/como-funciona"];

function Layout() {
  const session = useSession();
  const { pathname } = useLocation();
  const [preguntaInicial, setPreguntaInicial] = useState(null);

  // El modo demo (VITE_USE_MOCK=true, "Solo quiero previsualizar sin
  // logearme", Diana 12-sep) se mantiene por fuera de esta compuerta a
  // propósito: session.jsx sigue llamando a GET /auth/me sin importar el
  // modo, así que sin backend real ese request falla y el status queda en
  // "anonimo" -- sin este `if`, el modo demo mostraría Login.jsx en vez de
  // la app con datos de ejemplo, rompiendo la función que ya se construyó.
  if (!isDemoMode()) {
    if (session.status === "loading") {
      return <div style={{ minHeight: "100svh", background: "#0b1524" }} aria-hidden="true" />;
    }

    if (session.status === "anonimo" && !RUTAS_PUBLICAS.includes(pathname)) {
      return <Login />;
    }
  }

  return (
    <div style={{ minHeight: "100svh", background: "var(--color-bg)" }}>
      <Sidebar session={session} />
      <Header session={session} />
      <main style={{ paddingLeft: "var(--faro-sidebar-width)", paddingTop: "4rem" }}>
        <Outlet context={{ onPreguntar: setPreguntaInicial }} />
      </main>
      <AsistenteFaro
        visible={session.status === "autenticado"}
        preguntaInicial={preguntaInicial}
        onPreguntaInicialConsumida={() => setPreguntaInicial(null)}
      />
    </div>
  );
}

export default function App() {
  return (
    <SessionProvider>
      <Layout />
    </SessionProvider>
  );
}
