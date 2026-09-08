"""Dashboards embebidos de Superset (US-206).

Embebido por guest token con row-level security por rol. Sin token válido NO se muestra
ningún tablero (AC-002.1). Los filtros ciclo/entidad/nivel aplican al conjunto (AC-002.2)
y se reflejan en la URL del guest token vía parámetros de Superset.

Ver vault/03_Architecture/Frontend_Architecture.md §4.
"""
from __future__ import annotations

import httpx
import streamlit as st

from auth import encabezado
from superset_client import (
    SupersetDeshabilitado,
    SupersetError,
    tableros_embebidos,
    url_con_filtros,
)

CICLOS = ("2021-2022", "2022-2023", "2023-2024", "2024-2025")
NIVELES = ("Preescolar", "Primaria", "Secundaria", "Media Superior")


@st.cache_data(ttl=60)
def _tableros(rol: str) -> list:
    """Cachea el guest token por rol durante 60 s para no saturar Superset."""
    return tableros_embebidos(rol=rol)


def render() -> None:
    st.title("Dashboards")
    st.caption("Los 10 tableros de Superset, embebidos por guest token + RLS (US-206).")

    user = encabezado()  # sesión + botón de cerrar sesión (antes solo vivían en app.py)
    rol = (user or {}).get("role", "ciudadano")

    try:
        tableros = _tableros(rol)
    except SupersetDeshabilitado as exc:
        st.cache_data.clear()
        _tableros.clear()
        st.warning(
            "El embebido de Superset no está disponible todavía: "
            "falta habilitar el guest token del lado de despliegue (C5). "
            "Ningún tablero se muestra por diseño (AC-002.1)."
        )
        st.caption(str(exc))
        return
    except SupersetError as exc:
        st.cache_data.clear()
        _tableros.clear()
        st.error(f"No se pudo obtener el guest token de Superset: {exc}")
        return
    except httpx.HTTPError as exc:
        st.cache_data.clear()
        _tableros.clear()
        st.error(f"Superset no respondió correctamente: {exc}")
        return

    if not tableros:
        st.info("No hay dashboards disponibles para tu rol.")
        return

    st.sidebar.subheader("Filtros globales (AC-002.2)")
    ciclo = st.sidebar.selectbox("Ciclo escolar", CICLOS, index=len(CICLOS) - 1)
    entidad = st.sidebar.text_input("Entidad (opcional)", placeholder="e.g. 09 (CDMX)")
    nivel = st.sidebar.selectbox("Nivel", ["Todos"] + list(NIVELES), index=0)
    nivel = "" if nivel == "Todos" else nivel

    for tablero in tableros:
        st.subheader(tablero.titulo)
        url = url_con_filtros(tablero.iframe_url, ciclo, entidad, nivel)
        st.html(
            f"""
            <iframe
                src="{url}"
                width="100%"
                height="800"
                style="border:1px solid #ddd; border-radius:8px;"
                allow="fullscreen"
            ></iframe>
            """
        )


render()
