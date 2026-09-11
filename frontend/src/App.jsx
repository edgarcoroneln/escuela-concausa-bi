import { Outlet } from "react-router-dom";
import Topbar from "./components/Topbar.jsx";

// Layout raíz: barra superior fija + <Outlet/>. Sin padding/max-width aquí
// a propósito -> cada página decide su propio contenedor, porque Home
// necesita un hero a todo lo ancho (como en el mockup de UX/UI) mientras
// el resto de las pantallas van en un contenedor centrado.
export default function App() {
  return (
    <div style={{ minHeight: "100svh", background: "var(--color-bg)" }}>
      <Topbar />
      <Outlet />
    </div>
  );
}
