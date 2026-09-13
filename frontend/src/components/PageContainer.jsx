// 13-sep -- se sube de max-w-6xl a max-w-7xl para que el ancho del
// contenedor coincida con el que ya se uso en Login.jsx y en la seccion
// "hero" de Home.jsx (mockups: max-w-7xl mx-auto en el <body>/<main> de
// las 7 plantillas Stitch). Antes este componente y el resto de la
// pagina usaban dos anchos distintos.
export default function PageContainer({ children }) {
  return <div className="max-w-7xl mx-auto px-8 py-8 flex flex-col gap-6">{children}</div>;
}
