import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import App from "./App.jsx";
import Home from "./pages/Home.jsx";
import Panorama from "./pages/Panorama.jsx";
import LosSieteCasos from "./pages/LosSieteCasos.jsx";
import Conclusion from "./pages/Conclusion.jsx";
import Explorador from "./pages/Explorador.jsx";
import ExpedienteEscuela from "./pages/ExpedienteEscuela.jsx";
import Login from "./pages/Login.jsx";

// Rutas = las 7 pantallas del rediseño Fase 2 (US-641) contra las 7
// plantillas de UX/UI de Equipo 3, más /explorador. Las 6 vistas
// "heredadas" de Fase 1 (vista-general, mapa, drivers, comparacion-
// territorial, comparativa, hallazgos) se retiraron el 12-sep (decisión
// de arquitectura de Marina García del Buey, ver vault/_DevLog/2026-09-12-
// diana-alvarez-retiro-heredadas-diferenciador.md): la arquitectura final
// son 7 pantallas, no 7 + una sección secundaria de vistas duplicadas.
// Cada página es su propio archivo en src/pages/. Ver
// vault/08_CICD_DevOps/Arquitectura_Frontend_React.md.
const router = createBrowserRouter([
  // Ruta de solo vista previa (12-sep, a pedido de Diana): Login.jsx ya se
  // muestra automáticamente sin sesión (ver App.jsx), pero eso queda oculto
  // en modo demo (VITE_USE_MOCK=true) a propósito, para no romper
  // "previsualizar sin logearme". Esta ruta la muestra directo, sin tocar
  // el .env ni pasar por SessionProvider/App -- es la MISMA pantalla, solo
  // un atajo para verla sin apagar el modo demo.
  { path: "/login", element: <Login /> },
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      { path: "panorama", element: <Panorama /> },
      { path: "casos", element: <LosSieteCasos /> },
      { path: "escuela/:cct", element: <ExpedienteEscuela /> },
      { path: "conclusion", element: <Conclusion /> },
      { path: "explorador", element: <Explorador /> },
    ],
  },
]);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
