"""Pruebas del cliente de "Cómo funciona" (US-601).

Ejercitan `src/frontend/about_client.py` completo **sin red y sin API levantada**, inyectando
el verbo HTTP por el seam `get` — mismo patrón que `test_prediccion_client.py`.

Lo que estas pruebas defienden, en orden de importancia:

1. **Un tipo de bloque desconocido no rompe el parseo.** Es el contrato hacia adelante del
   diseño de US-601: si el backend agrega un tipo de bloque nuevo mañana, esta página debe
   seguir mostrando las demás secciones con una advertencia, no tronar entera.
2. Los tres modos de fallo de una sección se distinguen (404, API caída, contrato roto), porque
   la página los presenta distinto.
3. `valor: null` de una métrica se propaga como hueco, nunca como cero — misma regla `SIN_DATO`
   de todo el proyecto.
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
    """Importa src/frontend/about_client.py como módulo (sin red en import)."""
    ruta = RAIZ / "src" / "frontend" / "about_client.py"
    spec = importlib.util.spec_from_file_location("about_client_us225", ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("about_client_us225", modulo)
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


def _get_que_devuelve(payload, status=200):
    def _get(url, headers=None, timeout=None):
        return _RespuestaFalsa(payload, status)
    return _get


MANIFEST_OK = [
    {"id": "capas", "titulo": "Capas", "orden": 3},
    {"id": "arquitectura", "titulo": "Arquitectura del backend", "orden": 1},
    {"id": "stack", "titulo": "Memoria técnica", "orden": 5},
]

SECCION_OK = {
    "id": "capas",
    "titulo": "Capas",
    "fuente": ["Data_Model.md §1-§3"],
    "advertencias": [],
    "bloques": [
        {"tipo": "markdown", "texto": "**Bronze**: copia cruda."},
        {"tipo": "mermaid", "codigo": "erDiagram\n  a ||--o{ b : x"},
        {"tipo": "tabla", "columnas": ["Capa", "Filas"], "filas": [["bronze", "45276"]]},
        {
            "tipo": "metricas",
            "items": [
                {"etiqueta": "Filas en Gold", "valor": "45276", "nota": None},
                {"etiqueta": "Filas en Bronze", "valor": None, "nota": "Sin tabla todavía."},
            ],
        },
    ],
}


# ------------------------------------------------------- manifest: orden y forma


def test_listar_secciones_ordena_por_campo_orden(cliente) -> None:
    """El manifest puede llegar en cualquier orden del backend; el cliente lo normaliza."""
    secciones = cliente.listar_secciones("http://api", get=_get_que_devuelve(MANIFEST_OK))
    assert [s.id for s in secciones] == ["arquitectura", "capas", "stack"]


def test_manifest_fuera_de_contrato_se_rechaza(cliente) -> None:
    incompleto = [{"id": "capas", "titulo": "Capas"}]  # falta "orden"
    with pytest.raises(ValueError):
        cliente.listar_secciones("http://api", get=_get_que_devuelve(incompleto))


# ------------------------------------------------------- sección: los 4 tipos de bloque


def test_obtener_seccion_parsea_los_cuatro_tipos_de_bloque(cliente) -> None:
    seccion = cliente.obtener_seccion("http://api", "capas", get=_get_que_devuelve(SECCION_OK))
    assert isinstance(seccion.bloques[0], cliente.BloqueMarkdown)
    assert isinstance(seccion.bloques[1], cliente.BloqueMermaid)
    assert isinstance(seccion.bloques[2], cliente.BloqueTabla)
    assert isinstance(seccion.bloques[3], cliente.BloqueMetricas)


def test_metrica_sin_dato_se_propaga_como_hueco_no_como_cero(cliente) -> None:
    """La prueba más importante del archivo: `valor: null` no se convierte en `"0"`."""
    seccion = cliente.obtener_seccion("http://api", "capas", get=_get_que_devuelve(SECCION_OK))
    bloque_metricas = seccion.bloques[3]
    item_sin_dato = next(i for i in bloque_metricas.items if i.etiqueta == "Filas en Bronze")
    assert item_sin_dato.valor is None
    assert item_sin_dato.nota == "Sin tabla todavía."


def test_un_tipo_de_bloque_desconocido_no_rompe_el_parseo(cliente) -> None:
    """Contrato hacia adelante: un tipo de bloque nuevo el día de mañana se degrada a
    `BloqueDesconocido` en vez de tronar toda la sección."""
    payload = {**SECCION_OK, "bloques": [{"tipo": "grafico-3d", "datos": [1, 2, 3]}]}
    seccion = cliente.obtener_seccion("http://api", "capas", get=_get_que_devuelve(payload))
    assert len(seccion.bloques) == 1
    assert isinstance(seccion.bloques[0], cliente.BloqueDesconocido)
    assert seccion.bloques[0].tipo == "grafico-3d"


def test_bloque_svg_se_parsea(cliente) -> None:
    payload = {
        **SECCION_OK,
        "bloques": [
            {
                "tipo": "svg",
                "codigo": "<svg viewBox=\"0 0 10 10\"><rect width=\"10\" height=\"10\"/></svg>",
                "alt": "Un cuadrado.",
                "alto": 560,
            }
        ],
    }
    seccion = cliente.obtener_seccion("http://api", "arquitectura", get=_get_que_devuelve(payload))
    bloque = seccion.bloques[0]
    assert isinstance(bloque, cliente.BloqueSvg)
    assert bloque.codigo.startswith("<svg")
    assert bloque.alt == "Un cuadrado."
    assert bloque.alto == 560


def test_bloque_svg_sin_alto_deja_que_el_cliente_decida(cliente) -> None:
    """`alto` es opcional: sin él la página usa su valor por defecto, no un 0 que colapsaría
    el iframe."""
    payload = {
        **SECCION_OK,
        "bloques": [{"tipo": "svg", "codigo": "<svg/>", "alt": "x"}],
    }
    seccion = cliente.obtener_seccion("http://api", "arquitectura", get=_get_que_devuelve(payload))
    assert seccion.bloques[0].alto is None


def test_bloque_svg_sin_alt_esta_fuera_de_contrato(cliente) -> None:
    """El texto alternativo no es opcional: sin él el diagrama es invisible para un lector de
    pantalla, y el `aria-label` de dentro del iframe no llega al documento padre."""
    payload = {**SECCION_OK, "bloques": [{"tipo": "svg", "codigo": "<svg/>"}]}
    with pytest.raises(ValueError):
        cliente.obtener_seccion("http://api", "arquitectura", get=_get_que_devuelve(payload))


def test_bloque_mapa_se_parsea(cliente) -> None:
    payload = {
        **SECCION_OK,
        "bloques": [
            {
                "tipo": "mapa",
                "geojson": {"type": "FeatureCollection", "features": []},
                "resaltados": [{"cve_ent": "09", "nombre": "CDMX", "color": "#4C72B0"}],
            }
        ],
    }
    seccion = cliente.obtener_seccion("http://api", "modelo-datos", get=_get_que_devuelve(payload))
    bloque = seccion.bloques[0]
    assert isinstance(bloque, cliente.BloqueMapa)
    assert bloque.resaltados[0].cve_ent == "09"
    assert bloque.geojson["type"] == "FeatureCollection"
    assert bloque.fondo is None  # el payload de la prueba no trae fondo -- opcional


def test_bloque_mapa_con_fondo_nacional(cliente) -> None:
    """El fondo nacional es opcional (`fondo: None` por default) pero cuando viene se parsea
    igual que el geojson de municipios."""
    payload = {
        **SECCION_OK,
        "bloques": [
            {
                "tipo": "mapa",
                "geojson": {"type": "FeatureCollection", "features": []},
                "fondo": {"type": "FeatureCollection", "features": [{"type": "Feature"}]},
                "resaltados": [],
            }
        ],
    }
    seccion = cliente.obtener_seccion("http://api", "modelo-datos", get=_get_que_devuelve(payload))
    bloque = seccion.bloques[0]
    assert bloque.fondo is not None
    assert bloque.fondo["type"] == "FeatureCollection"


def test_bloque_barras_se_parsea(cliente) -> None:
    """Reemplaza al icicle: una lista plana de items, no un árbol. `valor: null` se propaga
    como hueco (SIN_DATO), nunca como cero."""
    payload = {
        **SECCION_OK,
        "bloques": [
            {
                "tipo": "barras",
                "items": [
                    {"etiqueta": "Bronze", "valor": 1016.0, "nota": None},
                    {"etiqueta": "Silver", "valor": 515.0, "nota": None},
                    {"etiqueta": "Gold", "valor": None, "nota": "Ninguna tabla materializada."},
                ],
            }
        ],
    }
    seccion = cliente.obtener_seccion("http://api", "capas", get=_get_que_devuelve(payload))
    bloque = seccion.bloques[0]
    assert isinstance(bloque, cliente.BloqueBarras)
    assert bloque.items[0].valor == 1016.0
    assert bloque.items[2].valor is None  # SIN_DATO se preserva, no se convierte en 0.0
    assert bloque.items[2].nota == "Ninguna tabla materializada."


def test_bloque_diagrama_flujo_se_parsea(cliente) -> None:
    payload = {
        **SECCION_OK,
        "bloques": [
            {
                "tipo": "diagrama_flujo",
                "nodos": [
                    {"id": "gold.fact_escuela_ciclo", "columna": 0, "etiqueta": "fact_escuela_ciclo"},
                    {"id": "cubo_matricula", "columna": 1, "etiqueta": "cubo_matricula"},
                    {"id": "DB-01", "columna": 2, "etiqueta": "DB-01"},
                ],
                "enlaces": [
                    {"origen": "gold.fact_escuela_ciclo", "destino": "cubo_matricula"},
                    {"origen": "cubo_matricula", "destino": "DB-01"},
                ],
            }
        ],
    }
    seccion = cliente.obtener_seccion("http://api", "cubos", get=_get_que_devuelve(payload))
    bloque = seccion.bloques[0]
    assert isinstance(bloque, cliente.BloqueDiagramaFlujo)
    assert len(bloque.nodos) == 3
    assert bloque.enlaces[1].destino == "DB-01"


def test_bloque_conocido_pero_mal_formado_se_rechaza(cliente) -> None:
    """Un `tipo: "tabla"` sin `columnas` es un bloque roto, no uno desconocido: debe fallar
    fuerte en vez de degradarse en silencio."""
    payload = {**SECCION_OK, "bloques": [{"tipo": "tabla", "filas": [["x"]]}]}
    with pytest.raises(ValueError):
        cliente.obtener_seccion("http://api", "capas", get=_get_que_devuelve(payload))


# ------------------------------------------------------- los tres modos de fallo


def test_seccion_inexistente_se_distingue_de_una_caida(cliente) -> None:
    with pytest.raises(LookupError):
        cliente.obtener_seccion("http://api", "no-existe", get=_get_que_devuelve({}, status=404))


def test_api_caida_es_error_de_conexion(cliente) -> None:
    def _get(url, headers=None, timeout=None):
        raise httpx.ConnectError("sin ruta")

    with pytest.raises(cliente.AboutNoDisponible):
        cliente.obtener_seccion("http://api", "capas", get=_get)


def test_respuesta_fuera_de_contrato_se_rechaza(cliente) -> None:
    incompleto = {k: v for k, v in SECCION_OK.items() if k != "bloques"}
    with pytest.raises(ValueError):
        cliente.obtener_seccion("http://api", "capas", get=_get_que_devuelve(incompleto))
