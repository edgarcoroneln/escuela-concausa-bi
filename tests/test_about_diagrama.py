"""Geometría del diagrama de arquitectura (US-601, bloque `svg`).

**Por qué existe este archivo.** El diagrama se coloca a mano: sus coordenadas viven en
`_ARQ_COMPONENTES` y `_ARQ_FLECHAS`. Nada en Python impide escribir una etiqueta encima de una
caja, y el defecto no se ve en ninguna prueba de contrato -- el JSON sale perfectamente válido y
el SVG renderiza sin error; simplemente queda texto sobre texto. La primera versión de este
diagrama tenía **tres** etiquetas encimadas (`features_escuela` sobre la caja de scikit-learn,
`predicciones` sobre la de PostgreSQL y `contexto RAG` sobre la de ChromaDB) y las tres se
cazaron con exactamente esta comprobación, no mirando la imagen.

Lo que se afirma es una propiedad del trazo, no el trazo: mover una caja está permitido, dejarla
encima de una etiqueta no. Así el diagrama se puede seguir editando sin pedir permiso a una
prueba, pero no se puede romper en silencio.
"""
from __future__ import annotations

import re

import pytest

from src.api.v1.about import (
    _ARQ_ALTO,
    _ARQ_ANCHO,
    _ARQ_CELULAS,
    _ARQ_COMPONENTES,
    _ARQ_FLECHAS,
    _diagrama_arquitectura,
)

#: Ancho medio de un carácter a 10px en la familia sans-serif del diagrama. Es una estimación
#: deliberadamente generosa: sobreestimar el ancho del texto hace la prueba más estricta, que es
#: el lado por el que conviene equivocarse.
_ANCHO_CARACTER = 5.1

#: Caja vertical aproximada de una línea de texto de 10px respecto de su línea base.
_SOBRE_LINEA_BASE, _BAJO_LINEA_BASE = 8.0, 2.0


def _caja_etiqueta(flecha: dict) -> tuple[float, float, float, float]:
    """Rectángulo que ocupa la etiqueta de una flecha, según su ancla horizontal."""
    ancho = len(flecha["etq"]) * _ANCHO_CARACTER
    x, y = float(flecha["ex"]), float(flecha["ey"])
    anclaje = flecha.get("anc")
    if anclaje == "middle":
        x0, x1 = x - ancho / 2, x + ancho / 2
    elif anclaje == "end":
        x0, x1 = x - ancho, x
    else:
        x0, x1 = x, x + ancho
    return x0, y - _SOBRE_LINEA_BASE, x1, y + _BAJO_LINEA_BASE


def _caja_componente(comp: dict) -> tuple[float, float, float, float]:
    return (
        float(comp["x"]),
        float(comp["y"]),
        float(comp["x"]) + float(comp["w"]),
        float(comp["y"]) + float(comp["h"]),
    )


def _se_encima(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return ax0 < bx1 and ax1 > bx0 and ay0 < by1 and ay1 > by0


@pytest.mark.parametrize("flecha", _ARQ_FLECHAS, ids=lambda f: f["etq"][:28])
def test_ninguna_etiqueta_de_flecha_cae_sobre_una_caja(flecha: dict) -> None:
    """El defecto que este archivo existe para cazar."""
    caja_texto = _caja_etiqueta(flecha)
    encimadas = [
        comp["titulo"]
        for comp in _ARQ_COMPONENTES
        if _se_encima(caja_texto, _caja_componente(comp))
    ]
    assert not encimadas, (
        f"la etiqueta '{flecha['etq']}' se encima con {encimadas}; "
        "muévela o recorre la caja en _ARQ_COMPONENTES"
    )


def test_ninguna_caja_se_encima_con_otra() -> None:
    """Dos componentes solapados esconderían uno de los dos por completo."""
    solapes = [
        (a["titulo"], b["titulo"])
        for i, a in enumerate(_ARQ_COMPONENTES)
        for b in _ARQ_COMPONENTES[i + 1:]
        if _se_encima(_caja_componente(a), _caja_componente(b))
    ]
    assert not solapes, f"cajas encimadas: {solapes}"


def test_todo_queda_dentro_del_viewbox() -> None:
    """Lo que se sale del `viewBox` no se dibuja: se recorta sin aviso."""
    fuera = [
        comp["titulo"]
        for comp in _ARQ_COMPONENTES
        if comp["x"] < 0
        or comp["y"] < 0
        or comp["x"] + comp["w"] > _ARQ_ANCHO
        or comp["y"] + comp["h"] > _ARQ_ALTO
    ]
    assert not fuera, f"componentes fuera del viewBox: {fuera}"


def test_cada_componente_declara_una_celula_conocida() -> None:
    """`celula=None` es válido (las fuentes públicas no son código nuestro); una clave
    inventada no lo es -- reventaría al pintar la leyenda."""
    invalidas = [
        (c["titulo"], c["celula"])
        for c in _ARQ_COMPONENTES
        if c["celula"] is not None and c["celula"] not in _ARQ_CELULAS
    ]
    assert not invalidas, f"células desconocidas: {invalidas}"


def test_el_svg_generado_esta_balanceado() -> None:
    """Marcado bien formado y sin etiquetas colgantes."""
    codigo = _diagrama_arquitectura().codigo
    assert codigo.startswith("<svg ") and codigo.endswith("</svg>")
    # Cada etiqueta abierta con <text ...> se cierra.
    assert codigo.count("<text ") == codigo.count("</text>")
    # El marcador que usan las flechas está definido en el mismo fragmento.
    referenciados = set(re.findall(r"url\(#([\w-]+)\)", codigo))
    definidos = set(re.findall(r'<marker id="([\w-]+)"', codigo))
    assert referenciados <= definidos, f"marcadores sin definir: {referenciados - definidos}"


def test_el_svg_no_trae_estilos_ni_scripts_propios() -> None:
    """El bloque vive en un iframe con `_ESTILO_CLARO`; un `<style>` o `<script>` propio
    duplicaría la fuente de la verdad del color y abriría una superficie que no necesita."""
    codigo = _diagrama_arquitectura().codigo
    assert "<style" not in codigo
    assert "<script" not in codigo
    assert "<foreignObject" not in codigo
