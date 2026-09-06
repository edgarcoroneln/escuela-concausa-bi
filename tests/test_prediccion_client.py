"""Pruebas del cliente de inferencia del panel de ML (US-207).

Ejercitan `src/frontend/prediccion_client.py` completo **sin red y sin API levantada**,
inyectando el verbo HTTP por el seam `get` — mismo patrón que `agente_client.py`.

Lo que estas pruebas defienden, en orden de importancia:

1. **`cluster = None` se propaga como hueco, nunca como cero.** ML-03 (US-321) no tiene
   productor todavía; si alguien "arregla" el `None` con un `0`, el panel afirmaría que la
   escuela pertenece al segmento 0 cuando nadie lo midió. Es la regla del proyecto y el
   modo de falla que ya costó BUG-017 y BUG-031.
2. **El umbral de 0.60 es el de DEC-006**, y `en_riesgo` se deriva de él — no se re-declara
   en la página.
3. Los tres modos de fallo se distinguen (404, API caída, contrato roto), porque la página
   los presenta distinto.
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
    """Importa src/frontend/prediccion_client.py como módulo (sin red en import)."""
    ruta = RAIZ / "src" / "frontend" / "prediccion_client.py"
    spec = importlib.util.spec_from_file_location("prediccion_client_us207", ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("prediccion_client_us207", modulo)
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


PAYLOAD_OK = {
    "cct": "15DJN0049A",
    "id_ciclo": "2024-2025",
    "indice_riesgo": 0.7423,
    "driver_dominante": "D1",
    "recomendacion": "Priorizar programas de becas y apoyo alimentario en la zona.",
    "cluster": None,
    "mlflow_run_id": "local-sin-mlflow",
}


def _get_que_devuelve(payload, status=200):
    def _get(url, headers=None, timeout=None):
        return _RespuestaFalsa(payload, status)
    return _get


# --------------------------------------------------------- ML-03: el hueco se respeta


def test_cluster_nulo_se_propaga_como_hueco_no_como_cero(cliente) -> None:
    """La prueba más importante del archivo.

    ML-03 (US-321) no tiene productor: la API devuelve `cluster: null`. Convertirlo en `0`
    haría que el panel afirmara que la escuela pertenece al segmento 0 cuando nadie lo
    midió — el mismo modo de falla de BUG-017 y BUG-031.
    """
    pred = cliente.obtener_prediccion("http://api", "15DJN0049A", get=_get_que_devuelve(PAYLOAD_OK))
    assert pred.cluster is None, "cluster nulo se convirtió en un valor inventado"
    assert pred.tiene_cluster is False, (
        "tiene_cluster debe ser False sin dato, para que la página pinte SIN_DATO"
    )


def test_cuando_ml03_aterrice_el_cluster_se_respeta(cliente) -> None:
    """Guarda hacia adelante: el día que US-321 publique, el cliente ya lo pasa."""
    pred = cliente.obtener_prediccion(
        "http://api", "15DJN0049A", get=_get_que_devuelve({**PAYLOAD_OK, "cluster": 3})
    )
    assert pred.cluster == 3
    assert pred.tiene_cluster is True


def test_un_cluster_no_entero_se_rechaza(cliente) -> None:
    """`cluster` es `StrictInt | None` en el contrato: una cadena es contrato roto."""
    with pytest.raises(ValueError):
        cliente.obtener_prediccion(
            "http://api", "15DJN0049A", get=_get_que_devuelve({**PAYLOAD_OK, "cluster": "3"})
        )


# --------------------------------------------------------- ML-01: el umbral de DEC-006


def test_el_umbral_es_el_de_dec_006(cliente) -> None:
    assert cliente.UMBRAL_RIESGO == 0.60


@pytest.mark.parametrize(
    "riesgo, esperado",
    [(0.7423, True), (0.60, True), (0.5999, False), (0.1637, False)],
)
def test_en_riesgo_se_deriva_del_umbral(cliente, riesgo: float, esperado: bool) -> None:
    """`>= 0.60`, no `> 0.60`: exactamente 0.60 ya es "pierde 5 %"."""
    pred = cliente.obtener_prediccion(
        "http://api", "15DJN0049A", get=_get_que_devuelve({**PAYLOAD_OK, "indice_riesgo": riesgo})
    )
    assert pred.en_riesgo is esperado


# --------------------------------------------------------- los tres modos de fallo


def test_cct_inexistente_se_distingue_de_una_caida(cliente) -> None:
    """404 no es lo mismo que la API caída: la página los presenta distinto."""
    with pytest.raises(cliente.EscuelaNoEncontrada):
        cliente.obtener_prediccion(
            "http://api", "00XXX00000", get=_get_que_devuelve({}, status=404)
        )


def test_gold_inalcanzable_es_error_de_conexion(cliente) -> None:
    """503 lo emite la API cuando Gold no responde (US-416)."""
    with pytest.raises(ConnectionError):
        cliente.obtener_prediccion(
            "http://api", "15DJN0049A", get=_get_que_devuelve({}, status=503)
        )


def test_api_caida_es_error_de_conexion(cliente) -> None:
    def _get(url, headers=None, timeout=None):
        raise httpx.ConnectError("sin ruta")

    with pytest.raises(ConnectionError):
        cliente.obtener_prediccion("http://api", "15DJN0049A", get=_get)


def test_respuesta_fuera_de_contrato_se_rechaza(cliente) -> None:
    """Falta `driver_dominante`: mejor fallar que pintar una recomendación huérfana."""
    incompleto = {k: v for k, v in PAYLOAD_OK.items() if k != "driver_dominante"}
    with pytest.raises(ValueError):
        cliente.obtener_prediccion("http://api", "15DJN0049A", get=_get_que_devuelve(incompleto))


# --------------------------------------------------------- entrada


@pytest.mark.parametrize("cct", ["", "123", "15DJN0049A1"])
def test_un_cct_de_longitud_invalida_no_llega_a_la_api(cliente, cct: str) -> None:
    """Se valida antes de salir a la red, para no gastar una llamada en algo imposible."""
    def _get(*a, **k):
        raise AssertionError("no debió llamarse a la API")

    with pytest.raises(ValueError):
        cliente.obtener_prediccion("http://api", cct, get=_get)


def test_el_cct_se_normaliza_a_mayusculas(cliente) -> None:
    """Quien teclea a mano escribe minúsculas; la clave canónica es en mayúsculas."""
    llamadas = []

    def _get(url, headers=None, timeout=None):
        llamadas.append(url)
        return _RespuestaFalsa(PAYLOAD_OK)

    cliente.obtener_prediccion("http://api", " 15djn0049a ", get=_get)
    assert llamadas[0].endswith("/api/v1/predicciones/15DJN0049A")
