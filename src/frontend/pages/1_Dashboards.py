"""Dashboards embebidos de Superset (andamiaje). Historia: US-206.

Embebido por guest token con row-level security por rol. Ver Frontend_Architecture.md §4.
"""
import streamlit as st

st.title("Dashboards")
st.caption("Los 10 tableros de Superset, embebidos por guest token + RLS.")
# TODO(US-206): pedir guest token a Superset según el rol y renderizar cada dashboard por iframe.
st.info("Andamiaje: el embebido con guest token se implementa en US-206.")
