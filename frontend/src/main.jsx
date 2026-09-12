import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import App from "./App.jsx";
import Home from "./pages/Home.jsx";
import LosSieteCasos from "./pages/LosSieteCasos.jsx";
import VistaGeneral from "./pages/VistaGeneral.jsx";
import Comparativa from "./pages/Comparativa.jsx";
import MapaCasos from "./pages/MapaCasos.jsx";
import MatrizDrivers from "./pages/MatrizDrivers.jsx";
import ExpedienteEscuela from "./pages/ExpedienteEscuela.jsx";
import ComparacionTerritorial from "./pages/ComparacionTerritorial.jsx";
import Hallazgos from "./pages/Hallazgos.jsx";

// Rutas = las 9 pantallas del storytelling de "los 7 casos" (mockup de
// UX/UI). Cada página es su propio archivo en src/pages/ para que el
// contenido se pueda ir llenando una por una sin tocar el layout ni el
// router. Ver vault/08_CICD_DevOps/Arquitectura_Frontend_React.md.
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      { path: "casos", element: <LosSieteCasos /> },
      { path: "escuela/:cct", element: <ExpedienteEscuela /> },
      { path: "vista-general", element: <VistaGeneral /> },
      { path: "comparativa", element: <Comparativa /> },
      { path: "mapa", element: <MapaCasos /> },
      { path: "drivers", element: <MatrizDrivers /> },
      { path: "comparacion-territorial", element: <ComparacionTerritorial /> },
      { path: "hallazgos", element: <Hallazgos /> },
    ],
  },
]);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
