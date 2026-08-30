"""Prueba de BUG-008.

Verifica que la aplicacion configurada en docker/api.Dockerfile
expone las rutas del contrato v1.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DOCKERFILE = RAIZ / "docker" / "api.Dockerfile"

# Referencia oficial del contrato v1: el modulo que SI debe exponer el
# contrato completo (US-401). No se escribe ninguna ruta a mano: se leen
# dinamicamente de su propio esquema OpenAPI, para que la prueba nunca quede
# desactualizada cuando el contrato crezca (pedido explicito de Edgar tras
# revisar el primer borrador de esta prueba).
MODULO_CONTRATO_V1 = "src.api.app"
ATRIBUTO_CONTRATO_V1 = "app"


def _extraer_app_del_cmd(texto_dockerfile: str) -> str:
    """Extrae la referencia modulo:atributo declarada en el CMD de uvicorn.

    Ejemplo: 'CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT}'
    devuelve 'src.api.main:app'.
    """
    coincidencia = re.search(r"CMD\s+uvicorn\s+([\w\.]+:\w+)", texto_dockerfile)
    assert coincidencia, "No se encontro una referencia modulo:app en el CMD de uvicorn"
    return coincidencia.group(1)


def _importar_app(referencia: str):
    """Importa dinamicamente la app FastAPI que el Dockerfile declara arrancar."""
    modulo_nombre, atributo = referencia.split(":")
    modulo = importlib.import_module(modulo_nombre)
    return getattr(modulo, atributo)


def _rutas_del_contrato_v1() -> set[str]:
    """Rutas oficiales del contrato v1, leidas del esquema OpenAPI en vivo.

    Se importa src.api.app (la app de referencia de US-401, no la que arranca
    el Dockerfile) y se leen sus rutas desde app.openapi()["paths"]. Nunca se
    escribe una ruta a mano: si el contrato crece o cambia, esta funcion
    siempre refleja el estado real del codigo.
    """
    modulo = importlib.import_module(MODULO_CONTRATO_V1)
    app_contrato = getattr(modulo, ATRIBUTO_CONTRATO_V1)
    return set(app_contrato.openapi()["paths"].keys())


def test_dockerfile_declara_un_cmd_uvicorn() -> None:
    """BUG-008: el Dockerfile debe declarar un CMD de uvicorn."""
    contenido = DOCKERFILE.read_text(encoding="utf-8")
    assert "CMD uvicorn" in contenido


def test_referencia_del_cmd_es_extraible() -> None:
    """El CMD debe declarar una referencia valida modulo:atributo."""
    contenido = DOCKERFILE.read_text(encoding="utf-8")
    referencia = _extraer_app_del_cmd(contenido)
    assert ":" in referencia


def test_app_que_arranca_el_contenedor_expone_el_contrato_v1() -> None:
    """BUG-008: la app que el Dockerfile arranca debe exponer el contrato v1.

    Este es el corazon del bug: hoy el CMD apunta a 'src.api.main:app' (el
    hola-mundo de 3 rutas), no a 'src.api.app:app' (el contrato real con 18
    rutas bajo /api/v1). Esta prueba falla mientras el Dockerfile no arranque
    la app correcta, y protege contra que el bug regrese en el futuro.

    Las rutas esperadas NO estan escritas a mano: se obtienen en vivo del
    esquema OpenAPI de src.api.app (la fuente oficial del contrato v1), para
    que la prueba nunca genere falsos positivos cuando el contrato crezca con
    rutas legitimas nuevas.
    """
    contenido = DOCKERFILE.read_text(encoding="utf-8")
    referencia = _extraer_app_del_cmd(contenido)
    app_arrancada = _importar_app(referencia)

    rutas_esperadas = _rutas_del_contrato_v1()
    rutas_expuestas = set(app_arrancada.openapi()["paths"].keys())

    faltantes = sorted(rutas_esperadas - rutas_expuestas)

    assert not faltantes, (
        f"El Dockerfile arranca '{referencia}', que NO expone el contrato v1. "
        f"Faltan {len(faltantes)} de {len(rutas_esperadas)} rutas: {faltantes}. "
        "El CMD debe apuntar a 'src.api.app:app' (BUG-008)."
    )
