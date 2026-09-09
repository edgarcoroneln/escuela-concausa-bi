"""Dashboards embebidos de Superset (US-206).

Embebido por **guest token** con el Embedded SDK de Superset (``@superset-ui/embedded-sdk``):
el servidor pide un guest token acotado a los ``embedded_uuid`` de los tableros y el navegador
los monta contra ``/embedded/{uuid}``. Sin token válido NO se muestra ningún tablero (AC-002.1).
Los filtros ciclo/entidad/nivel se aplican en la **barra de filtros nativa** de cada dashboard
(AC-002.2), visible dentro del embebido.

Ver vault/03_Architecture/Frontend_Architecture.md §4.
"""
from __future__ import annotations

import httpx
import streamlit as st
import streamlit.components.v1 as components

from auth import encabezado
from superset_client import (
    SupersetDeshabilitado,
    SupersetError,
    tableros_embebidos,
)

ALTO_TABLERO = 720  # px por dashboard embebido


@st.cache_data(ttl=60)
def _panel(rol: str):
    """Cachea el panel (guest token + uuids) por rol 60 s para no saturar Superset."""
    return tableros_embebidos(rol=rol)


def _embed_html(domain: str, uuid: str, token: str, alto: int) -> str:
    """HTML que monta un dashboard con el Embedded SDK (token por postMessage, no en la URL)."""
    return f"""
    <div id="dash-{uuid}" style="width:100%;height:{alto}px"></div>
    <script src="https://unpkg.com/@superset-ui/embedded-sdk"></script>
    <script>
      (function() {{
        var mount = document.getElementById("dash-{uuid}");
        if (!window.supersetEmbeddedSdk) {{
          mount.innerHTML = "<p style='color:#a00;font-family:sans-serif'>"
            + "No se pudo cargar el SDK de Superset (¿sin conexión al CDN?).</p>";
          return;
        }}
        window.supersetEmbeddedSdk.embedDashboard({{
          id: "{uuid}",
          supersetDomain: "{domain}",
          mountPoint: mount,
          fetchGuestToken: function() {{ return "{token}"; }},
          dashboardUiConfig: {{ hideTitle: true, filters: {{ visible: true, expanded: false }} }}
        }}).then(function() {{
          // El iframe que crea el SDK viene sin tamaño: forzarlo a llenar el contenedor.
          var f = mount.querySelector("iframe");
          if (f) {{ f.style.width = "100%"; f.style.height = "{alto}px"; f.style.border = "0"; }}
        }}).catch(function(e) {{
          mount.innerHTML = "<p style='color:#a00;font-family:sans-serif'>"
            + "No se pudo montar el tablero: " + e + "</p>";
        }});
      }})();
    </script>
    """


def render() -> None:
    st.title("Dashboards")
    st.caption(
        "Los tableros de Superset, embebidos por guest token + RLS (US-206). "
        "Filtra dentro de cada tablero con su barra de filtros (AC-002.2)."
    )

    user = encabezado()  # sesión + botón de cerrar sesión, unificado como en las otras páginas
    # BUG-071. `encabezado()` NO decide quién entra -- lo dice su docstring -- solo pinta el
    # estado, y esta página lo llamaba y seguía de largo con `rol = "ciudadano"` por defecto.
    # El agravante es que `superset_client` autentica con credenciales admin propias: sin
    # sesión la página montaba los diez embebidos igual, y quedaban en blanco **en silencio**,
    # como si los tableros estuvieran rotos. Se para antes de pedir el guest token.
    if user is None:
        st.info(
            "Inicia sesión para ver los tableros: se embeben con un guest token acotado a "
            "tu rol (US-206), así que sin sesión no hay nada que mostrar."
        )
        return
    rol = user.get("role", "ciudadano")

    try:
        panel = _panel(rol)
    except SupersetDeshabilitado as exc:
        _panel.clear()
        st.warning(
            "El embebido de Superset no está disponible todavía: "
            "falta habilitar el guest token del lado de despliegue (C5). "
            "Ningún tablero se muestra por diseño (AC-002.1)."
        )
        st.caption(str(exc))
        return
    except SupersetError as exc:
        _panel.clear()
        st.error(f"No se pudo obtener el guest token de Superset: {exc}")
        return
    except httpx.HTTPError as exc:
        _panel.clear()
        st.error(f"Superset no respondió correctamente: {exc}")
        return

    if not panel.tableros:
        st.info("No hay dashboards disponibles para tu rol.")
        return

    for tablero in panel.tableros:
        st.subheader(tablero.titulo)
        components.html(
            _embed_html(panel.superset_domain, tablero.uuid, panel.guest_token, ALTO_TABLERO),
            height=ALTO_TABLERO + 20,
        )


render()
