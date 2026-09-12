import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Header from "./components/Header.jsx";
import AsistenteFaro from "./components/AsistenteFaro.jsx";
import { SessionProvider, useSession } from "./lib/session.jsx";

// Layout raiz (Fase 2 del rediseño, US-641): barra lateral fija +
// cabecera fija + <Outlet/>, con el Asistente FARO flotante montado una
// sola vez aqui para que su conversacion sobreviva la navegacion entre
// pantallas (01_UX_Architecture.md §6). Antes era un unico Topbar plano
// (Fase 1) -- ver Sidebar.jsx y Header.jsx para el porque del cambio.
//
// El Asistente FARO solo aparece con sesion iniciada (equivalente a "no en
// Login/P0" del spec: esta SPA no tiene una ruta de login propia, el acceso
// es un redirect externo a Google, asi que "anonimo" es nuestro P0).
//
// `onPreguntar` viaja a cada pagina via el contexto del Outlet (useOutletContext)
// para que el glosario de cualquier pantalla pueda precargar una pregunta en
// el Asistente sin que este dependa de vivir dentro de esa pagina.
function Layout() {
  const session = useSession();
  const [preguntaInicial, setPreguntaInicial] = useState(null);

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
