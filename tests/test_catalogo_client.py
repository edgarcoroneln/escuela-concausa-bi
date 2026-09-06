"""Pruebas del cliente de catálogo del panel de ML (P0 del 2026-09-06).

Ejercitan `src/frontend/catalogo_client.py` completo **sin red y sin API levantada**,
inyectando el verbo HTTP por el seam `get` — mismo patrón que `test_prediccion_client.py`.

Lo que estas pruebas defienden, en orden de importancia:

1. **El listado se pide siempre ordenado.** Sin `order_by` el orden de la API no es
   determinista, y una búsqueda que reordena entre reruns es peor que no tener búsqueda:
   el plantel que el evaluador ve en pantalla deja de ser el que estaba ahí hace un
   segundo. Es la guarda más importante del archivo.
2. **`SIN_DATO` se propaga como hueco, nunca como cero** — ni el `indice_riesgo` ausente
   ni un driver sin observar se convierten en 0.
3. Los cuatro modos de fallo se distinguen (404, 401 sin sesión, 429 por rate limit,
   contrato roto), porque la página los presenta distinto.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import httpx
import pytest

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def cliente():
    """Importa src/frontend/catalogo_client.py como módulo (sin red en import)."""
    ruta = RAIZ / "src" / "frontend" / "catalogo_client.py"
    spec = importlib.util.spec_from_file_location("catalogo_client_p0", ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("catalogo_client_p0", modulo)
    spec.loader.exec_module(modulo)
    return modulo


class _RespuestaFalsa:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error", request=httpx.Request("GET", "http://x"), response=self
            )


ESCUELA = {
    "cct": "15DJN0049A",
    "nombre": "Jardín de Niños Sor Juana",
    "nivel": "PREESCOLAR",
    "cve_mun": "15106",
    "matricula_total": 114,
    "indice_riesgo": 0.7423,
    "driver_dominante": "D1",
    "tiene_prediccion": True,
}
SIN_PREDICCION = {**ESCUELA, "cct": "15DJN0050B", "indice_riesgo": None,
                  "driver_dominante": None, "tiene_prediccion": False}
FICHA = {
    **ESCUELA,
    "sostenimiento": "PÚBLICO",
    "indice_completitud_drivers": 0.6666666666666666,
    "d1": 0.70, "d2": 0.54, "d3": 0.33, "d4": 0.50, "d5": None, "d6": None,
    "latitud": 20.2, "longitud": -99.6,
}


def _get_que_devuelve(payload, status=200, registro=None):
    def _get(url, params=None, headers=None, timeout=None):
        if registro is not None:
            registro.append({"url": url, "params": params, "headers": headers})
        return _RespuestaFalsa(payload, status)
    return _get


# ------------------------------------------------- el orden, la guarda principal


def test_el_listado_se_pide_siempre_ordenado_por_riesgo(cliente) -> None:
    """La guarda más importante del archivo.

    La API declara `order_by` opcional y, sin él, `_aplicar_orden` no se llama: el orden es
    el natural de la consulta, que Postgres no garantiza estable entre ejecuciones. Una
    búsqueda que reordena sola es peor que ninguna — en la demo, el plantel que el
    evaluador está viendo se movería de sitio en el siguiente rerun.
    """
    registro = []
    cliente.listar_escuelas(
        "http://api", cve_ent="15", get=_get_que_devuelve({"items": [], "total": 0}, registro=registro)
    )
    params = registro[0]["params"]
    assert params["order_by"] == "indice_riesgo", "sin order_by el orden no es determinista"
    assert params["order"] == "desc", "el ranking prescriptivo va de mayor a menor riesgo"


def test_los_filtros_vacios_no_se_mandan(cliente) -> None:
    """Mandar `cve_mun=None` no es lo mismo que no mandarlo: la API lo valida a 5 chars."""
    registro = []
    cliente.listar_escuelas(
        "http://api", cve_ent="15", cve_mun=None, nivel=None,
        get=_get_que_devuelve({"items": [], "total": 0}, registro=registro),
    )
    params = registro[0]["params"]
    assert "cve_mun" not in params and "nivel" not in params
    assert params["cve_ent"] == "15"


def test_pedir_mas_del_tope_falla_antes_de_la_red(cliente) -> None:
    """La API responde 422 si `size > 100`. Se atrapa antes para no gastar la llamada."""
    def _get(*a, **k):
        raise AssertionError("no debió llamarse a la API")

    with pytest.raises(ValueError, match="100"):
        cliente.listar_escuelas("http://api", tamano=500, get=_get)


# ------------------------------------------------- SIN_DATO nunca es cero


def test_el_riesgo_ausente_se_propaga_como_hueco(cliente) -> None:
    """`indice_riesgo: null` significa "no puntuada", no "riesgo cero"."""
    payload = {"items": [SIN_PREDICCION], "total": 1}
    escuelas, _ = cliente.listar_escuelas("http://api", get=_get_que_devuelve(payload))
    assert escuelas[0].indice_riesgo is None, "un riesgo nulo se convirtió en un número"
    assert escuelas[0].driver_dominante is None
    assert escuelas[0].tiene_prediccion is False


def test_los_drivers_sin_observar_quedan_en_none(cliente) -> None:
    """D5 y D6 vienen `null` cuando la fuente no cubre esa escuela: es `SIN_DATO`."""
    ficha = cliente.obtener_ficha("http://api", "15DJN0049A", get=_get_que_devuelve(FICHA))
    assert ficha.drivers["d5"] is None and ficha.drivers["d6"] is None
    assert ficha.drivers_observados == 4, "solo cuentan los drivers con dato"


def test_la_entidad_se_deriva_de_la_clave_del_municipio(cliente) -> None:
    """Ni `EscuelaOut` ni `EscuelaDetalleOut` traen `cve_ent`; se deriva de `cve_mun[:2]`."""
    escuelas, _ = cliente.listar_escuelas(
        "http://api", get=_get_que_devuelve({"items": [ESCUELA], "total": 1})
    )
    assert escuelas[0].cve_ent == "15"
    ficha = cliente.obtener_ficha("http://api", "15DJN0049A", get=_get_que_devuelve(FICHA))
    assert ficha.cve_ent == "15"
    assert ficha.nombre_entidad == "Estado de México"


# ------------------------------------------------- los cuatro modos de fallo


def test_cct_inexistente_es_recurso_no_encontrado(cliente) -> None:
    with pytest.raises(cliente.RecursoNoEncontrado):
        cliente.obtener_ficha("http://api", "00XXX00000", get=_get_que_devuelve({}, status=404))


def test_sin_sesion_el_mensaje_dice_que_hay_que_iniciar_sesion(cliente) -> None:
    """Desde SEC-006 la lectura exige sesión en producción: un 401 no es "API caída"."""
    with pytest.raises(ConnectionError, match="sesión"):
        cliente.listar_escuelas("http://api", get=_get_que_devuelve({}, status=401))


def test_el_rate_limit_se_distingue_de_una_caida(cliente) -> None:
    """La cascada dispara una llamada por cambio de selector y el tope es 120/min."""
    with pytest.raises(ConnectionError, match="Demasiadas"):
        cliente.listar_escuelas("http://api", get=_get_que_devuelve({}, status=429))


def test_api_caida_es_error_de_conexion(cliente) -> None:
    def _get(*a, **k):
        raise httpx.ConnectError("sin ruta")

    with pytest.raises(ConnectionError):
        cliente.listar_escuelas("http://api", get=_get)


def test_respuesta_fuera_de_contrato_se_rechaza(cliente) -> None:
    """Falta `tiene_prediccion`: mejor fallar que inventar que sí tiene predicción."""
    incompleto = {k: v for k, v in ESCUELA.items() if k != "tiene_prediccion"}
    with pytest.raises(ValueError):
        cliente.listar_escuelas(
            "http://api", get=_get_que_devuelve({"items": [incompleto], "total": 1})
        )


# ------------------------------------------------- entrada y catálogos


@pytest.mark.parametrize("cct", ["", "123", "15DJN0049A1"])
def test_un_cct_de_longitud_invalida_no_llega_a_la_api(cliente, cct: str) -> None:
    def _get(*a, **k):
        raise AssertionError("no debió llamarse a la API")

    with pytest.raises(ValueError):
        cliente.obtener_ficha("http://api", cct, get=_get)


def test_los_municipios_se_piden_por_entidad_y_ordenados(cliente) -> None:
    """317 municipios y `size` topa en 100: pedirlos completos costaría 4 páginas."""
    registro = []
    payload = {"items": [{"cve_mun": "15106", "nombre_municipio": "Tepotzotlán"}], "total": 1}
    mapa = cliente.listar_municipios(
        "http://api", "15", get=_get_que_devuelve(payload, registro=registro)
    )
    assert mapa == {"15106": "Tepotzotlán"}
    assert registro[0]["params"]["cve_ent"] == "15"
    assert registro[0]["params"]["size"] <= cliente.TAMANO_MAXIMO


def test_los_municipios_se_paginan_hasta_completar_la_entidad(cliente) -> None:
    """Jalisco y Edomex tienen **125 municipios** y `size` topa en 100.

    Pedir una sola página deja fuera ~25 por entidad, y como la API ordena por nombre son
    siempre los del final del alfabeto. El fallo es **silencioso**: la ficha cae al
    `.get(cve_mun, cve_mun)` y muestra la clave INEGI cruda en vez del nombre del
    municipio — exactamente el problema que el panel venía a resolver. Se detectó mirando
    la página renderizada (`15106` salía como número), no leyendo el código.
    """
    paginas = {
        1: {"items": [{"cve_mun": f"15{i:03d}", "nombre_municipio": f"Muni {i:03d}"} for i in range(1, 101)],
            "total": 125},
        2: {"items": [{"cve_mun": f"15{i:03d}", "nombre_municipio": f"Muni {i:03d}"} for i in range(101, 126)],
            "total": 125},
    }
    pedidas = []

    def _get(url, params=None, headers=None, timeout=None):
        pedidas.append(params["page"])
        return _RespuestaFalsa(paginas[params["page"]])

    mapa = cliente.listar_municipios("http://api", "15", get=_get)
    assert len(mapa) == 125, f"solo se trajeron {len(mapa)} de 125 municipios"
    assert "15106" in mapa, "falta un municipio de la segunda pagina"
    assert pedidas == [1, 2], f"no pagino como debe: {pedidas}"


def test_una_entidad_chica_no_pide_una_segunda_pagina(cliente) -> None:
    """CDMX tiene 16 municipios: pedir una segunda pagina seria una llamada de mas.

    Importa por el rate limit de 120/min por ruta: la cascada ya consulta en cada cambio
    de selector.
    """
    pedidas = []

    def _get(url, params=None, headers=None, timeout=None):
        pedidas.append(params["page"])
        return _RespuestaFalsa(
            {"items": [{"cve_mun": "09010", "nombre_municipio": "Álvaro Obregón"}], "total": 1}
        )

    cliente.listar_municipios("http://api", "09", get=_get)
    assert pedidas == [1], f"pidio paginas de mas: {pedidas}"


def test_los_niveles_son_los_que_existen_en_gold(cliente) -> None:
    """«Media Superior» no está en Gold: el pipeline filtra a estos tres niveles.

    `1_Dashboards.py` sí la ofrece y siempre devuelve cero resultados — reportado aparte.
    Aquí se fija que este catálogo no repita el error.
    """
    assert cliente.NIVELES == ("PREESCOLAR", "PRIMARIA", "SECUNDARIA")
    assert not any("MEDIA" in n for n in cliente.NIVELES)


def test_las_entidades_son_las_cuatro_del_alcance(cliente) -> None:
    """`SCOPE_ENTIDADES` del CLAUDE.md §4. La API no sirve este catálogo."""
    assert set(cliente.ENTIDADES) == {"09", "15", "19", "14"}


def test_el_token_viaja_en_la_cabecera(cliente) -> None:
    """Sin esto, la búsqueda daría 401 contra producción con la sesión iniciada."""
    registro = []
    cliente.listar_escuelas(
        "http://api",
        get=_get_que_devuelve({"items": [], "total": 0}, registro=registro),
        access_token="abc123",
    )
    assert registro[0]["headers"] == {"Authorization": "Bearer abc123"}


def test_sin_token_no_se_manda_cabecera(cliente) -> None:
    """Mientras la lectura sea pública el panel funciona sin sesión."""
    registro = []
    cliente.listar_escuelas(
        "http://api", get=_get_que_devuelve({"items": [], "total": 0}, registro=registro)
    )
    assert registro[0]["headers"] is None
