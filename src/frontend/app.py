"""FARO Web — app Streamlit integrada (andamiaje).

Router + sesión + guardas por rol. La lógica de cada página vive en pages/.
Historia: US-206 (shell). Ver vault/03_Architecture/Frontend_Architecture.md.
"""
from __future__ import annotations

import streamlit as st

from auth import encabezado


def main() -> None:
    st.set_page_config(page_title="FARO Web", page_icon="🛰️", layout="wide")
    st.sidebar.title("FARO · Escuela como Sensor Social")

    user = encabezado()
    if user is None:
        st.title("FARO Web")
        st.info("Inicia sesión para acceder a los dashboards, el panel de ML y el agente.")
        return

    st.title("FARO Web")
    st.write(
        "Usa el menú lateral: **Dashboards**, **Panel de ML** y **Chat del agente**. "
        "Las vistas de analista requieren el rol correspondiente."
    )
    st.subheader("Acceso rápido")
    cols = st.columns(3)
    with cols[0]:
        st.button("📊 Dashboards", use_container_width=True)
    with cols[1]:
        st.button("🤖 Panel de ML", use_container_width=True)
    with cols[2]:
        st.button("💬 Chat del agente", use_container_width=True)


if __name__ == "__main__":
    main()
