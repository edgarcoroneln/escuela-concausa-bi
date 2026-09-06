"""Panel de ML interactivo (US-207).

Formulario de parámetros -> `/api/v1/predicciones/{cct}` (US-412/US-415) -> salida de los
tres modelos en FARO Web.

**Alcance entregado y por qué.** ML-01 (índice de riesgo) y ML-02 (driver dominante y
recomendación prescriptiva) se muestran con datos reales. **ML-03 (clustering) se muestra
como `SIN_DATO` explícito**: US-321 (Estefany Hernández, Célula 3) no ha aterrizado, así
que `gold.predicciones` no tiene columna `cluster` y la API devuelve `None` — lo documenta
el propio contrato en `src/api/schemas.py::PrediccionOut`. Se pinta el hueco en vez de
esconderlo, que es la regla del proyecto: nunca un cero, nunca un vacío silencioso.

El valor de la historia no es el conteo de modelos: es que **dos escuelas con riesgo
parecido reciben recomendaciones distintas según su driver dominante**, y eso ya funciona.

Ver vault/03_Architecture/Frontend_Architecture.md · Contrato: API_Specification.md
"""

from __future__ import annotations

import os

import streamlit as st

from auth import current_user
from prediccion_client import (
    UMBRAL_RIESGO,
    EscuelaNoEncontrada,
    Prediccion,
    obtener_prediccion,
)

API_BASE_URL = os.environ.get("FARO_API_BASE_URL", "http://localhost:8000").rstrip("/")

#: Nombres legibles de `gold.dim_driver`. El id viaja en la respuesta; el nombre es
#: presentación, así que vive aquí y no se le pide a la API.
NOMBRE_DRIVER = {
    "D1": "Pobreza y rezago social",
    "D2": "Inseguridad del entorno",
    "D3": "Infraestructura escolar",
    "D4": "Conectividad digital",
    "D5": "Estrés hídrico",
    "D6": "Calidad del aire",
}

#: CCT de ejemplo para que el panel sea usable sin conocer una clave de memoria.
#: Se eligen dos con **driver dominante distinto**, que es justo lo que la historia
#: quiere demostrar.
EJEMPLOS = ("15DJN0049A", "09DSN0042A")


def _render_ml01(pred: Prediccion) -> None:
    """ML-01 — índice de riesgo contra el umbral de DEC-006."""
    st.subheader("ML-01 · Índice de riesgo")
    izq, der = st.columns([1, 2])
    with izq:
        st.metric(
            "Índice de riesgo",
            f"{pred.indice_riesgo:.4f}",
            delta="En riesgo" if pred.en_riesgo else "Bajo el umbral",
            delta_color="inverse" if pred.en_riesgo else "off",
        )
    with der:
        if pred.en_riesgo:
            st.error(
                f"Cruza el umbral de **{UMBRAL_RIESGO:.2f}** (DEC-006): el modelo proyecta "
                "una pérdida de **5 % o más** de su matrícula."
            )
        else:
            st.success(
                f"Por debajo del umbral de **{UMBRAL_RIESGO:.2f}** (DEC-006): el modelo "
                "**no** proyecta una pérdida de 5 % o más."
            )
        st.caption(
            "El umbral no es arbitrario: la sigmoide de `src/modelos/riesgo.py` está "
            "calibrada con dos anclas de negocio — matrícula estable → 0.30, y perder "
            "5 % → 0.60."
        )


def _render_ml02(pred: Prediccion) -> None:
    """ML-02 — driver dominante y la recomendación que se deriva de él."""
    st.subheader("ML-02 · Driver dominante y recomendación")
    nombre = NOMBRE_DRIVER.get(pred.driver_dominante, pred.driver_dominante)
    st.markdown(f"**Driver dominante:** `{pred.driver_dominante}` · {nombre}")
    st.info(f"**Recomendación prescriptiva:** {pred.recomendacion}")
    st.caption(
        "Esta es la pieza que hace prescriptivo al proyecto: dos escuelas con riesgo "
        "parecido reciben recomendaciones distintas según el driver que lo explica."
    )


def _render_ml03(pred: Prediccion) -> None:
    """ML-03 — clustering. Hoy no tiene productor: se muestra el hueco, no un cero."""
    st.subheader("ML-03 · Segmento (clustering)")
    if pred.tiene_cluster:
        st.metric("Cluster", pred.cluster)
        return
    st.warning(
        "**SIN_DATO** — ML-03 todavía no tiene productor. `gold.predicciones` no expone "
        "la columna `cluster` porque **US-321** (clustering, Célula 3) sigue en curso, y "
        "el contrato de la API lo devuelve como `null`."
    )
    st.caption(
        "Se muestra el hueco a propósito, en vez de un cero o un espacio en blanco: "
        "donde no se midió, el sistema lo dice."
    )


def render() -> None:
    st.title("Panel de ML")
    st.caption(
        "Consulta la inferencia de los tres modelos para una escuela concreta (US-207). "
        "Lee la misma API que alimenta los tableros y FARO Web."
    )

    user = current_user()
    if user is None:
        st.info("Puedes consultar predicciones sin iniciar sesión: la lectura es pública.")

    with st.form("form_prediccion"):
        cct = st.text_input(
            "CCT de la escuela",
            max_chars=10,
            placeholder="15DJN0049A",
            help="Clave del Centro de Trabajo: 10 caracteres.",
        ).strip().upper()
        enviado = st.form_submit_button("Consultar predicción", type="primary")

    st.caption("Ejemplos con driver dominante distinto: " + " · ".join(f"`{c}`" for c in EJEMPLOS))

    if not enviado:
        return

    if len(cct) != 10:
        st.error("El CCT debe tener exactamente 10 caracteres.")
        return

    try:
        with st.spinner(f"Consultando la predicción de {cct}…"):
            pred = obtener_prediccion(
                API_BASE_URL, cct, access_token=(user or {}).get("access_token")
            )
    except EscuelaNoEncontrada as exc:
        st.warning(str(exc))
        st.caption(
            "Que no haya predicción no es un error: solo se publican las escuelas cuyo "
            "ciclo tiene features completas para el modelo."
        )
        return
    except ValueError as exc:
        st.error(str(exc))
        return
    except ConnectionError as exc:
        st.error(str(exc))
        return

    st.success(f"Predicción de **{pred.cct}** · ciclo **{pred.id_ciclo}**")
    _render_ml01(pred)
    st.divider()
    _render_ml02(pred)
    st.divider()
    _render_ml03(pred)
    st.divider()
    st.caption(f"Corrida de MLflow: `{pred.mlflow_run_id}`")


render()
