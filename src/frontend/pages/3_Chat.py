"""Widget de chat del agente (andamiaje). Historia: US-305.

Entrada de lenguaje natural -> API del agente RAG (US-304/US-323) -> respuesta citada.
"""
import streamlit as st

st.title("Agente FARO")
st.caption("Pregunta en lenguaje natural sobre los datos del proyecto.")
# TODO(US-305): input de chat + llamada a la API del agente + historial en sesión.
st.chat_input("Escribe tu pregunta…", disabled=True)
st.info("Andamiaje: el chat conectado al agente se implementa en US-305.")
