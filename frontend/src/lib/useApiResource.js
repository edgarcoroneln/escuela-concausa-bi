import { useEffect, useState } from "react";
import { isDemoMode } from "./demoMode.js";

// Hook mínimo para cargar un recurso del API real, con modo demo EXPLÍCITO
// (nunca un fallback silencioso a mock por error de red -- eso es justo lo
// que Edgar marcó en la revisión del PR #302, 10-sep). Uso:
//
//   const { status, data, error } = useApiResource(() => getKpis(), {
//     mock: kpisMock,
//   });
//   // status: "loading" | "ok" | "demo" | "error"
//
// Si isDemoMode() (VITE_USE_MOCK=true) devuelve el mock marcado como "demo"
// sin llamar al API. Si no, llama al API real; en error real deja status
// "error" (la pantalla debe mostrar un estado de error, NO mock silencioso).
export function useApiResource(fetchFn, { mock, deps = [] } = {}) {
  const [state, setState] = useState({ status: "loading", data: null, error: null });

  useEffect(() => {
    let cancelled = false;

    if (isDemoMode()) {
      setState({ status: "demo", data: mock, error: null });
      return () => {};
    }

    setState((s) => ({ ...s, status: "loading" }));
    fetchFn().then(({ data, error }) => {
      if (cancelled) return;
      if (error) setState({ status: "error", data: null, error });
      else setState({ status: "ok", data, error: null });
    });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
