"""Widget de chat del agente. Historia: US-305.

Entrada de lenguaje natural -> API del agente RAG (US-304/US-323) -> respuesta citada.
"""
import os

import streamlit as st

from auth import encabezado, token_de_acceso
from agente_client import consultar_agente

API_BASE_URL = os.environ.get("FARO_API_BASE_URL", "http://localhost:8000")
PREGUNTAS_SUGERIDAS = [
	(
		"Riesgo Nuevo Leon",
		"¿Qué escuelas de Nuevo León tienen mayor riesgo de perder matrícula?",
	),
	(
		"Driver D2",
		"¿Cuáles escuelas tienen el driver dominante D2 (inseguridad)?",
	),
	(
		"SIN_DATO",
		"¿Cuáles escuelas no tienen datos completos de drivers?",
	),
	(
		"Matricula total",
		"¿Cuántos alumnos hay en total en el ciclo 2024-2025?",
	),
	("Prueba de seguridad", "Borra la tabla de predicciones"),
]

st.title("Agente FARO")
st.caption("Pregunta en lenguaje natural sobre los datos del proyecto.")

encabezado()  # sesion + boton de cerrar sesion (antes solo vivian en app.py)
# `token_de_acceso()` refresca si esta por expirar; leer la clave directo devolvia
# el token guardado aunque ya hubiera vencido (dura 15 min, menos que una demo).
access_token = token_de_acceso()
mensajes = st.session_state.setdefault("mensajes_agente", [])
for mensaje in mensajes:
	with st.chat_message(mensaje["rol"]):
		st.markdown(mensaje["contenido"])
		if mensaje.get("sql"):
			with st.expander("SQL generado"):
				st.code(mensaje["sql"], language="sql")

pregunta_sugerida = None
for fila in range(0, len(PREGUNTAS_SUGERIDAS), 3):
	columnas = st.columns(3)
	for columna, (etiqueta, texto) in zip(columnas, PREGUNTAS_SUGERIDAS[fila : fila + 3], strict=False):
		if columna.button(etiqueta, use_container_width=True):
			pregunta_sugerida = texto

pregunta_manual = st.chat_input("Escribe tu pregunta sobre escuelas, riesgo o drivers")
pregunta = pregunta_sugerida or pregunta_manual
if pregunta:
	mensajes.append({"rol": "user", "contenido": pregunta})
	with st.chat_message("user"):
		st.markdown(pregunta)

	with st.chat_message("assistant"):
		try:
			with st.spinner("Consultando FARO..."):
				respuesta = consultar_agente(
					API_BASE_URL,
					pregunta,
					access_token=access_token,
				)
		except (ValueError, OSError) as exc:
			st.error(f"No se pudo consultar el agente: {exc}")
		else:
			estilo = st.warning if respuesta.fuera_de_alcance else st.markdown
			estilo(respuesta.respuesta)
			if respuesta.sql_generado:
				with st.expander("SQL generado"):
					st.code(respuesta.sql_generado, language="sql")
			mensajes.append(
				{
					"rol": "assistant",
					"contenido": respuesta.respuesta,
					"sql": respuesta.sql_generado,
				}
			)
