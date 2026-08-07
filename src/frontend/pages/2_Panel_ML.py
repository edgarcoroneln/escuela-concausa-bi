"""Panel de ML interactivo (andamiaje). Historia: US-207.

Form de parámetros -> API de inferencia (US-412/US-415) -> salida de ML-01/02/03.
"""
import streamlit as st

st.title("Panel de ML")
st.caption("Ingresa parámetros y obtén la predicción de los 3 modelos.")
# TODO(US-207): formulario + POST a los endpoints de inferencia + render de resultados.
st.info("Andamiaje: la inferencia interactiva se implementa en US-207.")
