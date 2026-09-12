import { Outlet } from "react-router-dom";
import Topbar from "./components/Topbar.jsx";
import { SessionProvider } from "./lib/session.jsx";

// Layout raíz: barra superior fija + <Outlet/>. Sin padding/max-width aquí
// a propósito -> cada página decide su propio contenedor, porque Home
// necesita un hero a todo lo ancho (como en el mockup de UX/UI) mientras
// el resto de las pantallas van en un contenedor centrado.
//
// SessionProvider (US-405, ADR-012) envuelve todo desde aquí -- corre el
// canje de ?code_faro= y la carga de sesión sin importar en qué ruta caiga
// la vuelta de Google, y Topbar es quien la consume para decidir entre
// "Iniciar sesión" y el avatar.
export default function App() {
  return (
    <SessionProvider>
      <div style={{ minHeight: "100svh", background: "var(--color-bg)" }}>
        <Topbar />
        <Outlet />
      </div>
    </SessionProvider>
  );
}
