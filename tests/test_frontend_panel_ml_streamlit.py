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


USUARIO = {"sub": "u-demo", "email": "demo@faro.mx", "name": "Demo", "role": "analista"}


def _app(*, con_sesion: bool = True) -> AppTest:
    """La página **con** sesión es el caso normal desde BUG-071.

    Antes estas pruebas corrían sin sesión y aun así llenaban el formulario, porque la
    página lo dejaba usable — que es justo el defecto que BUG-071 reporta. Se inyecta un
    usuario en `st.session_state`, que es de donde `auth.current_user()` lo lee.
    """
    app = AppTest.from_file(str(PAGINA))
    if con_sesion:
        app.session_state["user"] = dict(USUARIO)
    return app.run(timeout=30)


def _submit(app: AppTest):
    """El botón del formulario, **por etiqueta y no por índice**.

    Con sesión, `encabezado()` dibuja además "Cerrar sesión" en la barra lateral, así que
    `app.button[0]` dejó de ser el submit. Buscarlo por etiqueta es lo que hace que estas
    pruebas no dependan del orden de pintado.
    """
    return next(b for b in app.button if "Consultar" in b.label)


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
    _submit(app).click().run(timeout=30)
    assert not app.exception, app.exception
    assert app.error, "debió avisar que el CCT no tiene 10 caracteres"


def test_la_pagina_distingue_el_ancla_de_la_linea_de_alerta(_ruta_frontend) -> None:
    """El usuario tiene que poder leer contra qué se compara el índice — y son **dos**.

    Desde DEC-019 la calibración (0.60 ≡ perder 5 %) y la línea que enciende la alerta
    (0.50) son números distintos. Antes eran el mismo y la página los presentaba como uno
    solo, que es lo que hacía imposible bajar la alerta sin parecer que se recalibraba el
    modelo. Si vuelven a colapsarse en una sola constante, esta prueba lo dice.
    """
    import prediccion_client

    assert prediccion_client.ANCLA_SIGMOIDE == 0.60
    assert prediccion_client.LINEA_DE_ALERTA == 0.50

    fuente = PAGINA.read_text(encoding="utf-8")
    assert "DEC-019" in fuente, "la página no cita la decisión que fija la línea de alerta"
    assert "ANCLA_SIGMOIDE" in fuente and "LINEA_DE_ALERTA" in fuente, (
        "la página debe mostrar los dos números, no uno"
    )


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


# --------------------------------------------------------- P0 2026-09-06: ficha y búsqueda


def test_la_pagina_sigue_teniendo_un_solo_campo_y_un_solo_boton(_ruta_frontend) -> None:
    """Guarda de las guardas: protege a las dos pruebas que direccionan por índice.

    `test_un_cct_de_longitud_invalida_no_llama_a_la_api` hace `app.text_input[0]` y
    `app.button[0]`. Hoy funciona porque hay exactamente uno de cada, pero eso es un
    accidente afortunado, no un invariante declarado — y al añadir la búsqueda del P0 fue
    justo lo que hubo que cuidar. Sin esta prueba, el día que alguien meta un `st.button`
    de "Limpiar" arriba, aquella prueba **pasa a pulsar el botón equivocado** y falla por
    una razón que no tiene nada que ver con lo que dice medir.

    Por eso la búsqueda se construyó **solo con `st.selectbox`**: no entra en ninguna de
    las dos listas.
    """
    app = _app()
    assert len(app.text_input) == 1, (
        "hay más de un campo de texto: `app.text_input[0]` deja de ser el CCT"
    )
    submits = [b for b in app.button if "Consultar" in b.label]
    assert len(submits) == 1, (
        "hay más de un botón de consulta: `_submit()` deja de ser determinista"
    )
    assert len(app.title) == 1, "`app.title[0]` deja de ser el título de la página"


def test_ofrece_busqueda_por_filtros(_ruta_frontend) -> None:
    """El P0 pide llegar al CCT sin escribirlo: entidad -> municipio -> nivel -> plantel."""
    app = _app()
    assert app.selectbox, "no hay ningún selector de búsqueda"
    etiquetas = [s.label for s in app.selectbox]
    assert any("Entidad" in e for e in etiquetas), f"falta el selector de entidad: {etiquetas}"


def test_la_busqueda_no_llama_a_la_api_antes_de_elegir_entidad(_ruta_frontend) -> None:
    """Cargar la página no debe disparar la cascada.

    La API limita a 120 peticiones por minuto y por ruta; una cascada que consulta en cada
    rerun aunque no se haya elegido nada agota ese margen sola. El selector arranca en su
    centinela y `_buscador` sale antes de tocar la red.
    """
    app = _app()
    assert not app.exception, app.exception
    assert any("Elige una entidad" in c.value for c in app.caption), (
        "la página debería pedir elegir entidad antes de consultar nada"
    )


def test_la_ficha_se_renderiza_antes_del_indice(_ruta_frontend) -> None:
    """El P0 es que el panel diga **de qué escuela** habla antes de dar el número.

    Se comprueba sobre el orden del código, no sobre una corrida: renderizar la ficha exige
    una predicción real, y estas pruebas no levantan API.
    """
    fuente = PAGINA.read_text(encoding="utf-8")
    assert "_render_ficha" in fuente, "no existe la ficha del plantel"
    assert fuente.index("_render_ficha(ficha") < fuente.index("_render_ml01(pred)\n"), (
        "la ficha se pinta después del índice: el P0 pide lo contrario"
    )


def test_la_ficha_muestra_lo_que_pidio_el_p0(_ruta_frontend) -> None:
    """Nombre, nivel, municipio, sostenimiento, matrícula y completitud de drivers."""
    fuente = PAGINA.read_text(encoding="utf-8")
    for campo in ("ficha.nombre", "ficha.nivel", "nombre_municipio", "ficha.sostenimiento",
                  "ficha.matricula_total", "ficha.indice_completitud_drivers"):
        assert campo in fuente, f"la ficha no muestra {campo}"


# ------------------------------------------------ BUG-071: la página exige sesión


def test_sin_sesion_el_formulario_queda_inutilizable(_ruta_frontend) -> None:
    """El defecto de BUG-071 en esta página: avisaba, pero dejaba usar el formulario.

    No se esconde el formulario, se **apaga**: la página sigue explicando qué ofrece, pero
    no se puede disparar una consulta que la API va a rechazar. `AppTest` hace cumplir
    `disabled` igual que un navegador —rechaza `set_value` sobre un widget apagado—, así
    que esta prueba comprueba el comportamiento, no solo la bandera.
    """
    app = _app(con_sesion=False)
    assert not app.exception, app.exception

    assert app.text_input[0].disabled, "el campo de CCT sigue editable sin sesión"
    assert _submit(app).disabled, "el botón de consulta sigue pulsable sin sesión"
    assert app.selectbox[0].disabled, "la cascada sigue viva sin sesión"


def test_sin_sesion_se_dice_la_verdad_sobre_por_que(_ruta_frontend) -> None:
    """El aviso viejo decía "la lectura es pública" y desde DEC-018 **es falso**.

    Producción corre con `AUTH_LECTURA_PUBLICA=false`, así que sin sesión la API responde
    401 y el panel lo presentaba como *"La API rechazó la solicitud"*: un fallo de permiso
    disfrazado de fallo de servicio. Si alguien restaura la promesa vieja, esto lo dice.
    """
    app = _app(con_sesion=False)
    avisos = " ".join(i.value for i in app.info)
    assert "Inicia sesión" in avisos, f"no se pide iniciar sesión: {avisos!r}"
    assert "pública" not in avisos, (
        "la página vuelve a prometer lectura pública, que DEC-018 dejó sin efecto"
    )


def test_con_sesion_los_controles_vuelven(_ruta_frontend) -> None:
    """La guarda no puede romper el caso normal: con sesión, todo se usa."""
    app = _app()
    assert not app.text_input[0].disabled
    assert not _submit(app).disabled
    assert not app.selectbox[0].disabled
