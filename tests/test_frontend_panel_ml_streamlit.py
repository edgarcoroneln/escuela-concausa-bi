"""Pruebas de la página del panel de ML en FARO Web (US-207).

Ejercitan `src/frontend/pages/2_Panel_ML.py` con `AppTest`, sin navegador ni API levantada
—el cliente se sustituye por un doble—, igual que `test_frontend_dashboards_streamlit.py`.

Requiere el stack Streamlit (`importorskip`). Desde el 2026-09-04 `streamlit` está en
`requirements.txt`, así que **estas pruebas sí corren en CI**: antes se saltaban en silencio
y FARO Web quedaba sin cobertura efectiva.

Lo que defienden:

1. **El hueco de ML-03 se muestra como `SIN_DATO`, no como un cero ni un espacio en blanco.**
   Es el criterio del proyecto y la razón por la que la historia se entrega con 2 de 3
   modelos en vez de inventar el tercero.
2. La página distingue "no hay predicción para ese CCT" de "la API no responde".
3. El umbral que se comunica al usuario es el de DEC-006.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

streamlit = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
PAGINA = RAIZ / "src" / "frontend" / "pages" / "2_Panel_ML.py"
FRONTEND = RAIZ / "src" / "frontend"


@pytest.fixture(autouse=True)
def _ruta_frontend():
    """`2_Panel_ML.py` importa `auth` y `prediccion_client` como módulos planos.

    **Limpia el estado global de Streamlit al terminar.** `AppTest` comparte el caché de
    `st.cache_data`/`st.cache_resource` dentro del mismo proceso de pytest, así que una
    página que deja algo cacheado se lo hereda a la siguiente. `1_Dashboards.py` cachea su
    guest token con `@st.cache_data(ttl=60)`, y sin esta limpieza estas pruebas le
    cambiaban el resultado a `test_frontend_dashboards_streamlit.py` según el orden de
    ejecución. La fragilidad de esa suite es previa —se reproduce en el commit anterior a
    este—, pero no es correcto que un archivo nuevo la dispare: se limpia lo propio.
    """
    ruta = str(FRONTEND.resolve())
    if ruta not in sys.path:
        sys.path.insert(0, ruta)
    yield
    for limpiar in (
        getattr(streamlit, "cache_data", None),
        getattr(streamlit, "cache_resource", None),
    ):
        if limpiar is not None and hasattr(limpiar, "clear"):
            limpiar.clear()


def _app() -> AppTest:
    return AppTest.from_file(str(PAGINA)).run(timeout=30)


def test_la_pagina_carga_sin_excepcion(_ruta_frontend) -> None:
    app = _app()
    assert not app.exception, app.exception
    assert app.title[0].value == "Panel de ML"


def test_ofrece_el_formulario_de_cct(_ruta_frontend) -> None:
    """Sin formulario no hay 'panel interactivo': es el entregable de la historia."""
    app = _app()
    assert app.text_input, "no hay campo para el CCT"
    assert any("Consultar" in b.label for b in app.button), "no hay botón de consulta"


def test_un_cct_de_longitud_invalida_no_llama_a_la_api(_ruta_frontend) -> None:
    app = _app()
    app.text_input[0].set_value("123").run(timeout=30)
    app.button[0].click().run(timeout=30)
    assert not app.exception, app.exception
    assert app.error, "debió avisar que el CCT no tiene 10 caracteres"


def test_la_pagina_anuncia_el_umbral_de_dec_006(_ruta_frontend) -> None:
    """El usuario tiene que poder leer contra qué se compara el índice."""
    import prediccion_client

    assert prediccion_client.UMBRAL_RIESGO == 0.60


def test_ml03_sin_productor_se_documenta_en_la_pagina(_ruta_frontend) -> None:
    """El texto que explica el hueco de ML-03 vive en la página y debe seguir ahí.

    Si alguien borra ese aviso, la ausencia de ML-03 pasa de ser un hueco declarado a un
    silencio — que es justo lo que el proyecto prohíbe.
    """
    fuente = PAGINA.read_text(encoding="utf-8")
    assert "SIN_DATO" in fuente, "se perdió el aviso explícito de ML-03"
    assert "US-321" in fuente, "el hueco de ML-03 debe trazar a la historia que lo cierra"


def test_el_cliente_es_el_unico_que_habla_con_la_api(_ruta_frontend) -> None:
    """La página no arma URLs ni maneja httpx: eso vive en `prediccion_client`.

    Mantiene la página testeable y evita que el contrato se duplique en dos lugares.

    **Mira el CÓDIGO, no la prosa.** La primera versión de esta prueba buscaba la cadena
    en el archivo completo y reprobaba por el docstring que documenta qué endpoint se
    consume — misma clase de falla que el `sin_comentarios` de
    `test_drill_down_db03_db04.py`: una prueba que parece correcta y castiga la
    documentación en vez del defecto.
    """
    import ast

    arbol = ast.parse(PAGINA.read_text(encoding="utf-8"))

    importa_httpx = any(
        (isinstance(n, ast.Import) and any(a.name.split(".")[0] == "httpx" for a in n.names))
        or (isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "httpx")
        for n in ast.walk(arbol)
    )
    assert not importa_httpx, "la página no debe hablar HTTP directo; usa prediccion_client"

    # Los docstrings se identifican POR IDENTIDAD DE NODO, no comparando su texto:
    # `ast.get_docstring()` devuelve la versión limpiada (dedentada), que ya no coincide
    # con el literal crudo del árbol. Compararlos por valor dejaba todos los docstrings
    # fuera del conjunto y la prueba reprobaba por su propia documentación.
    ids_docstring = set()
    for nodo in ast.walk(arbol):
        cuerpo = getattr(nodo, "body", None)
        if not isinstance(nodo, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if (
            cuerpo
            and isinstance(cuerpo[0], ast.Expr)
            and isinstance(cuerpo[0].value, ast.Constant)
            and isinstance(cuerpo[0].value.value, str)
        ):
            ids_docstring.add(id(cuerpo[0].value))

    en_codigo = [
        n.value for n in ast.walk(arbol)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, str)
        and id(n) not in ids_docstring
    ]
    assert not any("/api/v1/predicciones" in s for s in en_codigo), (
        "la página construye la ruta a mano; debe pedírsela a prediccion_client"
    )
