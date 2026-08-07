"""Autenticación del frontend delegando en la API (andamiaje).

El front NO reimplementa OAuth: redirige a /auth/login de la API (US-402), guarda el JWT en sesión
y expone require_role(). Historia: US-405. Ver 03_Architecture/API_Specification.md.
"""
from __future__ import annotations

from typing import Optional

import streamlit as st

ROLES = ("ciudadano", "analista")


def current_user() -> Optional[dict]:
    """Devuelve el usuario en sesión o None. TODO(US-405): validar el JWT contra la API."""
    return st.session_state.get("user")


def login_button() -> None:
    """TODO(US-405): iniciar el flujo OAuth2 (Google) contra /auth/login de la API."""
    st.button("Iniciar sesión con Google", disabled=True, help="Pendiente US-405")


def logout_button() -> None:
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.pop("user", None)
        st.rerun()


def require_role(role: str) -> bool:
    """Guarda por rol para vistas protegidas. TODO(US-405): aplicar en cada página de analista."""
    assert role in ROLES, f"Rol inválido: {role}"
    user = current_user()
    return bool(user and (user.get("role") == role or user.get("role") == "analista"))
