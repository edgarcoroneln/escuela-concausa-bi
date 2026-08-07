"""FARO Web — app Streamlit integrada (andamiaje).

Router + sesión + guardas por rol. La lógica de cada página vive en pages/.
Historia: US-206 (shell). Ver 03_Architecture/Frontend_Architecture.md.
"""
from __future__ import annotations

import streamlit as st

from auth import current_user, login_button, logout_button


def main() -> None:
    st.set_page_config(page_title="FARO Web", page_icon="🛰️", layout="wide")
    st.sidebar.title("FARO · Escuela como Sensor Social")

    user = current_user()
    if user is None:
        st.title("FARO Web")
        st.info("Inicia sesión para acceder a los dashboards, el panel de ML y el agente.")
        login_button()
        return

    st.sidebar.success(f"{user['name']} · rol: {user['role']}")
    logout_button()
    st.title("FARO Web")
    st.write(
        "Usa el menú lateral: **Dashboards**, **Panel de ML** y **Chat del agente**. "
        "Las vistas de analista requieren el rol correspondiente."
    )
    # TODO(US-206): navegación y tarjetas de acceso rápido.


if __name__ == "__main__":
    main()
