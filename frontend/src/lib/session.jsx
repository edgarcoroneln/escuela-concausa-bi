import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getAuthMe, postAuthExchange, postAuthLogout } from "./api.js";

// Bootstrap de sesion (US-405, ADR-012). Vive en el layout raiz (App.jsx)
// para correr sin importar en que ruta caiga la vuelta de Google -- el
// `redirect` que arma getAuthLoginUrl() (api.js) es window.location.origin,
// sin path, pero cubrir cualquier path de aterrizaje es mas robusto que
// asumir que siempre es "/".
//
// Flujo:
//   1. Si la URL trae ?code_faro=, canjearlo por la cookie httpOnly
//      (postAuthExchange, modo cookie -- la respuesta nunca trae JWT, ver
//      SesionOut en src/api/schemas.py) y limpiar el parametro de la URL
//      con history.replaceState, para no reintentar el canje en un
//      refresh ni dejar el codigo de un solo uso visible/copiable.
//   2. Preguntar quien es el usuario actual (getAuthMe). Un 401 aqui es el
//      estado normal de "no ha iniciado sesion", no un error que mostrar.
const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [state, setState] = useState({ status: "loading", user: null });

  const cargarUsuario = useCallback(async () => {
    const { data, error } = await getAuthMe();
    setState(error ? { status: "anonimo", user: null } : { status: "autenticado", user: data });
  }, []);

  useEffect(() => {
    let cancelado = false;
    (async () => {
      const params = new URLSearchParams(window.location.search);
      const codigo = params.get("code_faro");
      if (codigo) {
        // Best-effort: si el canje falla (codigo vencido/usado dos veces),
        // cargarUsuario() de abajo simplemente no encuentra sesion y el
        // resultado visible es "no autenticado" -- el mismo estado que si
        // nunca se hubiera intentado, no un error aparte que anunciar.
        await postAuthExchange(codigo);
        params.delete("code_faro");
        const resto = params.toString();
        const url = `${window.location.pathname}${resto ? `?${resto}` : ""}${window.location.hash}`;
        window.history.replaceState({}, "", url);
      }
      if (!cancelado) await cargarUsuario();
    })();
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const logout = useCallback(async () => {
    await postAuthLogout();
    setState({ status: "anonimo", user: null });
  }, []);

  return (
    <SessionContext.Provider value={{ ...state, logout }}>{children}</SessionContext.Provider>
  );
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession debe usarse dentro de <SessionProvider>");
  return ctx;
}
